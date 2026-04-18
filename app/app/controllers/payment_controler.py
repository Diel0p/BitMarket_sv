"""
Payment Controller â€” standalone invoice endpoints.
"""

from fastapi import Depends, Request
from fastapi.responses import JSONResponse

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