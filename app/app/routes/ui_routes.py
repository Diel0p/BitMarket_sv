"""
UI Routes
=========
Serves the Jinja2 HTML templates for every page of the frontend.
All actual data is fetched client-side via the /api/* endpoints.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

_templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=_templates_dir)

router = APIRouter(tags=["UI"])


def _r(request: Request, template: str, **ctx):
    """Shorthand: render a template with request context."""
    return templates.TemplateResponse(template, {"request": request, **ctx})


# ── Public pages ───────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return _r(request, "home.html")


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return _r(request, "login.html")


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return _r(request, "register.html")


@router.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    return _r(request, "products.html")


@router.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: str):
    return _r(request, "product_detail.html")


# ── Checkout ───────────────────────────────────────────────

@router.get("/checkout/{order_id}", response_class=HTMLResponse)
async def checkout(request: Request, order_id: str):
    return _r(request, "checkout.html")


# ── Buyer ──────────────────────────────────────────────────

@router.get("/orders", response_class=HTMLResponse)
async def orders(request: Request):
    return _r(request, "orders.html")


# ── Seller ─────────────────────────────────────────────────

@router.get("/seller", response_class=HTMLResponse)
async def seller_dashboard(request: Request):
    return _r(request, "seller_dashboard.html")


@router.get("/seller/products", response_class=HTMLResponse)
async def seller_products(request: Request):
    return _r(request, "seller_products.html")


@router.get("/seller/orders", response_class=HTMLResponse)
async def seller_orders(request: Request):
    return _r(request, "seller_orders.html")


# ── Admin ──────────────────────────────────────────────────

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return _r(request, "admin_dashboard.html")


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    return _r(request, "admin_users.html")


@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request):
    return _r(request, "admin_products.html")


@router.get("/admin/orders", response_class=HTMLResponse)
async def admin_orders(request: Request):
    return _r(request, "admin_orders.html")
