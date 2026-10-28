# Shop

A tiny example storefront backend.

## Payments module

The payments module lives in `shop/payments.py`. It calculates order totals
including sales tax and handles simple refund arithmetic. It does not talk to
a payment provider; it only does the money math.

### Tax rate

`TAX_RATE` is `0.0825` (8.25%). It is applied to the whole order subtotal.

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line item.
  It does not round.
- `order_total(lines)` takes a list of `(price, quantity)` tuples. It sums the
  line totals, applies `TAX_RATE`, and returns the result rounded to two
  decimal places.
- `refund(order_total_amount, amount)` returns the amount left on the order
  after refunding `amount`. It does not check that `amount` is within the
  order total and does not round the result.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(3.25, 4)  # 13.0

total = order_total([(10.00, 2), (5.50, 1)])  # 25.50 subtotal + tax = 27.6
refund(total, 10)  # 17.6 left after a 10.00 refund
```

## Development

Run the tests with `python3 -m unittest discover -s tests`.
