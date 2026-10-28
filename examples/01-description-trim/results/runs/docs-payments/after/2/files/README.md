# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals and refunds. Prices are plain numbers.

- `TAX_RATE`: sales tax rate applied to the subtotal (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity`.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus `amount`,
  that is, the amount remaining after the refund. It does not validate `amount`.

```python
from shop.payments import line_total, order_total, refund

line_total(10.0, 3)                       # 30.0
total = order_total([(10.0, 3), (5.0, 1)])  # 35 * 1.0825 = 37.89
refund(total, 5.0)                        # 32.89
```
