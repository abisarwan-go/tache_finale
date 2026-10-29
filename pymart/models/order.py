"""Order domain model for PyMart back-office."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class OrderLine:
    sku: str
    quantity: int
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def describe(self) -> str:
        return (
            f"{self.sku} x{self.quantity} @ ${self.unit_price:.2f} "
            f"= ${self.line_total:.2f}"
        )


@dataclass
class Order:
    order_id: str
    customer_id: str
    order_date: date
    lines: list[OrderLine] = field(default_factory=list)
    status: str = "created"

    @property
    def total(self) -> float:
        return round(sum(line.line_total for line in self.lines), 2)

    def add_line(self, line: OrderLine) -> None:
        self.lines.append(line)

    def describe(self) -> str:
        return (
            f"Order {self.order_id} | customer={self.customer_id} | "
            f"date={self.order_date.isoformat()} | "
            f"lines={len(self.lines)} | total=${self.total:.2f} | "
            f"status={self.status}"
        )

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "lines": [
                {
                    "sku": line.sku,
                    "quantity": line.quantity,
                    "unit_price": line.unit_price,
                    "line_total": line.line_total,
                }
                for line in self.lines
            ],
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Order:
        order_date = data["order_date"]
        if isinstance(order_date, str):
            order_date = date.fromisoformat(order_date)
        order = cls(
            order_id=str(data["order_id"]),
            customer_id=str(data["customer_id"]),
            order_date=order_date,
            status=str(data.get("status", "created")),
        )
        for raw_line in data.get("lines", []):
            order.add_line(
                OrderLine(
                    sku=str(raw_line["sku"]),
                    quantity=int(raw_line["quantity"]),
                    unit_price=float(raw_line["unit_price"]),
                )
            )
        return order


def parse_order_date(value: str) -> date:
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date format: {value!r}")
