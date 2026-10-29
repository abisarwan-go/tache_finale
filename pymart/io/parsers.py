"""Streaming parsers for PyMart CSV-like text extracts."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pymart.exceptions import DataValidationError, RecordFormatError
from pymart.models.order import parse_order_date


def iter_text_rows(path: str | Path) -> Iterator[tuple[int, list[str]]]:
    """Yield (line_number, fields) for non-empty rows. Skips header-like first row."""
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as handle:
            first_data_seen = False
            for line_no, raw in enumerate(handle, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                fields = [part.strip() for part in line.split("|")]
                # Skip a header row when the first field looks non-numeric/non-sku-ish.
                if not first_data_seen and fields and fields[0].lower() in {
                    "sku",
                    "customer_id",
                    "order_id",
                    "id",
                }:
                    first_data_seen = True
                    continue
                first_data_seen = True
                yield line_no, fields
    except OSError as exc:
        raise RecordFormatError(
            f"cannot read file: {exc}", source=str(source)
        ) from exc


def _require_fields(
    fields: list[str], count: int, *, source: str, line: int
) -> None:
    if len(fields) < count:
        raise RecordFormatError(
            f"expected at least {count} fields, got {len(fields)}",
            source=source,
            line=line,
        )


def parse_product_row(
    fields: list[str], *, source: str, line: int
) -> dict[str, Any]:
    """sku|name|price|quantity|kind|extra

    kind: standard|perishable|electronic
    extra: expiry ISO date OR warranty_months
    """
    _require_fields(fields, 4, source=source, line=line)
    sku, name, price_raw, qty_raw = fields[:4]
    kind = fields[4].lower() if len(fields) > 4 and fields[4] else "standard"
    extra = fields[5] if len(fields) > 5 else ""

    if not sku:
        raise DataValidationError("missing sku", source=source, line=line)
    if not name:
        raise DataValidationError("missing name", source=source, line=line)

    try:
        price = float(price_raw.replace("$", "").replace(",", ""))
        quantity = int(float(qty_raw))
    except ValueError as exc:
        raise DataValidationError(
            f"invalid price/quantity: {price_raw!r}, {qty_raw!r}",
            source=source,
            line=line,
        ) from exc

    if price < 0 or quantity < 0:
        raise DataValidationError(
            "price and quantity must be non-negative",
            source=source,
            line=line,
        )

    return {
        "sku": sku.upper(),
        "name": " ".join(name.split()).title(),
        "price": round(price, 2),
        "quantity": quantity,
        "kind": kind,
        "extra": extra.strip(),
    }


def parse_customer_row(
    fields: list[str], *, source: str, line: int
) -> dict[str, Any]:
    """customer_id|name|email|loyalty_points"""
    _require_fields(fields, 3, source=source, line=line)
    customer_id, name, email = fields[:3]
    points_raw = fields[3] if len(fields) > 3 and fields[3] else "0"

    if not customer_id or not name or "@" not in email:
        raise DataValidationError(
            "customer_id, name, and email(@) are required",
            source=source,
            line=line,
        )
    try:
        points = int(points_raw)
    except ValueError as exc:
        raise DataValidationError(
            f"invalid loyalty_points: {points_raw!r}",
            source=source,
            line=line,
        ) from exc
    if points < 0:
        raise DataValidationError(
            "loyalty_points must be >= 0", source=source, line=line
        )

    return {
        "customer_id": customer_id.strip().upper(),
        "name": " ".join(name.split()).title(),
        "email": email.strip().lower(),
        "loyalty_points": points,
    }


def parse_order_row(
    fields: list[str], *, source: str, line: int
) -> dict[str, Any]:
    """order_id|customer_id|order_date|sku|quantity|unit_price"""
    _require_fields(fields, 6, source=source, line=line)
    order_id, customer_id, date_raw, sku, qty_raw, price_raw = fields[:6]

    if not order_id or not customer_id or not sku:
        raise DataValidationError(
            "order_id, customer_id, and sku are required",
            source=source,
            line=line,
        )
    try:
        order_date = parse_order_date(date_raw)
        quantity = int(qty_raw)
        unit_price = float(price_raw.replace("$", "").replace(",", ""))
    except ValueError as exc:
        raise DataValidationError(
            f"invalid date/qty/price on order: {exc}",
            source=source,
            line=line,
        ) from exc

    if quantity <= 0:
        raise DataValidationError(
            "order quantity must be > 0", source=source, line=line
        )
    if unit_price < 0:
        raise DataValidationError(
            "unit_price must be >= 0", source=source, line=line
        )

    return {
        "order_id": order_id.strip(),
        "customer_id": customer_id.strip().upper(),
        "order_date": order_date.isoformat(),
        "sku": sku.strip().upper(),
        "quantity": quantity,
        "unit_price": round(unit_price, 2),
    }
