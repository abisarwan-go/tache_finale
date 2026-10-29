"""Dated operational report writers for PyMart."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from pymart.services.store import Store


def _ensure_archive_dirs(out_dir: Path, day: date) -> Path:
    day_dir = out_dir / "daily" / day.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    return day_dir


def write_daily_report(
    store: Store,
    *,
    report_date: date,
    out_dir: str | Path = "reports",
) -> Path:
    out = Path(out_dir)
    day_dir = _ensure_archive_dirs(out, report_date)
    filename = f"daily_sales_{report_date.isoformat()}.txt"
    path = day_dir / filename

    orders = list(store.iter_orders_for_date(report_date))
    revenue = round(sum(order.total for order in orders), 2)
    next_review = report_date + timedelta(days=30)

    lines = [
        "PyMart Daily Sales Summary",
        "==========================",
        f"Report date: {report_date.isoformat()}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"Next review date: {next_review.isoformat()}",
        f"Orders: {len(orders)}",
        f"Revenue: ${revenue:.2f}",
        "",
        "Order details:",
    ]
    if not orders:
        lines.append("  (no orders)")
    else:
        for order in orders:
            lines.append(f"  - {order.describe()}")
            for line in order.lines:
                lines.append(f"      • {line.describe()}")

    lines.extend(
        [
            "",
            "Catalog snapshot (polymorphic describe):",
        ]
    )
    for product in store.products.values():
        lines.append(f"  - {product.describe()}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_monthly_report(
    store: Store,
    *,
    year: int,
    month: int,
    out_dir: str | Path = "reports",
) -> Path:
    out = Path(out_dir)
    month_key = f"{year:04d}-{month:02d}"
    month_dir = out / "monthly" / month_key
    month_dir.mkdir(parents=True, exist_ok=True)
    path = month_dir / f"monthly_summary_{month_key}.txt"

    orders = list(store.iter_orders_for_month(year, month))
    revenue = round(sum(order.total for order in orders), 2)

    by_sku: dict[str, int] = defaultdict(int)
    by_customer: dict[str, float] = defaultdict(float)
    for order in orders:
        by_customer[order.customer_id] += order.total
        for line in order.lines:
            by_sku[line.sku] += line.quantity

    top_skus = sorted(by_sku.items(), key=lambda item: item[1], reverse=True)[:5]
    top_customers = sorted(
        by_customer.items(), key=lambda item: item[1], reverse=True
    )[:5]

    _weekday, last_day = calendar.monthrange(year, month)
    month_calendar = calendar.month(year, month)
    is_leap = calendar.isleap(year)

    lines = [
        "PyMart Monthly Summary",
        "======================",
        f"Period: {month_key} (days 1–{last_day})",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"Leap year: {is_leap}",
        f"Orders: {len(orders)}",
        f"Revenue: ${revenue:.2f}",
        "",
        "Top-selling products:",
    ]
    if not top_skus:
        lines.append("  (none)")
    else:
        for sku, qty in top_skus:
            lines.append(f"  - {sku}: {qty} units")

    lines.append("")
    lines.append("Top customers by spend:")
    if not top_customers:
        lines.append("  (none)")
    else:
        for customer_id, spend in top_customers:
            name = store.customers.get(customer_id)
            label = name.name if name else customer_id
            lines.append(f"  - {label} ({customer_id}): ${spend:.2f}")

    lines.extend(
        [
            "",
            "Failed/rejected import messages:",
        ]
    )
    if not store.import_errors:
        lines.append("  (none)")
    else:
        for err in store.import_errors[-20:]:
            lines.append(f"  - {err}")

    lines.extend(["", "Month calendar:", month_calendar.rstrip("\n"), ""])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Also keep a stock level report alongside monthly outputs.
    stock_path = month_dir / f"stock_levels_{month_key}.txt"
    stock_lines = [
        "PyMart Stock Level Report",
        "=========================",
        f"As of period: {month_key}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    for product in sorted(store.products.values(), key=lambda p: str(p.sku)):
        stock_lines.append(
            f"{product.sku:<12} qty={product.quantity:<5} "
            f"price=${product.price:<8.2f} {product.describe()}"
        )
    stock_path.write_text("\n".join(stock_lines) + "\n", encoding="utf-8")

    return path
