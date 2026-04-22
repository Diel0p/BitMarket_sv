"""
Payment and Invoice domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    FAILED = "failed"


# -- Request schemas -------------------------------------------------

class CreateInvoiceRequest(BaseModel):
    # Amount is validated in sats to keep integer precision end-to-end.
    order_id: str
    amount_sats: int = Field(..., gt=0, description="Amount in satoshis")
    memo: Optional[str] = Field(None, max_length=200)


# -- Response schemas ------------------------------------------------

class InvoiceResponse(BaseModel):
    payment_hash: str
    payment_request: str
    amount_sats: int
    status: InvoiceStatus
    expires_at: datetime
    is_mock: bool
    created_at: datetime


class PaymentStatusResponse(BaseModel):
    payment_hash: str
    paid: bool
    status: InvoiceStatus
    settled_at: Optional[datetime] = None


class CheckoutResponse(BaseModel):
    """Combined response for POST /orders: order + invoice in one call."""
    order_id: str
    total_sats: int
    invoice: InvoiceResponse