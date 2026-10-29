---
marp: true
paginate: true
title: PyMart — Tâche finale (diapo complète)
description: Présentation détaillée du back-office CLI PyMart
---

<!--
COMMENT UTILISER
1) Google Slides / PowerPoint : copie chaque slide (titre + puces)
2) Marp VS Code : Preview → Export PDF ou PPTX
3) Notes orateur = texte entre <!-- Notes ... -->  (à coller dans “Notes” de Google Slides)
Durée cible oral : 8–12 minutes + questions
-->

# PyMart
## Back-office toolkit — Tâche finale

Livrable : package Python + CLI  
Entrée : `python -m pymart.cli`

<!-- Notes orateur :
Bonjour. Je présente mon livrable final PyMart : un outil en ligne de commande pour importer des données POS, traiter des commandes, et produire des rapports datés sur disque.
-->

---

# Plan

1. Contexte & problème
2. Objectifs / exigences du sujet
3. Architecture du package
4. Modèle OOP (héritage & polymorphisme)
5. Import & nettoyage des données
6. Gestion d’erreurs
7. Generators, fichiers, dates
8. CLI & démo
9. Rapports générés (preuves)
10. Checklist & conclusion

<!-- Notes orateur :
Annonce le plan rapidement (20s). Dis que tu feras une mini-démo au milieu.
-->

---

# 1. Contexte métier

- PyMart = enseigne retail multi-catégories
- Le personnel exporte des fichiers texte depuis le POS
- Les managers veulent :
  - des imports fiables
  - des commandes traçables
  - des rapports **daily / monthly** archivables

<!-- Notes orateur :
Cadre business avant technique. “Pas un exo abstrait : un vrai besoin magasin.”
-->

---

# Le problème concret

Les exports ne sont **pas propres** :

- espaces en trop
- casse incohérente
- colonnes manquantes
- quantités / prix invalides
- identifiants inconnus

Sans traitement → crash ou rapports faux.

<!-- Notes orateur :
Donne 1 exemple : quantité = "two", ou SKU inexistant.
-->

---

# 2. Objectif de la solution

Construire un **back-office CLI** capable de :

| Besoin | Commande |
|--------|----------|
| Importer | `pymart.cli import` |
| Créer / lister commandes | `pymart.cli order` |
| Générer rapports | `pymart.cli report` |
| Erreurs claires | messages sans crash |

<!-- Notes orateur :
Ces 4 lignes = le cœur du brief. Tout le reste sert ça.
-->

---

# Exigences techniques du sujet (rappel)

- Package multi-modules (pas un seul `.py`)
- Nettoyage string/list robuste
- ≥ 2 exceptions custom
- OOP : Product, Customer, Order + héritage
- ≥ 1 generator
- Rapports écrits sur disque (datés)
- datetime / calendar / filesystem
- Preuve de fonctionnement (screens / vidéo)

<!-- Notes orateur :
Dis : “Ma solution couvre chaque point ; je détaille ensuite.”
-->

---

# 3. Architecture — vue d’ensemble

```text
mini-projet/
├── data/                 # fichiers d’exemple POS
├── pymart/               # package applicatif
│   ├── cli.py
│   ├── models/
│   ├── io/
│   ├── services/
│   ├── reports/
│   └── exceptions.py
├── requirements.txt
└── README.md
```

<!-- Notes orateur :
Montre l’arborescence dans VS Code si possible.
-->

---

# Architecture — responsabilités

| Module | Rôle |
|--------|------|
| `cli.py` | arguments terminal (`argparse`) |
| `models/` | objets métier |
| `io/parsers.py` | lecture + nettoyage (stream) |
| `services/store.py` | import, stock, commandes, JSON |
| `reports/writers.py` | écriture daily/monthly |
| `exceptions.py` | erreurs métier typées |

Principe : **séparation des préoccupations**.

<!-- Notes orateur :
Insiste : CLI mince, logique dans services, domaine dans models.
-->

---

# Flux applicatif (bout en bout)

```text
fichiers data/*.txt
        ↓
   io/parsers  (yield lignes)
        ↓
 services/store (valide, stocke, vend)
        ↓
  .pymart_store.json
        ↓
 reports/writers → reports/daily|monthly/...
```

<!-- Notes orateur :
Décris le pipeline en 15s. C’est la slide “je comprends mon système”.
-->

---

# 4. OOP — classes du domaine

Classes minimales demandées + plus :

- `Product`
- `Customer`
- `Order` / `OrderLine`
- (bonus structure) `PerishableProduct`, `ElectronicProduct`

Chaque classe porte **état + comportement**.

<!-- Notes orateur :
Exemple : Product.sell(), Customer.add_loyalty_points(), Order.total.
-->

---

# Héritage produit

```text
Product
 ├── PerishableProduct   (+ expiry_date, storage)
 └── ElectronicProduct   (+ warranty_months, power)
```

