import unittest

from shop import payments
from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity(self):
        self.assertEqual(line_total(5, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(1.25, 4), 5.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + TAX_RATE), 2))
        self.assertEqual(order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        self.assertEqual(order_total([(10, 2), (5, 4)]), round(40 * (1 + TAX_RATE), 2))

    def test_result_rounded_to_two_decimals(self):
        total = order_total([(0.99, 3)])
        self.assertEqual(total, round(total, 2))
        self.assertEqual(total, 3.22)

    def test_uses_module_tax_rate(self):
        original = payments.TAX_RATE
        payments.TAX_RATE = 0.5
        try:
            self.assertEqual(order_total([(100, 1)]), 150.0)
        finally:
            payments.TAX_RATE = original

    def test_zero_quantity_lines_add_nothing(self):
        self.assertEqual(order_total([(100, 0), (10, 1)]), order_total([(10, 1)]))


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_is_zero(self):
        self.assertEqual(refund(100, 100), 0)

    def test_zero_refund_leaves_total(self):
        self.assertEqual(refund(100, 0), 100)

    @unittest.expectedFailure
    def test_over_refund_is_rejected(self):
        # Refunding more than the order total should be an error; currently
        # refund() silently returns a negative balance.
        with self.assertRaises(ValueError):
            refund(100, 150)


if __name__ == "__main__":
    unittest.main()
