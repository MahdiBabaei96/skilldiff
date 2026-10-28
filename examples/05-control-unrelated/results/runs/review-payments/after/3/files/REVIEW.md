# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money and rates must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: a negative amount, or an amount larger than the order total, is accepted and can return a negative balance. Reject both with a clear error.
- [major] shop/payments.py:7 `line_total` does no input validation. Negative or zero quantities and negative prices are accepted, and float prices are not rejected. Validate that quantity is a positive int and price is a non-negative `Decimal`.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed lines (wrong tuple length, `None` values). Failures surface as unclear `TypeError`/`ValueError`.
- [major] shop/payments.py:12 `subtotal = 0` starts as an `int`. This is fine with `Decimal`, but an empty `lines` returns a float `0.0` rather than `Decimal("0.00")`. Make the return type consistent.
- [major] shop/ No tests exist for this module. Add tests for tax rounding, empty orders, invalid input, and refund bounds.
- [nit] shop/payments.py:6,18 Public functions have no docstrings or type hints. `refund`'s parameter `order_total_amount` is also awkwardly named.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the module also handles refunds.

Verdict: REQUEST CHANGES
