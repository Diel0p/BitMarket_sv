"""
BitMarket SV â€” Demo Seed Script
================================
Populates the in-memory database with demo accounts and products.

Usage (from project root):
    python app/seed.py

    # Then start the server:
    uvicorn app.main:app --reload
"""

import os
import sys
import asyncio

_SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SRC_DIR)
for _p in (_ROOT_DIR, _SRC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bcrypt as _bcrypt
from app.app.config.database import db_insert, db_clear_all, db_find_one
from app.app.utils.helpers import utcnow



DEMO_USERS = [
    {
        "name":     "Admin BitMarket",
        "email":    "admin@bitmarket.sv",
        "password": "Admin1234!",
        "role":     "admin",
    },
    {
        "name":       "Ana LÃ³pez",
        "email":      "seller@bitmarket.sv",
        "password":   "Seller1234!",
        "role":       "seller",
        "store_name": "TechSV Store",
        "lightning_address": "seller@bitmarket.sv",
    },
    {
        "name":     "MarÃ­a GarcÃ­a",
        "email":    "buyer@bitmarket.sv",
        "password": "Buyer1234!",
        "role":     "buyer",
    },
]

DEMO_PRODUCTS = [
    {
        "title":       "Raspberry Pi 5 â€” 8GB",
        "description": "The latest Raspberry Pi 5 with 8GB RAM. Perfect for projects, servers, and learning embedded Linux.",
        "price_sats":  150_000,
        "category":    "Electronics",
        "stock":       10,
        "tags":        ["raspberry", "linux", "hardware"],
    },
    {
        "title":       "Mechanical Keyboard TKL RGB",
        "description": "Tenkeyless mechanical keyboard with Cherry MX Brown switches and per-key RGB backlight.",
        "price_sats":  80_000,
        "category":    "Electronics",
        "stock":       5,
        "tags":        ["keyboard", "gaming", "mechanical"],
    },
    {
        "title":       "The Bitcoin Standard â€” Spanish Edition",
        "description": "Saifedean Ammous' seminal book on Bitcoin as sound money.",
        "price_sats":  25_000,
        "category":    "Books",
        "stock":       30,
        "tags":        ["bitcoin", "book", "economics"],
    },
    {
        "title":       "Bitcoin Art Print â€” Limited Edition",
        "description": "High-quality art print celebrating Bitcoin. Only 21 copies.",
        "price_sats":  50_000,
        "category":    "Art",
        "stock":       21,
        "tags":        ["bitcoin", "art", "collectible"],
    },
    {
        "title":       "USB-C Hub 10-in-1",
        "description": "HDMI 4K, USB 3.0, SD card, PD charging â€” compact aluminum hub.",
        "price_sats":  35_000,
        "category":    "Electronics",
        "stock":       15,
        "tags":        ["usb", "hub", "accessories"],
    },
]


def seed():
    db_clear_all()
    print("ðŸŒ± Seeding demo dataâ€¦\n")

    # Users
    seller_id = None
    for u in DEMO_USERS:
        doc = {
            "name":            u["name"],
            "email":           u["email"],
            "hashed_password": _bcrypt.hashpw(u["password"].encode(), _bcrypt.gensalt()).decode(),
            "role":            u["role"],
            "is_active":       True,
            "created_at":      utcnow().isoformat(),
        }
        if u["role"] == "seller":
            doc["store_name"] = u.get("store_name", f"{u['name']}'s Store")
            doc["lightning_address"] = u.get("lightning_address")

        uid = db_insert("users", doc)
        if u["role"] == "seller":
            seller_id = uid
        print(f"  âœ“ {u['role'].upper():8s} {u['email']}")

    print()

    # Products (all owned by the seller)
    for p in DEMO_PRODUCTS:
        seller = db_find_one("users", id=seller_id) or {}
        db_insert("products", {
            **p,
            "price_btc":  round(p["price_sats"] / 100_000_000, 8),
            "status":     "active",
            "seller_id":  seller_id,
            "seller_name": seller.get("name", "Seller"),
            "images":     [],
            "created_at": utcnow().isoformat(),
        })
        print(f"  âœ“ Product   {p['title']}")

    print(f"""
âœ… Demo data ready!

  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
  â”‚ Role     â”‚ Email                       â”‚ Password     â”‚
  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
  â”‚ admin    â”‚ admin@bitmarket.sv          â”‚ Admin1234!   â”‚
  â”‚ seller   â”‚ seller@bitmarket.sv         â”‚ Seller1234!  â”‚
  â”‚ buyer    â”‚ buyer@bitmarket.sv          â”‚ Buyer1234!   â”‚
  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

    âš ï¸  Demo seller Lightning Address: seller@bitmarket.sv
            If you run live LNbits payouts, replace it with a real address.
    """)


if __name__ == "__main__":
    seed()

