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
        self.assertEqual(payments.order_total([(10, 2), (5, 4)]), 43.30)

    def test_rounds_to_two_decimals(self):
        # 1.01 * 1.0825 = 1.093325 -> 1.09
        self.assertEqual(payments.order_total([(1.01, 1)]), 1.09)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_full_refund(self):
        self.assertEqual(payments.refund(100, 100), 0)

    @unittest.expectedFailure
    def test_refund_larger_than_total_is_rejected(self):
        # Currently returns -20 instead of rejecting the refund.
        with self.assertRaises(ValueError):
            payments.refund(100, 120)

    @unittest.expectedFailure
    def test_negative_refund_is_rejected(self):
        # Currently returns 110, i.e. a "refund" that increases the balance.
        with self.assertRaises(ValueError):
            payments.refund(100, -10)


if __name__ == "__main__":
    unittest.main()
