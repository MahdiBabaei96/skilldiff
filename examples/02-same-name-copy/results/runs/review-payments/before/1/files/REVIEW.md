# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a `float`. Money math must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses banker's rounding on a float, so totals can be off by a cent. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total) and an `amount` larger than the order total (which returns a negative balance). It also returns the remaining balance, which is not what the name suggests. Reject amounts that are negative or exceed the total, and document what is returned.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative or non-numeric values, and zero or fractional quantities, pass through silently. Validate the inputs, and coerce prices to `Decimal` (ideally from `str`, not `float`).
- [major] shop/payments.py:10-15 `order_total` has no handling for malformed lines (wrong tuple length, `None`). An empty list returns `0.0` as a float rather than a `Decimal` zero.
- [major] shop/payments.py:12 `subtotal = 0` starts as an `int`, so the return type depends on the input types. Start from `Decimal("0")`.
- [major] No tests exist for this module. Add cases for rounding at half-cent boundaries, an empty order, invalid quantities, and refund bounds.
- [nit] shop/payments.py:1 The module docstring says "Order totals" but the module also handles refunds, and `refund` and `line_total` have no docstrings.
- [nit] shop/payments.py:3 `TAX_RATE` is hardcoded here. `shop/config.py` exists and may be a better home for it.

Verdict: REQUEST CHANGES
