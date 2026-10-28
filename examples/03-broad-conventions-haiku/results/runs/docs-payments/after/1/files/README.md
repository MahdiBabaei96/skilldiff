# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals, including tax, and refund balances.

The sales tax rate is the module constant `TAX_RATE` (`0.0825`, or 8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for a single line item.
- `order_total(lines)` takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`, the
  amount left after subtracting `amount` from the order total. It does not check
  that `amount` is valid.

### Example

```python
from shop.payments import line_total, order_total, refund

lines = [(10.00, 2), (3.50, 1)]  # subtotal 23.50

total = order_total(lines)  # 23.50 * 1.0825 = 25.44 (rounded)
left = refund(total, 5.00)  # 25.44 - 5.00 = 20.44
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
