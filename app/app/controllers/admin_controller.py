"""
Admin Controller
================
Marketplace moderation and metrics. Admin-only endpoints.
"""

from typing import Optional
from fastapi import Depends, Query

from app.app.config.database import get_db
from app.app.middleware.auth import get_admin
from app.app.services import admin_service


async def stats(current_user: dict = Depends(get_admin), db=Depends(get_db)):
    result = await admin_service.get_marketplace_stats(db)
    return {"success": True, "stats": result}


async def list_users(
    role: Optional[str] = Query(None, description="Filter by role: buyer, seller, admin"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_admin),
    db=Depends(get_db),
):
    result = await admin_service.list_users(role, page, limit, db)
    return {"success": True, **result}


async def toggle_user(
    user_id: str,
    current_user: dict = Depends(get_admin),
    db=Depends(get_db),
):
    result = await admin_service.toggle_user(user_id, db)
    return {"success": True, **result}


async def list_products(
    status: Optional[str] = Query(None, description="Filter: active, inactive, pending, rejected"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_admin),
    db=Depends(get_db),
):
    result = await admin_service.list_all_products(status, page, limit, db)
    return {"success": True, **result}


async def set_product_status(
    product_id: str,
    status: str,
    current_user: dict = Depends(get_admin),
    db=Depends(get_db),
):
    result = await admin_service.update_product_status(product_id, status, db)
    return {"success": True, **result}


async def list_orders(
    payment_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_admin),
    db=Depends(get_db),
):
    result = await admin_service.list_all_orders(payment_status, page, limit, db)
    return {"success": True, **result}

