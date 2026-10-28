import unittest

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity(self):
        self.assertEqual(line_total(5, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order(self):
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

    def test_zero_quantity_line_adds_nothing(self):
        self.assertEqual(order_total([(10, 0), (100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund(self):
        self.assertEqual(refund(100, 100), 0)

    def test_zero_refund(self):
        self.assertEqual(refund(100, 0), 100)

    @unittest.expectedFailure
    def test_over_refund_should_be_rejected(self):
        # Currently returns -50 instead of refusing to refund more than the total.
        with self.assertRaises(ValueError):
            refund(100, 150)


if __name__ == "__main__":
    unittest.main()
