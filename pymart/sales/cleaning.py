"""Clean messy PyMart sales records into typed [sku, name, qty, price] rows."""

from __future__ import annotations

EXPECTED_FIELDS = 4  # SKU, Name, Quantity, Price


def _strip_label(value: str, *labels: str) -> str:
    """Remove an optional leading label like 'qty:' or 'price:'."""
    cleaned = value.strip()
    lower = cleaned.lower()
    for label in labels:
        if lower.startswith(label):
            return cleaned[len(label) :].strip()
    return cleaned


def parse_quantity(raw: str) -> int:
    """Convert a qty field (e.g. 'qty: 03') to int."""
    text = _strip_label(raw, "qty:")
    return int(text)


def parse_price(raw: str) -> float:
    """Convert a price field (e.g. 'PRICE:$1,299.00') to float."""
    text = _strip_label(raw, "price:")
    text = text.replace("$", "").replace(",", "").strip()
    return float(text)


def clean_record(raw: str) -> list | None:
    """
    Split, strip, normalize, and convert one sales record.

    Returns [sku, name, qty, price] or None when the row should be skipped.
    """
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != EXPECTED_FIELDS:
        return None

    sku_raw, name_raw, qty_raw, price_raw = parts
    sku = sku_raw.strip().upper()
    name = " ".join(name_raw.strip().split()).title()

    try:
        qty = parse_quantity(qty_raw)
        price = parse_price(price_raw)
    except ValueError:
        return None

    return [sku, name, qty, price]


def clean_sales(raw_records: list[str]) -> list[list]:
    """Clean all records and return a list of typed rows."""
    cleaned: list[list] = []
    for record in raw_records:
        row = clean_record(record)
        if row is not None:
            cleaned.append(row)
    return cleaned
