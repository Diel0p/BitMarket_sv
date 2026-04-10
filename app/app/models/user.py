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
    name:       str      = Field(..., min_length=2, max_length=100)
    email:      EmailStr
    password:   str      = Field(..., min_length=8)
    role:       UserRole = UserRole.BUYER
    store_name: Optional[str] = Field(None, max_length=100)
    lightning_address: Optional[str] = Field(None, max_length=255)


class UserLoginRequest(BaseModel):
    email:    EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    name:  Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    store_name: Optional[str] = Field(None, max_length=100)
    lightning_address: Optional[str] = Field(None, max_length=255)


class UserResponse(BaseModel):
    id:         str
    name:       str
    email:      str
    role:       UserRole
    is_active:  bool
    created_at: str
    store_name: Optional[str] = None
    lightning_address: Optional[str] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse
