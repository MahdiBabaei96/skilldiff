# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds. It has no dependencies
and does no I/O.

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one order line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples. It sums the
  line totals, applies tax, and returns the result rounded to 2 decimals.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`,
  the balance left after refunding `amount`. It does not validate its inputs.

### Configuration

`TAX_RATE` is a module constant, currently `0.0825` (8.25%). It is applied to
the subtotal of the whole order, not per line.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.5 * 1.0825 -> 27.6
remaining = refund(total, 5.00)               # 22.6
```
