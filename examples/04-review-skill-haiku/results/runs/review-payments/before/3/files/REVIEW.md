# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money math must use `Decimal`; define the rate as `Decimal("0.0825")`.
- [blocker] shop/payments.py:7 `line_total` multiplies `price * quantity` with no type or precision guarantees. With float prices this gives binary rounding errors (e.g. `0.1 * 3`). Use `Decimal` and quantize to cents.
- [blocker] shop/payments.py:18-19 `refund` does no validation. It accepts a negative `amount`, an `amount` larger than `order_total_amount` (producing a negative or over-refund), and non-numeric input. It also returns an unrounded value. Reject `amount <= 0` and `amount > order_total_amount`, and return a `Decimal` quantized to cents.
- [major] shop/payments.py:12-15 `subtotal` starts as int `0` and accumulates floats. Rounding is `round(..., 2)` (banker's rounding on a float), which is not an explicit, documented money rounding mode. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [major] shop/payments.py:10-15 `order_total` does no input validation. Negative prices or quantities, non-integer quantities, and `None` values are all silently accepted and produce wrong totals. Validate each `(price, qty)` pair and raise `ValueError` on bad input.
- [major] shop/payments.py:18-19 Semantics of `refund` are unclear: it is not stated whether `amount` is tax-inclusive or whether `order_total_amount` is the tax-inclusive total. Document this in a docstring and add a return type.
- [major] No tests exist for this module. There is no `tests/` directory and no test file references `payments`. Add unit tests covering totals with tax, rounding at the cent boundary, empty orders, invalid input, and refund bounds.
- [nit] shop/payments.py:11 The docstring says "Returns the total including tax" but does not say the rounding mode or the currency precision.
- [nit] shop/payments.py:18 `refund` has no docstring; the other public function does.

Verdict: REQUEST CHANGES
