# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float, and `order_total` (lines 6-15) does all money arithmetic in float. Binary floats cannot represent most decimal cents exactly, so totals can drift by a cent. Use `Decimal` for prices, tax rate and totals, and quantize to cents with an explicit rounding mode (e.g. `ROUND_HALF_UP`).
- [blocker] shop/payments.py:15 `round(..., 2)` on a float uses banker's rounding (round-half-to-even), which will not match the half-up rounding customers and receipts usually expect. Fixing the float issue above also fixes this, but the rounding mode must be chosen explicitly.
- [major] shop/payments.py:18-19 `refund` does no validation. A negative `amount`, or an `amount` larger than `order_total_amount`, returns a meaningless value (negative or inflated refund) without an error. Reject non-positive amounts and amounts above the refundable total.
- [major] shop/payments.py:6-7 and 13-14 `line_total` and `order_total` accept any input. Negative prices or quantities, `None`, strings, and non-integer quantities all pass through silently. Validate inputs and raise `ValueError` (or `TypeError`) early.
- [major] shop/payments.py (module) There is no `tests/` directory and no tests for this module. Per team convention, add pytest tests in `tests/` using plain `assert`. At minimum cover: empty order, a cent-precision case that float gets wrong, rounding at the half-cent boundary, and refund bounds.
- [nit] shop/payments.py:11 An empty `lines` list returns the int `0` rather than a money value. Once `Decimal` is in use, return `Decimal("0.00")` for consistency.
- [nit] shop/payments.py:6, 18 `line_total` and `refund` have no docstrings, unlike `order_total`. Add one-line docstrings stating units and rounding.

Verdict: REQUEST CHANGES