- `super().__init__(...)` réutilise la base
- Pas de duplication sku/name/price/quantity

<!-- Notes orateur :
“Héritage = réutiliser le contrat Product.”
-->

---

# Polymorphisme

Méthode commune : **`describe()`**

```python
for p in products:
    print(p.describe())
```

- Product → description de base
- Perishable → + date d’expiry
- Electronic → + garantie / puissance

**Aucun** `if isinstance(...)` dans la boucle.

<!-- Notes orateur :
C’est LE point OOP à citer pour la grille “polymorphism”.
-->

---

# Encapsulation

- Validations à la création / via properties
- Exemples :
  - prix ≥ 0
  - email avec `@` / format
  - quantité de vente > 0
- Attributs internes protégés (`_price`, `__sku`…)

But : empêcher un état métier incohérent.

<!-- Notes orateur :
Relie à labs 6–7 si on te demande d’où ça vient.
-->

---

# 5. Formats d’entrée (data/)

Séparateur `|` (CSV-like)

**products**  
`sku|name|price|quantity|kind|extra`

**customers**  
`customer_id|name|email|loyalty_points`

**orders**  
`order_id|customer_id|order_date|sku|quantity|unit_price`

Les samples contiennent volontairement des **lignes invalides**.

<!-- Notes orateur :
Montre data/products.txt 5 secondes.
-->

---

# Nettoyage & validation

Techniques utilisées :

- `split`, `strip`, `join`, `replace`
- normalisation casse (`upper` / `title` / `lower`)
- conversion `int` / `float` sécurisée
- dates parsées (`YYYY-MM-DD`, variantes)
- règles métier (qty > 0, SKU connu, client connu, stock)

<!-- Notes orateur :
“String/list processing” du sujet = ici.
-->

---

# 6. Gestion d’erreurs

Hiérarchie :

```text
PyMartError
├── DataValidationError
├── RecordFormatError
├── UnknownProductError
├── DuplicateIdError
├── InsufficientStockError
└── InvalidDiscountError
```

≥ 2 custom exigées → largement couvert.

<!-- Notes orateur :
Cite 2–3 noms d’exceptions à l’oral.
-->

---

# Stratégie d’import robuste

Pour **chaque ligne** :

1. `try` parser / valider
2. si erreur métier → `rejected++`, message contextuel
3. sinon → importer
4. continuer la ligne suivante

Résultat typique samples :

- products `5` ok / `2` reject
- customers `3` ok / `2` reject
- order lines `5` ok / `3` reject

<!-- Notes orateur :
Montre le terminal d’import (screenshot ou live).
-->

---

# Erreurs actionnables

Messages du type :

```text
[file=data/orders.txt, line=7] Unknown product SKU 'UNKNOWN'.
[file=data/products.txt, line=8] price and quantity must be non-negative
```

En CLI :

```text
Order error: Unknown product SKU 'NOPE'.
```

→ pas de crash, pas de traceback “brut” pour l’utilisateur.

<!-- Notes orateur :
C’est la slide “graceful error handling”.
-->

---

# 7. Generators (exigence)

Exemple : lecture streaming

```python
def iter_text_rows(path):
    with open(path) as f:
        for line_no, raw in enumerate(f, start=1):
            ...
            yield line_no, fields
```

Aussi :  
`iter_orders_for_date`, `iter_orders_for_month`

Avantage : traite **1 enregistrement à la fois** (mémoire stable).

<!-- Notes orateur :
Dis le mot “yield” clairement pour la grille.
-->

---

# Filesystem & archivage

- Création auto de `reports/` si manquant
- Organisation :
  - `reports/daily/YYYY-MM-DD/`
  - `reports/monthly/YYYY-MM/`
- Écriture fichiers `.txt` (pas seulement stdout)
- Persistence état : `.pymart_store.json`

<!-- Notes orateur :
Ouvre le dossier reports/ pendant la présentation.
-->

---

# datetime / time / calendar

Utilisations dans le projet :

- nom / chemin de rapport **daté**
- période monthly via année-mois
- parsing dates d’orders
- calendrier / leap year dans résumé monthly
- “next review” (+30 jours) côté tooling rapports

→ couvre l’exigence “au moins deux usages”.

<!-- Notes orateur :
Cite daily filename + monthly calendar comme 2 preuves.
-->

---

# 8. CLI — surface complète

```bash
python -m pymart.cli --help
python -m pymart.cli import --products ... --customers ... --orders ...
python -m pymart.cli order list
python -m pymart.cli order create --id ... --customer ... --sku ... --qty ...
python -m pymart.cli report --type daily --date YYYY-MM-DD --out reports/
python -m pymart.cli report --type monthly --month YYYY-MM --out reports/
```

Option globale : `--store` (fichier JSON d’état)

<!-- Notes orateur :
Si démo live, enchaîne help → import → report.
-->

---

# Démo live #1 — Import

