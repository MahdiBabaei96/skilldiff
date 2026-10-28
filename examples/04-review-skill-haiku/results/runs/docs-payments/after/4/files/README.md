# Shop

A tiny example storefront backend.

## Payments module

The payments module lives in `shop/payments.py` and calculates order totals,
including sales tax, and refunds. It has no external dependencies.

`TAX_RATE` is the sales tax rate applied to every order (currently `0.0825`, or 8.25%).

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for a single line item.
  It does not apply tax.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`, the
  remaining amount after subtracting a refund. It does not validate its inputs.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # subtotal 25.50, plus 8.25% tax
print(total)  # 27.60

remaining = refund(total, 7.60)
print(remaining)  # 20.00
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
