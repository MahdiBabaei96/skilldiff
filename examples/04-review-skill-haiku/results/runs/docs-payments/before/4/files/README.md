# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals and refund amounts. It does not
charge cards or talk to a payment provider; it only does the arithmetic.

### Tax

Sales tax is applied with the module-level constant `TAX_RATE`, currently
`0.0825` (8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line. It
  does not round.
- `order_total(lines)` takes a list of `(price, quantity)` tuples, sums the
  line totals, adds tax, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`.
  It does not check that `amount` is positive or no greater than the order
  total, and it does not round.

### Example

```python
from shop.payments import line_total, order_total, refund

lines = [(10.00, 2), (3.50, 1)]

line_total(10.00, 2)   # 20.0
order_total(lines)     # 23.5 * 1.0825 = 25.43875, rounded to 25.44

refund(25.44, 5.00)    # 20.44
```

Note that `refund` returns a number only. Any money movement must be handled
by the caller.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
