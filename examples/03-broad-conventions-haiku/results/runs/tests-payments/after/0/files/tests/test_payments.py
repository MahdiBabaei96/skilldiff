import unittest

from shop import payments
from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(4, 3), 12)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 10 * 2 = 20 subtotal, plus 8.25% tax
        self.assertEqual(order_total([(10, 2)]), 21.65)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10, 2), (5, 1)]  # subtotal 25
        self.assertEqual(order_total(lines), round(25 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        # 1.00 with tax is 1.0825, which must come back rounded to two places
        result = order_total([(1.00, 1)])
        self.assertEqual(result, round(1.0 * (1 + TAX_RATE), 2))
        self.assertEqual(round(result, 2), result)

    def test_zero_price_lines_contribute_nothing(self):
        self.assertEqual(order_total([(0, 5)]), 0)


class RefundTests(unittest.TestCase):
    def test_refund_subtracts_amount(self):
        self.assertEqual(refund(100, 30), 70)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(42.5, 0), 42.5)


class ConstantsTests(unittest.TestCase):
    def test_tax_rate(self):
        self.assertEqual(payments.TAX_RATE, 0.0825)


if __name__ == "__main__":
    unittest.main()
