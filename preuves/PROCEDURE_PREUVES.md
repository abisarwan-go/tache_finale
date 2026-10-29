# Procedure document — PyMart final deliverable evidence

**Project:** PyMart back-office CLI (`python -m pymart.cli`)  
**Author evidence pack:** generated from a real local run  
**How to submit:** open this file (or `PROCEDURE_PREUVES.html`) → Print → Save as PDF, **or** paste into Google Docs.

This document covers the required evidence:

1. How to run the CLI  
2. A successful import  
3. At least two generated report files  
4. Examples of handled validation errors  

---

## 0. Setup (before the demo)

```bash
cd mini-projet
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
rm -f .pymart_store.json
```

Optional: regenerate all captures with:

```bash
bash preuves/regenerate_captures.sh
```

---

## Figure 1 — How to run the CLI

### Step
From the project root:

```bash
python -m pymart.cli --help
```

### Expected result
The CLI lists commands: `import`, `order`, `report`, `status`.

### Capture (terminal)

```text
usage: python -m pymart.cli [-h] [--store STORE]
                            {import,order,report,status} ...

PyMart back-office toolkit

positional arguments:
  {import,order,report,status}
    import              Import products/customers/orders
    order               Create or list orders
    report              Generate dated reports
    status              Show store summary (products/customers/orders)

options:
  -h, --help            show this help message and exit
  --store STORE         Path to persisted store JSON (default:
                        .pymart_store.json)
```

Source file: `preuves/captures/01_cli_help.txt`

---

## Figure 2 — Successful import

### Step

```bash
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt
```

### Expected result
- Products / customers / orders are imported
- Invalid rows are **rejected** (not a crash)
- Actionable messages include `file=` + `line=`

### Capture (terminal)

```text
Products imported=5 rejected=2
Customers imported=3 rejected=2
Order lines imported=5 rejected=3
Recent validation messages:
  - [file=data/products.txt, line=7] invalid price/quantity: 'abc', '10'
  - [file=data/products.txt, line=8] price and quantity must be non-negative
  - [file=data/customers.txt, line=5] customer_id, name, and email(@) are required
  - [file=data/customers.txt, line=6] customer_id, name, and email(@) are required
  - [file=data/orders.txt, line=7] Unknown product SKU 'UNKNOWN'.
  - [file=data/orders.txt, line=8] order quantity must be > 0
  - [file=data/orders.txt, line=9] unknown customer_id 'C9999'
```

Source file: `preuves/captures/02_import_success.txt`

### Store status after import

```bash
python -m pymart.cli status
```

```text
PyMart store status
  products : 5
  customers: 3
  orders   : 4
  import errors logged: 7
  catalog:
    - NB-001 | Notebook | $3.49
    - PN-101 | Pen Pack | $5.99
    - BK-550 | Backpack | $39.95
    - ML-001 | Fresh Milk | $3.49 | expires: 2027-08-01
    - HP-200 | Headphones | $79.99 | warranty: 24 months
```

Source file: `preuves/captures/03_status.txt`

---

## Figure 3 — Generated report #1 (daily)

### Step

```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
```

### Terminal

```text
Wrote daily report: reports/daily/2026-06-30/daily_sales_2026-06-30.txt
```

### Report file content (excerpt)

Path: `reports/daily/2026-06-30/daily_sales_2026-06-30.txt`  
Copy kept in: `preuves/rapports/daily_sales_2026-06-30.txt`

```text
PyMart Daily Sales Summary
==========================
Report date: 2026-06-30
Generated at: 2026-10-28T23:05:13
Next review date: 2026-07-30
Orders: 2
Revenue: $52.92

Order details:
  - Order 1001 | customer=C1001 | date=2026-06-30 | lines=2 | total=$12.97 | status=imported
      • NB-001 x2 @ $3.49 = $6.98
      • PN-101 x1 @ $5.99 = $5.99
  - Order 1002 | customer=C1002 | date=2026-06-30 | lines=1 | total=$39.95 | status=imported
      • BK-550 x1 @ $39.95 = $39.95

Catalog snapshot (polymorphic describe):
  - NB-001 | Notebook | $3.49
  - PN-101 | Pen Pack | $5.99
  - BK-550 | Backpack | $39.95
  - ML-001 | Fresh Milk | $3.49 | expires: 2027-08-01
  - HP-200 | Headphones | $79.99 | warranty: 24 months
```

