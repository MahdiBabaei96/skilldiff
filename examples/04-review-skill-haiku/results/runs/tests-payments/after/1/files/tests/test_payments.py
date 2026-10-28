import unittest

from shop import payments
from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_price_times_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + TAX_RATE), 2))

    def test_sums_multiple_lines_before_tax(self):
        lines = [(10, 2), (5, 3)]
        self.assertEqual(order_total(lines), round(35 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        result = order_total([(0.33, 1)])
        self.assertEqual(result, round(result, 2))

    def test_known_value(self):
        # 20.00 * 1.0825 = 21.65
        self.assertEqual(order_total([(20, 1)]), 21.65)

    def test_zero_quantity_line_contributes_nothing(self):
        self.assertEqual(order_total([(50, 0)]), 0)
        self.assertEqual(order_total([(50, 0), (20, 1)]), order_total([(20, 1)]))

    def test_uses_tax_rate_constant(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + payments.TAX_RATE), 2))


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(100, 100), 0)

    def test_zero_refund_leaves_total(self):
        self.assertEqual(refund(100, 0), 100)

    def test_float_amounts(self):
        self.assertAlmostEqual(refund(21.65, 10.25), 11.40)


if __name__ == "__main__":
    unittest.main()
