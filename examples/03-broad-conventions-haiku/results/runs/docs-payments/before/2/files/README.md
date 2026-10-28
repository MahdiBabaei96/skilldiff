# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order
totals, including sales tax, and computes refund balances. It does not
talk to a payment provider or store any data.

### Constants

- `TAX_RATE` (`0.0825`): the sales tax rate applied to order subtotals.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one line
  item. The result is not rounded.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and
  returns the subtotal plus tax, rounded to two decimal places.
- `refund(order_total_amount, amount)`: returns
  `order_total_amount - amount`, the balance left after a refund. It does
  not check that `amount` is positive or no larger than the order total.

### Example

```python
from shop.payments import order_total, refund

# Subtotal is 2 * 10.00 + 1 * 5.50 = 25.50, plus 8.25% tax.
total = order_total([(10.00, 2), (5.50, 1)])  # 27.6

remaining = refund(total, 10.00)  # 17.6
```
