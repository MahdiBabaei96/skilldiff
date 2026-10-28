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
