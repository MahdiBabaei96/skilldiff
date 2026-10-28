# Review: shop/payments.py

- [blocker] shop/payments.py:3 `TAX_RATE` is a `float`. Money math must use `Decimal`, e.g. `Decimal("0.0825")`.
- [blocker] shop/payments.py:15 `round(subtotal * (1 + TAX_RATE), 2)` does float arithmetic and uses banker's rounding on float values, so totals can be off by a cent. Use `Decimal` and `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
- [blocker] shop/payments.py:18-19 `refund` has no validation. It accepts negative amounts, which increase the total, and amounts larger than the order total, which give a negative balance. It also returns a bare subtraction, not a refund record. Validate `0 < amount <= order_total_amount` and raise `ValueError` otherwise.
- [major] shop/payments.py:6-7 `line_total` does not validate its inputs. Negative or non-numeric price or quantity gives silently wrong totals. Check that quantity is a positive int and price is a non-negative `Decimal`.
- [major] shop/payments.py:10-15 `order_total` has no handling for malformed tuples (unpacking errors) or an empty list. An empty list returns `0.0` as a float, so the return type is inconsistent.
- [major] No tests exist (there is no `tests/` directory). Tax rounding, empty orders, and refund edge cases (negative amount, over-refund, full refund) need coverage.
- [nit] shop/payments.py:1 The module docstring says "Order totals", but the module also handles refunds. `refund` and `line_total` have no docstrings, and none of the functions have type hints.
- [nit] shop/payments.py:3 `shop/config.py` exists, so check whether the tax rate belongs there.

Verdict: REQUEST CHANGES
