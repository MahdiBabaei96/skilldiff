# Shop

A tiny example storefront backend.

## Payments module

`shop/payments.py` calculates order totals and refunds. All amounts are plain
numbers in the shop's currency; no currency conversion is done.

The module exposes these names:

- `TAX_RATE`: the sales tax rate applied to order subtotals (`0.0825`, or 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line
  totals, applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the amount left after refunding
  `amount` from `order_total_amount`. It does not check that `amount` is valid.

Example:

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (5.50, 1)])  # (20.00 + 5.50) * 1.0825
print(total)  # 27.6

remaining = refund(total, 7.46)
print(remaining)  # 20.14
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
