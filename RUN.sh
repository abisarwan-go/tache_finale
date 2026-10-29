#!/usr/bin/env bash
# Lance tout le parcours de démo PyMart (tâche finale).
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Reset store"
rm -f .pymart_store.json

echo
echo "==> 1) Aide CLI"
python -m pymart.cli --help

echo
echo "==> 2) Import (produits + clients + commandes)"
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

echo
echo "==> 3) Status"
python -m pymart.cli status

echo
echo "==> 4) Rapport daily"
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/

echo
echo "==> 5) Rapport monthly (+ stock)"
python -m pymart.cli report --type monthly --month 2026-06 --out reports/

echo
echo "==> 6) Erreur gérée (SKU inconnu) — exit code attendu ≠ 0"
set +e
python -m pymart.cli order create --id 2002 --customer C1001 --sku NOPE --qty 1
echo "exit:$?"
set -e

echo
echo "OK — fichiers générés :"
find reports -type f | sort
echo
echo "Preuve PDF : ouvre preuves/PROCEDURE_PREUVES.html → Imprimer → PDF"
