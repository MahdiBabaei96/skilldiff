# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Tax on money should be computed with `Decimal` (e.g. `Decimal("0.0825")`), not float.
- [blocker] shop/payments.py:7 `line_total` multiplies `price * quantity` without `Decimal`, so per-line amounts carry binary float error (e.g. `0.1 * 3 != 0.3`).
- [blocker] shop/payments.py:15 `order_total` accumulates a float subtotal and rounds with `round(..., 2)`, which uses banker's rounding (half-to-even) and can be a cent off from the expected half-up rounding for money. Use `Decimal` with `ROUND_HALF_UP` quantized to cents.
- [blocker] shop/payments.py:18-19 `refund` has no validation: `amount` can be negative, larger than `order_total_amount`, or the result can go negative. It also returns an unrounded value. Validate the amount is non-negative and not greater than the order total, and return a cent-quantized `Decimal`.
- [major] shop/payments.py:6-7 `line_total` does no input validation. Negative prices or quantities, non-integer quantities, and `None` values all pass silently and produce wrong totals.
- [major] shop/payments.py:10-15 `order_total` does no validation of the `lines` argument (malformed tuples, negative values) and tax is applied to the whole subtotal, not per line. Confirm that matches the tax rules the shop must follow.
- [major] No tests exist for `shop/payments.py`. `grep` finds no test file or reference to the module in the repo. Add `unittest` coverage for totals, rounding at the half-cent boundary, empty orders, invalid input, and refund bounds before merge.
- [nit] shop/payments.py:18 `refund` has no docstring, unlike `order_total`. Its parameter `order_total_amount` is also a long name for what the function uses only as a cap.

Verdict: REQUEST CHANGES
