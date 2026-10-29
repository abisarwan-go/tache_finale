"""Unit tests for streaming parsers."""

from __future__ import annotations

import pytest

from pymart.exceptions import DataValidationError, RecordFormatError
from pymart.io.parsers import (
    iter_text_rows,
    parse_customer_row,
    parse_order_row,
    parse_product_row,
)


def test_iter_text_rows_skips_header_and_blank(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text(
        "sku|name|price|quantity\n\nNB-001|Notebook|3.49|10\n# comment\n",
        encoding="utf-8",
    )
    rows = list(iter_text_rows(path))
    assert len(rows) == 1
    line_no, fields = rows[0]
    assert line_no == 3
    assert fields[0] == "NB-001"


def test_parse_product_row_ok():
    raw = parse_product_row(
        ["nb-001", " notebook ", "3.49", "10", "standard", ""],
        source="p.txt",
        line=2,
    )
    assert raw["sku"] == "NB-001"
    assert raw["name"] == "Notebook"
    assert raw["price"] == 3.49
    assert raw["quantity"] == 10


def test_parse_product_row_rejects_bad_price():
    with pytest.raises(DataValidationError, match="invalid price"):
        parse_product_row(
            ["NB-001", "Notebook", "abc", "10"],
            source="p.txt",
            line=7,
        )


def test_parse_customer_row_requires_email_at():
    with pytest.raises(DataValidationError):
        parse_customer_row(
            ["C1", "Ada", "not-an-email", "0"],
            source="c.txt",
            line=1,
        )


def test_parse_order_row_requires_fields():
    with pytest.raises(RecordFormatError, match="expected at least 6"):
        parse_order_row(["1001", "C1"], source="o.txt", line=1)


def test_parse_order_row_ok():
    raw = parse_order_row(
        ["1001", "c1001", "2026-06-30", "nb-001", "2", "$3.49"],
        source="o.txt",
        line=2,
    )
    assert raw["customer_id"] == "C1001"
    assert raw["sku"] == "NB-001"
    assert raw["quantity"] == 2
    assert raw["unit_price"] == 3.49
