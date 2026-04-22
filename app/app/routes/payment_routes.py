"""
Payment Routes
--------------
POST /payments/create-invoice       â€” Create a Lightning invoice directly
GET  /payments/status/{hash}        â€” Check invoice payment status
POST /payments/webhook              â€” LNbits webhook (no auth)
GET  /payments/balance              â€” Wallet balance (admin only)
"""

from fastapi import APIRouter
from app.app.controllers import payment_controller

router = APIRouter(prefix="/payments", tags=["Payments"])

router.post(
    "/create-invoice",
    summary="Create a Lightning Network invoice for a given amount in satoshis",
)(payment_controller.create_invoice)

router.get(
    "/status/{payment_hash}",
    summary="Check if a Lightning invoice has been paid",
)(payment_controller.check_status)

router.post(
    "/webhook",
    summary="LNbits webhook â€” called automatically when a payment settles",
    # Internal callback endpoint; hide from public API docs.
    include_in_schema=False,   # hide from public docs
)(payment_controller.lnbits_webhook)

router.get(
    "/balance",
    summary="Get LNbits wallet balance (admin only)",
)(payment_controller.wallet_balance)

router.get(
    "/qr",
    summary="Render QR image for a BOLT11 invoice",
    # UI fallback endpoint when client-side QR rendering is unavailable.
    include_in_schema=False,
)(payment_controller.qr_code)

