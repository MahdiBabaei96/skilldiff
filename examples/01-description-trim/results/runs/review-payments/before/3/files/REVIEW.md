# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`. Money and rates must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses banker's rounding on a binary float, so totals can be off by a cent. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts, accepts an `amount` larger than the order total (returns a negative balance), and does not guard against non-numeric input.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative or zero quantities and negative prices pass through silently, and float prices are accepted.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines`. A tuple of the wrong length raises an unhelpful `ValueError`, and an empty list returns `0.0`, a float rather than a money type.
- [major] shop/payments.py:18 `refund` does not say whether it returns the remaining balance or the refunded amount. The name and the body disagree, so callers are likely to misuse it.
- [major] shop/ No tests exist for `line_total`, `order_total` or `refund`. Add tests for rounding, an empty order, invalid input and over-refunds.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the module also handles refunds. The filename `payments` also doesn't match what it contains.
- [nit] shop/payments.py:6,18 Public functions have no docstrings or type hints. Parameter names such as `order_total_amount` shadow the `order_total` function name.

Verdict: REQUEST CHANGES
