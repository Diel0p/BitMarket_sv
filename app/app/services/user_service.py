"""
User Service - auth, profile, moderation.
Uses in-memory DB helpers (swap to Motor by changing db_* calls).
"""

import re

from fastapi import HTTPException

from app.app.config.database import db_insert, db_find_one, db_update
from app.app.middleware.auth import hash_password, verify_password, create_access_token
from app.app.models.user import UserRegisterRequest, UserLoginRequest
from app.app.utils.helpers import utcnow


_LIGHTNING_ADDRESS_RE = re.compile(r"^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$", re.IGNORECASE)


def _normalize_lightning_address(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if not _LIGHTNING_ADDRESS_RE.match(normalized):
        raise HTTPException(status_code=400, detail="Invalid Lightning Address format")
    return normalized


async def register_user(data: UserRegisterRequest, db) -> dict:
    if db_find_one("users", email=data.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    lightning_address = _normalize_lightning_address(data.lightning_address)

    doc = {
        "name": data.name,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "role": data.role.value,
        "is_active": True,
        "created_at": utcnow().isoformat(),
    }
    if data.role.value == "seller":
        doc["store_name"] = data.store_name or f"{data.name}'s Store"
        if not lightning_address:
            raise HTTPException(status_code=400, detail="Seller accounts require a Lightning Address")
        doc["lightning_address"] = lightning_address
    elif lightning_address:
        doc["lightning_address"] = lightning_address

    user_id = db_insert("users", doc)
    token = create_access_token({"sub": user_id})
    safe = {k: v for k, v in doc.items() if k != "hashed_password"}
    return {"access_token": token, "token_type": "bearer", "user": safe}


async def login_user(data: UserLoginRequest, db) -> dict:
    user = db_find_one("users", email=data.email)
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account has been deactivated")

    token = create_access_token({"sub": user["id"]})
    safe = {k: v for k, v in user.items() if k != "hashed_password"}
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
        "message": f"User {'activated' if new_status else 'banned'}",
        "is_active": new_status,
    }


async def update_user_profile(user_id: str, updates: dict, db) -> dict:
    user = db_find_one("users", id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    normalized_updates = dict(updates)
    if "lightning_address" in normalized_updates:
        normalized_updates["lightning_address"] = _normalize_lightning_address(
            normalized_updates.get("lightning_address")
        )

    if user.get("role") == "seller":
        if "lightning_address" in normalized_updates and not normalized_updates["lightning_address"]:
            raise HTTPException(status_code=400, detail="Seller accounts require a Lightning Address")
    else:
        normalized_updates.pop("store_name", None)

    updated = db_update("users", user_id, normalized_updates)
    if not updated:
        raise HTTPException(status_code=500, detail="Could not update user")
    return {k: v for k, v in updated.items() if k != "hashed_password"}