# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float, and `order_total` (lines 12-15) sums and taxes money as floats. Binary float error can produce off-by-a-cent totals. Use `Decimal` for `TAX_RATE`, prices, and totals, and quantize with an explicit rounding mode (e.g. `ROUND_HALF_UP`).
- [blocker] shop/payments.py:7 `line_total` multiplies `price * quantity` with no type or value checks. Callers passing a float price, a negative price, or a negative or fractional quantity get silently wrong totals. Validate inputs (`Decimal` price, non-negative, integer quantity) and raise `ValueError` otherwise.
- [major] shop/payments.py:18-19 `refund` has no validation. A negative `amount`, or an `amount` greater than `order_total_amount`, returns a value without error, so a refund can exceed what was charged. Reject both cases and return a `Decimal` quantized to cents.
- [major] shop/payments.py:10-15 `order_total` has no guard for malformed `lines` entries (wrong tuple shape, `None` values). Failures surface as unrelated `TypeError`s deep in the arithmetic. Validate each entry at the boundary.
- [major] No tests exist for `shop/payments.py`. `tests/` is absent and nothing in the repo imports the module. Add pytest tests in `tests/` using plain `assert` covering: tax rounding on a multi-line order, empty `lines` (expect 0), negative and zero quantity rejection, and refund bounds (over-refund and negative amount rejected).
- [nit] shop/payments.py:18 `refund` has no docstring, unlike `order_total`. Name the parameters clearly (`charged_total`, `refund_amount`) to match the money semantics.

Verdict: REQUEST CHANGES
