"""Robust order import with targeted exception handling."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .exceptions import ValidationError

EXPECTED_FIELDS = 4  # order_id|sku|quantity|unit_price

logger = logging.getLogger("pymart.orders.import")


@dataclass
class ImportSummary:
    total: int = 0
    imported: int = 0
    rejected: int = 0
    failed: int = 0
    warnings: int = 0
    orders: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


def parse_order_line(line: str) -> dict[str, Any]:
    """Parse and validate one pipe-delimited order line.

    Raises:
        ValidationError: expected data problems ([PARSE] or [VALIDATION]).
    """
    raw = line.strip()
    if not raw:
        raise ValidationError("[PARSE] empty row")

    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != EXPECTED_FIELDS:
        raise ValidationError(
            f"[PARSE] expected {EXPECTED_FIELDS} fields, got {len(parts)}"
        )

    order_id_raw, sku, quantity_raw, unit_price_raw = parts

    if not order_id_raw:
        raise ValidationError("[VALIDATION] missing required field: order_id")
    if not sku:
        raise ValidationError("[VALIDATION] missing required field: sku")

    try:
        order_id = int(order_id_raw)
    except ValueError as exc:
        raise ValidationError(
            f"[PARSE] order_id is not an integer: {order_id_raw!r}"
        ) from exc

    try:
        quantity = int(quantity_raw)
    except ValueError as exc:
        raise ValidationError(
            f"[PARSE] quantity is not an integer: {quantity_raw!r}"
        ) from exc

    try:
        unit_price = float(unit_price_raw)
    except ValueError as exc:
        raise ValidationError(
            f"[PARSE] unit_price is not a float: {unit_price_raw!r}"
        ) from exc

    if quantity <= 0:
        raise ValidationError(
            f"[VALIDATION] quantity must be > 0, got {quantity}"
        )
    if unit_price < 0:
        raise ValidationError(
            f"[VALIDATION] unit_price must be >= 0, got {unit_price}"
        )

    return {
        "order_id": order_id,
        "sku": sku,
        "quantity": quantity,
        "unit_price": unit_price,
        "line_total": round(quantity * unit_price, 2),
    }


def import_orders(raw_lines: list[str]) -> ImportSummary:
    """Import orders from raw text lines without crashing the whole run."""
    summary = ImportSummary()
    logger.info("import.start")

    try:
        for index, line in enumerate(raw_lines, start=1):
            summary.total += 1
            status = "ERROR"
            order_id: int | None = None

            try:
                order = parse_order_line(line)
            except ValidationError as exc:
                summary.rejected += 1
                message = str(exc)
                category = (
                    "VALIDATION" if "[VALIDATION]" in message else "PARSE"
                )
                summary.errors.append(
                    {
                        "row": index,
                        "kind": "rejected",
                        "category": category,
                        "message": message,
                        "hint": "Fix the row values and re-run import.",
                        "row_data": line,
                    }
                )
                status = "REJECTED"
                logger.warning(
                    "import.row.rejected row=%s error=%s", index, message
                )
            except Exception as exc:
                summary.failed += 1
                summary.errors.append(
                    {
                        "row": index,
                        "kind": "failed",
                        "category": "UNEXPECTED",
                        "message": (
                            f"Unexpected error: {type(exc).__name__}: {exc}"
                        ),
                        "hint": (
                            "Check logs/traceback and fix code or dependency. "
                            "Row was skipped."
                        ),
                        "row_data": line,
                    }
                )
                status = "ERROR"
                logger.exception("import.row.failed row=%s", index)
            else:
                summary.imported += 1
                summary.orders.append(order)
                order_id = order["order_id"]
                status = "IMPORTED"
                logger.info(
                    "import.row.imported row=%s order_id=%s",
                    index,
                    order_id,
                )
            finally:
                logger.info(
                    "import.row.processed row=%s status=%s", index, status
                )
    finally:
        logger.info(
            "import.complete total=%s imported=%s rejected=%s failed=%s",
            summary.total,
            summary.imported,
            summary.rejected,
            summary.failed,
        )

    return summary
