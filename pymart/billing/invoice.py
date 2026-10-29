"""Invoice-related helpers for the PyMart billing subpackage."""

from .tax import add_tax


def line_total(unit_price: float, quantity: int) -> float:
    """Return the total for a single invoice line."""
    return round(unit_price * quantity, 2)


def invoice_total(subtotal: float, tax_rate: float) -> float:
    """Return the invoice total including tax (tax_rate like 0.07 for 7%)."""
    return round(subtotal * (1 + tax_rate), 2)


def compute_total(unit_price: float, quantity: int) -> float:
    """Return the invoice line total including default tax."""
    subtotal = line_total(unit_price, quantity)
    return add_tax(subtotal)
