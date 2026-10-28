# Shop

A tiny example storefront backend.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order totals,
including sales tax, and handles refund amounts. It has no external dependencies.

### Constants

- `TAX_RATE` (`0.0825`): the sales tax rate applied by `order_total`.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for a single line item.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`, the
  remaining balance after a refund of `amount`.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # subtotal 25.50, plus tax
print(total)  # 27.6

remaining = refund(total, 10.00)
print(remaining)  # 17.6
```

### Notes

- `refund` does not check that `amount` is at most `order_total_amount`, and it does
  not round its result. Callers must validate inputs and round as needed.
- Prices are plain numbers. Use `Decimal` in production code if exact cent
  arithmetic matters.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
