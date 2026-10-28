import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity(self):
        self.assertEqual(payments.line_total(5, 0), 0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        self.assertEqual(payments.order_total([(50, 1), (25, 2)]), 108.25)

    def test_result_rounded_to_two_places(self):
        total = payments.order_total([(9.99, 3)])
        self.assertEqual(total, round(total, 2))
        self.assertAlmostEqual(total, 29.97 * (1 + payments.TAX_RATE), places=2)


class RefundTests(unittest.TestCase):
    def test_partial_refund_subtracts_amount(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_full_refund_is_zero(self):
        self.assertEqual(payments.refund(100, 100), 0)


if __name__ == "__main__":
    unittest.main()
