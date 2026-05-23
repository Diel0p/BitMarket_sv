"""
Order and Cart domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator


_UNSAFE_TEXT_RE = re.compile(r"[<>]")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


class PaymentStatus(str, Enum):
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class FulfillmentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ── Cart schemas ───────────────────────────────────────────

class CartItemRequest(BaseModel):
    # Quantity must be at least 1; stock checks happen later in the service layer.
    product_id: str = Field(..., min_length=8, max_length=64)
    quantity: int = Field(..., ge=1)

    @field_validator("product_id", mode="before")
    @classmethod
    def _sanitize_product_id(cls, value: str):
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Product id is required")
        if _CONTROL_CHARS_RE.search(cleaned) or _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Product id contains invalid characters")
        return cleaned


class CartItem(BaseModel):
    product_id: str
    title: str
    price_sats: int
    quantity: int
    subtotal_sats: int
    seller_id: str


class CartStatus(str, Enum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class CartResponse(BaseModel):
    id: str
    buyer_id: str
    items: list[CartItem]
    total_sats: int
    status: CartStatus
    expires_at: datetime
    created_at: datetime


class CartCheckoutRequest(BaseModel):
    shipping_address: "ShippingAddress"
    notes: Optional[str] = Field(None, max_length=600)

    @field_validator("notes", mode="before")
    @classmethod
    def _sanitize_notes(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Notes contain invalid characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Notes contain unsupported characters")
        return cleaned


# ── Order schemas ──────────────────────────────────────────

class ShippingAddress(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    street: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=120)
    country: str = Field(..., min_length=2, max_length=80)
    zip: Optional[str] = Field(None, max_length=20)

    @field_validator("name", "street", "city", "country", "zip", mode="before")
    @classmethod
    def _sanitize_shipping_fields(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Address contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Address contains unsupported characters")
        return cleaned


CartCheckoutRequest.model_rebuild()


class OrderCreateRequest(BaseModel):
    # Force at least one item so empty checkout attempts fail at validation time.
    items: list[CartItemRequest] = Field(..., min_length=1)
    shipping_address: ShippingAddress
    notes: Optional[str] = Field(None, max_length=600)

    @field_validator("notes", mode="before")
    @classmethod
    def _sanitize_order_notes(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Notes contain invalid characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Notes contain unsupported characters")
        return cleaned


class OrderItemResponse(BaseModel):
    product_id: str
    seller_id: str
    title: str
    price_sats: int
    quantity: int
    subtotal_sats: int
    fulfillment_status: FulfillmentStatus = FulfillmentStatus.PENDING


class OrderResponse(BaseModel):
    id: str
    buyer_id: str
    items: list[OrderItemResponse]
    total_sats: int
    total_btc: float
    payment_status: PaymentStatus
    order_status: OrderStatus
    shipping_address: ShippingAddress
    invoice_id: Optional[str] = None
    notes: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime


class FulfillmentUpdateRequest(BaseModel):
    # Item index is zero-based and validated to avoid negative array access.
    item_index: int = Field(..., ge=0)
    status: FulfillmentStatus
