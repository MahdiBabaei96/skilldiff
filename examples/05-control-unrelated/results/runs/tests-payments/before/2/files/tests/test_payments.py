import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity(self):
        self.assertEqual(payments.line_total(5, 0), 0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines(self):
        self.assertEqual(payments.order_total([(10, 2), (5, 4)]), 43.3)

    def test_rounds_to_two_places(self):
        self.assertEqual(payments.order_total([(0.99, 1)]), 1.07)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_full_refund(self):
        self.assertEqual(payments.refund(100, 100), 0)

    @unittest.expectedFailure
    def test_refund_more_than_total_is_rejected(self):
        # Currently returns a negative balance instead of raising.
        with self.assertRaises(ValueError):
            payments.refund(50, 80)


if __name__ == "__main__":
    unittest.main()
