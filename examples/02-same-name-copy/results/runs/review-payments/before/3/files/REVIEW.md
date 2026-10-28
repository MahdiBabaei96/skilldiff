# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses banker's rounding on a binary float, so totals can be off by a cent. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [major] shop/payments.py:6 `line_total` does no validation. Negative or zero prices and quantities, non-integer quantities, and `None` are all accepted. Floats can also be passed in as prices.
- [major] shop/payments.py:18-19 `refund` does not check that `amount` is positive or that it is at most `order_total_amount`. It can return a negative balance, and a negative `amount` increases the total. It also does no rounding or `Decimal` handling.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines` (wrong tuple shape, `None`). An empty list returns `0.0`, which is a float, not a money value.
- [nit] shop/payments.py:18 The `order_total_amount` parameter name shadows the `order_total` function's concept and is verbose. Consider `total`.
- [nit] shop/payments.py:6,18 `line_total` and `refund` have no docstrings, and there are no type hints.
- [major] tests/ There are no tests. Cover tax rounding edge cases, empty orders, invalid input, and refund bounds.

Verdict: REQUEST CHANGES
