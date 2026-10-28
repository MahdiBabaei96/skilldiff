# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money math on floats gives binary rounding errors. Use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:6-7 `line_total` multiplies `price * quantity` with whatever types the caller passes. With float prices this returns inexact cents. Use `Decimal` for `price` and validate the type.
- [blocker] shop/payments.py:12-15 `subtotal` starts as int `0` and accumulates float line totals, so the error builds up across lines. `round(..., 2)` on a float uses binary rounding, not a defined money rounding mode. Sum `Decimal` values and quantize with `ROUND_HALF_UP` to cents.
- [major] shop/payments.py:6-14 No input validation. Negative or zero-price lines, negative or non-integer quantities, `None`, and strings are all accepted silently and produce wrong totals. Reject them with `ValueError`.
- [major] shop/payments.py:18-19 `refund` does not validate `amount`. Negative amounts, amounts greater than `order_total_amount`, and refunds on a zero total all return a result without error. A refund above the order total returns a negative balance.
- [major] shop/payments.py:18-19 `refund` returns an unrounded float difference. Quantize the result to cents, as `order_total` does.
- [major] No tests exist for this module. There is no `tests/` directory and nothing in the repo imports `shop.payments`. Add unittest coverage for `line_total`, `order_total` (tax rounding, empty list, multiple lines), and `refund` (full, partial, over-refund, negative input).
- [nit] shop/payments.py:6 and :18 Missing docstrings. `line_total` and `refund` have no description of units or expected types.
- [nit] shop/payments.py:18 Parameter `order_total_amount` is long and inconsistent with `order_total`. Consider `total` or `order_total_amount` documented in the docstring.

Verdict: REQUEST CHANGES
