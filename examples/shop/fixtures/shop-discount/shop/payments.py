"""Order totals for the shop."""

TAX_RATE = 0.0825


def line_total(price, quantity):
    return price * quantity


def order_total(lines):
    """lines: list of (price, quantity) tuples. Returns the total including tax."""
    subtotal = 0
    for price, qty in lines:
        subtotal += line_total(price, qty)
    return round(subtotal * (1 + TAX_RATE), 2)


def refund(order_total_amount, amount):
    return order_total_amount - amount


def apply_discount(total, percent):
    """Apply a percentage discount, e.g. apply_discount(100, 15) -> 85.0"""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(total * (1 - percent / 100), 2)
