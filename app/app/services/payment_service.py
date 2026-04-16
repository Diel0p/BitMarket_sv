"""
Payment Service â€” LNbits integration with guaranteed mock mode.

MOCK MODE (default when LNBITS_URL is not set):
  - create_invoice()      â†’ returns a realistic-looking fake BOLT11 string
  - check_invoice_status() â†’ returns paid=True after MOCK_CONFIRM_SECONDS seconds
  - The app runs fully without any external service

LIVE MODE (set LNBITS_URL + LNBITS_ADMIN_KEY in .env):
  - Connects to your LNbits instance
  - Returns real BOLT11 invoices scannable by any Lightning wallet

To swap providers: only this file changes.
"""

import secrets
import time
from datetime import timedelta
from urllib.parse import quote

import httpx
from fastapi import HTTPException

from app.app.config.settings import get_settings
from app.app.utils.helpers import utcnow

settings = get_settings()

# Track mock invoice creation timestamps {payment_hash: created_at_epoch}
_mock_registry: dict[str, float] = {}


# â”€â”€ Public API (same signature regardless of mode) â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def create_invoice(amount_sats: int, memo: str, order_id: str) -> dict:
    """
    Create a Lightning invoice.

    Returns:
        payment_hash     â€” unique identifier, use to check status
        payment_request  â€” BOLT11 string (encode as QR code for wallet)
        expires_at       â€” datetime when invoice expires
        is_mock          â€” True in mock mode (no real payment needed)
    """
    if settings.lnbits_mock_mode:
        return _create_mock_invoice(amount_sats, memo)
    return await _create_lnbits_invoice(amount_sats, memo)


async def check_invoice_status(payment_hash: str) -> dict:
    """
    Check whether an invoice has been paid.

    Returns:
        paid        â€” bool
        settled_at  â€” datetime or None
        is_mock     â€” bool
    """
    if settings.lnbits_mock_mode or payment_hash.startswith("mock_"):
        return _check_mock_status(payment_hash)
    return await _check_lnbits_status(payment_hash)


async def get_wallet_balance() -> dict:
    if settings.lnbits_mock_mode:
        return {"balance_sats": 1_337_000, "is_mock": True}
    return await _get_lnbits_balance()


async def payout_to_lightning_address(lightning_address: str, amount_sats: int, memo: str) -> dict:
    if amount_sats <= 0:
        raise HTTPException(status_code=400, detail="Payout amount must be greater than zero")

    if settings.lnbits_mock_mode:
        return _create_mock_payout(lightning_address, amount_sats)

    bolt11 = await _resolve_lightning_address_invoice(lightning_address, amount_sats, memo)
    return await _pay_bolt11_invoice(bolt11, lightning_address)


# â”€â”€ Mock implementation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _create_mock_invoice(amount_sats: int, memo: str) -> dict:
    payment_hash = f"mock_{secrets.token_hex(16)}"
    _mock_registry[payment_hash] = time.time()

    # Realistic-looking BOLT11 prefix + mock content
    payment_request = (
        f"lnbc{amount_sats}n1p"
        f"{secrets.token_hex(8)}"
        f"MOCK_INVOICE_bitmarket_sv"
    )

    return {
        "payment_hash":    payment_hash,
        "payment_request": payment_request,
        "expires_at":      utcnow() + timedelta(seconds=settings.invoice_expire_seconds),
        "is_mock":         True,
    }


def _check_mock_status(payment_hash: str) -> dict:
    """Auto-confirms after MOCK_CONFIRM_SECONDS seconds."""
    created_at = _mock_registry.get(payment_hash)

    if created_at is None:
        # Unknown hash â€” treat as paid (useful for testing)
        return {"paid": True, "settled_at": utcnow(), "is_mock": True}

    elapsed = time.time() - created_at
    paid    = elapsed >= settings.mock_confirm_seconds

    return {
        "paid":       paid,
        "settled_at": utcnow() if paid else None,
        "is_mock":    True,
        "elapsed_seconds": round(elapsed, 1),
        "confirm_after":   settings.mock_confirm_seconds,
    }


def _create_mock_payout(lightning_address: str, amount_sats: int) -> dict:
    return {
        "payment_hash": f"mock_payout_{secrets.token_hex(12)}",
        "destination": lightning_address,
        "amount_sats": amount_sats,
        "is_mock": True,
        "status": "paid",
    }


# â”€â”€ LNbits live implementation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _headers() -> dict:
    return {
        "X-Api-Key":    settings.lnbits_admin_key,
        "Content-Type": "application/json",
    }


async def _create_lnbits_invoice(amount_sats: int, memo: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            f"{settings.lnbits_url}/api/v1/payments",
            headers=_headers(),
            json={
                "out":    False,
                "amount": amount_sats,
                "memo":   memo,
                "expiry": settings.invoice_expire_seconds,
            },
        )
        r.raise_for_status()
        data = r.json()

    return {
        "payment_hash":    data["payment_hash"],
        "payment_request": data["payment_request"],
        "expires_at":      utcnow() + timedelta(seconds=settings.invoice_expire_seconds),
        "is_mock":         False,
    }


async def _resolve_lightning_address_invoice(
    lightning_address: str,
    amount_sats: int,
    memo: str,
) -> str:
    destination = lightning_address.strip()
    if destination.startswith("http://") or destination.startswith("https://"):
        lnurlp_url = destination
    else:
        name, domain = destination.split("@", 1)
        scheme = "http" if domain.startswith("localhost") or domain.startswith("127.0.0.1") else "https"
        lnurlp_url = f"{scheme}://{domain}/.well-known/lnurlp/{quote(name)}"

    amount_msat = amount_sats * 1000

    async with httpx.AsyncClient(timeout=15.0) as client:
        lnurlp_response = await client.get(lnurlp_url)
        lnurlp_response.raise_for_status()
        lnurlp_data = lnurlp_response.json()

        min_sendable = int(lnurlp_data.get("minSendable", 0))
        max_sendable = int(lnurlp_data.get("maxSendable", 0))
        if amount_msat < min_sendable or (max_sendable and amount_msat > max_sendable):
            raise HTTPException(status_code=400, detail="Seller Lightning Address does not accept this payout amount")

        callback_response = await client.get(
            lnurlp_data["callback"],
            params={"amount": amount_msat, "comment": memo[:120]},
        )
        callback_response.raise_for_status()
        callback_data = callback_response.json()

    bolt11 = callback_data.get("pr")
    if not bolt11:
        raise HTTPException(status_code=502, detail="LNURL payout callback did not return an invoice")
    return bolt11


async def _pay_bolt11_invoice(bolt11: str, lightning_address: str) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(
            f"{settings.lnbits_url}/api/v1/payments",
            headers=_headers(),
            json={
                "out": True,
                "bolt11": bolt11,
            },
        )
        r.raise_for_status()
        data = r.json()

    return {
        "payment_hash": data.get("payment_hash") or data.get("checking_id") or secrets.token_hex(12),
        "destination": lightning_address,
        "is_mock": False,
        "status": "paid",
    }


async def _check_lnbits_status(payment_hash: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{settings.lnbits_url}/api/v1/payments/{payment_hash}",
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()

    paid = data.get("paid", False)
    return {
        "paid":       paid,
        "settled_at": utcnow() if paid else None,
        "is_mock":    False,
    }


async def _get_lnbits_balance() -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{settings.lnbits_url}/api/v1/wallet",
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()

    return {"balance_sats": data["balance"] // 1000, "is_mock": False}
