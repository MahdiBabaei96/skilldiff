# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money math must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Totals are computed with float arithmetic and `round(..., 2)`, which gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts, which increase the total. It accepts amounts above the order total, which give a negative balance. It also accepts non-numeric input. Reject `amount <= 0` and `amount > order_total_amount`.
- [major] shop/payments.py:6-7 `line_total` doesn't validate `price` or `quantity`. Negative or zero quantities and negative prices pass silently. Float or `str` inputs are not rejected or coerced to `Decimal`.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines`. A wrong tuple shape raises a bare `ValueError`/`TypeError`. An empty list returns `0.0` without any signal.
- [major] shop/payments.py:18 `refund` returns a bare remaining balance and has no currency or rounding handling. It does not record or process a refund, so the name is misleading.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the file also holds refunds, and it is named `payments`. `line_total`, `order_total` and `refund` have no docstrings.
- [major] tests/ There are no tests. Cover tax rounding edge cases, empty orders, invalid quantities and prices, and refund bounds.

Verdict: REQUEST CHANGES
