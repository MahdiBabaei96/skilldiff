# Review: shop/payments.py

- [major] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Tax on money should use `Decimal` (for example `Decimal("0.0825")`).
- [major] shop/payments.py:7 `line_total` multiplies `price * quantity` with no type or range checks. Floats here cause rounding drift, and negative or zero quantities are accepted silently.
- [major] shop/payments.py:10-15 `order_total` accumulates a float subtotal and rounds only at the end with `round(..., 2)`, which uses binary floats and banker's rounding. Use `Decimal` quantized to cents with an explicit rounding mode such as `ROUND_HALF_UP`.
- [major] shop/payments.py:18-19 `refund` does no validation. It accepts a refund amount larger than the order total, negative amounts (which would increase the balance), and any previous refunds. Add checks and raise `ValueError` for invalid input.
- [major] shop/payments.py:18 `refund` has no docstring and does not say whether `order_total_amount` is pre-tax or tax-inclusive. Document the contract.
- [major] No tests exist for `shop/payments.py`. There is no `tests/` directory. Add pytest tests with plain `assert` statements covering tax rounding, empty orders, invalid quantities, and refund bounds.
- [nit] shop/payments.py:14 `subtotal` is initialised to the int `0`, which will be mixed with floats or `Decimal`. Initialise it with the same type as the money values.

Verdict: REQUEST CHANGES
