import unittest

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(2.5, 4), 10.0)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(19.99, 0), 0)

    def test_integer_inputs_stay_integer(self):
        self.assertEqual(line_total(3, 7), 21)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        # subtotal 45 * 1.0825 = 48.7125, rounded to cents
        self.assertEqual(order_total([(20, 2), (5, 1)]), 48.71)

    def test_quantity_is_applied_per_line(self):
        self.assertEqual(order_total([(10, 3)]), order_total([(30, 1)]))

    def test_result_is_rounded_to_two_decimals(self):
        result = order_total([(0.99, 3)])
        self.assertEqual(result, round(result, 2))

    def test_uses_tax_rate_constant(self):
        expected = round(50 * (1 + TAX_RATE), 2)
        self.assertEqual(order_total([(50, 1)]), expected)


class RefundTests(unittest.TestCase):
    def test_partial_refund_subtracts_amount(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(45.5, 45.5), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(50, 0), 50)


if __name__ == "__main__":
    unittest.main()
