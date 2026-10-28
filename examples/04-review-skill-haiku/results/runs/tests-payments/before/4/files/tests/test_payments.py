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

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10, 2), (5, 3)]
        self.assertEqual(order_total(lines), round(35 * (1 + TAX_RATE), 2))

    def test_rounds_to_two_decimal_places(self):
        result = order_total([(0.99, 3)])
        self.assertEqual(result, round(2.97 * (1 + TAX_RATE), 2))
        self.assertEqual(result, round(result, 2))

    def test_uses_tax_rate_constant(self):
        self.assertAlmostEqual(order_total([(200, 1)]), round(200 * (1 + TAX_RATE), 2))

    def test_accepts_any_iterable_of_pairs(self):
        self.assertEqual(order_total(iter([(100, 1)])), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(42.5, 0), 42.5)


class TaxRateTests(unittest.TestCase):
    def test_tax_rate_value(self):
        self.assertEqual(payments.TAX_RATE, 0.0825)


if __name__ == "__main__":
    unittest.main()
