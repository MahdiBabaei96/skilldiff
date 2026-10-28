# Shop

A tiny example storefront backend.

## Payments module

The `shop/payments.py` module calculates order totals and refunds.

Tax is applied at a flat `TAX_RATE` of `0.0825` (8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for a single line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples and returns
  the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns the remaining balance after
  refunding `amount` from `order_total_amount`.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # subtotal 25.50 -> 27.60
remaining = refund(total, 7.60)                # 27.60 - 7.60 -> 20.00
```

Note that `refund` does not validate its inputs. Passing an `amount` greater
than `order_total_amount` returns a negative balance.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
