"""
Product domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REJECTED = "rejected"


# ── Request schemas ────────────────────────────────────────

class ProductCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    price_sats: int = Field(..., gt=0, description="Price in satoshis")
    category: str = Field(..., min_length=2, max_length=60)
    stock: int = Field(..., ge=0)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)


class ProductUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    price_sats: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    tags: Optional[list[str]] = None
    images: Optional[list[str]] = None
    status: Optional[ProductStatus] = None


# ── Response schemas ───────────────────────────────────────

class ProductResponse(BaseModel):
    id: str
    title: str
    description: str
    price_sats: int
    price_btc: float
    category: str
    stock: int
    tags: list[str]
    status: ProductStatus
    seller_id: str
    seller_name: Optional[str] = None
    images: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Filters ────────────────────────────────────────────────

class ProductFilters(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: str = Field("created_at", pattern="^(created_at|price_asc|price_desc)$")
