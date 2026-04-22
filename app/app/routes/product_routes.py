"""
Product Routes
--------------
GET    /products           â€” List products (public, with search & filters)
GET    /products/{id}      â€” Get single product (public)
POST   /products           â€” Create product (seller only)
GET    /products/mine      â€” List own products (seller only)
PUT    /products/{id}      â€” Update product (seller only)
DELETE /products/{id}      â€” Deactivate product (seller or admin)
"""

from fastapi import APIRouter
from app.app.controllers import product_controller

router = APIRouter(prefix="/products", tags=["Products"])

# Declare static/specific paths before dynamic {product_id} to avoid route shadowing.
router.get("",         summary="List products with optional search and filters")(product_controller.list_products)
router.get("/mine",    summary="List authenticated seller's own products")(product_controller.my_products)
router.post("/upload-image", summary="Upload a product image (seller only)")(product_controller.upload_product_image)
router.get("/{product_id}", summary="Get a single product by ID")(product_controller.get_product)
router.post("",        summary="Create a new product listing (seller only)")(product_controller.create_product)
router.put("/{product_id}",    summary="Update a product (seller only)")(product_controller.update_product)
router.delete("/{product_id}", summary="Deactivate a product (seller or admin)")(product_controller.delete_product)

