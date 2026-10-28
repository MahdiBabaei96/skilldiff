# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money math must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`. This gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` doesn't validate `amount`. Negative amounts, or amounts above the order total, return a negative or inflated balance. Also takes and returns unrounded floats.
- [major] shop/payments.py:6-7 `line_total` doesn't validate `price` or `quantity`. Negative or zero quantity and negative prices pass silently, and nothing checks types (a float or str price gets through).
- [major] shop/payments.py:10-15 `order_total` has no error handling for malformed `lines` (wrong tuple shape, `None`). Empty `lines` returns `0.0` with no explicit handling.
- [major] shop/payments.py:3 Tax rate is hard-coded here. `shop/config.py` exists and is a more appropriate home for it.
- [major] tests/ There is no tests directory, so no tests for `line_total`, `order_total` (rounding, empty order) or `refund` (over-refund, negative).
- [nit] shop/payments.py:6,18 No docstrings or type hints on `line_total` and `refund`. The `refund` parameter name `order_total_amount` is awkward.

Verdict: REQUEST CHANGES
