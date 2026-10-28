# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals and refund amounts. It has no
external dependencies and does not call a payment provider.

### Tax rate

`TAX_RATE` is a flat sales tax rate of `0.0825` (8.25%). Every order total
applies this rate.

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line item.
- `order_total(lines)` takes a list of `(price, quantity)` tuples and returns
  the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`.
  It does not check that `amount` is positive or no larger than the total.

### Example

```python
from shop.payments import line_total, order_total, refund

lines = [(10.00, 2), (5.50, 1)]

subtotal = sum(line_total(price, qty) for price, qty in lines)  # 25.5
total = order_total(lines)  # 27.6
remaining = refund(total, 7.60)  # 20.0
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
