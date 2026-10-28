import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        expected = round(10 * (1 + TAX_RATE), 2)
        self.assertEqual(order_total([(10, 1)]), expected)

    def test_sums_multiple_lines_before_tax(self):
        lines = [(10, 2), (5, 3)]  # subtotal 35
        self.assertEqual(order_total(lines), round(35 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        total = order_total([(0.99, 3)])
        self.assertEqual(total, round(total, 2))

    def test_known_value(self):
        # 100 * 1.0825 = 108.25
        self.assertEqual(order_total([(100, 1)]), 108.25)

    def test_zero_tax_when_zero_priced_items(self):
        self.assertEqual(order_total([(0, 5)]), 0)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(42.5, 0), 42.5)


if __name__ == "__main__":
    unittest.main()
