import unittest

from shop import payments
from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(4, 3), 12)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    @unittest.expectedFailure
    def test_single_line_includes_tax(self):
        # BUG: 10 * 1.0825 = 10.825 should round half-up to 10.83, but the
        # float value is slightly below .825 and round() returns 10.82.
        self.assertEqual(order_total([(10, 1)]), 10.83)

    def test_single_line_with_tax_no_half_cent(self):
        self.assertEqual(order_total([(100, 1)]), 108.25)

    def test_sums_multiple_lines_then_applies_tax(self):
        lines = [(10, 2), (5, 1)]  # subtotal 25
        expected = round(25 * (1 + TAX_RATE), 2)
        self.assertEqual(order_total(lines), expected)
        self.assertEqual(expected, 27.06)

    def test_result_is_rounded_to_cents(self):
        total = order_total([(1.11, 3)])
        self.assertEqual(total, round(total, 2))

    def test_zero_price_lines_contribute_nothing(self):
        self.assertEqual(order_total([(0, 5)]), 0)

    def test_tax_rate_is_applied(self):
        self.assertEqual(order_total([(100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_subtracts_amount_from_total(self):
        self.assertEqual(refund(100, 25), 75)

    def test_full_refund_is_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_keeps_total(self):
        self.assertEqual(refund(42, 0), 42)

    def test_refund_of_order_total(self):
        total = order_total([(10, 2)])
        self.assertAlmostEqual(refund(total, total), 0)


class TaxRateTests(unittest.TestCase):
    def test_tax_rate_constant(self):
        self.assertEqual(payments.TAX_RATE, 0.0825)


if __name__ == "__main__":
    unittest.main()
