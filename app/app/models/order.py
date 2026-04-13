"""
Order and Cart domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


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
    product_id: str
    quantity: int = Field(..., ge=1)


class CartItem(BaseModel):
    product_id: str
    title: str
    price_sats: int
    quantity: int
    subtotal_sats: int
    seller_id: str


# ── Order schemas ──────────────────────────────────────────

class ShippingAddress(BaseModel):
    name: str
    street: str
    city: str
    country: str
    zip: Optional[str] = None


class OrderCreateRequest(BaseModel):
    items: list[CartItemRequest] = Field(..., min_length=1)
    shipping_address: ShippingAddress
    notes: Optional[str] = None


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
    item_index: int = Field(..., ge=0)
    status: FulfillmentStatus
