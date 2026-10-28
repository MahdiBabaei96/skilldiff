# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money math must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`, which causes binary rounding errors and banker's rounding. Use `Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation: a negative amount, or an amount greater than the order total, returns a negative or inflated balance. Reject amounts that are <= 0 or exceed the total, and raise a clear error.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative values, zero or non-numeric input silently produce wrong totals. Callers may pass floats, so convert or reject them explicitly.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines` (wrong tuple shape, `None`) and gives no useful error. An empty list returns `0.0`, not a `Decimal`, so the return type is inconsistent.
- [major] shop/payments.py:18 `refund` is not tied to payment state, so it cannot be used to detect a double refund. Confirm this is intended for this PR.
- [major] No tests exist for this module (there is no `tests/` directory). Add tests for tax rounding edge cases (for example a total of 0.10 * 3), empty orders, negative and zero quantities, and refund bounds.
- [nit] shop/payments.py:6,18 `line_total` and `refund` have no docstrings or type hints, unlike `order_total`. The parameter name `order_total_amount` also shadows the function name's meaning.

Verdict: REQUEST CHANGES
