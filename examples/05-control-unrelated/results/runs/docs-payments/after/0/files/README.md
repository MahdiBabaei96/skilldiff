# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds.

- `TAX_RATE`: flat sales tax rate, `0.0825` (8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus `amount`,
  i.e. the balance left after the refund. It does not validate that `amount`
  is positive or no larger than the order total.

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.50 plus tax -> 27.6
remaining = refund(total, 5.00)               # 22.6
```
