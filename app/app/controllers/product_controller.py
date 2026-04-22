"""
Product Controller
==================
Handles HTTP concerns for product endpoints.
Delegates all business logic to product_service.
"""

import uuid
from pathlib import Path

from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.app.config.database import get_db
from app.app.middleware.auth import get_current_user, get_seller
from app.app.models.product import ProductCreateRequest, ProductUpdateRequest, ProductFilters
from app.app.services import product_service


_UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads" / "products"
_ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


async def list_products(filters: ProductFilters = Depends(), db=Depends(get_db)):
    result = await product_service.list_products(filters, db)
    return {"success": True, **result}


async def get_product(product_id: str, db=Depends(get_db)):
    product = await product_service.get_product_by_id(product_id, db)
    return {"success": True, "product": product}


async def create_product(
    data: ProductCreateRequest,
    current_user: dict = Depends(get_seller),
    db=Depends(get_db),
):
    # Seller identity must come from auth context to prevent cross-account creation.
    product = await product_service.create_product(data, current_user["id"], db)
    return JSONResponse(status_code=201, content={"success": True, "product": product})


async def my_products(
    current_user: dict = Depends(get_seller),
    db=Depends(get_db),
):
    products = await product_service.get_seller_products(current_user["id"], db)
    return {"success": True, "products": products}


async def update_product(
    product_id: str,
    data: ProductUpdateRequest,
    current_user: dict = Depends(get_seller),
    db=Depends(get_db),
):
    product = await product_service.update_product(product_id, data, current_user["id"], db)
    return {"success": True, "product": product}


async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    # Service enforces role/ownership rules; controller keeps HTTP translation only.
    result = await product_service.delete_product(
        product_id, current_user["id"], current_user["role"], db
    )
    return {"success": True, **result}


async def upload_product_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_seller),
):
    # Validate extension before saving to reduce risk of unsupported/unexpected files.
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required")

    suffix = Path(image.filename).suffix.lower()
    if suffix not in _ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{current_user['id']}_{uuid.uuid4().hex}{suffix}"
    file_path = _UPLOAD_DIR / filename

    raw = await image.read()
    # Hard size cap protects memory and disk from oversized uploads.
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    with open(file_path, "wb") as f:
        f.write(raw)

    return {
        "success": True,
        "image_url": f"/static/uploads/products/{filename}",
    }

