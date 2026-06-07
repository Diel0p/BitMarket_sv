# Work Log

## Project timeline

### Phase 1 — Architecture and foundation
- Defined layered architecture: Routes → Controllers → Services → Models
- Chose FastAPI for async performance and auto-generated OpenAPI docs
- Chose Pydantic v2 for request validation and response serialization
- Implemented JWT authentication with role-based access control
- Created three roles: buyer, seller, admin

### Phase 2 — Core features
- Product system: create, list (with search/filter/pagination), update, delete
- Order system: validation, stock management, multi-item orders
- Payment service: decoupled abstraction supporting LNbits and mock mode
- Admin service: metrics, user moderation, product moderation

### Phase 3 — Database decision
- Initial implementation used MongoDB (Motor async driver)
- Replaced with PostgreSQL-backed document store (JSONB)
- Documents stored as JSONB inside collection-like tables; exposes same `db_insert/db_find_one/db_find_all/db_update` API
- Decision rationale: production-aligned engine, robust indexing, without changing service/controller code
- Migration path documented: only `database.py` needs to change

### Phase 4 — Demo hardening
- Moved `main.py` into `src/` to match required repository structure
- Fixed all import paths after relocation
- Replaced `passlib` with direct `bcrypt` calls (passlib incompatible with bcrypt 4.x on Python 3.12)
- Added `pytest.ini` `pythonpath = src` for clean test imports
- Verified all 15 tests pass: health, auth, products, invoices, orders, payment status

### Phase 5 — Documentation
- README focused on evaluation and demo workflow
- Strategy folder: Architecture, Impact Analysis, Operational Model, Work Log
- Seed script with clear demo account table
- `.env.example` with all defaults commented

## Key decisions and rationale

| Decision | Alternative considered | Reason chosen |
|----------|----------------------|---------------|
| FastAPI | Flask | Async, auto-docs, Pydantic integration |
| PostgreSQL JSONB | MongoDB | Production-friendly, strong indexing, still swappable at helper layer |
| Direct bcrypt | passlib | passlib broke with bcrypt 4.x on Python 3.12 |
| Mock payment mode | Require real LNbits | Demo must work without any external services |
| JWT in headers | Session cookies | Stateless, works with any client including curl |

## Known limitations (MVP scope)

- Some business flows still need stronger transactional guarantees under high concurrency
- No file upload for product images (placeholder field exists)
- No email notifications
- No rate limiting (add `slowapi` for production)
- Stock decrement is not atomic (add Redis lock for high concurrency)

## Suggested next commits

```bash
git commit -m "chore: move main.py to src/, update all imports"
git commit -m "feat(db): replace MongoDB with PostgreSQL-backed JSONB document store"
git commit -m "fix(auth): replace passlib with direct bcrypt for Python 3.12 compat"
git commit -m "test: all 15 integration tests passing, zero external dependencies"
git commit -m "docs: add strategy folder with architecture, impact, and operational docs"
git commit -m "docs: simplify README for evaluation and demo workflow"
```
