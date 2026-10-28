# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds. It has no external dependencies.

### Constants

- `TAX_RATE`: sales tax applied to every order (`0.0825`, i.e. 8.25%).

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for a single line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line totals,
  applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the remaining balance,
  `order_total_amount - amount`. It does not validate that `amount` is within the total.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.5 subtotal -> 27.6 with tax
remaining = refund(total, 10.00)              # 17.6
```
