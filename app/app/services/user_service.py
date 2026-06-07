"""
User Service â€” auth, profile, moderation.
Uses document DB helpers via app.app.config.database.
"""

import re
from datetime import timedelta

from fastapi import HTTPException, status

from app.app.config.database import (
    db_insert, db_find_one, db_update,
)
from app.app.middleware.auth import hash_password, verify_password, create_access_token
from app.app.models.user import UserRegisterRequest, UserLoginRequest
from app.app.utils.helpers import normalize_phone, utcnow


_LIGHTNING_ADDRESS_RE = re.compile(r"^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$", re.IGNORECASE)
_LNURLP_URL_RE = re.compile(
    r"^https?://[^\s]+/(\.well-known/lnurlp/[^\s/?#]+|lnurlp/link/[^\s/?#]+|wallet/[a-f0-9]+)(?:\?[^\s#]*)?$",
    re.IGNORECASE,
)

_MAX_LOGIN_ATTEMPTS = 5
_LOCKOUT_MINUTES = 15
_LOGIN_ATTEMPTS: dict[str, dict] = {}


def _normalize_lightning_address(value: str | None) -> str | None:
    # Normalize once at the boundary so the rest of the service can assume a consistent format.
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if _LNURLP_URL_RE.match(normalized):
        return normalized

    normalized_lower = normalized.lower()
    if not _LIGHTNING_ADDRESS_RE.match(normalized_lower):
        raise HTTPException(
            status_code=400,
            detail="Invalid payout destination. Use Lightning Address (user@domain) or LNURLp URL (not LndHub URL)",
        )
    return normalized_lower


async def register_user(data: UserRegisterRequest, db) -> dict:
    if data.role.value == "admin":
        raise HTTPException(status_code=403, detail="Admin accounts can only be created from the admin panel")

    # Enforce unique identity early to fail fast and avoid creating partial user records.
    if db_find_one("users", email=data.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    lightning_address = _normalize_lightning_address(data.lightning_address)

    doc = {
        "name":            data.name,
        "email":           data.email,
        "hashed_password": hash_password(data.password),
        "role":            data.role.value,
        "is_active":       True,
        "created_at":      utcnow().isoformat(),
    }
    if data.phone:
        try:
            doc["phone"] = normalize_phone(data.phone)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if data.address:
        doc["address"] = data.address.strip()
    if data.department:
        doc["department"] = data.department.strip()
    if data.municipality:
        doc["municipality"] = data.municipality.strip()
    if data.district:
        doc["district"] = data.district.strip()
    if data.role.value == "seller":
        # Seller accounts must always have payout info to prevent unpayable orders later.
        doc["store_name"] = data.store_name or f"{data.name}'s Store"
        if not lightning_address:
            raise HTTPException(status_code=400, detail="Seller accounts require a Lightning Address")
        doc["lightning_address"] = lightning_address
        if data.lnbits_invoice_key:
            doc["lnbits_invoice_key"] = data.lnbits_invoice_key.strip()
    elif lightning_address:
        doc["lightning_address"] = lightning_address

    user_id = db_insert("users", doc)
    token   = create_access_token({"sub": user_id})
    # Never return credential material to clients.
    safe    = {k: v for k, v in doc.items() if k != "hashed_password"}
    return {"access_token": token, "token_type": "bearer", "user": safe}


async def login_user(data: UserLoginRequest, db) -> dict:
    email_key = data.email.lower()
    attempts = _LOGIN_ATTEMPTS.get(email_key)
    if attempts and attempts.get("count", 0) >= _MAX_LOGIN_ATTEMPTS:
        lock_until = attempts.get("lock_until")
        if lock_until and utcnow() < lock_until:
            raise HTTPException(
                status_code=429,
                detail="Too many failed login attempts. Try again in a few minutes",
            )
        _LOGIN_ATTEMPTS.pop(email_key, None)

    user = db_find_one("users", email=data.email)
    # Use a generic auth error to avoid leaking whether an email exists.
    if not user or not verify_password(data.password, user["hashed_password"]):
        current = _LOGIN_ATTEMPTS.get(email_key, {"count": 0, "lock_until": None})
        new_count = current["count"] + 1
        lock_until = None
        if new_count >= _MAX_LOGIN_ATTEMPTS:
            lock_until = utcnow() + timedelta(minutes=_LOCKOUT_MINUTES)
        _LOGIN_ATTEMPTS[email_key] = {"count": new_count, "lock_until": lock_until}
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account has been deactivated")

    _LOGIN_ATTEMPTS.pop(email_key, None)

    token = create_access_token({"sub": user["id"]})
    safe  = {k: v for k, v in user.items() if k != "hashed_password"}
    return {"access_token": token, "token_type": "bearer", "user": safe}


async def get_user_by_id(user_id: str, db) -> dict | None:
    user = db_find_one("users", id=user_id)
    if not user:
        return None
    return {k: v for k, v in user.items() if k != "hashed_password"}


async def toggle_user_status(user_id: str, db) -> dict:
    user = db_find_one("users", id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Cannot modify admin accounts")

    new_status = not user.get("is_active", True)
    db_update("users", user_id, {"is_active": new_status})
    return {
        "message":   f"User {'activated' if new_status else 'banned'}",
        "is_active": new_status,
    }


async def update_user_profile(user_id: str, updates: dict, db) -> dict:
    user = db_find_one("users", id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    normalized_updates = dict(updates)
    # Store location is deprecated and should not be persisted anymore.
    normalized_updates.pop("store_location", None)
    if "phone" in normalized_updates:
        try:
            normalized_updates["phone"] = normalize_phone(normalized_updates.get("phone"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if "lightning_address" in normalized_updates:
        normalized_updates["lightning_address"] = _normalize_lightning_address(
            normalized_updates.get("lightning_address")
        )

    for location_field in ("address", "department", "municipality", "district"):
        value = normalized_updates.get(location_field)
        if isinstance(value, str):
            normalized_updates[location_field] = value.strip()

    if user.get("role") == "seller":
        # Keep seller payout destination mandatory after profile edits as well.
        if "lightning_address" in normalized_updates and not normalized_updates["lightning_address"]:
            raise HTTPException(status_code=400, detail="Seller accounts require a Lightning Address")
    else:
        # Prevent buyers/admins from mutating seller-only profile fields.
        normalized_updates.pop("store_name", None)

    updated = db_update("users", user_id, normalized_updates)
    if not updated:
        raise HTTPException(status_code=500, detail="Could not update user")
    return {k: v for k, v in updated.items() if k != "hashed_password"}

