# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money and rates must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`. This gives float rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total), an `amount` larger than the order total (negative result), and it mixes types freely. Validate `0 < amount <= order_total_amount` and raise `ValueError` otherwise.
- [major] shop/payments.py:6-7 `line_total` doesn't validate input. Negative or zero prices and quantities, non-integer quantities, and `None` all pass through silently.
- [major] shop/payments.py:10-15 `order_total` has no error handling. Malformed tuples raise bare unpack errors, and an empty list returns `0` (int) after the tax multiplication and `round`, so the return type is inconsistent.
- [major] shop/payments.py:18 `refund` doesn't track prior refunds, so the same order can be refunded repeatedly. It also returns a remaining balance rather than a refund record, and the name doesn't say so.
- [major] shop/ No tests exist for this module (no `tests/` directory). Cover tax rounding, empty orders, invalid input and refund bounds.
- [nit] shop/payments.py:18 Parameter `order_total_amount` is awkward and shadows the `order_total` function name conceptually. Consider `total`.
- [nit] shop/payments.py:6,10,18 No type hints, and `line_total` and `refund` lack docstrings.

Verdict: REQUEST CHANGES
