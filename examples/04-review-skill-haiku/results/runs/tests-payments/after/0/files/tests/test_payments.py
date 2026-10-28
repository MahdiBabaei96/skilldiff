import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    def test_single_line_includes_tax(self):
        # 100 * 1.0825 = 108.25
        self.assertEqual(payments.order_total([(100, 1)]), 108.25)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10, 2), (5, 4)]  # subtotal 40
        self.assertEqual(payments.order_total(lines), round(40 * 1.0825, 2))

    def test_result_is_rounded_to_cents(self):
        total = payments.order_total([(1.99, 3)])
        self.assertEqual(total, round(round(1.99 * 3, 10) * 1.0825, 2))
        self.assertEqual(total, round(total, 2))

    def test_zero_priced_items_contribute_nothing(self):
        self.assertEqual(payments.order_total([(0, 5), (20, 1)]),
                         payments.order_total([(20, 1)]))

    def test_accepts_any_iterable_of_pairs(self):
        lines = iter([(10, 1), (10, 1)])
        self.assertEqual(payments.order_total(lines), 21.65)


class RefundTests(unittest.TestCase):
    def test_partial_refund(self):
        self.assertEqual(payments.refund(100, 25), 75)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(50, 50), 0)

    def test_zero_refund_is_unchanged(self):
        self.assertEqual(payments.refund(42.5, 0), 42.5)


if __name__ == "__main__":
    unittest.main()
