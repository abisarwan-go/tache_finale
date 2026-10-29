"""Stock-related helpers for the PyMart inventory subpackage."""

_stock: dict[str, int] = {}


def add_stock(item: str, added_qty: int) -> int:
    """Add quantity for an item and return the new stock level."""
    _stock[item] = _stock.get(item, 0) + added_qty
    return _stock[item]


def get_stock(item: str) -> int:
    """Return the current stock level for an item (0 if unknown)."""
    return _stock.get(item, 0)


def is_in_stock(item: str, requested_qty: int) -> bool:
    """Return True when you can fulfill the requested quantity."""
    return get_stock(item) >= requested_qty
