# Review: shop/payments.py

- [major] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Tax and totals should be `Decimal`, not float, per team money-handling rules.
- [major] shop/payments.py:7 `line_total` multiplies `price * quantity` with no type conversion. If callers pass floats, the result is a float and inherits binary rounding error.
- [major] shop/payments.py:12-15 `order_total` accumulates a float subtotal and rounds only once at the end. Per-line rounding is not applied, so the total can differ from the sum of displayed line totals by a cent. Use `Decimal` with an explicit quantizing rule (for example `ROUND_HALF_UP` to 0.01).
- [major] shop/payments.py:6-15 No input validation. Negative prices or quantities, zero or non-numeric values, and an empty `lines` list are all accepted silently and produce a total.
- [major] shop/payments.py:18-19 `refund` does not check that `amount` is positive or that it does not exceed `order_total_amount`. An over-refund returns a negative balance without an error. It also returns a bare number with no record of the refund.
- [major] shop/payments.py (whole file) No tests exist. There is no `tests/` directory and nothing covers `line_total`, `order_total`, or `refund`. Add pytest tests with plain `assert` statements under `tests/`, covering rounding, empty orders, zero and negative inputs, and over-refund.
- [nit] shop/payments.py:12 `subtotal = 0` starts as an int. This disappears once the type is changed to `Decimal`, so start it as `Decimal("0")` at that point.
- [nit] shop/payments.py:18 `refund` has no docstring. The parameter names are also inconsistent with `order_total` ("order_total_amount" versus "lines").

Verdict: REQUEST CHANGES
