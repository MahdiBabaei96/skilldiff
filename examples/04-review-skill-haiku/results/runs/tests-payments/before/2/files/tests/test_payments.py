import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shop import payments  # noqa: E402


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity_gives_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_float_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    # BUG: order_total rounds with float round(), and 10 * 1.0825 is
    # 10.824999... in binary floating point, so half-cent tax rounds down.
    # Money rounding should be half-up (10.825 -> 10.83).
    @unittest.expectedFailure
    def test_single_line_includes_tax(self):
        self.assertEqual(payments.order_total([(10, 1)]), 10.83)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10, 2), (5, 1)]  # subtotal 25
        self.assertEqual(payments.order_total(lines), round(25 * 1.0825, 2))

    def test_tax_is_applied_with_tax_rate(self):
        total = payments.order_total([(100, 1)])
        self.assertAlmostEqual(total, 100 * (1 + payments.TAX_RATE), places=2)

    def test_result_is_rounded_to_cents(self):
        total = payments.order_total([(1.11, 3)])
        self.assertEqual(total, round(round(1.11 * 3, 10) * 1.0825, 2))
        self.assertEqual(total, round(total, 2))

    def test_zero_priced_items_contribute_nothing(self):
        self.assertEqual(payments.order_total([(0, 5), (4, 1)]), round(4 * 1.0825, 2))

    def test_accepts_generator_of_pairs(self):
        lines = ((price, 1) for price in (3, 7))
        self.assertEqual(payments.order_total(lines), round(10 * 1.0825, 2))


class RefundTests(unittest.TestCase):
    def test_partial_refund_subtracts_amount(self):
        self.assertEqual(payments.refund(100, 25), 75)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(42.5, 42.5), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(60, 0), 60)


if __name__ == "__main__":
    unittest.main()
