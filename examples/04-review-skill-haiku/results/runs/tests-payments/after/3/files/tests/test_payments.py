import unittest

from shop import payments
from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(4, 3), 12)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(line_total(19.99, 0), 0)

    def test_zero_price_gives_zero(self):
        self.assertEqual(line_total(0, 5), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(10, 2)]), round(20 * (1 + TAX_RATE), 2))
        self.assertEqual(order_total([(10, 2)]), 21.65)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10, 2), (5, 1)]
        self.assertEqual(order_total(lines), round(25 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        # 1.00 * 1.0825 = 1.0825 -> 1.08
        self.assertEqual(order_total([(1.00, 1)]), 1.08)

    def test_zero_priced_items_add_no_tax(self):
        self.assertEqual(order_total([(0, 10)]), 0)

    def test_accepts_any_iterable_of_pairs(self):
        self.assertEqual(order_total(iter([(10, 1)])), order_total([(10, 1)]))

    def test_tax_rate_is_applied(self):
        self.assertEqual(order_total([(100, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(refund(50, 20), 30)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(50, 50), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(refund(50, 0), 50)

    def test_refund_of_fractional_amounts(self):
        self.assertAlmostEqual(refund(21.65, 1.65), 20.0)


class ModuleTests(unittest.TestCase):
    def test_tax_rate_constant(self):
        self.assertEqual(payments.TAX_RATE, 0.0825)


if __name__ == "__main__":
    unittest.main()
