# Shop

A tiny example storefront backend.

## Payments module

The payments module lives in `shop/payments.py`. It computes order
totals, including sales tax, and handles simple refunds.

Amounts are plain numbers (`int` or `float`). The module does not
handle currencies, rounding rules beyond the final total, or payment
processing.

### Constants

- `TAX_RATE` is the sales tax rate applied to order subtotals.
  It is `0.0825` (8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line.
- `order_total(lines)` takes a list of `(price, quantity)` tuples and
  returns the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns the remaining amount
  after subtracting `amount` from `order_total_amount`. It does not
  check that `amount` is valid.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(10.00, 3)          # 30.0
order_total([(10.00, 2)])     # 21.65 (20.00 plus 8.25% tax)

total = order_total([(10.00, 2)])
remaining = refund(total, 5.00)  # about 16.65
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
