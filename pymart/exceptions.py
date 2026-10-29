"""PyMart domain exception hierarchy."""

from __future__ import annotations


class PyMartError(Exception):
    """Base class for all PyMart domain exceptions."""


class DataValidationError(PyMartError):
    """Raised when a parsed record violates business rules."""

    def __init__(self, message: str, *, source: str | None = None, line: int | None = None):
        self.source = source
        self.line = line
        context = []
        if source:
            context.append(f"file={source}")
        if line is not None:
            context.append(f"line={line}")
        prefix = f"[{', '.join(context)}] " if context else ""
        super().__init__(f"{prefix}{message}")


class RecordFormatError(PyMartError):
    """Raised when a raw record cannot be parsed into expected fields."""

    def __init__(self, message: str, *, source: str | None = None, line: int | None = None):
        self.source = source
        self.line = line
        context = []
        if source:
            context.append(f"file={source}")
        if line is not None:
            context.append(f"line={line}")
        prefix = f"[{', '.join(context)}] " if context else ""
        super().__init__(f"{prefix}{message}")


class UnknownProductError(PyMartError):
    """Raised when an order references an unknown SKU."""

    def __init__(self, sku: str, *, source: str | None = None, line: int | None = None):
        self.sku = sku
        self.source = source
        self.line = line
        context = []
        if source:
            context.append(f"file={source}")
        if line is not None:
            context.append(f"line={line}")
        prefix = f"[{', '.join(context)}] " if context else ""
        super().__init__(f"{prefix}Unknown product SKU '{sku}'.")


class DuplicateIdError(PyMartError):
    """Raised when an identifier already exists in the catalog/store."""

    def __init__(self, entity: str, identifier: str):
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"Duplicate {entity} id '{identifier}'.")


class InsufficientStockError(PyMartError):
    """Raised when requested quantity exceeds available stock."""

    def __init__(self, sku: str, requested_qty: int, available_stock: int):
        self.sku = sku
        self.requested_qty = requested_qty
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for SKU '{sku}': requested {requested_qty}, "
            f"available {available_stock}."
        )


class InvalidDiscountError(PyMartError):
    """Raised when an attempted discount percentage is invalid."""

    def __init__(
        self,
        sku: str,
        percentage: float,
        min_percent: float = 0,
        max_percent: float = 100,
    ):
        self.sku = sku
        self.percentage = percentage
        self.min_percent = min_percent
        self.max_percent = max_percent
        super().__init__(
            f"Invalid discount for SKU '{sku}': attempted {percentage}% "
            f"(allowed {min_percent}–{max_percent})."
        )
