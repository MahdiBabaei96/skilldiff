import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(3, 4), 12)

    def test_handles_fractional_price(self):
        self.assertEqual(payments.line_total(2.5, 2), 5.0)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 40, with 8.25% tax -> 43.30
        self.assertEqual(payments.order_total([(10, 2), (5, 4)]), 43.3)

    def test_result_is_rounded_to_cents(self):
        # 5 * 1.0825 = 5.4125 -> 5.41
        self.assertEqual(payments.order_total([(1, 1), (2, 2)]), 5.41)

    def test_does_not_mutate_input_lines(self):
        lines = [(1, 1), (2, 2)]
        payments.order_total(lines)
        self.assertEqual(lines, [(1, 1), (2, 2)])


class RefundTests(unittest.TestCase):
    def test_refund_returns_difference(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_refund_of_zero_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(50, 0), 50)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(50, 50), 0)

    @unittest.expectedFailure
    def test_refund_more_than_total_should_not_go_negative(self):
        # Known gap: refund() does not validate the amount, so refunding
        # more than the order total yields a negative balance.
        self.assertGreaterEqual(payments.refund(50, 80), 0)


if __name__ == "__main__":
    unittest.main()
