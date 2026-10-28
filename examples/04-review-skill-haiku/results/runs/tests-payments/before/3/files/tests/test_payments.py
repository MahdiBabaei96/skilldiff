import unittest

from shop.payments import TAX_RATE, line_total, order_total, refund


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(line_total(9.99, 0), 0)

    def test_float_price(self):
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
        total = order_total([(1.99, 1)])
        self.assertEqual(total, round(total, 2))

    def test_known_value(self):
        # 20.00 subtotal * 1.0825 = 21.65
        self.assertEqual(order_total([(20, 1)]), 21.65)


class RefundTests(unittest.TestCase):
    def test_subtracts_amount(self):
        self.assertEqual(refund(50, 20), 30)

    def test_full_refund_is_zero(self):
        self.assertEqual(refund(42, 42), 0)

    def test_zero_refund_is_unchanged(self):
        self.assertEqual(refund(42, 0), 42)

    @unittest.expectedFailure
    def test_refund_keeps_cent_precision(self):
        # Known bug: float subtraction leaves artifacts such as
        # 0.3 - 0.1 == 0.19999999999999998 instead of 0.20.
        self.assertEqual(refund(0.3, 0.1), 0.2)


if __name__ == "__main__":
    unittest.main()
