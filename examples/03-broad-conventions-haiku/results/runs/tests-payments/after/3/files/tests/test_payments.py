import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(10, 3), 30)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(payments.line_total(10, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 20 * 1.0825 = 21.65
        self.assertEqual(payments.order_total([(10, 2)]), 21.65)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 25 -> 25 * 1.0825 = 27.0625 -> 27.06
        self.assertEqual(payments.order_total([(10, 2), (5, 1)]), 27.06)

    def test_result_is_rounded_to_two_decimals(self):
        total = payments.order_total([(0.99, 3)])
        self.assertEqual(total, round(total, 2))

    def test_tax_rate_applied(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_refund_returns_remaining_amount(self):
        self.assertEqual(payments.refund(100, 40), 60)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(50, 0), 50)


if __name__ == "__main__":
    unittest.main()
