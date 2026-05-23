"""
Cart Controller
===============
Handles HTTP layer for all cart and cart-checkout endpoints.
"""

from fastapi import Depends
from fastapi.responses import JSONResponse

from app.app.config.database import get_db
from app.app.middleware.auth import get_current_user, get_buyer
from app.app.models.order import CartItemRequest, CartCheckoutRequest
from app.app.services import cart_service


async def get_cart(current_user: dict = Depends(get_buyer)):
    """GET /cart — Return the buyer's active cart."""
    cart = cart_service.get_cart(current_user["id"])
    if not cart:
        return {"success": True, "cart": None}
    return {"success": True, "cart": cart}


async def add_item(
    data: CartItemRequest,
    current_user: dict = Depends(get_buyer),
):
    """POST /cart/items — Add a product to the cart."""
    cart = cart_service.add_item(current_user["id"], data.product_id, data.quantity)
    return {"success": True, "cart": cart}


async def update_item(
    product_id: str,
    data: CartItemRequest,
    current_user: dict = Depends(get_buyer),
):
    """PATCH /cart/items/{product_id} — Update quantity (0 = remove)."""
    cart = cart_service.update_item(current_user["id"], product_id, data.quantity)
    return {"success": True, "cart": cart}


async def remove_item(
    product_id: str,
    current_user: dict = Depends(get_buyer),
):
    """DELETE /cart/items/{product_id} — Remove item from cart."""
    cart = cart_service.remove_item(current_user["id"], product_id)
    return {"success": True, "cart": cart}


async def clear_cart(current_user: dict = Depends(get_buyer)):
    """DELETE /cart — Clear all items from cart."""
    cart = cart_service.clear_cart(current_user["id"])
    return {"success": True, "cart": cart}


async def checkout(
    data: CartCheckoutRequest,
    current_user: dict = Depends(get_buyer),
):
    """POST /cart/checkout — Generate Lightning invoice for cart total."""
    result = await cart_service.checkout(current_user["id"], data)
    return JSONResponse(status_code=201, content={"success": True, **result})


async def cart_payment_status(
    payment_hash: str,
    current_user: dict = Depends(get_current_user),
):
    """GET /cart/payment-status/{payment_hash} — Poll invoice confirmation."""
    result = await cart_service.confirm_payment(payment_hash)
    return {"success": True, **result}
