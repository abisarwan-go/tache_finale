"""Custom exceptions for PyMart order imports."""


class ValidationError(Exception):
    """A flagged, expected data problem. Safe to reject a record and continue."""
