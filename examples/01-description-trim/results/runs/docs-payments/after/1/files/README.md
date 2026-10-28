# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals for the shop.

### API

- `TAX_RATE`: sales tax rate applied to orders (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for a single line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line totals,
  applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`, the
  balance left after refunding `amount`. It does not validate its arguments.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.5 plus tax -> 27.6
remaining = refund(total, 5.00)               # 22.6
```
