# Payments module

`shop/payments.py` calculates order totals and refunds. It has no I/O, no
external services, and no state; every function is a pure calculation.

## Constants

| Name       | Value    | Meaning                                   |
|------------|----------|-------------------------------------------|
| `TAX_RATE` | `0.0825` | Sales tax applied to the subtotal (8.25%). |

## Functions

### `line_total(price, quantity)`

Returns `price * quantity` for a single line item. No tax is applied.

```python
from shop.payments import line_total

line_total(4.50, 3)  # 13.5
```

### `order_total(lines)`

Returns the total for an order, including tax, rounded to 2 decimal places.

- `lines`: a list of `(price, quantity)` tuples.
- Computes the subtotal as the sum of `line_total` for each line, then
  multiplies by `1 + TAX_RATE` and rounds to cents.

```python
from shop.payments import order_total

order_total([(10.00, 2), (5.00, 1)])  # 25.0 subtotal -> 27.06
```

An empty list returns `0.0`.

### `refund(order_total_amount, amount)`

Returns `order_total_amount - amount`, the remaining balance after a refund.

- `order_total_amount`: the total that was charged, typically the value from
  `order_total`.
- `amount`: the amount being refunded.

```python
from shop.payments import refund

refund(27.06, 10.00)  # 17.06
```

## Behaviour to be aware of

- **No input validation.** Negative prices or quantities, and refunds larger
  than the order total, are not rejected. `refund` can return a negative
  balance.
- **Tax is always applied to the whole order.** There is no per-line or
  per-item tax, and `refund` does not recalculate tax on the refunded amount.
  Callers who need tax-accurate refunds must handle that themselves.
- **Floating-point arithmetic.** Prices are `float`s. Only `order_total`
  rounds, and only its final result. Intermediate values, and the output of
  `line_total` and `refund`, are not rounded.
- **`TAX_RATE` is a module constant.** Changing the rate means editing
  `shop/payments.py`. There is no per-region or per-order override.

## Tests

Tests for this module belong in `tests/` and run with
`python3 -m unittest discover -s tests`.
