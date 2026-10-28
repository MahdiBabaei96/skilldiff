import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 100 * 1.0825 = 108.25
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 10 + 20 = 30; 30 * 1.0825 = 32.475 -> 32.47 or 32.48
        total = payments.order_total([(10, 1), (5, 4)])
        self.assertAlmostEqual(total, 32.48, delta=0.01)

    def test_result_is_rounded_to_two_decimals(self):
        total = payments.order_total([(1.11, 3)])
        self.assertEqual(total, round(total, 2))

    def test_tax_rate_is_applied(self):
        total = payments.order_total([(200, 1)])
        self.assertAlmostEqual(total, 200 * (1 + payments.TAX_RATE), places=2)


class RefundTests(unittest.TestCase):
    def test_refund_subtracts_amount(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_full_refund_is_zero(self):
        self.assertEqual(payments.refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(42.5, 0), 42.5)


if __name__ == "__main__":
    unittest.main()
