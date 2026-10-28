# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825); money math must use `Decimal`. Use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which gives binary-float and banker's-rounding errors. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: it accepts a negative `amount` (which increases the total), an `amount` larger than the order total (negative balance), and non-numeric input. It also mixes types freely, so a float can slip in.
- [major] shop/payments.py:6-7 `line_total` does not validate that `price` is non-negative or that `quantity` is a positive integer. Negative values silently lower the total.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines` (wrong tuple shape, `None`, floats). It fails with a bare `TypeError` or `ValueError`, or silently accepts bad data. An empty list returns `0.0` as a float.
- [major] tests: no tests exist for this module (no `tests/` directory). Add coverage for tax rounding edge cases, empty orders, negative or zero quantities, and refund bounds.
- [nit] shop/payments.py:6,18 Missing docstrings and type hints on `line_total` and `refund`. Parameter `order_total_amount` is also awkwardly named and shadows the function name `order_total` conceptually.
- [nit] shop/payments.py:3 `TAX_RATE` is hardcoded here, but `shop/config.py` exists. Consider moving it there if config is the place for settings.

Verdict: REQUEST CHANGES
