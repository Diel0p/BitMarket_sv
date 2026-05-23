"""
Order Service â€” cart validation, order creation, payment confirmation.

Flow:
  POST /api/orders
    â†’ validate stock for each item
    â†’ create Order document
    â†’ call payment_service.create_invoice()
    â†’ return order + BOLT11 invoice string

  GET /api/orders/payment-status/{hash}
    â†’ poll payment_service.check_invoice_status()
    â†’ if paid: update order + invoice status
"""

from fastapi import HTTPException

from app.app.config.database import (
    db_insert, db_find_one, db_find_all, db_update,
)
from app.app.models.order import OrderCreateRequest, FulfillmentUpdateRequest
from app.app.config.settings import get_settings
from app.app.services import payment_service
from app.app.utils.helpers import sats_to_btc, utcnow

settings = get_settings()


def _group_order_items_by_seller(order_items: list[dict]) -> dict[str, int]:
    seller_totals: dict[str, int] = {}
    for item in order_items:
        seller_id = item["seller_id"]
        seller_totals[seller_id] = seller_totals.get(seller_id, 0) + item["subtotal_sats"]
    return seller_totals


async def _process_seller_payouts(order: dict, db) -> dict:
    existing_payouts = order.get("payouts") or []
    existing_commission = order.get("commission_payout")
    if existing_payouts:
        # Make payout handling idempotent: if already processed, reuse stored outcome.
        statuses = {p.get("status") for p in existing_payouts}
        commission_status = (existing_commission or {}).get("status")
        if statuses == {"paid"}:
            if commission_status in {"paid", "skipped"}:
                return {
                    "payout_status": "paid",
                    "payouts": existing_payouts,
                    "commission_payout": existing_commission,
                }
            return {
                "payout_status": "partial",
                "payouts": existing_payouts,
                "commission_payout": existing_commission,
            }
        if "failed" in statuses and "paid" in statuses:
            return {
                "payout_status": "partial",
                "payouts": existing_payouts,
                "commission_payout": existing_commission,
            }
        return {
            "payout_status": order.get("payout_status", "failed"),
            "payouts": existing_payouts,
            "commission_payout": existing_commission,
        }

    fee_percent = float(order.get("marketplace_fee_percent", settings.marketplace_fee_percent))
    seller_totals = _group_order_items_by_seller(order.get("items", []))
    payouts = []
    total_commission_sats = 0

    for seller_id, gross_sats in seller_totals.items():
        seller = db_find_one("users", id=seller_id)
        fee_sats = int(gross_sats * fee_percent / 100)
        payout_sats = gross_sats - fee_sats
        total_commission_sats += fee_sats
        payout_record = {
            "seller_id": seller_id,
            "seller_name": seller.get("name") if seller else "Unknown",
            "seller_lightning_address": seller.get("lightning_address") if seller else None,
            "gross_sats": gross_sats,
            "platform_fee_sats": fee_sats,
            "payout_sats": payout_sats,
            "status": "pending",
            "payment_hash": None,
            "error": None,
        }

        if not seller or not seller.get("lightning_address"):
            # Record failure per seller instead of aborting the whole order settlement.
            payout_record["status"] = "failed"
            payout_record["error"] = "Seller does not have a Lightning Address configured"
            payouts.append(payout_record)
            continue

        try:
            payout = await payment_service.payout_to_lightning_address(
                seller["lightning_address"],
                payout_sats,
                f"BitMarket payout {order['id'][-8:].upper()}",
                seller_invoice_key=seller.get("lnbits_invoice_key"),
            )
            payout_record["status"] = "paid"
            payout_record["payment_hash"] = payout.get("payment_hash")
            payout_record["is_mock"] = payout.get("is_mock", True)
        except Exception as exc:
            payout_record["status"] = "failed"
            payout_record["error"] = str(exc)

        payouts.append(payout_record)

    raw_commission_address = (settings.platform_commission_lightning_address or "").strip()
    # Skip explicit payout if address is empty or still has the default placeholder.
    # The 5% is already retained in the platform wallet because the buyer paid
    # the invoice created by the platform's admin key.
    _is_placeholder = not raw_commission_address or "REEMPLAZAR" in raw_commission_address.upper()
    commission_address = "" if _is_placeholder else raw_commission_address.lower()

    commission_payout = {
        "type": "platform_commission",
        "destination": commission_address or "platform_wallet",
        "amount_sats": total_commission_sats,
        "status": "pending",
        "payment_hash": None,
        "error": None,
    }

    if total_commission_sats <= 0:
        commission_payout["status"] = "skipped"
        commission_payout["error"] = "No commission amount to payout"
    elif not commission_address:
        # 5% stays in the platform wallet — no explicit transfer needed
        commission_payout["status"] = "retained"
        commission_payout["destination"] = "platform_wallet"
        commission_payout["error"] = None
    else:
        try:
            payout = await payment_service.payout_to_lightning_address(
                commission_address,
                total_commission_sats,
                f"BitMarket commission {order['id'][-8:].upper()}",
            )
            commission_payout["status"] = "paid"
            commission_payout["payment_hash"] = payout.get("payment_hash")
            commission_payout["is_mock"] = payout.get("is_mock", True)
        except Exception as exc:
            commission_payout["status"] = "failed"
            commission_payout["error"] = str(exc)

    payout_status = "paid"
    if any(p["status"] == "failed" for p in payouts) or commission_payout.get("status") == "failed":
        payout_status = "partial" if any(p["status"] == "paid" for p in payouts) else "failed"
    elif commission_payout.get("status") == "pending":
        payout_status = "pending"

    db_update(
        "orders",
        order["id"],
        {
            "payouts": payouts,
            "commission_payout": commission_payout,
            "payout_status": payout_status,
        },
    )
    return {
        "payout_status": payout_status,
        "payouts": payouts,
        "commission_payout": commission_payout,
    }


