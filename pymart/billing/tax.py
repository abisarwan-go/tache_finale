"""Tax helpers for the PyMart billing subpackage."""

DEFAULT_TAX_RATE = 0.07


def add_tax(subtotal: float, tax_rate: float = DEFAULT_TAX_RATE) -> float:
    """Return the amount after applying tax (tax_rate like 0.07 for 7%)."""
    return round(subtotal * (1 + tax_rate), 2)
