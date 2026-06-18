"""
Cart Routes
-----------
GET    /cart                              — Get active cart
POST   /cart/items                        — Add item
PATCH  /cart/items/{product_id}           — Update item quantity
DELETE /cart/items/{product_id}           — Remove item
DELETE /cart                              — Clear cart
POST   /cart/checkout                     — Checkout → Lightning invoice
GET    /cart/payment-status/{hash}        — Poll payment confirmation
"""

from fastapi import APIRouter
from app.app.controllers import cart_controller

router = APIRouter(prefix="/cart", tags=["Cart"])

router.get("",                                       summary="Get active cart")(cart_controller.get_cart)
router.post("/items",                                summary="Add item to cart")(cart_controller.add_item)
router.patch("/items/{product_id}",                  summary="Update item quantity")(cart_controller.update_item)
router.delete("/items/{product_id}",                 summary="Remove item from cart")(cart_controller.remove_item)
router.delete("",                                    summary="Clear cart")(cart_controller.clear_cart)
router.post("/checkout",                             summary="Checkout cart → Lightning invoice")(cart_controller.checkout)
router.get("/payment-status/{payment_hash}",         summary="Poll cart invoice payment")(cart_controller.cart_payment_status)
router.post("/cancel-invoice/{payment_hash}",        summary="Cancel cart invoice and unlock cart")(cart_controller.cancel_cart_invoice)
