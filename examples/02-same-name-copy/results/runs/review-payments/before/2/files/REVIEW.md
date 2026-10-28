# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money handling must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 `order_total` multiplies by `(1 + TAX_RATE)` and uses `round(..., 2)` on a float. This gives binary floating-point error and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount`, which increases the total. It also accepts an `amount` greater than the order total, so the result can go negative. Both should raise `ValueError`.
- [major] shop/payments.py:6-7 `line_total` does no input validation. Negative or non-numeric `price` or `quantity` silently produce wrong totals. `quantity` should be a positive int and `price` a non-negative `Decimal`.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines`, such as wrong tuple length or `None`. An empty list silently returns `0`, which is an `int` rather than a money value, so the return type is inconsistent.
- [major] shop/payments.py:12 `subtotal = 0` starts as an `int`. Start from `Decimal("0")` so the result type stays consistent.
- [major] shop/payments.py (whole file) There are no tests. The repo has no `tests/` directory. Tax rounding, empty orders, and refund bounds all need coverage.
- [nit] shop/payments.py:6,10,18 There are no type hints, and `refund` has no docstring. The `order_total_amount` parameter name also shadows the `order_total` function name.
- [nit] shop/payments.py:3 `TAX_RATE` is hardcoded here although `shop/config.py` exists. Consider moving it there.

Verdict: REQUEST CHANGES
