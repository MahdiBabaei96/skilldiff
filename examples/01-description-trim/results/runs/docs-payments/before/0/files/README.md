# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals. All amounts are plain numbers in a single currency.

### Constants

- `TAX_RATE`: sales tax rate applied to the order subtotal (`0.0825`, i.e. 8.25%).

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples, sums the line totals,
  applies `TAX_RATE`, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`, the
  balance remaining after refunding `amount`. It does not validate that `amount` is
  not larger than the order total.

### Example

```python
from shop.payments import order_total, refund

lines = [(10.00, 2), (5.50, 1)]
total = order_total(lines)  # 25.5 * 1.0825 -> 27.6
remaining = refund(total, 10.00)  # 17.6
```
