# Shop

A tiny example storefront backend.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order totals,
applies sales tax, and computes refunds. It does not talk to a payment
provider.

### Tax

`TAX_RATE` is the sales tax rate applied to every order (`0.0825`, or 8.25%).

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line item.
- `order_total(lines)` takes a list of `(price, quantity)` tuples, sums the
  line totals, adds tax, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns the remaining balance after
  `amount` is refunded from `order_total_amount`.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # subtotal 25.50, plus tax
print(total)  # 27.60

remaining = refund(total, 7.60)
print(remaining)  # 20.00
```

### Notes

- Prices and amounts are plain numbers. Use `Decimal` if you need exact
  currency arithmetic, because `float` values can drift slightly.
- `refund` does not check that `amount` is positive or that it does not exceed
  `order_total_amount`. Validate those values before calling it.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
