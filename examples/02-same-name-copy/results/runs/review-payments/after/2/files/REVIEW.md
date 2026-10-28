# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`; money math must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which gives binary-float errors and banker's rounding. Use `Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: a negative `amount`, or an `amount` larger than the order total, is accepted and can return a negative or inflated balance. It also does no rounding and uses floats.
- [major] shop/payments.py:6-7 `line_total` does not validate input. Negative or non-numeric price or quantity, and non-integer quantity, are silently accepted.
- [major] shop/payments.py:10-15 `order_total` has no error handling. Malformed tuples raise a bare `ValueError`/`TypeError`, and an empty `lines` returns `0.0`, which is not documented.
- [major] shop/payments.py (whole file) No tests exist; there is no `tests/` directory. Add coverage for rounding, tax, empty orders, and refund bounds.
- [nit] shop/payments.py:18 The parameter name `order_total_amount` shadows the `order_total` function's meaning. Also add a docstring to `refund` and `line_total`.
- [nit] shop/payments.py:1 The module is named `payments` but only computes totals and refunds. It does no payment processing, so the name is misleading.

Verdict: REQUEST CHANGES