---

## Figure 4 — Generated report #2 (monthly + stock)

### Step

```bash
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

### Terminal

```text
Wrote monthly report: reports/monthly/2026-06/monthly_summary_2026-06.txt
Wrote stock report: reports/monthly/2026-06/stock_levels_2026-06.txt
```

### Monthly summary (excerpt)

Path: `reports/monthly/2026-06/monthly_summary_2026-06.txt`  
Copy: `preuves/rapports/monthly_summary_2026-06.txt`

```text
PyMart Monthly Summary
======================
Period: 2026-06 (days 1–30)
Generated at: 2026-10-28T23:05:13
Orders: 4
Revenue: $139.89

Top-selling products:
  - ML-001: 2 units
  - NB-001: 2 units
  - HP-200: 1 units
  ...

Top customers by spend:
  - Ava Chen (C1003): $79.99
  - Miguel Rivera (C1002): $39.95
  - Aisha Khan (C1001): $19.95
```

### Stock report (2nd/3rd dated report file)

Path: `reports/monthly/2026-06/stock_levels_2026-06.txt`  
Copy: `preuves/rapports/stock_levels_2026-06.txt`

```text
PyMart Stock Level Report
=========================
As of period: 2026-06
Generated at: 2026-10-28T23:05:13

BK-550       qty=7     price=$39.95    BK-550 | Backpack | $39.95
HP-200       qty=11    price=$79.99    HP-200 | Headphones | $79.99 | warranty: 24 months
ML-001       qty=22    price=$3.49     ML-001 | Fresh Milk | $3.49 | expires: 2027-08-01
NB-001       qty=118   price=$3.49     NB-001 | Notebook | $3.49
PN-101       qty=44    price=$5.99     PN-101 | Pen Pack | $5.99
```

---

## Figure 5 — Handled validation errors

### A) Errors during import (already in Figure 2)
Examples of handled bad rows:

| File | Issue |
|------|--------|
| `products.txt` line 7 | price = `abc` (not a number) |
| `products.txt` line 8 | negative price |
| `customers.txt` line 5–6 | invalid email / empty name |
| `orders.txt` line 7 | unknown SKU |
| `orders.txt` line 8 | quantity = 0 |
| `orders.txt` line 9 | unknown customer |

The CLI **continues**, prints counters, and lists reasons. No full crash.

### B) Graceful CLI error on order create

```bash
python -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1
```

### Capture

```text
Order error: Unknown product SKU 'NOPE'.
exit:1
```

Source file: `preuves/captures/06_validation_error.txt`

Interpretation:
- custom / domain error path
- non-zero exit code
- clear message, no traceback dump for the user

---

## Optional: add real screenshots (Mac)

If the teacher wants **pixel screenshots** in addition to this transcript pack:

1. Open Terminal in project root  
2. Run each command above  
3. `Cmd + Shift + 4` then select the terminal window  
4. Drop images into `preuves/screenshots/` and insert them under each Figure in a Google Doc/PDF  

This markdown already satisfies the “procedure + evidence” requirement with captured outputs + report files.

---

## Mapping to assignment checklist

| Requirement | Evidence in this pack |
|-------------|------------------------|
| How to run CLI | Figure 1 |
| Successful import | Figure 2 |
| ≥ 2 report files | Figures 3 & 4 (daily + monthly/stock) |
| Handled validation errors | Figures 2 & 5 |

---

## Files included in `preuves/`

```text
preuves/
  PROCEDURE_PREUVES.md          ← this document
  PROCEDURE_PREUVES.html        ← same content, nicer for PDF print
  regenerate_captures.sh
  captures/
    01_cli_help.txt
    02_import_success.txt
    03_status.txt
    04_report_daily.txt
    05_report_monthly.txt
    06_validation_error.txt
  rapports/
    daily_sales_2026-06-30.txt
    monthly_summary_2026-06.txt
    stock_levels_2026-06.txt
```
