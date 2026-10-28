# Shop

A tiny example storefront backend.

## Payments module

The `shop/payments.py` module holds the order arithmetic: line totals, order totals
with sales tax, and a simple refund calculation. It does not talk to a payment
gateway, so it only computes amounts.

`TAX_RATE` is a module constant set to `0.0825` (8.25%), applied to every order.

### Functions

- `line_total(price, quantity)` returns `price * quantity` for one line item.
- `order_total(lines)` takes a list of `(price, quantity)` tuples, sums the line
  totals, adds tax, and returns the result rounded to 2 decimal places.
- `refund(order_total_amount, amount)` returns `order_total_amount - amount`, the
  amount left on the order after a refund. It does not check that `amount` is
  positive or no larger than the order total.

### Example

```python
from shop.payments import line_total, order_total, refund

line_total(5.50, 3)                          # 16.5
order_total([(10.00, 2), (5.50, 1)])         # 27.6 (25.50 subtotal + 8.25% tax)
refund(27.6, 10)                             # 17.6
```

Prices are plain numbers. `order_total` multiplies by a float tax rate, so pass
`int` or `float` prices, not `Decimal`.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
