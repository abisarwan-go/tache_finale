"""In-memory PyMart store with JSON persistence."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from pymart.exceptions import (
    DataValidationError,
    DuplicateIdError,
    InsufficientStockError,
    PyMartError,
    RecordFormatError,
    UnknownProductError,
)
from pymart.io.parsers import (
    iter_text_rows,
    parse_customer_row,
    parse_order_row,
    parse_product_row,
)
from pymart.models import Customer, ElectronicProduct, PerishableProduct, Product
from pymart.models.order import Order, OrderLine


class Store:
    def __init__(self, state_path: str | Path = ".pymart_store.json") -> None:
        self.state_path = Path(state_path)
        self.products: dict[str, Product] = {}
        self.customers: dict[str, Customer] = {}
        self.orders: dict[str, Order] = {}
        self.import_errors: list[str] = []

    def save(self) -> None:
        payload = {
            "products": [self._product_to_dict(p) for p in self.products.values()],
            "customers": [
                {
                    "customer_id": c.customer_id,
                    "name": c.name,
                    "email": c.email,
                    "loyalty_points": c.loyalty_points,
                }
                for c in self.customers.values()
            ],
            "orders": [o.to_dict() for o in self.orders.values()],
            "import_errors": self.import_errors,
        }
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.state_path.exists():
            return
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.products.clear()
        self.customers.clear()
        self.orders.clear()
        self.import_errors = list(payload.get("import_errors", []))

        for raw in payload.get("products", []):
            product = self._product_from_dict(raw)
            self.products[str(product.sku)] = product
        for raw in payload.get("customers", []):
            customer = Customer(
                customer_id=raw["customer_id"],
                name=raw["name"],
                email=raw["email"],
                loyalty_points=int(raw.get("loyalty_points", 0)),
            )
            self.customers[customer.customer_id] = customer
        for raw in payload.get("orders", []):
            order = Order.from_dict(raw)
            self.orders[order.order_id] = order

    @staticmethod
    def _product_to_dict(product: Product) -> dict[str, Any]:
        data: dict[str, Any] = {
            "sku": product.sku,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "kind": "standard",
        }
        if isinstance(product, PerishableProduct):
            data["kind"] = "perishable"
            data["extra"] = product.expiry_date.isoformat()
            data["storage_temp_c"] = product.storage_temp_c
        elif isinstance(product, ElectronicProduct):
            data["kind"] = "electronic"
            data["extra"] = str(product.warranty_months)
            data["power_watts"] = product.power_watts
        return data

    @staticmethod
    def _product_from_dict(raw: dict[str, Any]) -> Product:
        kind = raw.get("kind", "standard")
        sku = raw["sku"]
        name = raw["name"]
        price = float(raw["price"])
        quantity = int(raw["quantity"])
        extra = raw.get("extra", "")
        if kind == "perishable":
            return PerishableProduct(
                sku=sku,
                name=name,
                price=price,
                quantity=quantity,
                expiry_date=extra or "2099-12-31",
                storage_temp_c=raw.get("storage_temp_c"),
            )
        if kind == "electronic":
            months = int(extra) if str(extra).isdigit() else 12
            return ElectronicProduct(
                sku=sku,
                name=name,
                price=price,
                quantity=quantity,
                warranty_months=months,
                power_watts=raw.get("power_watts"),
            )
        return Product(sku=sku, name=name, price=price, quantity=quantity)

    def _build_product(self, raw: dict[str, Any]) -> Product:
        kind = raw["kind"]
        if kind == "perishable":
            return PerishableProduct(
                sku=raw["sku"],
                name=raw["name"],
                price=raw["price"],
                quantity=raw["quantity"],
                expiry_date=raw["extra"] or "2099-12-31",
            )
        if kind == "electronic":
            months = int(raw["extra"]) if str(raw["extra"]).isdigit() else 12
            return ElectronicProduct(
                sku=raw["sku"],
                name=raw["name"],
                price=raw["price"],
                quantity=raw["quantity"],
                warranty_months=months,
            )
        return Product(
            sku=raw["sku"],
            name=raw["name"],
            price=raw["price"],
            quantity=raw["quantity"],
        )

    def import_products(self, path: str | Path) -> tuple[int, int]:
        imported = 0
        rejected = 0
        source = str(path)
        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_product_row(fields, source=source, line=line_no)
                if raw["sku"] in self.products:
                    raise DuplicateIdError("product", raw["sku"])
                product = self._build_product(raw)
            except PyMartError as exc:
                rejected += 1
                self.import_errors.append(str(exc))
            else:
                self.products[str(product.sku)] = product
                imported += 1
        return imported, rejected

    def import_customers(self, path: str | Path) -> tuple[int, int]:
        imported = 0
        rejected = 0
        source = str(path)
        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_customer_row(fields, source=source, line=line_no)
                if raw["customer_id"] in self.customers:
                    raise DuplicateIdError("customer", raw["customer_id"])
                customer = Customer(
                    customer_id=raw["customer_id"],
                    name=raw["name"],
                    email=raw["email"],
                    loyalty_points=raw["loyalty_points"],
                )
            except PyMartError as exc:
                rejected += 1
                self.import_errors.append(str(exc))
            else:
                self.customers[customer.customer_id] = customer
                imported += 1
        return imported, rejected

    def import_orders(self, path: str | Path) -> tuple[int, int]:
        """Import order lines; groups by order_id into Order objects."""
        imported_lines = 0
        rejected = 0
        source = str(path)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for line_no, fields in iter_text_rows(path):
            try:
                raw = parse_order_row(fields, source=source, line=line_no)
                if raw["sku"] not in self.products:
                    raise UnknownProductError(
                        raw["sku"], source=source, line=line_no
                    )
                if raw["customer_id"] not in self.customers:
                    raise DataValidationError(
                        f"unknown customer_id '{raw['customer_id']}'",
                        source=source,
                        line=line_no,
                    )
                product = self.products[raw["sku"]]
                if raw["quantity"] > product.quantity:
                    raise InsufficientStockError(
                        raw["sku"], raw["quantity"], product.quantity
                    )
            except (
                RecordFormatError,
                DataValidationError,
                UnknownProductError,
                InsufficientStockError,
                DuplicateIdError,
            ) as exc:
                rejected += 1
                self.import_errors.append(str(exc))
            else:
                grouped[raw["order_id"]].append(raw)
                imported_lines += 1

        for order_id, rows in grouped.items():
            if order_id in self.orders:
                self.import_errors.append(
                    str(DuplicateIdError("order", order_id))
                )
                continue
            first = rows[0]
            order = Order(
                order_id=order_id,
                customer_id=first["customer_id"],
                order_date=date.fromisoformat(first["order_date"]),
                status="imported",
            )
            for raw in rows:
                product = self.products[raw["sku"]]
                product.sell(raw["quantity"])
                order.add_line(
                    OrderLine(
                        sku=raw["sku"],
                        quantity=raw["quantity"],
                        unit_price=raw["unit_price"],
                    )
                )
            self.orders[order_id] = order

        return imported_lines, rejected

    def create_order(
        self,
        order_id: str,
        customer_id: str,
        sku: str,
        quantity: int,
        order_date: date | None = None,
    ) -> Order:
        if order_id in self.orders:
            raise DuplicateIdError("order", order_id)
        if customer_id not in self.customers:
            raise DataValidationError(f"unknown customer_id '{customer_id}'")
        if sku not in self.products:
            raise UnknownProductError(sku)

        product = self.products[sku]
        product.sell(quantity)
        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            order_date=order_date or date.today(),
            status="created",
        )
        order.add_line(
            OrderLine(sku=sku, quantity=quantity, unit_price=product.price)
        )
        self.orders[order_id] = order
        return order

    def list_orders(self) -> list[Order]:
        return sorted(self.orders.values(), key=lambda o: (o.order_date, o.order_id))

    def iter_orders_for_date(self, day: date):
        """Generator: yield orders matching a calendar day."""
        for order in self.list_orders():
            if order.order_date == day:
                yield order

    def iter_orders_for_month(self, year: int, month: int):
        """Generator: yield orders in a calendar month."""
        for order in self.list_orders():
            if order.order_date.year == year and order.order_date.month == month:
                yield order
