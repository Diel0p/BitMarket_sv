"""
BitMarket SV – Integration Tests
==================================
Run from project root:
    pytest unit_tests/ -v

All tests use in-memory storage.
No MongoDB, no LNbits, no external services needed.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# pytest.ini adds app/ to pythonpath, so these resolve cleanly
from main import app
from app.app.config.database import db_clear_all


# ─ Fixtures ────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    """Wipe in-memory DB before every test for full isolation."""
    db_clear_all()
    yield
    db_clear_all()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seller_token(client):
    await client.post("/api/auth/register", json={
        "name": "Test Seller", "email": "seller@test.com",
        "password": "Test1234!", "role": "seller", "store_name": "Test Store",
        "lightning_address": "seller@test.com",
    })
    r = await client.post("/api/auth/login", json={
        "email": "seller@test.com", "password": "Test1234!",
    })
    return r.json()["access_token"]


@pytest_asyncio.fixture
async def buyer_token(client):
    await client.post("/api/auth/register", json={
        "name": "Test Buyer", "email": "buyer@test.com",
        "password": "Test1234!", "role": "buyer",
    })
    r = await client.post("/api/auth/login", json={
        "email": "buyer@test.com", "password": "Test1234!",
    })
    return r.json()["access_token"]


# ─ 1. Health check ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"]   == "ok"
    assert r.json()["database"] == "sqlite"
    assert r.json()["payments"] == "mock"


# ─ 2. Auth – login ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_buyer(client):
    r = await client.post("/api/auth/register", json={
        "name": "Jane Doe", "email": "jane@test.com",
        "password": "Password1!", "role": "buyer",
    })
    assert r.status_code == 201
    assert r.json()["success"] is True
    assert "access_token" in r.json()
    assert r.json()["user"]["role"] == "buyer"


@pytest.mark.asyncio
async def test_register_seller(client):
    r = await client.post("/api/auth/register", json={
        "name": "Bob Shop", "email": "bob@test.com",
        "password": "Password1!", "role": "seller", "store_name": "Bob's Store",
        "lightning_address": "bob@test.com",
    })
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "seller"
    assert r.json()["user"]["lightning_address"] == "bob@test.com"


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={
        "name": "Alice", "email": "alice@test.com",
        "password": "Test1234!", "role": "buyer",
    })
    r = await client.post("/api/auth/login", json={
        "email": "alice@test.com", "password": "Test1234!",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "name": "Alice", "email": "alice@test.com",
        "password": "Test1234!", "role": "buyer",
    })
    r = await client.post("/api/auth/login", json={
        "email": "alice@test.com", "password": "wrongpassword",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client):
    payload = {"name": "Ali", "email": "dup@test.com", "password": "Test1234!", "role": "buyer"}
    await client.post("/api/auth/register", json=payload)
    r = await client.post("/api/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_me_authenticated(client, buyer_token):
    r = await client.get("/api/auth/me",
                         headers={"Authorization": f"Bearer {buyer_token}"})
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "buyer"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    r = await client.get("/api/auth/me")
    assert r.status_code == 403


# ─ 3. Products ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_products_public_no_auth(client):
    r = await client.get("/api/products")
    assert r.status_code == 200
    assert "products" in r.json()
    assert "total" in r.json()


@pytest.mark.asyncio
async def test_create_product_as_seller(client, seller_token):
    r = await client.post(
        "/api/products",
        json={
            "title": "Test Widget",
            "description": "A great widget for demo purposes.",
            "price_sats": 10_000,
            "category": "Electronics",
            "stock": 5,
        },
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert r.status_code == 201
    p = r.json()["product"]
    assert p["price_sats"] == 10_000
    assert p["price_btc"]  == 0.0001
    assert p["status"]     == "active"
    assert p["stock"]      == 5


@pytest.mark.asyncio
async def test_buyer_cannot_create_product(client, buyer_token):
    r = await client.post(
        "/api/products",
        json={
            "title": "Not allowed",
            "description": "Buyers should not create products.",
            "price_sats": 1_000,
            "category": "Test",
            "stock": 1,
        },
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_created_product_appears_in_list(client, seller_token):
    await client.post(
        "/api/products",
        json={
            "title": "Visible Product",
            "description": "Should appear in the public listing.",
            "price_sats": 5_000,
            "category": "Books",
            "stock": 10,
        },
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    r = await client.get("/api/products")
    assert r.json()["total"] >= 1
    titles = [p["title"] for p in r.json()["products"]]
    assert "Visible Product" in titles


# ─ 4. Create invoice (mock mode) ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invoice_mock_mode(client, buyer_token):
    """
    POST /api/payments/create-invoice
    Should work with zero LNbits configuration (mock mode).
    """
    r = await client.post(
        "/api/payments/create-invoice",
        json={
            "order_id":   "demo-order-001",
            "amount_sats": 5_000,
            "memo":        "Demo payment",
        },
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert r.status_code == 200
    inv = r.json()["invoice"]
    assert inv["amount_sats"]     == 5_000
    assert inv["is_mock"]         is True
    assert inv["payment_request"].startswith("lnbc")
    assert len(inv["payment_hash"]) > 10


@pytest.mark.asyncio
async def test_create_order_returns_lightning_invoice(client, seller_token, buyer_token):
    """Full order flow: place order → receive BOLT11 invoice."""
    # Create product as seller
    prod_r = await client.post(
        "/api/products",
        json={
            "title": "Order Test Item",
            "description": "This item will be ordered.",
            "price_sats": 20_000,
            "category": "Electronics",
            "stock": 3,
        },
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    product_id = prod_r.json()["product"]["id"]

    # Place order as buyer
    order_r = await client.post(
        "/api/orders",
        json={
            "items": [{"product_id": product_id, "quantity": 1}],
            "shipping_address": {
                "name": "Test Buyer",
                "street": "123 Main St",
                "city": "San Salvador",
                "country": "El Salvador",
            },
        },
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert order_r.status_code == 201
    data = order_r.json()

    assert data["success"]    is True
    assert data["total_sats"] == 20_000

    inv = data["invoice"]
    assert inv["amount_sats"]     == 20_000
    assert inv["is_mock"]         is True
    assert inv["payment_request"].startswith("lnbc")
    assert "payment_hash" in inv


# ─ 5. Payment status check ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_payment_status_returns_mock_info(client, buyer_token):
    """
    GET /api/payments/status/{hash}
    Should respond with paid status info even in mock mode.
    """
    create_r = await client.post(
        "/api/payments/create-invoice",
        json={"order_id": "poll-test-001", "amount_sats": 1_000},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    payment_hash = create_r.json()["invoice"]["payment_hash"]

    status_r = await client.get(
        f"/api/payments/status/{payment_hash}",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert status_r.status_code == 200
    data = status_r.json()
    assert "paid"    in data
    assert "status"  in data
    assert "is_mock" in data
    assert data["is_mock"] is True   # no LNbits configured in tests
