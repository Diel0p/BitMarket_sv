# Operational Model

## How the marketplace works end-to-end

```
Seller registers → creates products → sets price in satoshis
                                              │
                                              ▼
Buyer registers → browses catalog → adds to cart
                                              │
                                              ▼
                              POST /api/orders
                                              │
                          ┌───────────────────┘
                          │
                    Validate stock
                    Create order document
                    Call payment_service.create_invoice()
                          │
                          ▼
                   BOLT11 invoice returned
                   (QR code string)
                          │
                          ▼
                   Buyer scans with Lightning wallet
                   (Phoenix / Zeus / Muun / Breez)
                          │
                          ▼
                   GET /api/orders/payment-status/{hash}
                   (poll every 3 seconds)
                          │
                          ▼
                   paid = true
                   Order confirmed, stock decremented
                          │
                          ▼
                   Seller sees order in dashboard
                   Updates fulfillment status:
                   pending → processing → shipped → delivered
```

## User roles and permissions

### Buyer
- Register, login
- Browse and search products (no auth required)
- Place orders and pay via Lightning
- View own order history

### Seller
- Register with store name
- Create, edit, delete own products
- View orders containing their products
- Update fulfillment status per item

### Admin
- View marketplace metrics (users, revenue, orders)
- Ban or unban user accounts
- Approve, reject, or deactivate product listings
- View all orders

## Payment modes

### Mock mode (default — no setup required)
- Activated automatically when `LNBITS_URL` is not set
- `create_invoice()` returns a realistic-looking fake BOLT11 string
- `check_invoice_status()` returns `paid=true` after 10 seconds
- Entire demo flow works without real Bitcoin

### Live mode (set LNBITS_URL + LNBITS_ADMIN_KEY)
- Real BOLT11 invoices returned
- Scannable by any Lightning wallet
- Settlement detected via polling or webhook

## Data lifecycle

| Entity | Created when | Persists | Deleted when |
|--------|-------------|---------|-------------|
| User | Register | Until banned | Admin action |
| Product | Seller creates | Until deactivated | Seller/admin action |
| Order | Checkout | Permanently | Never (audit trail) |
| Invoice | Order created | Until expired | Never (audit trail) |

## Revenue model (suggested for production)

| Model | Description | Rate |
|-------|-------------|------|
| Commission | % of each transaction | 1–2% |
| Subscription | Monthly seller plan | $10–$50/mo |
| Featured listings | Promoted placement | Per listing |

## Infrastructure requirements (production)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| API server | 1 vCPU, 512MB RAM | 2 vCPU, 2GB RAM |
| Database | PostgreSQL (current MVP) | PostgreSQL gestionado dedicado |
| LNbits | Self-hosted VPS | Dedicated node |
| Storage | Local disk | S3-compatible |
