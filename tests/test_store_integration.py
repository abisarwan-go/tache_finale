"""Integration tests for Store import/order/persistence flow."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from pymart.exceptions import DuplicateIdError, UnknownProductError
from pymart.models import PerishableProduct
from pymart.services.store import Store


def test_import_sample_files_counts(tmp_store: Store, sample_files: dict[str, Path]):
    p_ok, p_bad = tmp_store.import_products(sample_files["products"])
    c_ok, c_bad = tmp_store.import_customers(sample_files["customers"])
    o_ok, o_bad = tmp_store.import_orders(sample_files["orders"])

    assert (p_ok, p_bad) == (3, 1)
    assert (c_ok, c_bad) == (2, 1)
    assert (o_ok, o_bad) == (3, 1)
    assert "NB-001" in tmp_store.products
    assert isinstance(tmp_store.products["ML-001"], PerishableProduct)
    assert "1001" in tmp_store.orders
    assert tmp_store.products["NB-001"].quantity == 18  # 20 - 2


def test_store_save_and_load_roundtrip(tmp_store: Store, sample_files: dict[str, Path]):
    tmp_store.import_products(sample_files["products"])
    tmp_store.import_customers(sample_files["customers"])
    tmp_store.import_orders(sample_files["orders"])
    tmp_store.save()

    restored = Store(state_path=tmp_store.state_path)
    restored.load()
    assert set(restored.products) == set(tmp_store.products)
    assert set(restored.customers) == set(tmp_store.customers)
    assert set(restored.orders) == set(tmp_store.orders)
    assert restored.orders["1001"].total == tmp_store.orders["1001"].total


def test_create_order_and_list(seeded_store: Store):
    order = seeded_store.create_order(
        order_id="2001",
        customer_id="C1001",
        sku="NB-001",
        quantity=1,
        order_date=date(2026, 6, 30),
    )
    assert order.total == 3.49
    assert seeded_store.products["NB-001"].quantity == 19
    assert len(seeded_store.list_orders()) == 1


def test_create_order_unknown_sku(seeded_store: Store):
    with pytest.raises(UnknownProductError):
        seeded_store.create_order(
            order_id="2002",
            customer_id="C1001",
            sku="NOPE",
            quantity=1,
        )


def test_create_order_duplicate_id(seeded_store: Store):
    seeded_store.create_order(
        order_id="2001",
        customer_id="C1001",
        sku="NB-001",
        quantity=1,
    )
    with pytest.raises(DuplicateIdError):
        seeded_store.create_order(
            order_id="2001",
            customer_id="C1001",
            sku="NB-001",
            quantity=1,
        )


def test_iter_orders_for_date_generator(tmp_store: Store, sample_files: dict[str, Path]):
    tmp_store.import_products(sample_files["products"])
    tmp_store.import_customers(sample_files["customers"])
    tmp_store.import_orders(sample_files["orders"])

    day = date(2026, 6, 30)
    orders = list(tmp_store.iter_orders_for_date(day))
    assert {o.order_id for o in orders} == {"1001", "1002"}
