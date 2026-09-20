# DataStore360 — Pipeline de données Retail (Staging / Core)

Pipeline de données complet et automatisé pour fiabiliser, sécuriser et exploiter les données de vente d'une enseigne retail. Le projet couvre l'exploration (EDA), l'audit qualité (data profiling), la mise en conformité RGPD, le nettoyage, la transformation, puis le chargement dans une base **PostgreSQL** structurée en deux couches (**staging** / **core**). L'ensemble est orchestré avec **Apache Airflow** dans un environnement conteneurisé **Docker**.

---

## Sommaire

- [Objectifs](#objectifs)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration (.env)](#configuration-env)
- [Exécution](#exécution)
- [Étapes du pipeline](#étapes-du-pipeline)
- [Modèle de données](#modèle-de-données)
- [RGPD](#rgpd)
- [Rapports](#rapports)
- [Auteur](#auteur)

---

## Objectifs

- Explorer et auditer la qualité d'un jeu de données de ventes brut (valeurs manquantes, doublons, incohérences, valeurs aberrantes).
- Identifier et **pseudonymiser** la donnée à caractère personnel (RGPD) par hashing SHA-256.
- Nettoyer, transformer et enrichir les données (variables métier dérivées).
- Concevoir une base PostgreSQL normalisée en couches **staging** (brut) et **core** (transformé).
- Automatiser et rendre **idempotent** l'ensemble du pipeline via Airflow.

---

## Architecture

```
                 ┌──────────────┐
   store_data.csv│   EXTRACT    │
   ──────────────▶  (Python)    │
                 └──────┬───────┘
                        │ données brutes
                        ▼
                 ┌──────────────┐
                 │   STAGING    │  staging.superstore_raw
                 │ (PostgreSQL) │  miroir du CSV, sans contrainte
                 └──────┬───────┘
                        │ nettoyage + RGPD + variables dérivées
                        ▼
                 ┌──────────────┐
                 │  TRANSFORM   │  pandas / SQL
                 └──────┬───────┘
                        │ données normalisées
                        ▼
                 ┌──────────────┐
                 │     CORE     │  core.customers
                 │ (PostgreSQL) │  core.products
                 │              │  core.orders
                 └──────────────┘

        Orchestration : Apache Airflow (TaskFlow API)
        Infrastructure : Docker Compose
```

---

## Stack technique

| Domaine | Technologies |
|---|---|
| Exploration & préparation | `pandas`, `numpy`, `matplotlib`, `seaborn` |
| Audit qualité | `ydata-profiling` |
| Conformité RGPD | `hashlib` (SHA-256) |
| Base de données | PostgreSQL (OLTP), pgAdmin, SQLAlchemy / psycopg2 |
| Orchestration | Apache Airflow (`@dag`, `@task`, PostgresHook) |
| Infrastructure | Docker Compose |
| Dépendances & versioning | `uv`, Git / GitHub |

---

## Structure du projet

```
datastore360/
├── data/
│   ├── raw/                  # données brutes (store_data.csv)
│   └── processed/            # données transformées
├── notebooks/                # EDA, profiling, RGPD, cleaning, chargement
├── src/                      # fonctions réutilisables
│   ├── extract.py            # extraction du CSV
│   ├── clean.py              # nettoyage & transformation
│   ├── load.py               # chargement PostgreSQL
│   └── db_connection.py      # connexion à la base
├── dags/                     # DAG Airflow
│   └── datastore360_dag.py
├── include/
│   └── sql/                  # scripts de création des schémas
│       ├── staging.sql
│       └── core.sql
├── reports/                  # rapport de data profiling (HTML)
│   └── rapport_profiling.html
├── docker-compose.yml        # PostgreSQL + pgAdmin + Airflow
├── pyproject.toml            # dépendances (uv)
├── uv.lock
├── .env.example              # modèle de variables d'environnement
├── .gitignore
├── README.md
└── DOCUMENTATION.md          # journal de bord technique
```

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose
- [uv](https://github.com/astral-sh/uv) (gestion des dépendances Python)
- Git

---

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/<utilisateur>/datastore360.git
cd datastore360

# 2. Installer les dépendances Python (pour les notebooks / scripts locaux)
uv sync

# 3. Créer le fichier d'environnement à partir du modèle
cp .env.example .env
# puis renseigner les variables (voir section ci-dessous)
```

---

## Configuration (.env)

Créez un fichier `.env` à la racine à partir de `.env.example` :

```env
# PostgreSQL
POSTGRES_USER=datastore
POSTGRES_PASSWORD=change_me
POSTGRES_DB=datastore360
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@datastore360.local
PGADMIN_DEFAULT_PASSWORD=change_me

# Airflow
AIRFLOW_UID=50000
```

> `.env` est ignoré par Git : aucune information sensible ne doit être versionnée.

---

## Exécution

```bash
# 1. Démarrer l'environnement conteneurisé
docker compose up -d

# 2. Vérifier les services
docker compose ps
```

Services disponibles :

| Service | URL | Identifiants |
|---|---|---|
| Airflow UI | http://localhost:8080 | définis dans docker-compose |
| pgAdmin | http://localhost:5050 | `PGADMIN_DEFAULT_*` du `.env` |
| PostgreSQL | localhost:5432 | `POSTGRES_*` du `.env` |

Puis, dans l'interface Airflow :

1. Activer le DAG `datastore360_dag`.
2. Lancer une exécution (**Trigger DAG**).
3. Suivre le déroulement des tâches (extract → staging → transform → core).

Le pipeline est **idempotent** : une relance ne produit ni doublons ni erreurs.

---

## Étapes du pipeline

1. **Extract** — lecture de `store_data.csv`.
2. **Load staging** — chargement brut dans `staging.superstore_raw` (aucune contrainte, données telles quelles).
3. **Transform** — nettoyage (valeurs manquantes, doublons, formats de date, règles de gestion), pseudonymisation SHA-256, création des variables dérivées.
4. **Load core** — répartition normalisée dans `core.customers`, `core.products`, `core.orders`.
5. **Validation** — contrôles qualité (comptages, contraintes, absence de PII en clair dans `core`).

---

## Modèle de données

### Couche `staging`

- **`staging.superstore_raw`** : miroir brut du CSV source, sans contrainte, toutes colonnes d'origine. La donnée personnelle y figure encore en clair.

### Couche `core` (normalisée, OLTP)

| Table | Clés | Colonnes principales |
|---|---|---|
| `core.customers` | `customerid` (PK) | `customername` (pseudonymisé), `segment`, `country`, `city`, `state`, `postal_code`, `region` |
| `core.products` | `productid` (PK) | `category`, `subcategory`, `product_name` |
| `core.orders` | `rowid` (PK) | `orderid`, `customerid` (FK), `productid` (FK), `orderdate`, `shipdate`, `shipmode`, `sales`, `quantity`, `discount`, `profit`, `deliverytime`, `profit_margin` |

**Relations :** un client peut avoir plusieurs commandes (1:N) ; un produit peut apparaître dans plusieurs commandes (1:N). La table `orders` relie clients et produits.

**Règles de gestion appliquées :**
- Remise > 100 %, quantité négative ou `shipdate` antérieure à `orderdate` → considérées comme invalides et traitées.
- Chaque commande est associée à un client unique et un produit unique.

---

## RGPD

- **Donnée personnelle identifiée :** `Customer Name`.
- **Technique appliquée :** pseudonymisation par **hashing SHA-256** (`hashlib`).
- **Garantie :** aucune donnée personnelle en clair ne subsiste dans la couche `core`. Le nom en clair n'existe que dans `staging`, qui reçoit les données avant toute transformation.

---

## Rapports

- Rapport d'audit qualité automatisé : [`reports/rapport_profiling.html`](reports/rapport_profiling.html) (généré via `ydata-profiling`).

Statistiques restituées en fin de pipeline :
- Nombre total de commandes, clients et produits chargés.
- Répartition des ventes par catégorie, région et segment.
- Anomalies détectées et corrigées, taux de complétude final, techniques RGPD appliquées.

---

## Auteur

Projet réalisé dans le cadre de la certification **RNCP Développeur·se en intelligence artificielle** (YouCode – UM6P).

> Voir [`DOCUMENTATION.md`](DOCUMENTATION.md) pour le journal de bord technique détaillé (choix et justifications à chaque étape).