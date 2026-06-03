"""
Cart Service
============
Manages the shopping cart lifecycle:

  - add_item / remove_item / clear_cart
  - Cart auto-expires 20 min after first item is added
  - checkout() generates ONE Lightning invoice (total carrito)
  - After payment confirmed → distributes payouts per vendor internally

Cart document structure (stored in "carts" collection):
{
  "id": str,
  "buyer_id": str,
  "items": [ { product_id, title, price_sats, quantity, subtotal_sats, seller_id } ],
  "total_sats": int,
  "status": "active" | "checked_out" | "expired" | "cancelled",
  "expires_at": ISO str  (20 min from creation),
  "created_at": ISO str,
}
"""

from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.app.config.database import (
    db_insert, db_find_one, db_find_all, db_update, new_id,
)
from app.app.models.order import CartCheckoutRequest
from app.app.config.settings import get_settings
from app.app.services import payment_service
from app.app.utils.helpers import utcnow, sats_to_btc

settings = get_settings()

CART_TTL_MINUTES = 20       # carrito expira 20 min desde creación
INVOICE_TTL_SECONDS = 300   # invoice expira 5 min desde checkout


# ── Helpers ────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expires_at(minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _is_expired(cart: dict) -> bool:
    expires_at = cart.get("expires_at")
    if not expires_at:
        return False
    exp = datetime.fromisoformat(expires_at)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp


def _assert_active(cart: dict) -> None:
    if cart["status"] != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Cart is not active (status: {cart['status']})",
        )
    if _is_expired(cart):
        db_update("carts", cart["id"], {"status": "expired"})
        raise HTTPException(status_code=410, detail="Cart has expired")


# ── Public API ─────────────────────────────────────────────

def get_cart(buyer_id: str) -> dict | None:
    """Return the active cart for buyer, or None."""
    cart = db_find_one("carts", buyer_id=buyer_id, status="active")
    if cart and _is_expired(cart):
        db_update("carts", cart["id"], {"status": "expired"})
        return None
    return cart


def get_or_create_cart(buyer_id: str) -> dict:
    """Return existing active cart or create a new one."""
    cart = get_cart(buyer_id)
    if cart:
        return cart
    now = _now_iso()
    doc = {
        "id": new_id(),
        "buyer_id": buyer_id,
        "items": [],
        "total_sats": 0,
        "status": "active",
        "expires_at": _expires_at(CART_TTL_MINUTES),
        "created_at": now,
    }
    db_insert("carts", doc)
    return doc


def add_item(buyer_id: str, product_id: str, quantity: int) -> dict:
    """Add or update a product in the cart. Returns updated cart."""
    cart = get_or_create_cart(buyer_id)
    _assert_active(cart)

    product = db_find_one("products", id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.get("status") != "active":
        raise HTTPException(status_code=400, detail="Product is not available")
    if product.get("stock", 0) < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {product.get('stock', 0)}",
        )

    items: list[dict] = list(cart.get("items", []))

    # Update quantity if already in cart
    existing = next((i for i in items if i["product_id"] == product_id), None)
    if existing:
        new_qty = existing["quantity"] + quantity
        if product.get("stock", 0) < new_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock. Available: {product.get('stock', 0)}",
            )
        existing["quantity"] = new_qty
        existing["subtotal_sats"] = product["price_sats"] * new_qty
    else:
        items.append({
            "product_id": product_id,
            "title": product["title"],
            "price_sats": product["price_sats"],
            "quantity": quantity,
            "subtotal_sats": product["price_sats"] * quantity,
            "seller_id": product["seller_id"],
        })

    total = sum(i["subtotal_sats"] for i in items)
    updated = db_update("carts", cart["id"], {"items": items, "total_sats": total})
    return updated


def update_item(buyer_id: str, product_id: str, quantity: int) -> dict:
    """Set exact quantity for a cart item. quantity=0 removes it."""
    cart = get_cart(buyer_id)
    if not cart:
        raise HTTPException(status_code=404, detail="No active cart")
    _assert_active(cart)

    items: list[dict] = list(cart.get("items", []))

    if quantity == 0:
        items = [i for i in items if i["product_id"] != product_id]
    else:
        product = db_find_one("products", id=product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.get("stock", 0) < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock. Available: {product.get('stock', 0)}",
            )
        existing = next((i for i in items if i["product_id"] == product_id), None)
        if not existing:
            raise HTTPException(status_code=404, detail="Item not in cart")
        existing["quantity"] = quantity
        existing["subtotal_sats"] = existing["price_sats"] * quantity

    total = sum(i["subtotal_sats"] for i in items)
    updated = db_update("carts", cart["id"], {"items": items, "total_sats": total})
    return updated


def remove_item(buyer_id: str, product_id: str) -> dict:
    """Remove a product from the cart."""
    return update_item(buyer_id, product_id, 0)


