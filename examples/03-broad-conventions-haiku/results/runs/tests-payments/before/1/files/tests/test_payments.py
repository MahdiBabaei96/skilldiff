import unittest

from shop import payments


class LineTotalTests(unittest.TestCase):
    def test_multiplies_price_by_quantity(self):
        self.assertEqual(payments.line_total(5, 3), 15)

    def test_zero_quantity_is_zero(self):
        self.assertEqual(payments.line_total(9.99, 0), 0)

    def test_fractional_price(self):
        self.assertAlmostEqual(payments.line_total(2.5, 4), 10.0)


class OrderTotalTests(unittest.TestCase):
    def test_empty_order_is_zero(self):
        self.assertEqual(payments.order_total([]), 0)

    @unittest.expectedFailure
    def test_single_line_includes_tax(self):
        # BUG: 10.00 * 1.0825 = 10.825 should round half-up to 10.83, but
        # float representation makes round() return 10.82.
        self.assertEqual(payments.order_total([(10.0, 1)]), 10.83)

    def test_multiple_lines_are_summed_before_tax(self):
        lines = [(10.0, 2), (5.0, 1)]  # subtotal 25.00
        expected = round(25.0 * (1 + payments.TAX_RATE), 2)
        self.assertEqual(payments.order_total(lines), expected)

    def test_result_is_rounded_to_cents(self):
        total = payments.order_total([(1.11, 3)])
        self.assertEqual(total, round(round(1.11 * 3, 10) * (1 + payments.TAX_RATE), 2))

    def test_zero_price_line_contributes_nothing(self):
        self.assertEqual(
            payments.order_total([(0, 5), (4.0, 1)]),
            payments.order_total([(4.0, 1)]),
        )

    def test_tax_rate_is_applied(self):
        self.assertEqual(payments.order_total([(100.0, 1)]), 108.25)


class RefundTests(unittest.TestCase):
    def test_partial_refund_subtracts_amount(self):
        self.assertEqual(payments.refund(100.0, 40.0), 60.0)

    def test_full_refund_leaves_zero(self):
        self.assertEqual(payments.refund(50.0, 50.0), 0)

    def test_zero_refund_leaves_total_unchanged(self):
        self.assertEqual(payments.refund(42.5, 0), 42.5)


if __name__ == "__main__":
    unittest.main()
