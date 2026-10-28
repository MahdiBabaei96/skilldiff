# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`. Money handling must use `Decimal`; define it as `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses banker's rounding on a binary float, so totals can be off by a cent. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total) and an `amount` greater than the order total (which returns a negative balance).
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative or non-numeric values, and a non-integer quantity, pass through silently.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines`. A tuple of the wrong length raises a bare `ValueError` from unpacking. An empty list returns `0.0` (a float) rather than a `Decimal`.
- [major] shop/payments.py (whole file) There are no tests. No `tests/` directory exists. Cover tax rounding, an empty order, negative and zero inputs, and refund bounds.
- [nit] shop/payments.py:18 `refund` takes `order_total_amount`, which is easily confused with the `order_total` function. Consider `total`.
- [nit] shop/payments.py:6,10,18 The functions have no type hints. `refund` and `line_total` have no docstrings.

Verdict: REQUEST CHANGES
