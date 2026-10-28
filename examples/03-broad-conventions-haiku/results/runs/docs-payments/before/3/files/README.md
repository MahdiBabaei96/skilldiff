# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals and refunds. It has no
external dependencies and does not talk to a payment provider.

Tax is applied at a flat `TAX_RATE` of `0.0825` (8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples, sums
  the line totals, applies tax, and returns the result rounded to 2
  decimal places.
- `refund(order_total_amount, amount)` returns the remaining balance,
  `order_total_amount - amount`.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (3.50, 1)])  # subtotal 23.50, with tax
remaining = refund(total, 5.00)               # balance after a 5.00 refund
```

### Notes

- Amounts are plain numbers. The module uses binary floats, so results
  can carry small rounding error. Only `order_total` rounds its result.
- `refund` does not check that `amount` is positive or that it does not
  exceed the order total. Validate input before calling it.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
