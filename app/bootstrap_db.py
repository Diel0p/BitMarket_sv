"""
Database bootstrap utility.

What it does:
1) Connects to PostgreSQL using DATABASE_URL from environment/.env
2) Ensures document-store schema exists (users, products, orders, invoices, carts, cart_orders)
3) Creates or updates one superuser (admin role)

Usage (from repository root):
    python app/bootstrap_db.py

Custom superuser:
    python app/bootstrap_db.py --email root@bitmarket.sv --password "StrongPass123!" --name "Root Admin"
"""

import argparse
import asyncio
import os
import sys

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SRC_DIR)
for _p in (_ROOT_DIR, _SRC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.app.config.database import connect_db, close_db, db_find_one, db_insert, db_update
from app.app.middleware.auth import hash_password
from app.app.utils.helpers import utcnow


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap PostgreSQL connection and admin user")
    parser.add_argument(
        "--name",
        default=os.getenv("SUPERUSER_NAME", "Super Admin"),
        help="Superuser display name",
    )
    parser.add_argument(
        "--email",
        default=os.getenv("SUPERUSER_EMAIL", "admin@bitmarket.sv"),
        help="Superuser email",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("SUPERUSER_PASSWORD", "Admin1234!"),
        help="Superuser password",
    )
    parser.add_argument(
        "--keep-password",
        action="store_true",
        help="If user exists, keep current password instead of replacing it",
    )
    return parser


async def _bootstrap_superuser(name: str, email: str, password: str, keep_password: bool) -> None:
    existing = db_find_one("users", email=email)

    if not existing:
        db_insert(
            "users",
            {
                "name": name,
                "email": email,
                "hashed_password": hash_password(password),
                "role": "admin",
                "is_active": True,
                "created_at": utcnow().isoformat(),
            },
        )
        print(f"Created superuser: {email}")
        return

    updates = {
        "name": name,
        "role": "admin",
        "is_active": True,
    }
    if not keep_password:
        updates["hashed_password"] = hash_password(password)

    db_update("users", existing["id"], updates)
    print(f"Updated existing user as superuser: {email}")


async def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        await connect_db()
        print("PostgreSQL connection OK")

        await _bootstrap_superuser(
            name=args.name,
            email=args.email,
            password=args.password,
            keep_password=args.keep_password,
        )

        print("Bootstrap completed successfully")
        return 0
    except Exception as exc:
        print(f"Bootstrap failed: {exc}")
        return 1
    finally:
        try:
            await close_db()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
