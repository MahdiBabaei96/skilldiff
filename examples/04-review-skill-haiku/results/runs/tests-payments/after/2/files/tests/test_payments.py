import unittest

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(4, 3), 12)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(10, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + TAX_RATE), 2))

    def test_sums_multiple_lines_before_tax(self):
        lines = [(10, 2), (5, 3)]
        expected = round(35 * (1 + TAX_RATE), 2)
        self.assertEqual(order_total(lines), expected)

    def test_result_is_rounded_to_cents(self):
        result = order_total([(0.99, 3)])
        self.assertEqual(result, round(result, 2))

    def test_known_value(self):
        # 20.00 * 1.0825 = 21.65
        self.assertEqual(order_total([(20, 1)]), 21.65)

    def test_zero_quantity_line_contributes_nothing(self):
        self.assertEqual(order_total([(50, 0)]), 0)

    def test_tax_rate_is_applied(self):
        self.assertEqual(order_total([(1000, 1)]), 1082.5)


class RefundTests(unittest.TestCase):
    def test_refund_subtracts_amount(self):
        self.assertEqual(refund(100, 25), 75)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(40, 40), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(40, 0), 40)

    def test_refund_can_produce_float_result(self):
        self.assertAlmostEqual(refund(10.50, 0.25), 10.25)


if __name__ == "__main__":
    unittest.main()
