"""Product entity with validated properties and instance tracking."""

from __future__ import annotations

from pymart.exceptions import InsufficientStockError, InvalidDiscountError


class Product:
    _total_products = 0

    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        quantity: int = 0,
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError("quantity must be an integer")
        if quantity < 0:
            raise ValueError("quantity must be zero or more")

        self.name = name.strip()
        self.quantity = quantity
        self.__sku = None  # name-mangled; set through set_sku / sku property
        self.sku = sku  # validated via property setter
        self.price = price  # validated via property setter
        self.__class__._register_new_product()

    @classmethod
    def _register_new_product(cls) -> None:
        cls._total_products += 1

    @classmethod
    def total_products(cls) -> int:
        return cls._total_products

    @classmethod
    def reset_counter(cls) -> None:
        """Reset instance counter (useful in tests)."""
        cls._total_products = 0

    @property
    def sku(self) -> str | None:
        return self.__sku

    @sku.setter
    def sku(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("sku must be a non-empty string")
        self.__sku = value.strip()

    def set_sku(self, sku: str) -> None:
        self.sku = sku

    def get_sku(self) -> str | None:
        return self.__sku

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("price must be a number")
        if value < 0:
            raise ValueError("price must be >= 0")
        self._price = round(float(value), 2)

    def sell(self, qty: int) -> int:
        """Reduce on-hand stock for a sale.

        Returns:
            Remaining quantity after the sale.
        """
        if not isinstance(qty, int) or isinstance(qty, bool):
            raise TypeError("qty must be an integer")
        if qty <= 0:
            raise ValueError("qty must be positive")
        if qty > self.quantity:
            raise InsufficientStockError(
                sku=str(self.sku),
                requested_qty=qty,
                available_stock=self.quantity,
            )

        self.quantity -= qty
        return self.quantity

    def apply_discount(self, percentage: float) -> float:
        """Reduce price by a percentage from 0 to 100."""
        if not isinstance(percentage, (int, float)) or isinstance(
            percentage, bool
        ):
            raise TypeError("percentage must be a number")
        if percentage < 0 or percentage > 100:
            raise InvalidDiscountError(
                sku=str(self.sku),
                percentage=percentage,
                min_percent=0,
                max_percent=100,
            )

        self.price = self.price * (1 - percentage / 100)
        return self.price

    def describe(self) -> str:
        """Canonical polymorphic description shared by all products."""
        return f"{self.sku} | {self.name} | ${self.price:.2f}"

    def __str__(self) -> str:
        return (
            f"SKU={self.sku} | Name={self.name} | "
            f"Price=${self.price:.2f} | Qty={self.quantity}"
        )

    def __repr__(self) -> str:
        return f"Product(name={self.name!r}, price={self.price:.2f})"
