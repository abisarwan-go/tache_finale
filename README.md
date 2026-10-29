# PyMart — Tâche finale (livrable complet)

Ce dossier **contient tout le travail à rendre**. Tu n’as rien à reconstruire.

| Contenu | Rôle |
|---------|------|
| `pymart/` | code de l’application |
| `data/` | fichiers d’exemple (produits, clients, commandes) |
| `preuves/` | preuve demandée (captures + rapports) |
| `tests/` | tests automatiques |
| `DIAPO_TACHE_FINAL.md` | diapo pour l’oral (optionnel) |

---

## 1) Installer (une seule fois)

```bash
cd ~/Documents/estiam/python/tache_finale
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## 2) Tout lancer d’un coup (recommandé)

```bash
source .venv/bin/activate
bash RUN.sh
```

Ce script fait : import → status → 2 rapports → exemple d’erreur.

---

## 3) Ou commande par commande (copier-coller)

```bash
source .venv/bin/activate
rm -f .pymart_store.json

python -m pymart.cli --help

python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt

python -m pymart.cli status

python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

Rapports créés :

- `reports/daily/2026-06-30/daily_sales_2026-06-30.txt`
- `reports/monthly/2026-06/monthly_summary_2026-06.txt`
- `reports/monthly/2026-06/stock_levels_2026-06.txt`

---

## 4) Preuve à rendre au prof

1. Ouvre **`preuves/PROCEDURE_PREUVES.html`** dans Safari/Chrome  
2. Menu **Fichier → Imprimer → Enregistrer en PDF**  
3. Rends ce PDF **+** ce dossier `tache_finale` (zip ou lien GitHub)

Le document montre déjà : CLI, import, 2 rapports, erreurs gérées.

---

## 5) Tests (optionnel)

```bash
source .venv/bin/activate
python -m pytest
```
