"""
User domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    BUYER  = "buyer"
    SELLER = "seller"
    ADMIN  = "admin"


class UserRegisterRequest(BaseModel):
    # Keep registration payload strict to reduce malformed identities.
    name:       str      = Field(..., min_length=2, max_length=100)
    email:      EmailStr
    password:   str      = Field(..., min_length=8)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)
    role:       UserRole = UserRole.BUYER
    store_name: Optional[str] = Field(None, max_length=100)
    lightning_address: Optional[str] = Field(None, max_length=255)
    lnbits_invoice_key: Optional[str] = Field(None, max_length=255)


class UserLoginRequest(BaseModel):
    email:    EmailStr
    password: str


class AdminCreateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)


class UserUpdateRequest(BaseModel):
    # All fields optional to support partial profile updates (PATCH-like behavior).
    name:  Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    department: Optional[str] = Field(None, max_length=80)
    store_name: Optional[str] = Field(None, max_length=100)
    lightning_address: Optional[str] = Field(None, max_length=255)


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
    store_name: Optional[str] = None
    lightning_address: Optional[str] = None
    lnbits_invoice_key: Optional[str] = None

    # Allows building responses directly from dict-like ORM/document objects.
    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse
