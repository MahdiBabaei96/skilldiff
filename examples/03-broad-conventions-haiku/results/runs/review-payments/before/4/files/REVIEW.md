# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money math must use `Decimal`. Tax on a float rate produces rounding drift in every order total.
- [blocker] shop/payments.py:6-7 `line_total` multiplies whatever it receives. With float prices, `0.1 * 3` gives `0.30000000000000004`. Use `Decimal` inputs and convert at the boundary.
- [blocker] shop/payments.py:12-15 `order_total` accumulates a float subtotal and applies `round(..., 2)`. Python's `round` on floats uses banker's rounding and is not reliable for currency. Use `Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [major] shop/payments.py:7 and :14 No validation of `price` or `quantity`. Negative values, zero-quantity edge cases, and non-numeric input pass silently and can produce negative totals.
- [major] shop/payments.py:18-19 `refund` has no validation. `amount` can be negative, can exceed `order_total_amount` (which would create a negative balance or over-refund), and the result is unrounded. Add checks for `0 < amount <= order_total_amount` and raise `ValueError` otherwise.
- [major] shop/payments.py:18 `refund` has no docstring and no stated units or currency contract, unlike `order_total`.
- [major] No tests exist. The repository has no `tests/` directory and no test references `payments`. Add unittest coverage for: tax rounding on a known total, empty order, multi-line totals, refund within and beyond the order total, and invalid inputs.
- [nit] shop/payments.py:12 `subtotal = 0` starts as an int. This works, but `Decimal("0")` keeps the type consistent once the blockers above are fixed.

Verdict: REQUEST CHANGES
