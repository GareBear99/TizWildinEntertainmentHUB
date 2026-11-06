# Stripe Notes

## Billing products to create

### One-time products
Create one-time Stripe products/prices for paid plugins as needed.

### Complete Collection
One-time or subscription bundle for `ownsEveryVST`.

### Extra Seats
- Product: `TizWildin Extra Seats`
- Billing: monthly recurring
- Unit amount: $3.00
- Quantity-based: yes
- Quantity cap enforced by ARC: 0..9 extra seats

> **Not the Master Key.** The 0..9 cap above (and `maxExtraSeats: 9` in `arc_service/app/data/products.catalog.json`) belongs to the ARC-side "Extra Seats" product for the ownsEveryVST bundle. The live license worker (tizwildin-hub) caps **Master Key at 3 seats** (`Math.min(3, …)` on checkout and link; $3 CAD/seat/month, max $9 CAD/month). Do not read the 9 as a Master Key seat count — the two numbers are different products enforced in different places.

## Webhooks ARC should ingest
- checkout.session.completed
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.paid
- invoice.payment_failed

## Portal expectations
Use the Stripe customer portal for:
- quantity changes
- payment method updates
- invoice history
- cancellation/reactivation
