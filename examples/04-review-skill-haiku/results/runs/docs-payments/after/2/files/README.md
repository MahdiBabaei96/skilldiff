# Shop

A tiny example storefront backend.

## Payments module

The payments module, `shop/payments.py`, calculates order totals and refunds.
It has no external dependencies and does not talk to a payment provider.

Amounts are plain numbers in the shop's currency. Tax is a flat rate applied
to the subtotal.

### Configuration

- `TAX_RATE` (`0.0825`): the tax rate applied by `order_total()`.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one line item.
  It does not round or apply tax.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples. It sums the
  line totals, applies `TAX_RATE`, and returns the result rounded to 2 decimals.
- `refund(order_total_amount, amount)`: returns the remaining amount,
  `order_total_amount - amount`. It does not validate its inputs.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.00, 2), (3.50, 1)])  # (20.00 + 3.50) * 1.0825
print(total)  # 25.44

remaining = refund(total, 5.00)
print(remaining)  # 20.44
```

### Notes

- `refund()` does not check that `amount` is positive or no larger than the
  order total. Callers must validate it.
- `order_total()` returns a float rounded to 2 decimals. Values are not
  converted to integer cents, so float rounding applies.

## Development

Run the tests with `python3 -m unittest discover -s tests`.
