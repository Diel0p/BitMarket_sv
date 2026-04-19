"""
Order Controller
================
Handles HTTP concerns for order and payment endpoints.
"""

from fastapi import Depends
from fastapi.responses import JSONResponse

from app.app.config.database import get_db
from app.app.middleware.auth import get_current_user, get_buyer, get_seller
from app.app.models.order import OrderCreateRequest, FulfillmentUpdateRequest
from app.app.services import order_service


async def create_order(
    data: OrderCreateRequest,
    current_user: dict = Depends(get_buyer),
    db=Depends(get_db),
):
    """
    POST /orders
    Creates an order and returns a Lightning invoice for payment.
    """
    result = await order_service.create_order(data, current_user["id"], db)
    return JSONResponse(status_code=201, content={"success": True, **result})


async def my_orders(
    current_user: dict = Depends(get_buyer),
    db=Depends(get_db),
):
    orders = await order_service.get_buyer_orders(current_user["id"], db)
    return {"success": True, "orders": orders}


async def seller_orders(
    current_user: dict = Depends(get_seller),
    db=Depends(get_db),
):
    orders = await order_service.get_seller_orders(current_user["id"], db)
    return {"success": True, "orders": orders}


async def update_fulfillment(
    order_id: str,
    data: FulfillmentUpdateRequest,
    current_user: dict = Depends(get_seller),
    db=Depends(get_db),
):
    result = await order_service.update_fulfillment(order_id, data, current_user["id"], db)
    return {"success": True, **result}


async def payment_status(
    payment_hash: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    GET /orders/payment-status/{payment_hash}
    Poll this endpoint to check if a Lightning invoice was paid.
    """
    result = await order_service.check_and_confirm_payment(payment_hash, db)
    return {"success": True, **result}

