"""
Shared utility functions.
No external dependencies — safe for in-memory and MongoDB modes.
"""

from datetime import datetime, timezone
import re


def sats_to_btc(sats: int) -> float:
    """Convert satoshis to BTC with 8 decimal precision."""
    return round(sats / 100_000_000, 8)


def btc_to_sats(btc: float) -> int:
    """Convert BTC to satoshis."""
    return round(btc * 100_000_000)


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def normalize_phone(phone: str | None) -> str | None:
    """Normalize Salvadoran phone to XXXX-XXXX or +503 XXXX-XXXX."""
    if phone is None:
        return None

    raw = phone.strip()
    if not raw:
        return None

    digits = re.sub(r"\D", "", raw)
    if len(digits) == 8:
        if digits[0] not in {"2", "6", "7"}:
            raise ValueError("Invalid phone prefix. Use a valid Salvadoran number (2, 6, or 7)")
        return f"{digits[:4]}-{digits[4:]}"

    # Accept Salvadoran format with country code, e.g. +503 7777-8888
    if len(digits) == 11 and digits.startswith("503"):
        local = digits[3:]
        if local[0] not in {"2", "6", "7"}:
            raise ValueError("Invalid phone prefix. Use a valid Salvadoran number (2, 6, or 7)")
        return f"+503 {local[:4]}-{local[4:]}"

    raise ValueError("Invalid phone number. Use 8 digits, with or without +503")
