# ⚡ BitMarket SV

Multi-vendor marketplace with Bitcoin Lightning payments.
**Python + FastAPI backend** with a complete **HTML/JS frontend** served by the same server.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## What it is

BitMarket SV is a complete marketplace application where:

- **Buyers** browse products, place orders, and pay with Bitcoin Lightning
- **Sellers** list products and manage fulfillment
- **Admins** moderate users, products, and view revenue metrics

All payments go through the **Lightning Network** via LNbits.
A **mock mode** runs automatically with no external services — invoices auto-confirm in ~10 seconds.
Orders and users persist locally in SQLite.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/bitmarket-py.git
cd bitmarket-py

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (optional — all defaults work out of the box)
copy .env.example .env
```

---

## How to run

```bash
uvicorn src.main:app --reload
```

That's it. One command starts everything — backend API and frontend UI together.

Data is persisted in `src/data/bitmarket.db`.

---

## How to access the UI

| URL | What you get |
|-----|-------------|
| **http://localhost:8000/** | Marketplace home page |
| http://localhost:8000/products | Product catalog |
| http://localhost:8000/login | Login page |
| http://localhost:8000/register | Sign up |
| http://localhost:8000/seller | Seller dashboard |
| http://localhost:8000/admin | Admin panel |
| **http://localhost:8000/docs** | Swagger API docs |

---

## How to seed demo data

The server must be **running** before seeding:

```bash
# In a second terminal, while the server is running:
python src/seed.py
```

Demo accounts:

| Role | Email | Password |
|------|-------|----------|
| admin | admin@bitmarket.sv | Admin1234! |
| seller | seller@bitmarket.sv | Seller1234! |
| buyer | buyer@bitmarket.sv | Buyer1234! |

5 sample products are created, owned by the seller account.

> **Note:** Data is stored in SQLite at `src/data/bitmarket.db`.

---

## Demo flow

### 1. Browse products (no login needed)
Go to **http://localhost:8000/products** — see the product catalog with filtering.

### 2. Login as buyer
Go to **http://localhost:8000/login**
```
Email:    buyer@bitmarket.sv
Password: Buyer1234!
```

### 3. Buy a product
- Click any product → **View**
- Click **⚡ Buy now**
- You land on the **checkout page** with a Lightning invoice

### 4. Watch the mock payment
- The page shows the BOLT11 invoice string (what a real QR code would contain)
- A progress bar fills over ~10 seconds
- Payment status automatically changes to **confirmed** ✅
- You're redirected to your orders

### 5. Explore seller dashboard
Login as seller → **http://localhost:8000/seller**
- Create new products
- View incoming orders
- Update fulfillment status

### 6. Explore admin panel
Login as admin → **http://localhost:8000/admin**
- View marketplace metrics (revenue in sats, user count, orders)
- Ban/unban users
- Approve or deactivate products

---

## Running tests

```bash
pytest tests/ -v
```

All 15 tests run with zero external services:

```
test_health_ok                          PASSED
test_register_buyer                     PASSED
test_register_seller                    PASSED
test_login_success                      PASSED
test_login_wrong_password               PASSED
test_duplicate_email_rejected           PASSED
test_get_me_authenticated               PASSED
test_get_me_unauthenticated             PASSED
test_list_products_public_no_auth       PASSED
test_create_product_as_seller           PASSED
test_buyer_cannot_create_product        PASSED
test_created_product_appears_in_list    PASSED
test_create_invoice_mock_mode           PASSED
test_create_order_returns_lightning_invoice  PASSED
test_payment_status_returns_mock_info   PASSED

15 passed
```

---

## LNbits live mode

To use real Lightning payments with your LNbits server in AWS:

1. Create or choose the platform wallet in LNbits.
2. Copy its Admin Key.
3. Set these values in `.env`:

```env
LNBITS_URL=https://your-lnbits-domain
LNBITS_ADMIN_KEY=your_platform_wallet_admin_key
MARKETPLACE_FEE_PERCENT=5.0
```

How it works:

- Buyer pays the invoice generated from the platform wallet.
- After LNbits confirms payment, the app pays each seller to their Lightning Address.
- The platform wallet keeps the configured fee percentage.

Seller requirement:

- Seller accounts must register a valid Lightning Address, for example `shop@yourdomain.com`.
- That address is used for automatic payout after the buyer payment settles.

Recommended LNbits setup:

- Expose LNbits over HTTPS on your AWS server.
- Keep the platform wallet Admin Key only in `.env`.
- If sellers use LNbits wallets too, enable Lightning Address/LNURL-pay for their wallets.

---

## Project structure

```
bitmarket-py/
├── src/
│   ├── main.py                    FastAPI app — API + static files + UI router
│   ├── seed.py                    Demo data seeder
│   └── app/
│       ├── config/
│       │   ├── settings.py        Environment config (pydantic-settings)
│       │   └── database.py        In-memory store + CRUD helpers
│       ├── middleware/
│       │   └── auth.py            JWT + bcrypt + role guards
│       ├── models/                Pydantic schemas
│       ├── services/
│       │   ├── payment_service.py ⚡ LNbits + mock mode
│       │   ├── order_service.py
│       │   ├── product_service.py
│       │   ├── user_service.py
│       │   └── admin_service.py
│       ├── controllers/           HTTP layer
│       ├── routes/
│       │   ├── auth_routes.py
│       │   ├── product_routes.py
│       │   ├── order_routes.py
│       │   ├── payment_routes.py
│       │   ├── admin_routes.py
│       │   └── ui_routes.py       ← Serves HTML templates
│       ├── templates/             ← Jinja2 HTML pages
│       │   ├── base.html
│       │   ├── home.html
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── products.html
│       │   ├── product_detail.html
│       │   ├── checkout.html
│       │   ├── orders.html
│       │   ├── seller_dashboard.html
│       │   ├── seller_products.html
│       │   ├── seller_orders.html
│       │   ├── admin_dashboard.html
│       │   ├── admin_users.html
│       │   ├── admin_products.html
│       │   └── admin_orders.html
│       └── static/
│           ├── css/app.css        Dark Bitcoin theme design system
│           └── js/app.js          API client + auth + shared utils
├── strategy/
│   ├── ARCHITECTURE.md
│   ├── IMPACT_ANALYSIS.md
│   ├── OPERATIONAL_MODEL.md
│   └── WORK_LOG.md
├── tests/
│   └── test_api.py               15 integration tests
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## Enabling real Lightning payments (optional)

```env
# .env
LNBITS_URL=https://your-lnbits-instance.com
LNBITS_ADMIN_KEY=your_admin_key_here
```

The payment service switches to live mode automatically.

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Backend | FastAPI 0.111 |
| Frontend | Jinja2 templates + Vanilla JS |
| Database | In-memory dict (swap to MongoDB with one file) |
| Auth | JWT (python-jose) + bcrypt |
| Payments | LNbits API with mock fallback |
| Styling | Vanilla CSS with CSS variables (dark Bitcoin theme) |
| Tests | pytest + pytest-asyncio |

---

## License

MIT
