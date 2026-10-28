# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which gives binary rounding errors and banker's rounding. Use `Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts and amounts greater than the order total, so it can return a negative balance or "refund" more than was paid. Validate `0 < amount <= order_total_amount` and raise `ValueError` otherwise.
- [major] shop/payments.py:6-7 `line_total` does not validate input. Negative or zero price/quantity and non-integer quantities are accepted silently, which can reduce the total. Validate types and ranges.
- [major] shop/payments.py:10-15 `order_total` has no error handling. Malformed tuples raise a bare `ValueError`/`TypeError`, and an empty list returns int `0` rather than a rounded money value. The return type is inconsistent (int vs float).
- [major] shop/payments.py:18 `refund` returns a bare number with no currency or rounding handling, so it inherits the float problem if callers pass floats.
- [major] tests: no tests exist for this module (no `tests/` directory). Add coverage for tax rounding, empty orders, negative/invalid inputs, and refund limits.
- [nit] shop/payments.py:6,10,18 Missing docstrings on `line_total` and `refund`, and no type hints. Parameter `order_total_amount` is also awkward and shadows the `order_total` function name.

Verdict: REQUEST CHANGES
