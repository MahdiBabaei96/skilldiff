# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`; money handling must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which causes binary rounding errors and uses banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: negative `amount`, or `amount` greater than the order total, yields a negative or inflated balance. It also doesn't track prior refunds, and returns a raw subtraction with no rounding.
- [major] shop/payments.py:6-7 `line_total` doesn't validate `price` or `quantity` (negative, zero, non-numeric, or float inputs are all accepted).
- [major] shop/payments.py:10-15 `order_total` doesn't handle malformed `lines` (wrong tuple shape raises a bare `ValueError`/`TypeError`) and returns `0` for an empty order without saying so. Behavior for empty orders should be explicit.
- [major] shop/payments.py (whole file) No tests exist for any function. Add tests for rounding, tax, empty orders, and refund bounds.
- [nit] shop/payments.py:18 `order_total_amount` shadows the `order_total` function name conceptually; rename to `total`.
- [nit] shop/payments.py:6,10,18 Missing type hints, and `line_total` and `refund` have no docstrings.
- [nit] shop/payments.py:1 The module docstring says "Order totals" but the module also handles refunds.

Verdict: REQUEST CHANGES
