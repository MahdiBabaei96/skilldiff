import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_price_times_quantity(self):
        self.assertEqual(payments.line_total(3, 4), 12)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 3), 7.5)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 2 * 10.00 = 20.00; 20.00 * 1.0825 = 21.65
        self.assertEqual(payments.order_total([(10.0, 2)]), 21.65)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 6.47; 6.47 * 1.0825 = 7.003775 -> 7.00
        self.assertEqual(payments.order_total([(1.99, 3), (0.5, 1)]), 7.0)

    def test_result_is_rounded_to_cents(self):
        result = payments.order_total([(0.01, 1)])
        self.assertEqual(result, round(result, 2))

    def test_tax_rate_applied(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(payments.refund(50, 20), 30)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(10, 10), 0)

    def test_refund_of_zero_is_unchanged(self):
        self.assertEqual(payments.refund(42.5, 0), 42.5)


if __name__ == "__main__":
    unittest.main()
