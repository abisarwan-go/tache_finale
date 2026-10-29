"""Customer entity with validated email property and loyalty tracking."""

from __future__ import annotations

import re

MAX_LOYALTY_POINTS = 1_000_000
_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class Customer:
    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        loyalty_points: int = 0,
    ) -> None:
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("customer_id must be a non-empty string")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(loyalty_points, int) or isinstance(
            loyalty_points, bool
        ):
            raise TypeError("loyalty_points must be an integer")
        if loyalty_points < 0 or loyalty_points > MAX_LOYALTY_POINTS:
            raise ValueError(
                "loyalty_points must be between 0 and 1,000,000"
            )

        self.customer_id = customer_id.strip()
        self.name = name.strip()
        self.loyalty_points = loyalty_points
        self.email = email  # validated via property setter

    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not isinstance(email, str):
            return False
        return _EMAIL_PATTERN.match(email.strip()) is not None

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        if not Customer.is_valid_email(value):
            raise ValueError(f"Invalid email: {value}")
        self.__email = value.strip()

    def add_loyalty_points(self, amount: int) -> int:
        """Add non-negative points to the loyalty balance."""
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError("amount must be an integer")
        if amount < 0:
            raise ValueError("amount must be non-negative")

        new_total = self.loyalty_points + amount
        if new_total > MAX_LOYALTY_POINTS:
            raise ValueError("loyalty_points cannot exceed 1,000,000")

        self.loyalty_points = new_total
        return self.loyalty_points

    def __str__(self) -> str:
        return (
            f"Customer={self.name} | Email={self.email} | "
            f"Points={self.loyalty_points}"
        )

    def __repr__(self) -> str:
        return f"Customer(name={self.name!r}, email={self.email!r})"
