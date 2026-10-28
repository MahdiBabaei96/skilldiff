# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order
totals with sales tax and handles refund amounts. It has no I/O and no
external dependencies.

### Constants

- `TAX_RATE` (`0.0825`): the sales tax rate applied to every order.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one line.
  No rounding is applied.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and
  returns the subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns
  `order_total_amount - amount`, the remaining balance after a refund.
  It does not check that `amount` is positive or within the total.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(2.50, 4)  # 10.0

total = order_total([(2.50, 4), (10.00, 1)])  # 20.0 subtotal -> 21.65 with tax

refund(total, 5.00)  # 16.65
```

### Notes

- Prices and amounts are plain numbers. Floats are used, so
  rounding errors can occur before the final rounding in `order_total`.
- Callers are responsible for validating refund amounts.
