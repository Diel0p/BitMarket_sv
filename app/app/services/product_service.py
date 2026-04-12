"""
Product Service â€” create, list, update, delete products.
"""

from fastapi import HTTPException

from app.app.config.database import (
    db_insert, db_find_one, db_find_all, db_update, db_count,
)
from app.app.models.product import ProductCreateRequest, ProductUpdateRequest, ProductFilters
from app.app.utils.helpers import sats_to_btc, utcnow


async def create_product(data: ProductCreateRequest, seller_id: str, db) -> dict:
    seller = db_find_one("users", id=seller_id)
    doc = {
        "title":       data.title,
        "description": data.description,
        "price_sats":  data.price_sats,
        "price_btc":   sats_to_btc(data.price_sats),
        "category":    data.category,
        "stock":       data.stock,
        "tags":        [t.strip().lower() for t in data.tags],
        "status":      "active",
        "seller_id":   seller_id,
        "seller_name": seller["name"] if seller else "Unknown",
        "images":      data.images,
        "created_at":  utcnow().isoformat(),
    }
    db_insert("products", doc)
    return doc


async def list_products(filters: ProductFilters, db) -> dict:
    all_products = db_find_all("products", status="active")

    # Apply filters
    results = []
    for p in all_products:
        if p.get("stock", 0) <= 0:
            continue
        if filters.q and filters.q.lower() not in (p["title"] + p["description"]).lower():
            continue
        if filters.category and filters.category.lower() not in p["category"].lower():
            continue
        if filters.min_price is not None and p["price_sats"] < filters.min_price:
            continue
        if filters.max_price is not None and p["price_sats"] > filters.max_price:
            continue
        results.append(p)

    # Sort
    if filters.sort == "price_asc":
        results.sort(key=lambda x: x["price_sats"])
    elif filters.sort == "price_desc":
        results.sort(key=lambda x: x["price_sats"], reverse=True)
    # default: created_at desc (already sorted by db_find_all)

    total = len(results)
    skip  = (filters.page - 1) * filters.limit
    page_results = results[skip: skip + filters.limit]

    return {
        "products": page_results,
        "total":    total,
        "page":     filters.page,
        "pages":    max(1, -(-total // filters.limit)),
    }


async def get_product_by_id(product_id: str, db) -> dict:
    product = db_find_one("products", id=product_id)
    if not product or product.get("status") != "active":
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def get_seller_products(seller_id: str, db) -> list[dict]:
    return db_find_all("products", seller_id=seller_id)


async def update_product(product_id: str, data: ProductUpdateRequest, seller_id: str, db) -> dict:
    product = db_find_one("products", id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != seller_id:
        raise HTTPException(status_code=403, detail="You don't own this product")

    updates = data.model_dump(exclude_none=True)
    if "price_sats" in updates:
        updates["price_btc"] = sats_to_btc(updates["price_sats"])

    updated = db_update("products", product_id, updates)
    return updated


async def delete_product(product_id: str, seller_id: str, role: str, db) -> dict:
    product = db_find_one("products", id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["seller_id"] != seller_id and role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_update("products", product_id, {"status": "inactive"})
    return {"message": "Product deactivated"}

