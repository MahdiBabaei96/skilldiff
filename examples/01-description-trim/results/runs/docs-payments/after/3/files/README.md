# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds.

- `TAX_RATE`: sales tax rate applied to orders (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus `amount`,
  i.e. the balance remaining after the refund.

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # (20.00 + 5.50) * 1.0825 = 27.6
remaining = refund(total, 10.00)              # 17.6
```
