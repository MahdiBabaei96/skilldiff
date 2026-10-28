# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money math should use `Decimal` (e.g. `Decimal("0.0825")`), never float.
- [blocker] shop/payments.py:7 `line_total` multiplies untyped price and quantity with no `Decimal` conversion, so binary float error reaches totals (e.g. `0.1 * 3 != 0.3`). Accept and return `Decimal`.
- [major] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` rounds a float, which can land on the wrong cent at half-cent boundaries. Use `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` and state the rounding mode explicitly.
- [major] shop/payments.py:10-14 `order_total` does no input validation: negative prices or quantities, non-integer quantities, `None` entries and malformed tuples all pass silently and produce a total. Reject these with `ValueError`.
- [major] shop/payments.py:18-19 `refund` has no validation: `amount` may be negative, or greater than `order_total_amount`, which yields a negative refund. It also returns an unrounded value and does not say whether `amount` includes tax. Validate the range and quantize the result.
- [major] No tests exist for this module. The repo has no `tests/` directory and nothing imports `shop.payments`. Add unittest coverage for rounding, tax, empty orders, invalid input and refund bounds before merging.
- [nit] shop/payments.py:12 `subtotal = 0` should be `Decimal("0")` once the module moves to `Decimal`.
- [nit] shop/payments.py:18 `refund` has no docstring. Document the units and whether the amounts are tax-inclusive.
- [nit] shop/payments.py:11 The docstring says the function "returns the total including tax" but does not say whether tax is applied per line or to the subtotal. The code applies it to the subtotal, so state that.

Verdict: REQUEST CHANGES
