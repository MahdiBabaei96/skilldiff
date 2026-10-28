# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals, tax, and refunds. All amounts
are plain numbers in the shop's currency; the module does no rounding except
in `order_total`.

### Constants

- `TAX_RATE` (`0.0825`): the sales tax rate applied to every order total.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one line item.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the
  line totals, applies `TAX_RATE`, and returns the result rounded to 2 places.
- `refund(order_total_amount, amount)`: returns the remaining balance,
  `order_total_amount - amount`. It does not check that `amount` is positive
  or no larger than the order total.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # 25.50 * 1.0825 = 27.60375 -> 27.6
remaining = refund(total, 7.60)               # 27.6 - 7.6 = 20.0
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
