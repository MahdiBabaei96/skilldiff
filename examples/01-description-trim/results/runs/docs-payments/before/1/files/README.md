# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds.

- `TAX_RATE`: sales tax rate applied to orders (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`, the
  balance left after refunding `amount`.

```python
from shop.payments import line_total, order_total, refund

line_total(5.00, 3)                      # 15.0
total = order_total([(10.00, 2), (5.00, 1)])
print(total)                             # 27.06 (25.00 subtotal + 8.25% tax)
print(refund(total, 5.00))               # 22.06
```
