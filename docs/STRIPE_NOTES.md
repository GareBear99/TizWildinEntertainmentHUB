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
