"""Unit tests for domain models and polymorphism."""

from __future__ import annotations

from datetime import date

import pytest

from pymart.exceptions import InsufficientStockError, InvalidDiscountError
from pymart.models import (
    Customer,
    ElectronicProduct,
    Order,
    OrderLine,
    PerishableProduct,
    Product,
)


def test_product_sell_and_discount():
    product = Product(sku="NB-001", name="Notebook", price=10.0, quantity=5)
    assert product.sell(2) == 3
    assert product.apply_discount(10) == 9.0


def test_product_sell_insufficient_stock():
    product = Product(sku="NB-001", name="Notebook", price=10.0, quantity=1)
    with pytest.raises(InsufficientStockError) as exc:
        product.sell(3)
    assert exc.value.available_stock == 1
    assert exc.value.requested_qty == 3


def test_product_invalid_discount():
    product = Product(sku="NB-001", name="Notebook", price=10.0, quantity=1)
    with pytest.raises(InvalidDiscountError):
        product.apply_discount(-5)


def test_polymorphic_describe():
    items = [
        Product(sku="G1", name="Gift", price=25.0, quantity=1),
        PerishableProduct(
            sku="M1",
            name="Milk",
            price=3.0,
            quantity=2,
            expiry_date="2099-08-01",
            storage_temp_c=4,
        ),
        ElectronicProduct(
            sku="H1",
            name="Headphones",
            price=80.0,
            quantity=1,
            warranty_months=24,
            power_watts=5,
        ),
    ]
    texts = [item.describe() for item in items]
    assert "G1 | Gift | $25.00" in texts[0]
    assert "expires: 2099-08-01" in texts[1]
    assert "warranty: 24 months" in texts[2]


def test_customer_email_property_rejects_invalid():
    customer = Customer(
        customer_id="C1", name="Ada", email="ada@example.com", loyalty_points=0
    )
    with pytest.raises(ValueError, match="Invalid email"):
        customer.email = "bad-email"


def test_order_total():
    order = Order(
        order_id="1001",
        customer_id="C1001",
        order_date=date(2026, 6, 30),
    )
    order.add_line(OrderLine(sku="NB-001", quantity=2, unit_price=3.49))
    order.add_line(OrderLine(sku="PN-101", quantity=1, unit_price=5.99))
    assert order.total == 12.97
