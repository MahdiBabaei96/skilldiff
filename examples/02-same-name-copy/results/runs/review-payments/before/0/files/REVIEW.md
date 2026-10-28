# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:12-15 Totals are computed with float arithmetic and `round(..., 2)`. This gives binary rounding errors and banker's rounding on halves. Use `Decimal` throughout and quantize explicitly (e.g. `quantize(Decimal("0.01"), ROUND_HALF_UP)`).
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts `amount > order_total_amount` (negative result) and negative amounts (which increase the total), and it is float-based. Reject invalid amounts and raise a clear error.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative, zero, non-numeric or fractional quantities pass silently.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines` (wrong tuple shape, `None`). Empty `lines` returns `0` (an int), not a rounded money value, so the return type is inconsistent.
- [major] shop/ No tests exist for this module. Add tests for tax rounding, empty orders, invalid input and refund bounds.
- [nit] shop/payments.py:18 Parameter name `order_total_amount` shadows the `order_total` naming and is awkward. Consider `total`. Also add docstrings to `line_total` and `refund`.
- [nit] shop/payments.py:1 The module is named `payments` but only computes totals and refunds arithmetic, with no payment processing. Check that the name matches intent.

Verdict: REQUEST CHANGES
