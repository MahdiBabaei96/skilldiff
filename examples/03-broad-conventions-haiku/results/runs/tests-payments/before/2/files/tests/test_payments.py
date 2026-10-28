import unittest

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(4, 3), 12)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + TAX_RATE), 2))

    def test_sums_multiple_lines_before_tax(self):
        lines = [(10, 2), (5, 3)]
        self.assertEqual(order_total(lines), round(35 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        result = order_total([(1.11, 1)])
        self.assertEqual(result, round(result, 2))

    def test_tax_rate_is_8_25_percent(self):
        self.assertEqual(order_total([(1000, 1)]), 1082.5)

    def test_accepts_generator_of_tuples(self):
        lines = ((price, qty) for price, qty in [(20, 1), (30, 2)])
        self.assertEqual(order_total(lines), round(80 * (1 + TAX_RATE), 2))


class RefundTests(unittest.TestCase):
    def test_refund_subtracts_amount(self):
        self.assertEqual(refund(100, 40), 60)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(75, 0), 75)

    def test_refund_of_order_total(self):
        total = order_total([(10, 1)])
        self.assertAlmostEqual(refund(total, total), 0)


if __name__ == "__main__":
    unittest.main()
