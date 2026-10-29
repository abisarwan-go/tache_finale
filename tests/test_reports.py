"""Integration tests for dated report writers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pymart.reports.writers import write_daily_report, write_monthly_report
from pymart.services.store import Store


def test_daily_and_monthly_reports_written(
    tmp_store: Store, sample_files: dict[str, Path], tmp_path: Path
):
    tmp_store.import_products(sample_files["products"])
    tmp_store.import_customers(sample_files["customers"])
    tmp_store.import_orders(sample_files["orders"])

    out = tmp_path / "reports"
    daily = write_daily_report(
        tmp_store, report_date=date(2026, 6, 30), out_dir=out
    )
    monthly = write_monthly_report(
        tmp_store, year=2026, month=6, out_dir=out
    )
    stock = monthly.parent / "stock_levels_2026-06.txt"

    assert daily.exists()
    assert monthly.exists()
    assert stock.exists()
    assert "2026-06-30" in daily.as_posix()
    assert "2026-06" in monthly.as_posix()

    daily_text = daily.read_text(encoding="utf-8")
    assert "PyMart Daily Sales Summary" in daily_text
    assert "Revenue:" in daily_text
    assert "NB-001" in daily_text or "HP-200" in daily_text

    monthly_text = monthly.read_text(encoding="utf-8")
    assert "PyMart Monthly Summary" in monthly_text
    assert "Top-selling products" in monthly_text
