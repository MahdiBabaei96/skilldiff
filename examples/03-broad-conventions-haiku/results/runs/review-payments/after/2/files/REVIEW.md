# Review: shop/payments.py

- [major] shop/payments.py:3 `TAX_RATE = 0.0825` is a float. Money math should use `Decimal` (e.g. `Decimal("0.0825")`), not float.
- [major] shop/payments.py:7 `line_total` multiplies `price * quantity` with whatever types it receives. With float prices this accumulates binary rounding error. Use `Decimal` and make the function return a quantized value.
- [major] shop/payments.py:12-15 `order_total` starts `subtotal` at int `0` and sums floats. The final `round(..., 2)` uses Python's banker's rounding (round-half-to-even) on a float, which can produce results that differ from the usual half-up rule for currency. Use `Decimal` with an explicit `ROUND_HALF_UP` quantize.
- [major] shop/payments.py:13 No input validation. Negative or zero quantities, negative prices, non-integer quantities, and `None` or non-numeric values are all accepted silently and can produce negative or nonsensical totals.
- [major] shop/payments.py:18-19 `refund` does not validate its arguments. It allows a negative `amount`, an `amount` greater than `order_total_amount` (producing a negative refund), and it returns an unrounded float, so `refund(10.00, 3.10)` yields `6.9` with float error rather than `6.90`.
- [major] shop/payments.py:1-19 No tests cover this module. Add pytest tests under `tests/` for tax rounding, empty orders, multi-line totals, and refund boundary cases (zero, equal to total, exceeding total, negative).
- [nit] shop/payments.py:18 `refund` has no docstring, unlike `order_total`. Its parameter `order_total_amount` also shares a name with the function `order_total`, which is easy to confuse.

Verdict: REQUEST CHANGES