async def create_order(data: OrderCreateRequest, buyer_id: str, db) -> dict:
    if not data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    order_items = []
    total_sats  = 0

    for item in data.items:
        # Re-read product state at checkout time; never trust client-side stock/price snapshots.
        product = db_find_one("products", id=item.product_id)
        if not product or product.get("status") != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} is not available",
            )
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for: {product['title']} (available: {product['stock']})",
            )

        subtotal    = product["price_sats"] * item.quantity
        total_sats += subtotal

        order_items.append({
            "product_id":         product["id"],
            "seller_id":          product["seller_id"],
            "title":              product["title"],
            "price_sats":         product["price_sats"],
            "quantity":           item.quantity,
            "subtotal_sats":      subtotal,
            "fulfillment_status": "pending",
        })

    fee_percent = max(0.0, settings.marketplace_fee_percent)
    platform_fee_sats = int(total_sats * fee_percent / 100)
    seller_net_sats = total_sats - platform_fee_sats

    # Create order
    order_doc = {
        "buyer_id":        buyer_id,
        "items":           order_items,
        "total_sats":      total_sats,
        "total_btc":       sats_to_btc(total_sats),
        "marketplace_fee_percent": fee_percent,
        "platform_fee_sats": platform_fee_sats,
        "seller_net_sats": seller_net_sats,
        "payment_status":  "awaiting_payment",
        "order_status":    "pending",
        "shipping_address": data.shipping_address.model_dump(),
        "notes":           data.notes,
        "invoice_id":      None,
        "paid_at":         None,
        "created_at":      utcnow().isoformat(),
    }
    order_id = db_insert("orders", order_doc)

    # Generate Lightning invoice
    invoice_data = await payment_service.create_invoice(
        amount_sats=total_sats,
        memo=f"BitMarket SV Order {order_id[-8:].upper()}",
        order_id=order_id,
    )

    # Save invoice
    invoice_doc = {
        "order_id":        order_id,
        "buyer_id":        buyer_id,
        "payment_hash":    invoice_data["payment_hash"],
        "payment_request": invoice_data["payment_request"],
        "amount_sats":     total_sats,
        "status":          "pending",
        "expires_at":      invoice_data["expires_at"].isoformat(),
        "is_mock":         invoice_data["is_mock"],
        "paid_at":         None,
        "created_at":      utcnow().isoformat(),
    }
    db_insert("invoices", invoice_doc)

    # Decrement stock
    # Reserve stock only after order+invoice are persisted to keep audit traceability.
    for item in order_items:
        product = db_find_one("products", id=item["product_id"])
        if product:
            db_update("products", item["product_id"], {"stock": product["stock"] - item["quantity"]})

    # Attach invoice_id to order
    db_update("orders", order_id, {"invoice_id": invoice_data["payment_hash"]})

    return {
        "order_id":   order_id,
        "total_sats": total_sats,
        "marketplace_fee_percent": fee_percent,
        "platform_fee_sats": platform_fee_sats,
        "seller_net_sats": seller_net_sats,
        "invoice": {
            "payment_hash":    invoice_data["payment_hash"],
            "payment_request": invoice_data["payment_request"],
            "amount_sats":     total_sats,
            "status":          "pending",
            "expires_at":      invoice_data["expires_at"].isoformat(),
            "is_mock":         invoice_data["is_mock"],
            "created_at":      utcnow().isoformat(),
        },
    }


