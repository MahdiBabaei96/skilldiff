# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`; money math must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which gives binary-float rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: a negative `amount`, or an `amount` larger than `order_total_amount`, silently returns a nonsensical value (an increased total or a negative balance). It also returns the remaining balance rather than the refund, which the name doesn't make clear.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative, zero or non-numeric values (including floats) are accepted.
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines`, such as wrong tuple shape or `None`. An empty list returns `0.0`, a float, rather than a `Decimal`.
- [major] shop/payments.py:1-19 No tests exist for this module (there is no `tests/` directory). Cover tax rounding, empty orders, invalid input and refund bounds.
- [nit] shop/payments.py:6,10,18 Functions are missing type hints, and `refund` has no docstring.
- [nit] shop/payments.py:18 The parameter `order_total_amount` shadows the name of the `order_total` function in intent. Consider `total`.

Verdict: REQUEST CHANGES
