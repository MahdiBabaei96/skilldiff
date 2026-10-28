# Review: shop/payments.py

- [blocker] `shop/payments.py:3` `TAX_RATE = 0.0825` is a float. Money and tax must use `Decimal` (e.g. `Decimal("0.0825")`); binary floats produce rounding errors in currency amounts.
- [blocker] `shop/payments.py:7` `line_total` multiplies `price * quantity` with whatever types it receives. With float prices this carries the same float error; the function should accept and return `Decimal`.
- [blocker] `shop/payments.py:12-15` `order_total` starts `subtotal = 0` and accumulates floats, then calls `round(..., 2)` on a float result. The total is computed in float and rounded with the float `round`, which is not a correct money calculation. Use `Decimal` throughout and quantize with `ROUND_HALF_UP` to cents.
- [major] `shop/payments.py:6-7` `line_total` does no input validation. Negative prices, negative or zero quantities, and non-integer quantities are all accepted silently.
- [major] `shop/payments.py:10-15` `order_total` does not validate `lines`. An empty list returns 0 with no signal, and malformed tuples fail with an unhelpful unpacking error rather than a clear one.
- [major] `shop/payments.py:18-19` `refund` has no validation. It accepts a refund larger than the order total, a negative refund amount (which would increase the balance), and no check that the refund does not exceed what was paid. This is a money-moving function and needs guards and a clear error.
- [major] `shop/payments.py:15` Tax is applied to the summed subtotal and rounded once. Whether that matches the business rule (per-line rounding vs. order-level rounding) is not stated or tested. Confirm the rule and encode it.
- [major] No tests exist for this module. There is no test file under `tests/` and nothing imports `shop/payments.py`. Add unit tests covering totals with tax, rounding edge cases (e.g. half-cent values), empty orders, invalid input, and refund bounds.
- [nit] `shop/payments.py:1` Module docstring says "Order totals" but the module also contains `refund`. Update the docstring to cover both.
- [nit] `shop/payments.py:11` Docstring says "Returns the total including tax" but does not name the return type or currency precision. State it.

Verdict: REQUEST CHANGES