async def check_and_confirm_payment(payment_hash: str, db) -> dict:
    invoice = db_find_one("invoices", payment_hash=payment_hash)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.get("status") == "paid":
        # Fast path for repeated polls: return cached paid state without side effects.
        order = db_find_one("orders", invoice_id=payment_hash)
        return {
            "payment_hash": payment_hash,
            "payment_request": invoice.get("payment_request"),
            "paid": True,
            "status": "paid",
            "settled_at": invoice.get("paid_at"),
            "payout_status": order.get("payout_status") if order else None,
            "payouts": order.get("payouts", []) if order else [],
            "commission_payout": order.get("commission_payout") if order else None,
        }

    result = await payment_service.check_invoice_status(payment_hash)

    if result["paid"]:
        # Persist payment confirmation before triggering payouts to avoid double processing.
        settled_at = result.get("settled_at") or utcnow()
        settled_str = settled_at.isoformat() if hasattr(settled_at, "isoformat") else str(settled_at)

        db_update("invoices", invoice["id"], {"status": "paid", "paid_at": settled_str})

        # Update linked order
        order = db_find_one("orders", invoice_id=payment_hash)
        if order:
            db_update("orders", order["id"], {
                "payment_status": "paid",
                "order_status":   "confirmed",
                "paid_at":        settled_str,
            })
            payout_result = await _process_seller_payouts({**order, "paid_at": settled_str}, db)
        else:
            payout_result = {"payout_status": None, "payouts": [], "commission_payout": None}
    else:
        payout_result = {"payout_status": None, "payouts": [], "commission_payout": None}

    return {
        "payment_hash": payment_hash,
        "payment_request": invoice.get("payment_request"),
        "paid":         result["paid"],
        "status":       "paid" if result["paid"] else "pending",
        "settled_at":   result.get("settled_at"),
        "is_mock":      result.get("is_mock", True),
        "payout_status": payout_result["payout_status"],
        "payouts": payout_result["payouts"],
        "commission_payout": payout_result["commission_payout"],
    }


async def get_buyer_orders(buyer_id: str, db) -> list[dict]:
    # Backfill safety: older paid cart checkouts may exist without mirrored orders.
    paid_cart_orders = db_find_all("cart_orders", buyer_id=buyer_id, payment_status="paid")
    if paid_cart_orders:
        from app.app.services.cart_service import _ensure_orders_from_cart_order

        for cart_order in paid_cart_orders:
            if not db_find_one("orders", cart_order_id=cart_order["id"]):
                await _ensure_orders_from_cart_order(cart_order)

    return db_find_all("orders", buyer_id=buyer_id)


async def get_seller_orders(seller_id: str, db) -> list[dict]:
    all_orders = db_find_all("orders")
    result = []
    for order in all_orders:
        if any(item["seller_id"] == seller_id for item in order.get("items", [])):
            result.append(order)
    return result


async def update_fulfillment(order_id: str, data: FulfillmentUpdateRequest, seller_id: str, db) -> dict:
    order = db_find_one("orders", id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = order.get("items", [])
    if data.item_index >= len(items):
        raise HTTPException(status_code=400, detail="Invalid item index")
    if items[data.item_index]["seller_id"] != seller_id:
        raise HTTPException(status_code=403, detail="You don't own this item")

    items[data.item_index]["fulfillment_status"] = data.status.value
    db_update("orders", order_id, {"items": items})
    return {"message": "Fulfillment status updated", "new_status": data.status.value}

