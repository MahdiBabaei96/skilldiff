# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order
totals, including sales tax, and handles refund amounts. It does not
talk to a payment provider.

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples and
  returns the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns the remaining amount
  after a refund, `order_total_amount - amount`.

### Tax

Tax is applied to the whole order using the module constant
`TAX_RATE = 0.0825` (8.25%). The rate is not configurable per call.

### Example

```python
from shop.payments import line_total, order_total, refund

lines = [(10.00, 2), (3.50, 1)]

subtotal = sum(line_total(price, qty) for price, qty in lines)  # 23.5
total = order_total(lines)  # 25.44 (23.5 + 8.25% tax)
remaining = refund(total, 5.00)  # 20.44
```

### Notes

- `refund` does not check that `amount` is at most `order_total_amount`,
  nor that it is positive. Validate inputs before calling it.
- Amounts are floats. For money in production, consider `Decimal`.
