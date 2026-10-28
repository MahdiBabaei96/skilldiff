# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`; money math must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and Python's banker's rounding on a float, so totals can be off by a cent. Use `Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:6 `line_total` takes any numeric type, so callers can pass float prices and bring float errors in. Convert or reject non-`Decimal` input.
- [major] shop/payments.py:18-19 `refund` has no validation. A negative `amount`, or an `amount` greater than the order total, silently gives a wrong result (a negative balance or an inflated one). Raise `ValueError` in both cases.
- [major] shop/payments.py:10-15 `order_total` doesn't validate input. Negative or zero quantities, negative prices and malformed tuples are accepted without error. Empty `lines` returns `0.0`, which is a float and not a `Decimal`.
- [major] shop/payments.py:18 `refund` doesn't round or quantize its result, and it takes no currency or precision, so the result can carry stray fractional cents.
- [nit] shop/payments.py:18 `order_total_amount` shadows the function name `order_total` in meaning. Rename it to `total`.
- [nit] shop/payments.py:6,10,18 Missing docstrings on `line_total` and `refund`, and no type hints.
- [major] tests/ There are no tests for this module (the repo has no `tests/` directory). Add cases for rounding at the half-cent, empty orders, invalid quantities and refund limits.

Verdict: REQUEST CHANGES
