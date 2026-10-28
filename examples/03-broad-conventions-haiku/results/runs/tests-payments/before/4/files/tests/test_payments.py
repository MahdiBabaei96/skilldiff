import unittest

from shop import payments
from shop.payments import line_total, order_total, refund, TAX_RATE


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(order_total([]), 0)

    def test_single_line_includes_tax(self):
        self.assertEqual(order_total([(100, 1)]), round(100 * (1 + TAX_RATE), 2))

    def test_sums_multiple_lines_before_tax(self):
        lines = [(10, 2), (5, 3)]  # subtotal 35
        self.assertEqual(order_total(lines), round(35 * (1 + TAX_RATE), 2))

    def test_result_is_rounded_to_cents(self):
        result = order_total([(0.99, 3)])
        self.assertEqual(result, round(result, 2))

    def test_known_value(self):
        # 20.00 * 1.0825 = 21.65
        self.assertEqual(order_total([(20, 1)]), 21.65)

    def test_accepts_generator(self):
        gen = ((p, q) for p, q in [(10, 1), (10, 1)])
        self.assertEqual(order_total(gen), order_total([(10, 1), (10, 1)]))


class RefundTests(unittest.TestCase):
    def test_subtracts_amount(self):
        self.assertEqual(refund(100, 25), 75)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(refund(40, 40), 0)

    def test_zero_refund_is_no_change(self):
        self.assertEqual(refund(40, 0), 40)


class TaxRateTests(unittest.TestCase):
    def test_tax_rate_constant(self):
        self.assertEqual(payments.TAX_RATE, 0.0825)


if __name__ == "__main__":
    unittest.main()
