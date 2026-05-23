"""
Admin Service â€” marketplace metrics, user and product moderation.
"""

from fastapi import HTTPException

from app.app.config.database import db_insert, db_find_all, db_find_one, db_update, db_count
from app.app.middleware.auth import hash_password
from app.app.models.user import AdminCreateUserRequest
from app.app.utils.helpers import normalize_phone, sats_to_btc, utcnow


async def get_marketplace_stats(db) -> dict:
    users    = db_find_all("users")
    products = db_find_all("products", status="active")
    orders   = db_find_all("orders")
    paid     = [o for o in orders if o.get("payment_status") == "paid"]
    revenue  = sum(o.get("total_sats", 0) for o in paid)
    platform_revenue = sum(o.get("platform_fee_sats", 0) for o in paid)
    seller_net_total = sum(o.get("seller_net_sats", o.get("total_sats", 0)) for o in paid)

    return {
        "total_users":        len(users),
        "total_products":     len(products),
        "total_orders":       len(orders),
        "total_paid_orders":  len(paid),
        "total_revenue_sats": revenue,
        "total_revenue_btc":  sats_to_btc(revenue),
        "platform_revenue_sats": platform_revenue,
        "seller_net_total_sats": seller_net_total,
    }


async def list_users(role: str | None, page: int, limit: int, db) -> dict:
    users = db_find_all("users") if not role else db_find_all("users", role=role)
    safe  = [{k: v for k, v in u.items() if k != "hashed_password"} for u in users]
    total = len(safe)
    skip  = (page - 1) * limit
    return {
        "users": safe[skip: skip + limit],
        "total": total,
        "page":  page,
        "pages": max(1, -(-total // limit)),
    }


async def create_super_user(data: AdminCreateUserRequest, db) -> dict:
    if db_find_one("users", email=data.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "name": data.name,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "role": "admin",
        "is_active": True,
        "created_at": utcnow().isoformat(),
    }
    if data.phone:
        try:
            doc["phone"] = normalize_phone(data.phone)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if data.address:
        doc["address"] = data.address.strip()
    if data.department:
        doc["department"] = data.department.strip()
    if data.municipality:
        doc["municipality"] = data.municipality.strip()
    if data.district:
        doc["district"] = data.district.strip()

    user_id = db_insert("users", doc)
    safe = {k: v for k, v in doc.items() if k != "hashed_password"}
    return {"message": "Super admin created successfully", "user_id": user_id, "user": safe}


async def toggle_user(user_id: str, db) -> dict:
    from app.services.user_service import toggle_user_status
    return await toggle_user_status(user_id, db)


async def list_all_products(status_filter: str | None, page: int, limit: int, db) -> dict:
    products = db_find_all("products") if not status_filter else db_find_all("products", status=status_filter)
    total    = len(products)
    skip     = (page - 1) * limit
    return {
        "products": products[skip: skip + limit],
        "total":    total,
        "page":     page,
        "pages":    max(1, -(-total // limit)),
    }


async def update_product_status(product_id: str, new_status: str, db) -> dict:
    allowed = {"active", "inactive", "pending", "rejected"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {allowed}")

    product = db_find_one("products", id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_update("products", product_id, {"status": new_status})
    return {"message": f"Product status updated to '{new_status}'"}


async def list_all_orders(payment_status: str | None, page: int, limit: int, db) -> dict:
    orders = db_find_all("orders") if not payment_status else db_find_all("orders", payment_status=payment_status)
    total  = len(orders)
    skip   = (page - 1) * limit
    return {
        "orders": orders[skip: skip + limit],
        "total":  total,
        "page":   page,
        "pages":  max(1, -(-total // limit)),
    }

