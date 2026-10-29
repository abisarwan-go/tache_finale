"""Streaming sales record cleaning and threshold filters."""

from __future__ import annotations

import csv
import io
import random
import re
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable, Iterator

Record = dict[str, Any]

HEADER = (
    "order_id,timestamp,store_id,cashier_id,sku,qty,unit_price,"
    "discount,total,payment_method,customer_id,notes"
)

EMPTY_MARKERS = {"", "n/a", "na", "null", "none", "-"}

PAYMENT_MAP = {
    "credit": "card",
    "credit card": "card",
    "card": "card",
    "debit": "card",
    "cash": "cash",
    "mobile": "mobile",
    "apple pay": "mobile",
    "google pay": "mobile",
}


def build_sales_dataset(size: int = 500, seed: int = 42) -> list[str]:
    """Build a large messy in-memory CSV-like sales dataset (header + rows)."""
    rng = random.Random(seed)
    lines = [HEADER]

    # Keep the lab's hand-written messy examples first.
    lines.extend(
        [
            '1000042, 2026-06-14 09:03:12 , S-007 , C-19, SKU-00421 , 2 , $19.99 , 10% , $35.98 , Credit Card , , " first-time buyer "',
            '1000043,2026-06-14T09:04:01Z,S-007,C-19,SKU-00017,1,"USD 1,299.00",,1299.00,CARD,CUST-8812,',
            '1000044, 2026/06/14 09:04:41, S-012, C-03, SKU-01000, two, $3.50, $0.00, $3.50, cash , CUST-1044, ""',
        ]
    )

    start = datetime(2026, 6, 14, 9, 5, 0)
    for i in range(size - 3):
        order_id = 1000045 + i
        ts = start + timedelta(seconds=i * 17)
        store = f"S-{rng.choice(['007', '012', '003', '021'])}"
        cashier = f"C-{rng.randint(1, 30):02d}"
        sku = f"SKU-{rng.randint(1, 9999):05d}"
        qty = rng.choice([1, 2, 3, 5, "2.0", "two", " 4 "])
        price = rng.choice([9.99, 19.99, 49.5, 1299.0, 3.5, 250.0, 75.25])
        discount = rng.choice(["10%", "0.10", "$1.00", "", "0%", "25%"])
        payment = rng.choice(
            ["credit", "Credit Card", "CARD", "cash", "CASH", "mobile", "Apple Pay"]
        )
        customer = rng.choice(["", "N/A", f"CUST-{rng.randint(1000, 9999)}", "null"])
        notes = rng.choice(["", " pickup ", '""', "first-time buyer", "N/A"])

        # Intentionally messy money formatting.
        price_text = rng.choice(
            [
                f"${price:,.2f}",
                f"USD {price:,.2f}",
                f" {price} ",
                f"{price:.2f}",
            ]
        )
        total = float(price) * (int(qty) if str(qty).isdigit() else 1)
        total_text = rng.choice([f"${total:,.2f}", f"{total:.2f}", f" {total} "])

        ts_text = rng.choice(
            [
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                ts.strftime("%Y/%m/%d %H:%M:%S"),
                f" {ts.strftime('%Y-%m-%d %H:%M:%S')} ",
            ]
        )

        # Quote notes when they may contain spaces.
        notes_field = f'"{notes}"' if notes else ""
        line = (
            f"{order_id}, {ts_text} , {store} , {cashier}, {sku} , {qty} , "
            f"{price_text} , {discount} , {total_text} , {payment} , {customer}, "
            f"{notes_field}"
        )
        lines.append(line)

    return lines


def _blank_to_none(value: str) -> str | None:
    cleaned = value.strip().strip('"').strip()
    if cleaned.lower() in EMPTY_MARKERS:
        return None
    return cleaned


def _parse_money(value: str) -> float:
    text = value.strip().strip('"')
    if not text or text.lower() in EMPTY_MARKERS:
        return 0.0
    text = re.sub(r"(?i)^usd\s*", "", text)
    text = text.replace("$", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def _parse_qty(value: str) -> int:
    text = value.strip().strip('"').lower()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    if text in words:
        return words[text]
    try:
        return int(float(text))
    except ValueError:
        return 0


def _parse_discount_rate(value: str, unit_price: float) -> float:
    text = value.strip().strip('"')
    if not text or text.lower() in EMPTY_MARKERS:
        return 0.0
    if text.endswith("%"):
        try:
            return max(0.0, min(1.0, float(text[:-1].strip()) / 100.0))
        except ValueError:
            return 0.0
    if text.startswith("$"):
        amount = _parse_money(text)
        if unit_price <= 0:
            return 0.0
        return max(0.0, min(1.0, amount / unit_price))
    try:
        rate = float(text.replace(",", ""))
    except ValueError:
        return 0.0
    if rate > 1:
        rate = rate / 100.0
    return max(0.0, min(1.0, rate))


def _normalize_payment(value: str) -> str:
    text = value.strip().strip('"').lower()
    if not text or text in EMPTY_MARKERS:
        return "other"
    return PAYMENT_MAP.get(text, "other")


def _normalize_timestamp(value: str) -> str:
    text = value.strip().strip('"')
    if not text:
        return ""
    text = text.replace("Z", "")
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return text


def _clean_row(fields: list[str]) -> Record | None:
    if len(fields) < 11:
        return None

    # Pad optional trailing notes.
    while len(fields) < 12:
        fields.append("")

    order_raw = fields[0].strip()
    try:
        order_id = int(order_raw)
    except ValueError:
        return None

    unit_price = _parse_money(fields[6])
    discount_rate = _parse_discount_rate(fields[7], unit_price)
    total = _parse_money(fields[8])
    if total == 0.0 and unit_price > 0:
        qty = _parse_qty(fields[5])
        total = round(unit_price * qty * (1 - discount_rate), 2)

    return {
        "order_id": order_id,
        "timestamp": _normalize_timestamp(fields[1]),
        "store_id": fields[2].strip(),
        "cashier_id": fields[3].strip(),
        "sku": fields[4].strip(),
        "qty": _parse_qty(fields[5]),
        "unit_price": unit_price,
        "discount_rate": discount_rate,
        "total": total,
        "payment_method": _normalize_payment(fields[9]),
        "customer_id": _blank_to_none(fields[10]),
        "notes": _blank_to_none(fields[11]),
    }


def read_sales_records(data: Iterable[str]) -> Iterator[Record]:
    """Yield one cleaned sales record at a time from CSV-like text lines."""
    # Materialize a thin csv reader over the iterable without building records.
    reader = csv.reader(data)
    for index, row in enumerate(reader):
        if not row:
            continue
        if index == 0 and row and row[0].strip().lower() == "order_id":
            continue
        cleaned = _clean_row(row)
        if cleaned is not None:
            yield cleaned


def make_threshold_filter(
    min_amount: float | None = None,
    *,
    min_total: float | None = None,
) -> Callable[[Record], bool]:
    """Return a keep(record) closure for high-value sales filtering."""
    threshold = min_total if min_total is not None else min_amount
    if threshold is None:
        raise ValueError("min_amount or min_total is required")

    def keep(record: Record) -> bool:
        total = record.get("total", record.get("amount", 0.0))
        try:
            return float(total) >= threshold
        except (TypeError, ValueError):
            return False

    return keep


def dataset_as_text(lines: list[str]) -> str:
    """Join dataset lines for file-like consumers."""
    return "\n".join(lines)


def iter_dataset_file(text: str) -> Iterator[str]:
    """Yield lines from an in-memory text blob (simulates a file iterator)."""
    yield from io.StringIO(text)
