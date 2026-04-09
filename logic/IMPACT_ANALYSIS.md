# Impact Analysis

## Problem this project solves

Traditional online marketplaces (Amazon, eBay, Mercado Libre) require:
- Bank accounts or credit cards for buyers
- Payment processors that charge 2–5% per transaction
- Settlement delays of 1–5 business days
- Geographic restrictions (many payment processors don't serve Latin America)

**BitMarket SV solves all four problems using Bitcoin Lightning Network:**
- Anyone with a smartphone can pay — no bank required
- Transaction fees are fractions of a cent
- Settlement is instant (seconds, not days)
- Works globally with no geographic restrictions

## Who benefits

| Stakeholder | Problem today | Benefit with BitMarket SV |
|-------------|--------------|--------------------------|
| Small sellers in LatAm | Can't accept international cards | Accept any Lightning wallet globally |
| Unbanked buyers | Excluded from e-commerce | Buy with Bitcoin on a phone |
| Marketplace operators | Stripe/PayPal fees eat margins | Near-zero payment processing costs |
| Developers | Complex payment integrations | One clean API, mock mode for testing |

## Financial impact (illustrative)

A seller doing $10,000/month in sales:

| Method | Fee rate | Monthly cost |
|--------|----------|-------------|
| Stripe | 2.9% + $0.30/txn | ~$350 |
| PayPal | 3.49% + $0.49/txn | ~$400 |
| Bitcoin Lightning | ~0.01% | ~$1 |

Annual savings: ~$4,200 per seller.

## Technical impact

- **Latency**: Lightning payments settle in 1–3 seconds vs 1–3 business days (cards)
- **Availability**: No third-party processor downtime risk
- **Privacy**: No PII shared with payment networks
- **Programmability**: Invoice creation is a single HTTP POST

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| LNbits downtime | Medium | Decoupled payment layer — swap provider in one file |
| Lightning liquidity issues | Low for small amounts | Mock mode always available for demos |
| Bitcoin volatility | Medium | Future: stablecoin layer (e.g. USDT on Lightning) |
| Regulatory uncertainty | Medium | System is non-custodial — sellers hold their own keys |

## Comparison with existing solutions

| Feature | BitMarket SV | OpenBazaar | Shopify + Crypto |
|---------|-------------|-----------|-----------------|
| Lightning-native | ✅ | ❌ | Plugin only |
| No KYC required | ✅ | ✅ | ❌ |
| Multi-vendor | ✅ | ✅ | ✅ (paid plan) |
| Role-based access | ✅ | ❌ | ✅ |
| Open source | ✅ | ✅ | ❌ |
| Demo-friendly | ✅ (mock mode) | ❌ | ❌ |
