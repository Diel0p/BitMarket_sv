"""
User domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import re
from pydantic import BaseModel, EmailStr, Field, field_validator


_UNSAFE_TEXT_RE = re.compile(r"[<>]")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


class UserRole(str, Enum):
    BUYER  = "buyer"
    SELLER = "seller"
    ADMIN  = "admin"


class UserRegisterRequest(BaseModel):
    # Keep registration payload strict to reduce malformed identities.
    name:       str      = Field(..., min_length=2, max_length=100)
    email:      EmailStr
    password:   str      = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)
    municipality: Optional[str] = Field(None, max_length=120)
    district: Optional[str] = Field(None, max_length=120)
    role:       UserRole = UserRole.BUYER
    store_name: Optional[str] = Field(None, max_length=100)
    store_location: Optional[str] = Field(None, max_length=255)
    lightning_address: Optional[str] = Field(None, max_length=255)
    lnbits_invoice_key: Optional[str] = Field(None, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_email(cls, value: str | None):
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("name", "address", "department", "municipality", "district", "store_name", "store_location", "lightning_address", "lnbits_invoice_key", mode="before")
    @classmethod
    def _sanitize_text_fields(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Text contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Text contains unsupported characters")
        return cleaned

    @field_validator("password")
    @classmethod
    def _validate_password_strength(cls, value: str):
        password = value.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must include at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must include at least one special character")
        return password


class UserLoginRequest(BaseModel):
    email:    EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_login_email(cls, value: str | None):
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("password", mode="before")
    @classmethod
    def _normalize_login_password(cls, value: str | None):
        if value is None:
            return value
        return str(value).strip()


class AdminCreateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)
    municipality: Optional[str] = Field(None, max_length=120)
    district: Optional[str] = Field(None, max_length=120)

    @field_validator("email", mode="before")
    @classmethod
    def _normalize_admin_email(cls, value: str | None):
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("name", "address", "department", "municipality", "district", mode="before")
    @classmethod
    def _sanitize_admin_text_fields(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Text contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Text contains unsupported characters")
        return cleaned

    @field_validator("password")
    @classmethod
    def _validate_admin_password_strength(cls, value: str):
        password = value.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must include at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must include at least one special character")
        return password


class UserUpdateRequest(BaseModel):
    # All fields optional to support partial profile updates (PATCH-like behavior).
    name:  Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)
    municipality: Optional[str] = Field(None, max_length=120)
    district: Optional[str] = Field(None, max_length=120)
    store_name: Optional[str] = Field(None, max_length=100)
    store_location: Optional[str] = Field(None, max_length=255)
    lightning_address: Optional[str] = Field(None, max_length=255)

    @field_validator("name", "address", "department", "municipality", "district", "store_name", "store_location", "lightning_address", mode="before")
    @classmethod
    def _sanitize_update_text_fields(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Text contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Text contains unsupported characters")
        return cleaned


class UserResponse(BaseModel):
    id:         str
    name:       str
    email:      str
    role:       UserRole
    is_active:  bool
    created_at: str
    phone: Optional[str] = None
    address: Optional[str] = None
    department: Optional[str] = None
    municipality: Optional[str] = None
    district: Optional[str] = None
    store_name: Optional[str] = None
    store_location: Optional[str] = None
    lightning_address: Optional[str] = None
    lnbits_invoice_key: Optional[str] = None

    # Allows building responses directly from dict-like ORM/document objects.
    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse
