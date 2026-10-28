# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Tax and totals must use `Decimal` (e.g. `Decimal("0.0825")`), not float.
- [blocker] shop/payments.py:6-7 `line_total` multiplies `price * quantity` with no type conversion. If prices arrive as floats or strings, the result is inexact or raises. Convert inputs to `Decimal` at the boundary.
- [blocker] shop/payments.py:12-15 `order_total` accumulates money as floats (`subtotal = 0`, then `+=`). Float error accumulates across lines, and `round(..., 2)` on a float does not reliably produce the cent value the customer is charged. Use `Decimal` throughout and quantize with an explicit rounding mode (e.g. `ROUND_HALF_UP`); `round()` uses banker's rounding.
- [blocker] shop/payments.py:18-19 `refund` does no validation. A negative `amount`, or an `amount` greater than `order_total_amount`, is accepted and can over-refund or produce a negative balance. Reject non-positive amounts and amounts above the refundable total, and make it raise a clear error.
- [major] shop/payments.py:6-14 No input validation. Negative or zero quantities, negative prices, and `None` values are silently summed. Validate each line before computing.
- [major] shop/payments.py:12 An empty `lines` list returns `0` (an int) rather than a money value, which is inconsistent with the non-empty case and with `Decimal` handling.
- [major] shop/payments.py:15 Tax is applied to the full subtotal and rounded once. Confirm this matches how the business rounds tax (per line vs per order); per-line rounding can differ by a cent. If it is intended, document it in the docstring.
- [major] No tests exist for this module (no `tests/` directory and no test file references `payments`). Add unit tests covering: float-free money, rounding at the half-cent boundary, empty order, invalid inputs, and refund bounds. Use the `test-writer` skill or standard-library `unittest`.
- [nit] shop/payments.py:18 `refund` has no docstring, unlike `order_total`. Add one stating units and the validation rules.
- [nit] shop/payments.py:18 Parameter name `order_total_amount` is long and redundant with the function's purpose; consider `order_total`-style naming consistent with the rest of the module.

Verdict: REQUEST CHANGES
