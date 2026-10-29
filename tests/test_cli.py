"""CLI integration tests (no subprocess required)."""

from __future__ import annotations

from pathlib import Path

from pymart.cli import main


def test_cli_help_exits_zero_via_status_after_import(
    tmp_path: Path, sample_files: dict[str, Path], capsys
):
    store = tmp_path / "cli_store.json"
    code = main(
        [
            "--store",
            str(store),
            "import",
            "--products",
            str(sample_files["products"]),
            "--customers",
            str(sample_files["customers"]),
            "--orders",
            str(sample_files["orders"]),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "Products imported=3 rejected=1" in out
    assert "Customers imported=2 rejected=1" in out
    assert "Order lines imported=3 rejected=1" in out

    code = main(["--store", str(store), "status"])
    assert code == 0
    status_out = capsys.readouterr().out
    assert "products : 3" in status_out
    assert "orders   : 3" in status_out


def test_cli_report_creates_files(tmp_path: Path, sample_files: dict[str, Path]):
    store = tmp_path / "cli_store.json"
    out = tmp_path / "out_reports"
    assert (
        main(
            [
                "--store",
                str(store),
                "import",
                "--products",
                str(sample_files["products"]),
                "--customers",
                str(sample_files["customers"]),
                "--orders",
                str(sample_files["orders"]),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "--store",
                str(store),
                "report",
                "--type",
                "daily",
                "--date",
                "2026-06-30",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "--store",
                str(store),
                "report",
                "--type",
                "monthly",
                "--month",
                "2026-06",
                "--out",
                str(out),
            ]
        )
        == 0
    )
    assert (out / "daily" / "2026-06-30" / "daily_sales_2026-06-30.txt").exists()
    assert (out / "monthly" / "2026-06" / "monthly_summary_2026-06.txt").exists()
    assert (out / "monthly" / "2026-06" / "stock_levels_2026-06.txt").exists()


def test_cli_order_unknown_sku_is_graceful(
    tmp_path: Path, sample_files: dict[str, Path], capsys
):
    store = tmp_path / "cli_store.json"
    main(
        [
            "--store",
            str(store),
            "import",
            "--products",
            str(sample_files["products"]),
            "--customers",
            str(sample_files["customers"]),
        ]
    )
    code = main(
        [
            "--store",
            str(store),
            "order",
            "create",
            "--id",
            "2002",
            "--customer",
            "C1001",
            "--sku",
            "NOPE",
            "--qty",
            "1",
        ]
    )
    assert code == 1
    err = capsys.readouterr().err
    assert "Order error:" in err
    assert "NOPE" in err
