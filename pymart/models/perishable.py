"""Perishable product subclass with expiry and storage temperature."""

from __future__ import annotations

from datetime import date, datetime

from .product import Product


class PerishableProduct(Product):
    def __init__(
        self,
        sku: str,
        name: str,
        price: float,
        expiry_date: date | str | None = None,
        storage_temp_c: float | None = None,
        quantity: int = 0,
        *,
        expiration_date: date | str | None = None,
    ) -> None:
        super().__init__(sku=sku, name=name, price=price, quantity=quantity)

        raw_expiry = expiry_date if expiry_date is not None else expiration_date
        if raw_expiry is None:
            raise ValueError("expiry_date is required")

        self.expiry_date = self._normalize_expiry(raw_expiry)
        if storage_temp_c is not None and not isinstance(
            storage_temp_c, (int, float)
        ):
            raise TypeError("storage_temp_c must be a number")
        self.storage_temp_c = (
            float(storage_temp_c) if storage_temp_c is not None else None
        )

    @staticmethod
    def _normalize_expiry(value: date | str) -> date:
        if isinstance(value, datetime):
            parsed = value.date()
        elif isinstance(value, date):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = date.fromisoformat(value.strip())
            except ValueError as exc:
                raise ValueError(
                    f"expiry_date must be ISO format YYYY-MM-DD, got {value!r}"
                ) from exc
        else:
            raise TypeError("expiry_date must be a date or ISO string")

        if parsed < date.today():
            raise ValueError(f"expiry_date cannot be in the past: {parsed}")
        return parsed

    def describe(self) -> str:
        base = super().describe()
        parts = [f"{base} | expires: {self.expiry_date.isoformat()}"]
        if self.storage_temp_c is not None:
            parts.append(f"store at {self.storage_temp_c:g}°C")
        return " | ".join(parts)
