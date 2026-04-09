# Architecture

## Layer diagram

```
HTTP Request
     │
     ▼
 [Routes]          url mapping, FastAPI router
     │
     ▼
 [Controllers]     parse request → call service → return response
     │
     ▼
 [Services]        business logic, validation, orchestration
     │
     ▼
 [Database]        in-memory dict store (swap to MongoDB/Postgres later)
```

## Layer responsibilities

**Routes** (`src/app/routes/`)
Register URL paths, HTTP methods, and authentication guards. No logic.

**Controllers** (`src/app/controllers/`)
Extract data from requests, delegate to services, shape HTTP responses.
Never touch the database directly.

**Services** (`src/app/services/`)
Own all business rules. Raise `HTTPException` for expected errors.
Orchestrate multi-step operations (create order → generate invoice → decrement stock).

**Models** (`src/app/models/`)
Pydantic v2 schemas for request validation and response serialization.
Auto-documented via FastAPI's OpenAPI integration.

**Database** (`src/app/config/database.py`)
Currently in-memory (`dict`). All DB access goes through four helpers:
`db_insert`, `db_find_one`, `db_find_all`, `db_update`.
Swapping to MongoDB only requires replacing these four functions.

## Payment layer

`src/app/services/payment_service.py` exposes three functions:

```python
create_invoice(amount_sats, memo, order_id) → dict
check_invoice_status(payment_hash)          → dict
get_wallet_balance()                        → dict
```

Mock mode activates when `LNBITS_URL` is empty (the default).
Mock invoices auto-confirm after `MOCK_CONFIRM_SECONDS` seconds.
To swap providers (Alby, OpenNode, Strike): only `payment_service.py` changes.

## Authentication

JWT tokens, HS256, configurable expiry (default 7 days). Role guards:

```python
get_buyer  = require_roles(UserRole.BUYER)
get_seller = require_roles(UserRole.SELLER)
get_admin  = require_roles(UserRole.ADMIN)
```

## Why in-memory instead of MongoDB

MongoDB was replaced with in-memory storage for this MVP:
- Zero external dependencies — no install, no config, no connection errors
- Identical dict-based API — trivial to swap back to Motor
- Sufficient for demo and evaluation

To restore MongoDB: replace the four `db_*` helpers in `database.py`
with Motor calls. Services and controllers stay unchanged.

## Scalability path

| Step | Action |
|------|--------|
| 1 | Replace in-memory DB with MongoDB Motor — only `database.py` changes |
| 2 | Add Redis for rate limiting and session caching |
| 3 | Replace LNbits with per-seller split-payment provider |
| 4 | Extract payment service into standalone microservice |
| 5 | Add Celery queue for stock decrement race-condition safety |
