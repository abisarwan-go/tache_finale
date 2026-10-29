"""PyMart back-office CLI: import, orders, and reports."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from pymart.exceptions import PyMartError
from pymart.reports.writers import write_daily_report, write_monthly_report
from pymart.services.store import Store


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_month(value: str) -> tuple[int, int]:
    parsed = datetime.strptime(value, "%Y-%m")
    return parsed.year, parsed.month


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pymart.cli",
        description="PyMart back-office toolkit",
    )
    parser.add_argument(
        "--store",
        default=".pymart_store.json",
        help="Path to persisted store JSON (default: .pymart_store.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    import_p = sub.add_parser("import", help="Import products/customers/orders")
    import_p.add_argument("--products", help="Products text file")
    import_p.add_argument("--customers", help="Customers text file")
    import_p.add_argument("--orders", help="Orders text file")

    order_p = sub.add_parser("order", help="Create or list orders")
    order_sub = order_p.add_subparsers(dest="order_command", required=True)
    create_p = order_sub.add_parser("create", help="Create one order line")
    create_p.add_argument("--id", required=True, help="Order id")
    create_p.add_argument("--customer", required=True, help="Customer id")
    create_p.add_argument("--sku", required=True, help="Product SKU")
    create_p.add_argument("--qty", required=True, type=int, help="Quantity")
    create_p.add_argument(
        "--date",
        default=None,
        help="Order date YYYY-MM-DD (default: today)",
    )
    order_sub.add_parser("list", help="List orders")

    report_p = sub.add_parser("report", help="Generate dated reports")
    report_p.add_argument(
        "--type",
        required=True,
        choices=["daily", "monthly"],
        dest="report_type",
    )
    report_p.add_argument("--date", help="Daily report date YYYY-MM-DD")
    report_p.add_argument("--month", help="Monthly report period YYYY-MM")
    report_p.add_argument(
        "--out",
        default="reports/",
        help="Output directory (default: reports/)",
    )

    sub.add_parser("status", help="Show store summary (products/customers/orders)")

    return parser


def cmd_import(store: Store, args: argparse.Namespace) -> int:
    if not any([args.products, args.customers, args.orders]):
        print(
            "Error: provide at least one of --products/--customers/--orders",
            file=sys.stderr,
        )
        return 2

    try:
        if args.products:
            ok, bad = store.import_products(args.products)
            print(f"Products imported={ok} rejected={bad}")
        if args.customers:
            ok, bad = store.import_customers(args.customers)
            print(f"Customers imported={ok} rejected={bad}")
        if args.orders:
            ok, bad = store.import_orders(args.orders)
            print(f"Order lines imported={ok} rejected={bad}")
        store.save()
    except PyMartError as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"I/O error during import: {exc}", file=sys.stderr)
        return 1

    if store.import_errors:
        print("Recent validation messages:")
        for message in store.import_errors[-10:]:
            print(f"  - {message}")
    return 0


def cmd_order(store: Store, args: argparse.Namespace) -> int:
    try:
        if args.order_command == "list":
            orders = store.list_orders()
            if not orders:
                print("No orders.")
                return 0
            for order in orders:
                print(order.describe())
            return 0

        order_date = _parse_date(args.date) if args.date else date.today()
        order = store.create_order(
            order_id=args.id,
            customer_id=args.customer.upper(),
            sku=args.sku.upper(),
            quantity=args.qty,
            order_date=order_date,
        )
        store.save()
        print("Created:", order.describe())
        return 0
    except PyMartError as exc:
        print(f"Order error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Invalid argument: {exc}", file=sys.stderr)
        return 2


def cmd_report(store: Store, args: argparse.Namespace) -> int:
    try:
        if args.report_type == "daily":
            if not args.date:
                print("Error: --date YYYY-MM-DD is required for daily", file=sys.stderr)
                return 2
            day = _parse_date(args.date)
            path = write_daily_report(store, report_date=day, out_dir=args.out)
            print(f"Wrote daily report: {path}")
            return 0

        if not args.month:
            print("Error: --month YYYY-MM is required for monthly", file=sys.stderr)
            return 2
        year, month = _parse_month(args.month)
        path = write_monthly_report(
            store, year=year, month=month, out_dir=args.out
        )
        print(f"Wrote monthly report: {path}")
        stock = path.parent / f"stock_levels_{year:04d}-{month:02d}.txt"
        if stock.exists():
            print(f"Wrote stock report: {stock}")
        return 0
    except PyMartError as exc:
        print(f"Report error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Invalid date/month: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"I/O error writing report: {exc}", file=sys.stderr)
        return 1


def cmd_status(store: Store, _args: argparse.Namespace) -> int:
    print("PyMart store status")
    print(f"  products : {len(store.products)}")
    print(f"  customers: {len(store.customers)}")
    print(f"  orders   : {len(store.orders)}")
    print(f"  import errors logged: {len(store.import_errors)}")
    if store.products:
        print("  catalog:")
        for product in list(store.products.values())[:5]:
            print(f"    - {product.describe()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = Store(state_path=args.store)
    store.load()

    if args.command == "import":
        return cmd_import(store, args)
    if args.command == "order":
        return cmd_order(store, args)
    if args.command == "report":
        return cmd_report(store, args)
    if args.command == "status":
        return cmd_status(store, args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
