"""
Order Routes
------------
POST  /orders                              â€” Create order + Lightning invoice (buyer)
GET   /orders/mine                         â€” Buyer's order history
GET   /orders/seller                       â€” Orders with seller's items
GET   /orders/payment-status/{hash}        â€” Poll payment confirmation
PATCH /orders/{id}/fulfillment             â€” Update fulfillment status (seller)
"""

from fastapi import APIRouter
from app.app.controllers import order_controller

router = APIRouter(prefix="/orders", tags=["Orders"])

router.post("",        summary="Create an order and generate a Lightning invoice")(order_controller.create_order)
router.get("/mine",    summary="Get the authenticated buyer's orders")(order_controller.my_orders)
router.get("/seller",  summary="Get orders containing the seller's products")(order_controller.seller_orders)
router.get("/payment-status/{payment_hash}", summary="Poll Lightning payment confirmation")(order_controller.payment_status)
router.patch("/{order_id}/fulfillment",      summary="Update fulfillment status for an order item")(order_controller.update_fulfillment)

