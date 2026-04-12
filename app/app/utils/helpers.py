"""
Shared utility functions.
No external dependencies — safe for in-memory and MongoDB modes.
"""

from datetime import datetime, timezone


def sats_to_btc(sats: int) -> float:
    """Convert satoshis to BTC with 8 decimal precision."""
    return round(sats / 100_000_000, 8)


def btc_to_sats(btc: float) -> int:
    """Convert BTC to satoshis."""
    return round(btc * 100_000_000)


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
