# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`. Money and rates must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Totals are computed with float arithmetic and `round(..., 2)`, which gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts `amount` greater than the order total, negative amounts and non-numeric input, and can return a negative balance or increase the total.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative, zero or non-integer quantities and negative prices are silently accepted.
- [major] shop/payments.py:13 `order_total` unpacks `(price, qty)` with no error handling. Malformed lines raise a bare `ValueError` or `TypeError`, and an empty `lines` returns `0.0`, which is not a consistent type.
- [major] shop/payments.py:1-19 There are no tests. The repo has no `tests/` directory. Cover tax rounding, empty orders, invalid input and refund bounds.
- [nit] shop/payments.py:6,10,18 No docstrings or type hints on `line_total` and `refund`. The `refund` parameter `order_total_amount` is awkwardly named.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the module also handles refunds.

Verdict: REQUEST CHANGES
