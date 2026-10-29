"""Shared fixtures for PyMart integrated tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from pymart.models import Customer, Product
from pymart.models.product import Product as ProductCls
from pymart.services.store import Store


@pytest.fixture(autouse=True)
def _reset_product_counter() -> None:
    ProductCls.reset_counter()
    yield
    ProductCls.reset_counter()


@pytest.fixture
def tmp_store(tmp_path: Path) -> Store:
    return Store(state_path=tmp_path / "store.json")


@pytest.fixture
def sample_files(tmp_path: Path) -> dict[str, Path]:
    products = tmp_path / "products.txt"
    customers = tmp_path / "customers.txt"
    orders = tmp_path / "orders.txt"

    products.write_text(
        "\n".join(
            [
                "sku|name|price|quantity|kind|extra",
                "NB-001|Notebook|3.49|20|standard|",
                "ML-001|Milk|2.50|10|perishable|2099-01-01",
                "HP-200|Headphones|79.99|5|electronic|24",
                "BAD|Broken|abc|1|standard|",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    customers.write_text(
        "\n".join(
            [
                "customer_id|name|email|loyalty_points",
                "C1001|Aisha Khan|aisha@example.com|20",
                "C1002|Miguel Rivera|miguel@example.com|0",
                "C1003|Bad|not-an-email|1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    orders.write_text(
        "\n".join(
            [
                "order_id|customer_id|order_date|sku|quantity|unit_price",
                "1001|C1001|2026-06-30|NB-001|2|3.49",
                "1002|C1002|2026-06-30|HP-200|1|79.99",
                "1003|C1001|2026-06-15|ML-001|1|2.50",
                "1004|C1001|2026-06-30|UNKNOWN|1|9.99",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"products": products, "customers": customers, "orders": orders}


@pytest.fixture
def seeded_store(tmp_store: Store) -> Store:
    tmp_store.products["NB-001"] = Product(
        sku="NB-001", name="Notebook", price=3.49, quantity=20
    )
    tmp_store.customers["C1001"] = Customer(
        customer_id="C1001",
        name="Aisha Khan",
        email="aisha@example.com",
        loyalty_points=20,
    )
    return tmp_store