def clear_cart(buyer_id: str) -> dict:
    """Remove all items from the active cart."""
    cart = get_cart(buyer_id)
    if not cart:
        raise HTTPException(status_code=404, detail="No active cart")
    _assert_active(cart)
    updated = db_update("carts", cart["id"], {"items": [], "total_sats": 0})
    return updated


async def checkout(buyer_id: str, data: CartCheckoutRequest) -> dict:
    """
    Initiate checkout:
      1. Validate cart and stock
      2. Create ONE Lightning invoice for the full cart total
      3. Create a pending cart_order document
      4. Mark cart as checked_out
      5. Return invoice details + cart_order_id
    """
    cart = get_cart(buyer_id)
    if not cart:
        raise HTTPException(status_code=404, detail="No active cart")
    _assert_active(cart)

    items = cart.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Re-validate stock for every item before locking
    for item in items:
        product = db_find_one("products", id=item["product_id"])
        if not product or product.get("status") != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Product '{item['title']}' is no longer available",
            )
        if product.get("stock", 0) < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{item['title']}'",
            )

    total_sats = cart["total_sats"]
    memo = f"BitMarket carrito {cart['id'][-8:].upper()} ({len(items)} items)"

    invoice = await payment_service.create_invoice(
        amount_sats=total_sats,
        memo=memo,
        order_id=cart["id"],
    )

    now = _now_iso()
    invoice_expires = (
        datetime.now(timezone.utc) + timedelta(seconds=INVOICE_TTL_SECONDS)
    ).isoformat()

    # Create a cart_order document that tracks this checkout
    cart_order = {
        "id": new_id(),
        "cart_id": cart["id"],
        "buyer_id": buyer_id,
        "items": items,
        "total_sats": total_sats,
        "payment_status": "awaiting_payment",
        "shipping_address": data.shipping_address.model_dump(),
        "notes": data.notes,
        "payment_hash": invoice["payment_hash"],
        "payment_request": invoice["payment_request"],
        "invoice_expires_at": invoice_expires,
        "marketplace_fee_percent": settings.marketplace_fee_percent,
        "payouts": [],
        "payout_status": None,
        "created_at": now,
        "paid_at": None,
    }
    db_insert("cart_orders", cart_order)

    # Mark cart as checked out so it can't be modified
    db_update("carts", cart["id"], {
        "status": "checked_out",
        "cart_order_id": cart_order["id"],
    })

    return {
        "cart_order_id": cart_order["id"],
        "payment_hash": invoice["payment_hash"],
        "payment_request": invoice["payment_request"],
        "amount_sats": total_sats,
        "expires_at": invoice_expires,
        "is_mock": invoice.get("is_mock", False),
    }


async def confirm_payment(payment_hash: str) -> dict:
    """
    Check payment status for a cart_order invoice.
    If paid: process payouts and create individual orders per seller.
    Returns { paid, cart_order_id, orders, ... }
    """
    from app.app.services import order_service  # avoid circular import

    cart_order = db_find_one("cart_orders", payment_hash=payment_hash)
    if not cart_order:
        raise HTTPException(status_code=404, detail="Cart order not found")

    # Already confirmed previously — return cached result
    if cart_order["payment_status"] == "paid":
        created_order_ids = await _ensure_orders_from_cart_order(cart_order)
        return {
            "paid": True,
            "cart_order_id": cart_order["id"],
            "payment_request": cart_order.get("payment_request"),
            "payout_status": cart_order.get("payout_status"),
            "order_ids": created_order_ids,
        }

    # Check invoice expiry
    invoice_expires = cart_order.get("invoice_expires_at")
    if invoice_expires:
        exp = datetime.fromisoformat(invoice_expires)
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > exp and cart_order["payment_status"] != "paid":
            db_update("cart_orders", cart_order["id"], {"payment_status": "expired"})
            # Cancel and clear cart after invoice expiry so stale items are not kept locked in checkout state.
            if cart_order.get("cart_id"):
                db_update("carts", cart_order["cart_id"], {
                    "status": "expired",
                    "items": [],
                    "total_sats": 0,
                    "expires_at": _now_iso(),
                })
            return {"paid": False, "expired": True, "cart_order_id": cart_order["id"]}

    status = await payment_service.check_invoice_status(payment_hash)

    if not status["paid"]:
        return {
            "paid": False,
            "cart_order_id": cart_order["id"],
            "payment_request": cart_order.get("payment_request"),
            "is_mock": status.get("is_mock", False),
        }

    # ── Payment confirmed ─────────────────────────────────
    now = _now_iso()
    db_update("cart_orders", cart_order["id"], {
        "payment_status": "paid",
        "paid_at": now,
    })

    created_order_ids = await _ensure_orders_from_cart_order({**cart_order, "payment_status": "paid", "paid_at": now})

    # Deduct stock for each item
    for item in cart_order.get("items", []):
        product = db_find_one("products", id=item["product_id"])
        if product:
            new_stock = max(0, product.get("stock", 0) - item["quantity"])
            db_update("products", item["product_id"], {"stock": new_stock})

    # Process payouts per seller
    payout_result = await _process_cart_payouts(cart_order)
    db_update("cart_orders", cart_order["id"], {
        "payouts": payout_result["payouts"],
        "payout_status": payout_result["payout_status"],
    })

    return {
        "paid": True,
        "cart_order_id": cart_order["id"],
        "payout_status": payout_result["payout_status"],
        "payment_request": cart_order.get("payment_request"),
        "order_ids": created_order_ids,
    }


