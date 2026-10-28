import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity(self):
        self.assertEqual(payments.line_total(5, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(payments.line_total(1.5, 4), 6.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        self.assertEqual(payments.order_total([(10, 2), (20, 4)]), 108.25)

    def test_result_rounded_to_cents(self):
        # 1 * 1.0825 -> 1.08
        self.assertEqual(payments.order_total([(1, 1)]), 1.08)

    def test_uses_tax_rate_constant(self):
        original = payments.TAX_RATE
        payments.TAX_RATE = 0
        try:
            self.assertEqual(payments.order_total([(10, 3)]), 30)
        finally:
            payments.TAX_RATE = original


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(payments.refund(100, 30), 70)

    def test_full_refund(self):
        self.assertEqual(payments.refund(100, 100), 0)

    @unittest.expectedFailure
    def test_refund_exceeding_total_is_rejected(self):
        # Bug: refund() does no validation and returns a negative balance.
        with self.assertRaises(ValueError):
            payments.refund(100, 150)


if __name__ == "__main__":
    unittest.main()
