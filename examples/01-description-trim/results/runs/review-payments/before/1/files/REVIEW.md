# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money handling must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`. This gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` does no validation. It accepts negative amounts and amounts larger than the order total, so it can return a negative balance or a refund that increases the total. It also does float subtraction if given floats.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative or zero quantities and negative prices pass silently, and nothing enforces the type (`Decimal` / `int`).
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines` (wrong tuple length, `None`). An empty list returns `0.0` with no explicit handling.
- [major] shop/payments.py:18 `refund` is named like a payment operation but only subtracts. It has no currency or order-state checks, no idempotency and no record of the refund.
- [nit] shop/payments.py:6,10,18 No type hints. `refund` has no docstring, and `order_total_amount` is a clumsy parameter name that shadows the function `order_total`.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the module also contains refund logic.
- [major] tests/ There are no tests for this module. Tax rounding, empty orders, negative values and over-refunds all need coverage.

Verdict: REQUEST CHANGES