Commande :

```bash
rm -f .pymart_store.json
python -m pymart.cli import \
  --products data/products.txt \
  --customers data/customers.txt \
  --orders data/orders.txt
```

À montrer :

- compteurs imported / rejected
- messages file/line
- puis `order list`

<!-- Notes orateur :
Parle pendant que ça tourne : “les rejects sont normaux, c’est voulu.”
-->

---

# Démo live #2 — Rapports

```bash
python -m pymart.cli report --type daily --date 2026-06-30 --out reports/
python -m pymart.cli report --type monthly --month 2026-06 --out reports/
```

Ouvrir ensuite les fichiers générés.

<!-- Notes orateur :
Zoom sur revenue + détails commandes daily, puis top products monthly.
-->

---

# 9. Preuve — rapport daily

Fichier :

`reports/daily/2026-06-30/daily_sales_2026-06-30.txt`

Contenu typique :

- date du rapport + timestamp génération
- nombre de commandes / revenue du jour
- détail des orders + lines
- snapshot catalogue via `describe()` (polymorphisme)

<!-- Notes orateur :
Screenshot ou ouverture fichier = evidence #1.
-->

---

# Preuve — rapport monthly (+ stock)

Fichiers :

- `reports/monthly/2026-06/monthly_summary_2026-06.txt`
- `reports/monthly/2026-06/stock_levels_2026-06.txt`

Contenu monthly :

- CA du mois
- top produits / top clients
- erreurs d’import récentes
- calendrier du mois

→ **≥ 2 types de rapports** exigés = OK

<!-- Notes orateur :
Evidence #2 et #3 (stock en bonus).
-->

---

# Qualité de code (grille 20%)

- Modularité package
- Noms explicites
- PEP8 globalement respecté
- Couches séparées (cli / io / services / models / reports)
- Pas de “gros script unique”

<!-- Notes orateur :
Si question qualité : pointe services/store.py vs cli.py.
-->

---

# OOP (grille 20%) — récap oral

| Critère | Preuve dans le projet |
|---------|------------------------|
| Domain modeling | Product, Customer, Order |
| Inheritance | Perishable / Electronic |
| Polymorphism | `describe()` |
| Encapsulation | validations / properties |

<!-- Notes orateur :
Apprends ce tableau par cœur pour l’oral.
-->

---

# Robustesse (grille 10%) — récap

- Exceptions custom + messages riches
- Import résilient (reject/continue)
- CLI ne crashe pas sur erreur métier
- Contexte fichier/ligne

<!-- Notes orateur :
Relie à la capture “SKU NOPE” / rejects import.
-->

---

# Stdlib (grille 10%) — récap

| Besoin | Module / usage |
|--------|----------------|
| Chemins / dossiers | `pathlib`, création `reports/` |
| Dates rapports | `datetime` |
| Mois / calendrier | `calendar` |
| Streaming | generators (`yield`) |
| CLI | `argparse` |
| Persistance | `json` |

<!-- Notes orateur :
Tu n’as pas besoin de libs lourdes pour le cœur métier.
-->

---

# Documentation & preuves (grille 5%)

Fourni dans le repo :

- `README.md` (runbook complet)
- `DEMO.md` / `PREUVE_SOUMISSION.md`
- `DIAPO_TACHE_FINAL.md` (ce diapo)
- Samples `data/`
- Screenshots / vidéo à joindre au rendu

<!-- Notes orateur :
Dis où se trouve la preuve demandée par le sujet.
-->

---

# 10. Checklist de soumission

- [x] Package complet
- [x] Structure claire
- [x] `requirements.txt`
- [x] CLI E2E
- [x] Generator présent
- [x] ≥ 2 exceptions custom
- [x] ≥ 2 rapports datés sur disque
- [ ] Preuve jointe (screens **ou** vidéo) ← à finaliser si pas fait
- [x] Instructions de run

<!-- Notes orateur :
Coche mentalement. La case preuve = ton action restante.
-->

---

# Limites & pistes d’amélioration

Limites actuelles :

- store local JSON (pas de vraie DB)
- 1 ligne produit par `order create` (simple)

Améliorations possibles :

- base SQLite
- tests unitaires automatisés
- export CSV/PDF des rapports

<!-- Notes orateur :
Montre que tu es critique et conscient : ça plaît souvent.
-->

---

# Conclusion

PyMart final = **CLI de back-office** qui :

1. importe et nettoie des extracts POS
2. gère commandes + stock
3. produit des rapports daily/monthly archivés
4. reste robuste face aux données sales

Aligné sur le brief `tache_final.md`.

<!-- Notes orateur :
Phrase de fin nette, puis “Je suis prêt pour vos questions.”
-->

---

# Merci

## Questions ?

Lancement rapide :

```bash
python -m pip install -r requirements.txt
python -m pymart.cli --help
```

Repo : package `pymart/` · docs `README.md`
