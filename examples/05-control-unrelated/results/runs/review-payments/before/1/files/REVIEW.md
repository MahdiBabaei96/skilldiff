# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money handling must use `Decimal`; use `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 Totals are computed with float arithmetic and `round(..., 2)`, which gives binary-float rounding errors and banker's rounding. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total) and an `amount` larger than the order total (which returns a negative balance). It also does not say what it returns.
- [major] shop/payments.py:6-7 `line_total` does not validate inputs. Negative prices or quantities, non-integer quantities and `None` are all accepted, and `float` prices pass through silently.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines`. A tuple of the wrong length raises a bare `ValueError`, and an empty list returns the int `0` rather than a rounded money value.
- [major] shop/payments.py:12 `subtotal = 0` starts as an `int`, so the return type varies between `int` and `float`. It should be `Decimal("0")`.
- [major] No tests exist for this module (there is no `tests/` directory). Cover tax rounding, an empty order, negative and invalid inputs, and full and partial refunds.
- [nit] shop/payments.py:6,10,18 There are no type hints, and `line_total` and `refund` have no docstrings. In `refund`, `order_total_amount` shadows the name of `order_total`.

Verdict: REQUEST CHANGES
