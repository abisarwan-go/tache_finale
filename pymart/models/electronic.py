"""Electronic product subclass with warranty and power rating."""

from __future__ import annotations

from .product import Product


class ElectronicProduct(Product):
    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        warranty_months: int | None = None,
        power_watts: float | None = None,
        quantity: int = 0,
        *,
        warranty_years: int | None = None,
    ) -> None:
        super().__init__(sku=sku, name=name, price=price, quantity=quantity)

        if warranty_months is None and warranty_years is None:
            raise ValueError("warranty_months or warranty_years is required")
        if warranty_months is None:
            if not isinstance(warranty_years, int) or isinstance(
                warranty_years, bool
            ):
                raise TypeError("warranty_years must be an integer")
            if warranty_years < 0:
                raise ValueError("warranty_years cannot be negative")
            warranty_months = warranty_years * 12

        if not isinstance(warranty_months, int) or isinstance(
            warranty_months, bool
        ):
            raise TypeError("warranty_months must be an integer")
        if warranty_months < 0:
            raise ValueError("warranty_months cannot be negative")

        self.warranty_months = warranty_months

        if power_watts is not None:
            if not isinstance(power_watts, (int, float)) or isinstance(
                power_watts, bool
            ):
                raise TypeError("power_watts must be a number")
            if power_watts < 0:
                raise ValueError("power_watts cannot be negative")
            self.power_watts = float(power_watts)
        else:
            self.power_watts = None

    def describe(self) -> str:
        base = super().describe()
        parts = [f"{base} | warranty: {self.warranty_months} months"]
        if self.power_watts is not None:
            parts.append(f"power: {self.power_watts:g}W")
        return " | ".join(parts)
