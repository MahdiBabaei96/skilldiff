# Shop

A tiny example storefront backend.

## Development

Run the tests with `python3 -m unittest discover -s tests`.

## Payments module

The `shop.payments` module (`shop/payments.py`) calculates order totals and refunds.
It has no external dependencies.

### Constants

- `TAX_RATE` (`0.0825`): sales tax rate applied by `order_total`.

### Functions

- `line_total(price, quantity)`: returns `price * quantity` for one line item.
- `order_total(lines)`: takes a list of `(price, quantity)` tuples and returns the
  subtotal plus tax, rounded to 2 decimal places.
- `refund(order_total_amount, amount)`: returns `order_total_amount - amount`.

### Example

```python
from shop.payments import order_total, refund

total = order_total([(10.0, 2)])  # subtotal 20.00, plus 8.25% tax
print(total)  # 21.65

print(refund(100, 25))  # 75
```

### Notes

- `refund` does not validate its inputs. It does not check that `amount` is
  positive or no larger than `order_total_amount`, and it does not round the result.
  Callers must validate amounts before calling it.
