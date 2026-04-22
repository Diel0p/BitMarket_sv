"""
Auth middleware â€” JWT creation/verification and role-based access control.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt as _bcrypt

from app.app.config.settings import get_settings
from app.app.config.database import get_db, db_find_one
from app.app.models.user import UserRole

settings    = get_settings()
bearer_scheme = HTTPBearer()


# â”€â”€ Password helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def hash_password(password: str) -> str:
    # Store only salted hashes; never persist or log plaintext passwords.
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# â”€â”€ Token helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Embed expiration in token claims so revoked/expired tokens are rejected server-side.
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


# â”€â”€ FastAPI dependencies â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
) -> dict:
    """Decode JWT and return the user dict. Raises 401 on any failure."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Treat any JWT decode issue as unauthorized without leaking parse details.
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    user = db_find_one("users", id=user_id)
    if not user or not user.get("is_active", True):
        raise exc

    return {k: v for k, v in user.items() if k != "hashed_password"}


def require_roles(*roles: UserRole):
    """
    Dependency factory â€” guards a route to one or more roles.

    Usage:
        @router.post("/products", dependencies=[Depends(require_roles("seller"))])
    or:
        current_user: dict = Depends(require_roles("admin"))
    """
    async def guard(current_user: dict = Depends(get_current_user)) -> dict:
        # Normalize enum/string role values once for robust comparisons.
        allowed = [r.value if hasattr(r, "value") else r for r in roles]
        if current_user.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {' or '.join(str(r) for r in roles)}",
            )
        return current_user
    return guard


# â”€â”€ Convenience guards â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
get_buyer  = require_roles(UserRole.BUYER)
get_seller = require_roles(UserRole.SELLER)
get_admin  = require_roles(UserRole.ADMIN)

