#!/usr/bin/env bash
# Regenerate terminal captures + report copies for the evidence pack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY=python3
fi

CAP="${ROOT}/preuves/captures"
RAP="${ROOT}/preuves/rapports"
mkdir -p "$CAP" "$RAP"
rm -f .pymart_store.json

"$PY" -m pymart.cli --help > "$CAP/01_cli_help.txt" 2>&1

"$PY" -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt \
  > "$CAP/02_import_success.txt" 2>&1

"$PY" -m pymart.cli status > "$CAP/03_status.txt" 2>&1

"$PY" -m pymart.cli report --type daily --date 2026-06-30 --out reports/ \
  > "$CAP/04_report_daily.txt" 2>&1

"$PY" -m pymart.cli report --type monthly --month 2026-06 --out reports/ \
  > "$CAP/05_report_monthly.txt" 2>&1

set +e
"$PY" -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1 \
  > "$CAP/06_validation_error.txt" 2>&1
echo "exit:$?" >> "$CAP/06_validation_error.txt"
set -e

cp -f reports/daily/2026-06-30/daily_sales_2026-06-30.txt "$RAP/"
cp -f reports/monthly/2026-06/monthly_summary_2026-06.txt "$RAP/"
cp -f reports/monthly/2026-06/stock_levels_2026-06.txt "$RAP/"

echo "OK — captures in preuves/captures/ and reports in preuves/rapports/"
