# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money and rates must use `Decimal` (e.g. `Decimal("0.0825")`).
- [blocker] shop/payments.py:15 Total is computed with float arithmetic and `round(..., 2)`. This gives binary rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts, and amounts larger than the order total, so it can return a negative balance or increase the total. Reject `amount <= 0` and `amount > order_total_amount`.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative, zero or non-numeric values pass through silently. Also reject `float` input.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines` (wrong tuple shape, `None`). It also returns an `int`/`float` mix for empty input (`round(0 * 1.0825, 2)` gives `0.0`). Return a `Decimal` consistently.
- [major] shop/payments.py:18 `refund` returns a float or int from float inputs and is not rounded to cents. Apply the same `Decimal` quantization as `order_total`.
- [major] shop/payments.py (whole file) No tests exist; the repo has no `tests/` directory. Add tests for tax rounding, empty orders, negative or zero quantities, and refund bounds.
- [nit] shop/payments.py:6,10,18 No docstrings or type hints on `line_total` and `refund`. The `order_total_amount` parameter name also shadows the `order_total` function name conceptually.
- [nit] shop/payments.py:3 `TAX_RATE` is hardcoded here, although `shop/config.py` exists. Consider moving it there.

Verdict: REQUEST CHANGES
