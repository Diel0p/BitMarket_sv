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
 [Database]        PostgreSQL-backed document store (JSONB docs)
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
Currently PostgreSQL-backed via `DATABASE_URL`. Documents are stored as JSONB inside collection-like tables. All DB access goes through four helpers:
`db_insert`, `db_find_one`, `db_find_all`, `db_update`.
Swapping providers primarily requires replacing these helpers.

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

## Why PostgreSQL document store

The current MVP uses a PostgreSQL-backed document store:
- JSONB offers document-style flexibility with relational reliability
- Works well for local development and production deployment paths
- Keeps a simple NoSQL-style API (`db_insert`, `db_find_one`, etc.)
- Avoids introducing a second database engine for this stage

To migrate providers later, replace the `db_*` helpers in `database.py`.
Services and controllers stay unchanged.

## Scalability path

| Step | Action |
|------|--------|
| 1 | Keep PostgreSQL and evolve schema/index strategy as traffic grows |
| 2 | Add Redis for rate limiting and session caching |
| 3 | Replace LNbits with per-seller split-payment provider |
| 4 | Extract payment service into standalone microservice |
| 5 | Add Celery queue for stock decrement race-condition safety |
