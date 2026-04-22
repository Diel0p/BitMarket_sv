"""
Admin Routes  (all require admin role)
--------------------------------------
GET   /admin/stats                     â€” Marketplace metrics
GET   /admin/users                     â€” List all users
PATCH /admin/users/{id}/status         â€” Ban or unban a user
GET   /admin/products                  â€” All products (any status)
PATCH /admin/products/{id}/status      â€” Approve / reject / deactivate
GET   /admin/orders                    â€” All orders
"""

from fastapi import APIRouter
from app.app.controllers import admin_controller

router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin routes centralize moderation and reporting operations behind role checks.
router.get("/stats",                        summary="Marketplace overview metrics")(admin_controller.stats)
router.get("/users",                        summary="List all users")(admin_controller.list_users)
router.post("/users/super",                 summary="Create a new super admin user")(admin_controller.create_super_user)
router.patch("/users/{user_id}/status",     summary="Toggle user active/banned status")(admin_controller.toggle_user)
router.get("/products",                     summary="List all products (any status)")(admin_controller.list_products)
router.patch("/products/{product_id}/status", summary="Set product moderation status")(admin_controller.set_product_status)
router.get("/orders",                       summary="List all marketplace orders")(admin_controller.list_orders)

