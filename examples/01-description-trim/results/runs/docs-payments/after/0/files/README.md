# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` computes order totals, including sales tax, and refunds.

- `TAX_RATE`: sales tax rate applied to the subtotal (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for one line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus the refunded
  amount. It does no validation, so `amount` may exceed the total.

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.5 * 1.0825 -> 27.6
remaining = refund(total, 5.00)
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
