# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Tax and every total derived from it are computed in binary floating point. Use `Decimal("0.0825")`.
- [blocker] shop/payments.py:18-19 `refund` does no validation. It accepts any `amount`, so a refund larger than the order total, a negative amount (which increases the refund), or a refund of an already-refunded order all go through and return a negative or inflated balance. Reject `amount <= 0` and `amount > order_total_amount`, and track refunded totals if partial refunds are allowed.
- [major] shop/payments.py:6-7 `line_total` multiplies `price * quantity` with no type or range checks. Floats leak in from callers, and negative prices or quantities are accepted silently. Use `Decimal` inputs and reject negative values.
- [major] shop/payments.py:12-14 `subtotal` starts as the int `0` and accumulates whatever `line_total` returns. Float addition drifts across lines, and mixed int/float/Decimal types make the result type depend on the input. Start with `Decimal("0")`.
- [major] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` uses Python's float `round`, which rounds half to even on the binary approximation, so a half-cent can land on the wrong side. Use `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`, and state the rounding rule.
- [major] shop/payments.py:10-11 `order_total` does not validate `lines`. An empty list returns `0` (an int, not a money value), and malformed tuples fail with unclear errors. Validate the input and document or raise on empty orders.
- [major] No tests exist for `shop/payments.py`. Nothing covers rounding, tax, empty orders, or refund bounds. Add `tests/test_payments.py` with `unittest` cases for these, including a half-cent tax case.
- [nit] shop/payments.py:19 `refund` has no docstring, unlike `order_total`. State whether `amount` is pre-tax or tax-inclusive.

Verdict: REQUEST CHANGES
