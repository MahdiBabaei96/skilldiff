import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(4, 3), 12)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_handles_float_price(self):
        self.assertAlmostEqual(payments.line_total(1.5, 2), 3.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 20.00 * 1.0825 = 21.65
        self.assertEqual(payments.order_total([(10.00, 2)]), 21.65)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 6.47 * 1.0825 = 7.003775 -> 7.0
        self.assertEqual(payments.order_total([(1.99, 3), (0.50, 1)]), 7.0)

    def test_result_is_rounded_to_cents(self):
        total = payments.order_total([(0.01, 1)])
        self.assertEqual(total, round(total, 2))

    def test_tax_rate_is_applied(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund_subtracts_amount(self):
        self.assertAlmostEqual(payments.refund(21.65, 5.00), 16.65)

    def test_full_refund_leaves_zero(self):
        self.assertAlmostEqual(payments.refund(21.65, 21.65), 0.0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(21.65, 0), 21.65)


if __name__ == "__main__":
    unittest.main()
