# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money math must use `Decimal`; define it as `Decimal("0.0825")`.
- [blocker] shop/payments.py:12-15 `order_total` accumulates and multiplies with floats and finishes with `round(..., 2)`. This gives binary-float rounding errors and banker's rounding on halves. Use `Decimal` throughout and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total) or an `amount` larger than the order total (which returns a negative balance). It also does no rounding or type checks.
- [major] shop/payments.py:6-7 `line_total` does not validate input. Negative or zero `price`/`quantity`, non-integer quantities and `None` are all accepted silently. Callers can produce negative totals.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines`. A tuple of the wrong length raises an unhelpful `ValueError`, and an empty list returns `0.0` with no explicit policy.
- [major] shop/payments.py:18 `refund` has no tracking of prior refunds, so the same order can be refunded repeatedly. It is also not idempotent. Confirm whether that is handled by the caller.
- [major] No tests exist for this module (there is no `tests/` directory). Add cases for tax rounding at half-cent boundaries, empty orders, negative or invalid input, and refunds that exceed the total.
- [nit] shop/payments.py:1 The module docstring says "Order totals" but the module also contains refund logic. Consider updating the docstring, or renaming the module.
- [nit] shop/payments.py:6,10,18 There are no type hints, and `line_total` and `refund` have no docstrings. `order_total_amount` shadows the function name `order_total` conceptually; consider a clearer parameter name.

Verdict: REQUEST CHANGES
