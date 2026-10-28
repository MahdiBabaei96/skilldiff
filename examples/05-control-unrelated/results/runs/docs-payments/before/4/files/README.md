# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds.

- `TAX_RATE`: sales tax rate applied to every order (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: price multiplied by quantity for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus the refunded
  amount, i.e. what remains after the refund. It does not validate `amount`.

```python
from shop.payments import line_total, order_total, refund

line_total(10.00, 3)                     # 30.0
total = order_total([(10.00, 2), (5.50, 1)])  # 27.6 (25.50 + 8.25% tax, rounded)
remaining = refund(total, 5.00)          # 22.6
```
