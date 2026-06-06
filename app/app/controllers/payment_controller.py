"""
Payment Controller â€” standalone invoice endpoints.
"""

import io

import segno
from fastapi import Depends, Request
from fastapi.responses import JSONResponse, Response

from app.app.config.database import get_db, db_insert
from app.app.middleware.auth import get_current_user, get_admin
from app.app.models.payment import CreateInvoiceRequest
from app.app.services import payment_service
from app.app.services.order_service import check_and_confirm_payment
from app.app.utils.helpers import utcnow


async def create_invoice(
    data: CreateInvoiceRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    POST /api/payments/create-invoice

    Create a Lightning invoice for any amount.
    Works in mock mode (no LNbits needed).

    Body:
        { "order_id": "abc", "amount_sats": 50000, "memo": "optional" }

    Response:
        {
          "payment_hash": "...",
          "payment_request": "lnbc...",   â† encode as QR code
          "amount_sats": 50000,
          "expires_at": "...",
          "is_mock": true
        }
    """
    invoice_data = await payment_service.create_invoice(
        amount_sats=data.amount_sats,
        memo=data.memo or "BitMarket SV payment",
        order_id=data.order_id,
    )

    # Persist invoice metadata so status checks remain source-of-truth in our DB.
    db_insert("invoices", {
        "order_id":        data.order_id,
        "buyer_id":        current_user["id"],
        "payment_hash":    invoice_data["payment_hash"],
        "payment_request": invoice_data["payment_request"],
        "amount_sats":     data.amount_sats,
        "status":          "pending",
        "expires_at":      invoice_data["expires_at"].isoformat(),
        "is_mock":         invoice_data["is_mock"],
        "paid_at":         None,
        "created_at":      utcnow().isoformat(),
    })

    return {
        "success": True,
        "invoice": {
            "payment_hash":    invoice_data["payment_hash"],
            "payment_request": invoice_data["payment_request"],
            "amount_sats":     data.amount_sats,
            "status":          "pending",
            "expires_at":      invoice_data["expires_at"].isoformat(),
            "is_mock":         invoice_data["is_mock"],
        },
    }


async def check_status(
    payment_hash: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    GET /api/payments/status/{payment_hash}
    Poll every few seconds after showing the QR code.
    Returns paid=true once the invoice settles.
    """
    result = await check_and_confirm_payment(payment_hash, db)
    return {"success": True, **result}


async def lnbits_webhook(request: Request, db=Depends(get_db)):
    """
    POST /api/payments/webhook
    LNbits calls this when a payment settles. No auth required.
    """
    try:
        # Webhook payloads are untrusted input: validate minimal required fields.
        body = await request.json()
        payment_hash = body.get("payment_hash")
        if not payment_hash:
            return JSONResponse(status_code=400, content={"error": "Missing payment_hash"})
        result = await check_and_confirm_payment(payment_hash, db)
        return {"ok": True, "paid": result["paid"]}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


async def wallet_balance(current_user: dict = Depends(get_admin)):
    """GET /api/payments/balance â€” admin only."""
    result = await payment_service.get_wallet_balance()
    return {"success": True, **result}


async def qr_code(text: str):
    """
    GET /api/payments/qr?text=<bolt11>
    Returns an SVG QR image for checkout fallback when JS CDN fails.
    """
    payload = (text or "").strip()
    # Guard resource usage for public endpoint returning dynamically generated SVG.
    if not payload:
        return JSONResponse(status_code=400, content={"error": "Missing text"})
    if len(payload) > 5000:
        return JSONResponse(status_code=400, content={"error": "QR payload too large"})

    # Generate QR with high contrast for better camera recognition
    qr = segno.make(payload, error="h", boost_error=False)
    out = io.BytesIO()
    qr.save(
        out, 
        kind="svg", 
        scale=8,           # Larger scale for better definition
        border=3,          # More border/quiet zone
        dark="black",      # Pure black modules
        light="white",     # Pure white background
        xmldecl=False,     # Skip XML declaration for cleaner SVG
    )
    return Response(content=out.getvalue().decode("utf-8"), media_type="image/svg+xml")


async def create_donation_invoice(
    data: CreateInvoiceRequest,
    db=Depends(get_db),
):
    """
    POST /api/payments/create-donation-invoice

    Create a Lightning invoice for donations (public endpoint, no auth required).
    Allows anyone to donate to the platform.

    Body:
        { "amount_sats": 50000, "memo": "Donación a BitMarket SV" }

    Response:
        {
          "payment_hash": "...",
          "payment_request": "lnbc...",
          "amount_sats": 50000,
          "expires_at": "...",
          "is_mock": false
        }
    """
    invoice_data = await payment_service.create_invoice(
        amount_sats=data.amount_sats,
        memo=data.memo or "Donación a BitMarket SV",
        order_id="donation",
    )

    # Persist donation invoice metadata (no buyer_id since it's public)
    db_insert("invoices", {
        "order_id":        "donation",
        "buyer_id":        None,  # Public donations don't require auth
        "payment_hash":    invoice_data["payment_hash"],
        "payment_request": invoice_data["payment_request"],
        "amount_sats":     data.amount_sats,
        "status":          "pending",
        "expires_at":      invoice_data["expires_at"].isoformat(),
        "is_mock":         invoice_data["is_mock"],
        "paid_at":         None,
        "created_at":      utcnow().isoformat(),
    })

    return {
        "success": True,
        "invoice": {
            "payment_hash":    invoice_data["payment_hash"],
            "payment_request": invoice_data["payment_request"],
            "amount_sats":     data.amount_sats,
            "status":          "pending",
            "expires_at":      invoice_data["expires_at"].isoformat(),
            "is_mock":         invoice_data["is_mock"],
        },
    }


async def check_donation_status(payment_hash: str, db=Depends(get_db)):
    """
    GET /api/payments/donation-status/{payment_hash}
    Check donation payment status (public endpoint, no auth required).
    """
    result = await check_and_confirm_payment(payment_hash, db)
    return {"success": True, **result}

