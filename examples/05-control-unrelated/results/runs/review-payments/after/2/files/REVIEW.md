# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float` (0.0825). Money math must use `Decimal`; define it as `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses float rounding, which gives wrong cents on some totals. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts a negative `amount` (which increases the total), an `amount` greater than the order total (negative result), and non-numeric input. Reject `amount <= 0` and `amount > order_total_amount`.
- [major] shop/payments.py:6-7 `line_total` does not validate `price` or `quantity`. Negative or zero quantities, negative prices, and float inputs are all accepted. Raise `ValueError` for invalid values and convert or require `Decimal` for `price`.
- [major] shop/payments.py:10-15 `order_total` does not handle malformed `lines` (wrong tuple shape, `None`). An empty list silently returns `0.0`. Decide whether that is intended and document it.
- [major] No tests exist (there is no `tests/` directory). Money logic needs tests for tax rounding, empty orders, invalid input, and refund bounds.
- [nit] shop/payments.py:1 The module docstring says "Order totals" but the module also holds refunds. The filename `payments.py` also suggests payment processing. Update the docstring or rename the module.
- [nit] shop/payments.py:6,18 `line_total` and `refund` have no docstrings or type hints. `refund`'s parameter `order_total_amount` shadows the function name `order_total`.

Verdict: REQUEST CHANGES
