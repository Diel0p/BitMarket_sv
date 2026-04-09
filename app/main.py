"""
BitMarket SV â€” FastAPI Application Entry Point
==============================================

Run from project root:
    uvicorn app.main:app --reload

    # or directly:
    python app/main.py
"""

import os
import sys

# â”€â”€ Path setup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SRC_DIR)
for _p in (_ROOT_DIR, _SRC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.app.config.settings import get_settings
from app.app.config.database import connect_db, close_db
from app.app.routes import (
    auth_routes,
    product_routes,
    order_routes,
    payment_routes,
    admin_routes,
    ui_routes,
)

settings = get_settings()

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_STATIC_DIR = os.path.join(_SRC_DIR, "app", "static")


# â”€â”€ Lifespan â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"""
  âš¡ {settings.app_name} v{settings.app_version}
  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  Port      : {settings.app_port}
  UI        : http://localhost:{settings.app_port}/
  API docs  : http://localhost:{settings.app_port}/docs
    Database  : SQLite document store
  Payments  : {"ðŸŸ¡ Mock mode (auto-confirms in 10s)" if settings.lnbits_mock_mode else "ðŸŸ¢ LNbits live"}
  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  Seed demo data: python app/seed.py
    """)
    await connect_db()
    yield
    await close_db()


# â”€â”€ App â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
app = FastAPI(
    title="BitMarket SV",
    version=settings.app_version,
    description="""
## âš¡ BitMarket SV â€” Bitcoin Lightning Marketplace

Multi-vendor marketplace with instant Bitcoin Lightning payments.

### Demo accounts (after running `python app/seed.py`)
| Role | Email | Password |
|------|-------|----------|
| admin | admin@bitmarket.sv | Admin1234! |
| seller | seller@bitmarket.sv | Seller1234! |
| buyer | buyer@bitmarket.sv | Buyer1234! |

### UI
Visit **http://localhost:8000/** for the full marketplace interface.
    """,
    lifespan=lifespan,
)

# â”€â”€ CORS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# â”€â”€ Static files â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# â”€â”€ Global error handler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": str(exc)},
    )


# â”€â”€ Health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status":   "ok",
        "version":  settings.app_version,
        "database": "sqlite",
        "payments": "mock" if settings.lnbits_mock_mode else "lnbits-live",
    }


# â”€â”€ API routers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PREFIX = "/api"
app.include_router(auth_routes.router,    prefix=PREFIX)
app.include_router(product_routes.router, prefix=PREFIX)
app.include_router(order_routes.router,   prefix=PREFIX)
app.include_router(payment_routes.router, prefix=PREFIX)
app.include_router(admin_routes.router,   prefix=PREFIX)

# â”€â”€ UI router (must come last â€” catches all remaining paths) â”€
app.include_router(ui_routes.router)


# â”€â”€ Dev runner â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)

