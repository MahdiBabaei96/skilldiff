# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

`shop/payments.py` computes order totals, including sales tax, and refund balances.

### API

- `TAX_RATE`: sales tax rate applied to orders (`0.0825`, i.e. 8.25%).
- `line_total(price, quantity)`: returns `price * quantity` for a single order line.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns the order total minus the refunded
  `amount`. It does not validate its inputs, so callers must ensure `amount` does not
  exceed the order total.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(10.00, 3)                     # 30.0
total = order_total([(10.00, 3), (4.50, 2)])  # 39.0 * 1.0825 -> 42.22
remaining = refund(total, 10.00)         # 32.22
```