async def _ensure_orders_from_cart_order(cart_order: dict) -> list[str]:
    """
    Ensure paid cart checkout is represented in the canonical orders collection.
    Creates one order per seller and is safe to call multiple times.
    """
    if not cart_order:
        return []

    existing_orders = db_find_all("orders", cart_order_id=cart_order["id"])
    if existing_orders:
        order_ids = [o["id"] for o in existing_orders if o.get("id")]
        if not cart_order.get("created_order_ids"):
            db_update("cart_orders", cart_order["id"], {"created_order_ids": order_ids})
        return order_ids

    fee_percent = float(cart_order.get("marketplace_fee_percent", settings.marketplace_fee_percent))
    items_by_seller: dict[str, list[dict]] = {}
    for item in cart_order.get("items", []):
        seller_id = item.get("seller_id")
        if not seller_id:
            continue
        normalized_item = {
            "product_id": item.get("product_id"),
            "seller_id": seller_id,
            "title": item.get("title", "Item"),
            "price_sats": int(item.get("price_sats", 0)),
            "quantity": int(item.get("quantity", 1)),
            "subtotal_sats": int(item.get("subtotal_sats", 0)),
            "fulfillment_status": item.get("fulfillment_status", "pending"),
        }
        items_by_seller.setdefault(seller_id, []).append(normalized_item)

    created_ids: list[str] = []
    for seller_id, seller_items in items_by_seller.items():
        total_sats = sum(i["subtotal_sats"] for i in seller_items)
        platform_fee_sats = int(total_sats * fee_percent / 100)
        seller_net_sats = total_sats - platform_fee_sats

        order_doc = {
            "buyer_id": cart_order.get("buyer_id"),
            "items": seller_items,
            "total_sats": total_sats,
            "total_btc": sats_to_btc(total_sats),
            "marketplace_fee_percent": fee_percent,
            "platform_fee_sats": platform_fee_sats,
            "seller_net_sats": seller_net_sats,
            "payment_status": "paid",
            "order_status": "confirmed",
            "shipping_address": cart_order.get("shipping_address"),
            "notes": cart_order.get("notes"),
            "invoice_id": cart_order.get("payment_hash"),
            "cart_order_id": cart_order.get("id"),
            "paid_at": cart_order.get("paid_at") or _now_iso(),
            "created_at": cart_order.get("created_at") or _now_iso(),
        }
        new_order_id = db_insert("orders", order_doc)
        created_ids.append(new_order_id)

    if created_ids:
        db_update("cart_orders", cart_order["id"], {"created_order_ids": created_ids})
    return created_ids


async def _process_cart_payouts(cart_order: dict) -> dict:
    """Distribute funds to each seller after payment is confirmed."""
    fee_percent = float(
        cart_order.get("marketplace_fee_percent", settings.marketplace_fee_percent)
    )

    # Group items by seller
    seller_totals: dict[str, int] = {}
    for item in cart_order.get("items", []):
        sid = item["seller_id"]
        seller_totals[sid] = seller_totals.get(sid, 0) + item["subtotal_sats"]

    payouts = []
    for seller_id, gross_sats in seller_totals.items():
        seller = db_find_one("users", id=seller_id)
        fee_sats = int(gross_sats * fee_percent / 100)
        payout_sats = gross_sats - fee_sats

        record = {
            "seller_id": seller_id,
            "seller_name": seller.get("name") if seller else "Unknown",
            "gross_sats": gross_sats,
            "platform_fee_sats": fee_sats,
            "payout_sats": payout_sats,
            "status": "pending",
            "payment_hash": None,
            "error": None,
        }

        if not seller or not seller.get("lightning_address"):
            record["status"] = "failed"
            record["error"] = "Seller has no Lightning Address configured"
            payouts.append(record)
            continue

        try:
            payout = await payment_service.payout_to_lightning_address(
                seller["lightning_address"],
                payout_sats,
                f"BitMarket pago {cart_order['id'][-8:].upper()}",
                seller_invoice_key=seller.get("lnbits_invoice_key"),
            )
            record["status"] = "paid"
            record["payment_hash"] = payout.get("payment_hash")
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = str(exc)

        payouts.append(record)

    statuses = {p["status"] for p in payouts}
    if statuses == {"paid"}:
        payout_status = "paid"
    elif "paid" in statuses:
        payout_status = "partial"
    else:
        payout_status = "failed"

    return {"payouts": payouts, "payout_status": payout_status}
