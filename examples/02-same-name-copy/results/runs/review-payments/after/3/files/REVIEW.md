# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`. Money math must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:6-7 `line_total` multiplies caller-supplied prices with no type contract. Floats passed in produce binary rounding errors. Convert to `Decimal` or reject non-`Decimal` input.
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` on floats uses banker's rounding on inexact values, so totals can be off by a cent. Use `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts (which increase the balance) and amounts larger than the order total (which produce a negative result). It also never records or returns anything useful beyond a subtraction.
- [major] shop/payments.py:10-15 `order_total` does no input validation. It accepts negative prices or quantities, non-integer quantities and malformed tuples, and it raises an unhelpful `ValueError` or `TypeError` on bad shapes.
- [major] shop/payments.py:12 `subtotal = 0` starts as an `int`. An empty `lines` returns `0.0` or `0`, which is inconsistent with the `Decimal` return type once money handling is fixed.
- [major] shop/payments.py:18 `refund(order_total_amount, amount)` is a naming mismatch and has no docstring. It is unclear whether `amount` is pre-tax or post-tax, or whether this should be a partial refund.
- [major] tests: no tests exist for this module (no `tests/` directory). Add coverage for rounding at half-cent boundaries, empty orders, negative and zero inputs, and refund bounds.
- [nit] shop/payments.py:6 `line_total` and `refund` lack docstrings, unlike `order_total`.
- [nit] shop/payments.py:3 `TAX_RATE` is hard-coded here. `shop/config.py` exists and is a better home for it.

Verdict: REQUEST CHANGES
