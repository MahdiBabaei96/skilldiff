# Shop

A tiny example storefront backend.

## Payments module

The `shop.payments` module (`shop/payments.py`) calculates order totals.
It does not charge cards or talk to a payment provider.

Amounts are plain numbers in the shop's currency. The sales tax rate is
`TAX_RATE = 0.0825` (8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples and returns
  the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`,
  the balance left after a refund. It does not issue a refund.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(4.50, 3)  # 13.5

total = order_total([(4.50, 3), (10.00, 1)])  # (13.5 + 10.0) * 1.0825
total  # 25.44

refund(total, 5.00)  # 20.44
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
