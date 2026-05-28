# AI IT OPTIMIZATION — FinOps Platform
## Complete Technical Documentation, Architecture Reference & Knowledge Transfer Document

> **Document Type:** System Design Document · Developer Guide · Architecture Document · API Reference · Deployment Guide · Knowledge Transfer Document · Interview Preparation Document
> **Project Version:** 0.1.0
> **Author:** Yathish Shetty
> **Document Generated:** 2026-05-28
> **Reading Time:** ~90 minutes (full read)

---

# TABLE OF CONTENTS

1. [Section 1 — Project Overview](#section-1--project-overview)
2. [Section 2 — Complete Folder Structure](#section-2--complete-folder-structure)
3. [Section 3 — Frontend Deep Analysis (Streamlit Dashboard)](#section-3--frontend-deep-analysis-streamlit-dashboard)
4. [Section 4 — Backend Deep Analysis (FastAPI + ML + Pipeline)](#section-4--backend-deep-analysis-fastapi--ml--pipeline)
5. [Section 5 — Database / Data Layer Documentation](#section-5--database--data-layer-documentation)
6. [Section 6 — API Documentation (Swagger-Style)](#section-6--api-documentation-swagger-style)
7. [Section 7 — Authentication & Security](#section-7--authentication--security)
8. [Section 8 — Complete Execution Flow](#section-8--complete-execution-flow)
9. [Section 9 — DevOps & Deployment](#section-9--devops--deployment)
10. [Section 10 — Configuration & Environment Variables](#section-10--configuration--environment-variables)
11. [Section 11 — Dependencies & Libraries](#section-11--dependencies--libraries)
12. [Section 12 — Important Algorithms & Logic](#section-12--important-algorithms--logic)
13. [Section 13 — Recreating the Project from Scratch](#section-13--recreating-the-project-from-scratch)
14. [Section 14 — Improvements & Scalability](#section-14--improvements--scalability)
15. [Section 15 — Interview Preparation](#section-15--interview-preparation)

---

# SECTION 1 — PROJECT OVERVIEW

## 1.1 Project Name

**AI IT OPTIMIZATION — FinOps Platform**
*(Internal codename: `AI_IT_OPTIMIZATION`)*

## 1.2 Project Objective

Build an end-to-end **data engineering + machine learning platform** that automatically detects cloud and SaaS spending waste in a mid-sized IT organisation, quantifies the savings opportunity in Indian Rupees, and surfaces prioritised, actionable recommendations to FinOps analysts, engineering leaders, and finance teams.

The platform fuses **deterministic rule-based detectors** with **probabilistic ML classifiers** to:

- Forecast cloud spend 1–180 days into the future.
- Detect anomalous cost days (runaway batch jobs, mis-scaled prod traffic, dev environments not torn down).
- Identify idle EC2-style instances draining budget.
- Recommend "rightsize" downgrades for over-provisioned servers.
- Flag SaaS licenses (Salesforce, Slack, GitHub, Figma, etc.) that should be revoked.
- Compute an organisation-wide "potential annual savings" KPI.

## 1.3 Real-World Problem Solved

Cloud and SaaS bills routinely contain **15–30% pure waste**. Examples drawn from real-world FinOps reports:

| Waste Category | Symptom | Why It Persists |
|----------------|---------|-----------------|
| Idle instances | Engineer launched a dev box, left for vacation, never killed it | No one is paid to delete things |
| Oversized prod boxes | `m5.4xlarge` running at 12% CPU | Originally sized for peak Diwali load |
| Zombie SaaS licenses | Employee changed teams, license never revoked | License renewals are automatic |
| Cost anomalies | A `for` loop with no termination shipped to prod | Bills land 30 days later — incident is forgotten |
| Mismatched seats | Marketing dept assigned an Enterprise GitHub license | Procurement bundles license tiers |

The platform replaces **monthly manual spreadsheet audits** (which catch maybe 20% of waste 30 days late) with **daily automated detection** that flags issues within 24 hours.

## 1.4 Business Use Case

**Persona 1 — FinOps Analyst** (the daily user): opens the Streamlit dashboard every morning, sorts recommendations by annual savings, downloads a CSV of high-severity items, and emails owners to action them.

**Persona 2 — Engineering Manager**: looks at the anomaly view weekly to catch any team's runaway workload before it shows on the CFO's monthly bill.

**Persona 3 — CFO / Finance Lead**: looks at the headline KPIs (Total Annual Savings, Forecasted Next 30 Days) once a quarter for board reporting.

**Quantified business outcome (from a typical generated dataset):**

| Metric | Value |
|--------|-------|
| Total cloud spend under analysis | ~₹6 Cr/year |
| Potential SaaS savings identified | ~₹4.8 Cr/year |
| Idle instance-days flagged | ~7,500 |
| "Truly unused" licenses flagged | ~700 out of ~3,100 (≈22%) |
| Anomalous days auto-detected | ~19 per year |

## 1.5 Core Features

### Feature 1 — ETL Pipeline (3-stage)
- **Ingest** — read CSV files, validate schema, log row counts.
- **Clean** — deduplicate, coerce types, fill nulls with per-instance medians, clip negative costs.
- **Transform** — feature engineering: `day_of_week`, `month`, `is_weekend`, `utilization_band`, `is_idle_candidate`, `daily_waste_inr`, `usage_category`, `annual_cost_inr`, `days_since_last_login`.

### Feature 2 — Three ML Models
- **Cost Forecaster** (`LinearRegression`) — predicts daily cloud spend.
- **Anomaly Detector** (`IsolationForest`, 5% contamination, unsupervised) — flags weird cost days.
- **License Classifier** (`LogisticRegression` with `StandardScaler`) — predicts probability that a SaaS license should be revoked.

### Feature 3 — Unified Recommendation Engine
Combines rule-based detectors (`detect_idle_instances`, `detect_rightsize_candidates`) with ML-driven detectors (`detect_unused_licenses`, `detect_recent_anomalies`) into a single `Recommendation` Pydantic model.

### Feature 4 — REST API (FastAPI)
Four endpoints — `/health`, `/cost-forecast`, `/anomalies`, `/recommendations` — with auto-generated Swagger UI at `/docs`.

### Feature 5 — Interactive Dashboard (Streamlit)
- **Landing page** — headline KPIs + top 5 high-impact items.
- **Cost Trends page** — adjustable forecast slider (7–90 days).
- **Anomalies page** — chronological list with metadata.
- **Recommendations page** — filter by category/severity, export to CSV.

### Feature 6 — Synthetic Data Generator
A probabilistic data generator that plants **different anomalies and behaviours on every run** so models cannot memorise specific dates or hardcoded labels.

## 1.6 User Roles and Permissions

| Role | Permission Level | Pages Accessed | Actions Allowed |
|------|------------------|----------------|-----------------|
| **FinOps Analyst** | Read-only operational | All dashboard pages + CSV export | View, filter, export recommendations |
| **Engineering Manager** | Read-only investigative | Cost Trends + Anomalies | Investigate anomalies for own team |
| **CFO / Finance Lead** | Read-only executive | Landing page + Cost Trends | Quarterly KPI review |
| **Platform Engineer (dev)** | Read + retrain | All + CLI access | Run `train_models.py`, regenerate data |
| **System (cron)** | Service account | None | Execute `run_pipeline.py` + `train_models.py` at 02:00 / 03:00 IST daily |

> **Note (v0.1.0 reality):** Authentication is **not yet enabled**. The API is open by design for the local development cycle. All `User Roles` above are conceptual until JWT auth is bolted on (see Section 14).

## 1.7 End-to-End Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DAILY EXECUTION (02:00–03:00 IST)                   │
├─────────────────────────────────────────────────────────────────────────┤
│  02:00 cron → scripts/run_pipeline.py                                   │
│         ├── ingest.load_cloud_usage()    (data/raw/cloud_usage.csv)     │
│         ├── clean.clean_cloud_usage()    (dedup, types, nulls)          │
│         ├── transform.transform_cloud_usage()  (+ feature engineering)  │
│         └── writes data/processed/cloud_usage_processed.csv             │
│                                                                         │
│         ├── ingest.load_saas_usage()     (data/raw/saas_usage.csv)      │
│         ├── clean.clean_saas_usage()                                    │
│         ├── transform.transform_saas_usage()                            │
│         └── writes data/processed/saas_usage_processed.csv              │
│                                                                         │
│  03:00 cron → scripts/train_models.py                                   │
│         ├── forecast.train_forecast_model()  → forecast_model.joblib   │
│         ├── anomaly.train_anomaly_model()    → anomaly_model.joblib    │
│         └── license_classifier.train_license_classifier()              │
│                                                → license_classifier.joblib│
├─────────────────────────────────────────────────────────────────────────┤
│                ONLINE EXECUTION (continuously available)                │
├─────────────────────────────────────────────────────────────────────────┤
│  FastAPI (uvicorn :8000)                                                │
│    ├── GET /health             → liveness + model+data freshness       │
│    ├── GET /cost-forecast?days_ahead=N                                 │
│    ├── GET /anomalies                                                  │
│    └── GET /recommendations?top_n=&category=&severity=                 │
│                                                                         │
│  Streamlit (streamlit run … :8501)                                      │
│    ├── app.py             — landing, KPIs, top 5                        │
│    ├── 1_📊_Cost_Trends   — forecast slider                             │
│    ├── 2_🚨_Anomalies     — anomalies chart + cards                     │
│    └── 3_💡_Recommendations — filterable list + CSV export             │
└─────────────────────────────────────────────────────────────────────────┘
```

## 1.8 System Architecture Overview

This is a **modular, layered, file-system-backed Python application** with three clear runtime tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│  TIER 3 — PRESENTATION LAYER (Streamlit, port 8501)                    │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ app.py  │  pages/1_Cost  │  pages/2_Anom  │  pages/3_Reco          ││
│  │  └──────────────── api_client.py (single point of contact) ──────┘ ││
│  └─────────────────────────────┬──────────────────────────────────────┘│
│                                 │  HTTP GET (requests lib)             │
│  ──────────────────────────────▼──────────────────────────────────────  │
│  TIER 2 — APPLICATION LAYER (FastAPI, port 8000)                       │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │  main.py (app + lifespan + CORS)                                   ││
│  │   ├── routes/forecast.py        → ML forecast layer                ││
│  │   ├── routes/anomalies.py       → ML anomaly layer                 ││
│  │   ├── routes/recommendations.py → engine.py orchestration          ││
│  │   ├── dependencies.py (lru_cache CSV loaders)                      ││
│  │   └── schemas.py (Pydantic contracts)                              ││
│  └─────────────────────────────┬──────────────────────────────────────┘│
│                                 │ Python imports                       │
│  ──────────────────────────────▼──────────────────────────────────────  │
│  TIER 1 — DATA + ML LAYER                                              │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │  src/pipeline/  → ingest, clean, transform                         ││
│  │  src/ml/        → forecast, anomaly, license_classifier            ││
│  │  src/recommendations/ → engine (rules + ML), schema (Pydantic)     ││
│  │  src/utils/     → logger                                            ││
│  └─────────────────────────────┬──────────────────────────────────────┘│
│                                 │ pandas read/write                    │
│  ──────────────────────────────▼──────────────────────────────────────  │
│  TIER 0 — PERSISTENCE LAYER (filesystem; Postgres-ready)               │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ data/raw/*.csv         data/processed/*.csv                        ││
│  │ models/*.joblib        (scripts/generate_data.py creates raw/)     ││
│  └────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘
```

**Design properties:**

- **Single direction of data flow** — UI → API → ML/Engine → CSV/Joblib. No circular dependencies.
- **Stateless API** — every request reloads from cached CSV; no in-memory state outside `lru_cache`.
- **No database in v0.1** — CSVs are the database. `psycopg2` and `sqlalchemy` are pinned in `requirements.txt` precisely so the migration is a single `dependencies.py` rewrite.
- **Models persisted as `.joblib`** — train once at 03:00, serve all day.
- **Stateless workers** — multiple `uvicorn --workers 4` processes can run in parallel; each warms its own LRU cache.

## 1.9 Tech Stack with Reasons

| Layer | Technology | Why Chosen | Alternative & Why Not |
|-------|-----------|------------|----------------------|
| **Language** | Python 3.14 | Pandas/sklearn ecosystem unmatched | Go (no ML lib), Java (verbose), R (no API ecosystem) |
| **Data manipulation** | pandas ≥2.1 | Industry standard | Polars (faster but smaller ecosystem) |
| **Numerical computing** | NumPy ≥1.26 | Required by pandas + sklearn | — |
| **ML framework** | scikit-learn ≥1.4 | Industry-grade classical ML | PyTorch (overkill for tabular), XGBoost (less interpretable) |
| **API framework** | FastAPI ≥0.110 | Async-native, auto-Swagger, Pydantic-tight | Flask (no async/auto-docs), Django (heavyweight) |
| **ASGI server** | uvicorn[standard] ≥0.27 | FastAPI's reference server | Hypercorn (similar, smaller adoption) |
| **Validation** | Pydantic ≥2.6 | Already FastAPI's substrate | dataclasses (no validation), marshmallow (slower) |
| **Dashboard** | Streamlit ≥1.32 | Build a real UI in Python in one file | Dash (verbose), React+Plotly (full frontend skillset) |
| **Charting** | Plotly ≥5.19 (declared, light usage) | Interactive charts in Python | Matplotlib (static only) |
| **Excel I/O** | openpyxl ≥3.1 | Future-ready for `.xlsx` ingest | xlsxwriter (write-only) |
| **DB driver** | psycopg2-binary ≥2.9 | Standard Postgres adapter | asyncpg (async, future migration) |
| **ORM** | SQLAlchemy ≥2.0 | Industry standard, async-capable | Tortoise (smaller ecosystem) |
| **Env mgmt** | python-dotenv ≥1.0 | `.env` file → `os.environ` | Manual env vars |
| **Model persistence** | joblib (bundled in sklearn) | Faster than pickle on NumPy arrays | pickle, ONNX |
| **Scheduler** | cron / Airflow (planned) | Daily ETL is a cron problem | systemd timers (Linux-only) |

## 1.10 High-Level Execution Flow

```
1. NIGHTLY (02:00 IST)
   cron → run_pipeline.py
        ├─ ingest reads raw CSVs (validates schema)
        ├─ clean dedups, coerces types, fills nulls
        └─ transform engineers features → writes processed CSVs

2. NIGHTLY (03:00 IST)
   cron → train_models.py
        ├─ trains LinearRegression on daily cloud cost
        ├─ trains IsolationForest on daily aggregates
        └─ trains LogisticRegression on license features
        → persists 3 .joblib bundles

3. DAYTIME (online, multi-user)
   FinOps Analyst opens browser → Streamlit (:8501)
        Streamlit calls api_client.fetch_recommendations(top_n=500)
             → HTTP GET to FastAPI (:8000)
                  → routes/recommendations.py
                       → dependencies.get_cloud_data() (cached)
                       → dependencies.get_saas_data() (cached)
                       → engine.build_all_recommendations()
                            ├─ detect_idle_instances() (rule)
                            ├─ detect_rightsize_candidates() (rule)
                            ├─ detect_unused_licenses() (ML)
                            └─ detect_recent_anomalies() (ML)
                       → engine.summarize()
                  → JSON response
        Streamlit renders KPI cards + expandable cards + CSV export
```

---

# SECTION 2 — COMPLETE FOLDER STRUCTURE

## 2.1 Top-Level Tree

```
AI_IT_OPTIMIZATION/
├── .gitignore                          # Ignore venv, __pycache__, .env, IDE configs
├── .venv/                              # Local Python virtual environment (gitignored)
├── README.md                           # Quickstart guide + KPIs
├── requirements.txt                    # Python dependency pins
├── data/
│   ├── raw/
│   │   ├── cloud_usage.csv             # Raw cloud telemetry (generated)
│   │   └── saas_usage.csv              # Raw SaaS license usage (generated)
│   └── processed/
│       ├── cloud_usage_processed.csv   # ETL output for cloud
│       └── saas_usage_processed.csv    # ETL output for SaaS
├── models/
│   ├── forecast_model.joblib           # Trained LinearRegression bundle
│   ├── anomaly_model.joblib            # Trained IsolationForest bundle
│   └── license_classifier.joblib       # Trained LogisticRegression + scaler bundle
├── scripts/
│   ├── generate_data.py                # Synthetic data generator (probabilistic)
│   ├── run_pipeline.py                 # ETL entrypoint (calls ingest→clean→transform)
│   └── train_models.py                 # ML training entrypoint
└── src/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   ├── main.py                     # FastAPI app, CORS, lifespan, /health, /root
    │   ├── dependencies.py             # lru_cache CSV loaders (DB-swappable)
    │   ├── schemas.py                  # Pydantic request/response models
    │   └── routes/
    │       ├── __init__.py
    │       ├── forecast.py             # GET /cost-forecast
    │       ├── anomalies.py            # GET /anomalies
    │       └── recommendations.py      # GET /recommendations
    ├── dashboard/
    │   ├── __init__.py
    │   ├── app.py                      # Streamlit landing page
    │   ├── api_client.py               # Single point of contact w/ API
    │   └── pages/
    │       ├── __init__.py
    │       ├── 1_📊_Cost_Trends.py
    │       ├── 2_🚨_Anomalies.py
    │       └── 3_💡_Recommendations.py
    ├── ml/
    │   ├── __init__.py                 # (implicit)
    │   ├── anomaly.py                  # IsolationForest training/inference
    │   ├── forecast.py                 # LinearRegression training/inference
    │   └── license_classifier.py       # LogisticRegression + StandardScaler
    ├── pipeline/
    │   ├── __init__.py
    │   ├── ingest.py                   # Stage 1 — schema-validated CSV read
    │   ├── clean.py                    # Stage 2a — dedup/types/nulls
    │   └── transform.py                # Stage 2b — feature engineering
    ├── recommendations/
    │   ├── __init__.py
    │   ├── engine.py                   # detect_idle / rightsize / revoke / anomaly
    │   └── schema.py                   # Recommendation Pydantic + severity rules
    └── utils/
        ├── __init__.py
        └── logger.py                   # Project-wide logging helper
```

## 2.2 File-by-File Documentation

Each file below is documented with **Purpose**, **Why It Exists**, **Interactions**, **Removal Impact**, and **Dependencies**.

---

### 2.2.1 — `/.gitignore`

| Field | Detail |
|-------|--------|
| **Purpose** | Tell git to ignore the local Python venv (`.venv/`, `venv/`), bytecode caches (`__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`), VS Code settings (`.vscode/`), OS metadata (`.DS_Store`, `Thumbs.db`), and secrets (`*.env`). |
| **Why It Exists** | Prevent committing 200MB+ of venv binaries, IDE-specific configs that pollute other dev environments, and accidentally leaking AWS keys / passwords. |
| **Interactions** | Read by git only. |
| **If Removed** | First `git add .` will commit `.venv/`, `__pycache__/`, secrets — catastrophic for repository hygiene. |
| **Dependencies** | None. |

### 2.2.2 — `/README.md`

| Field | Detail |
|-------|--------|
| **Purpose** | Front-door documentation: project blurb, illustrative KPIs, folder map, 7-step quickstart, output table, ML model rationale, status checklist, tech stack, cron schedule, author. |
| **Why It Exists** | First file GitHub renders. Onboarding and recruiter touch-point. |
| **Interactions** | Read by humans, parsed by GitHub. |
| **If Removed** | Project becomes hostile to new contributors. |
| **Dependencies** | None. |

### 2.2.3 — `/requirements.txt`

| Field | Detail |
|-------|--------|
| **Purpose** | Lower-bound dependency pins for reproducible installs. |
| **Why It Exists** | Single source of truth for `pip install -r requirements.txt`. Pinning a lower bound (`>=2.1`) rather than exact version allows security patches. |
| **Interactions** | Consumed by `pip` and any CI/CD pipeline. |
| **If Removed** | Onboarding takes hours of trial-and-error library installation. |
| **Dependencies** | The whole runtime stack — see Section 11 for the full breakdown. |

### 2.2.4 — `/.venv/`

| Field | Detail |
|-------|--------|
| **Purpose** | Local Python virtual environment. |
| **Why It Exists** | Isolates project deps from system Python (which on macOS / corporate Windows often has mismatched versions). |
| **Interactions** | Activated by `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows). All `pip install` writes here. |
| **If Removed** | Re-create with `python -m venv .venv && pip install -r requirements.txt`. |
| **Dependencies** | Python 3.14 binary in PATH. |

### 2.2.5 — `/data/raw/cloud_usage.csv`

| Field | Detail |
|-------|--------|
| **Purpose** | Raw, dirty cloud usage telemetry. ~49,000 rows × 13 columns. One row per (instance × day). |
| **Why It Exists** | Mimics what a real billing exporter (AWS CUR, Azure Cost Mgmt Export) would dump nightly. |
| **Schema** | `date`, `instance_id`, `instance_type`, `region`, `environment`, `cpu_utilization_avg`, `cpu_utilization_max`, `hours_running`, `cost_compute_inr`, `cost_storage_inr`, `cost_transfer_inr`, `cost_other_inr`, `cost_inr` (total). |
| **Interactions** | Created by `scripts/generate_data.py`. Read by `src/pipeline/ingest.py`. |
| **If Removed** | Run `python scripts/generate_data.py` to regenerate. |
| **Dependencies** | None (filesystem only). |

### 2.2.6 — `/data/raw/saas_usage.csv`

| Field | Detail |
|-------|--------|
| **Purpose** | Raw SaaS license assignment + usage signal. ~3,100 rows × 11 columns. One row per (user × tool). |
| **Schema** | `user_id`, `employee_name`, `department`, `tool`, `license_type`, `monthly_cost_inr`, `logins_last_30d`, `active_days_last_30d`, `last_login_date`, `assigned_date`, `truly_unused` (ground-truth label). |
| **Why It Exists** | Mimics a Workday/Okta SSO export joined with vendor-side login telemetry. |
| **Interactions** | Created by `scripts/generate_data.py`. Read by `src/pipeline/ingest.py`. |
| **If Removed** | Regenerate via the data generator. |
| **Dependencies** | None. |

### 2.2.7 — `/data/processed/cloud_usage_processed.csv`

| Field | Detail |
|-------|--------|
| **Purpose** | Cleaned + feature-engineered cloud telemetry. Same row count as raw minus duplicates and bad-date rows. Adds 6 new columns. |
| **Schema (added)** | `day_of_week`, `month`, `is_weekend`, `utilization_band` (idle/low/normal/high), `is_idle_candidate` (bool), `daily_waste_inr`. |
| **Interactions** | Written by `scripts/run_pipeline.py`. Read by `src/api/dependencies.get_cloud_data()` and `scripts/train_models.py`. |
| **If Removed** | Re-run `python scripts/run_pipeline.py`. API returns `503 Service Unavailable` until present. |
| **Dependencies** | Upstream raw CSV must exist. |

### 2.2.8 — `/data/processed/saas_usage_processed.csv`

| Field | Detail |
|-------|--------|
| **Purpose** | Cleaned + feature-engineered SaaS data. |
| **Schema (added)** | `has_ever_logged_in`, `days_since_last_login`, `usage_category` (active/low/unused), `annual_cost_inr`, `is_recommendation_candidate`. |
| **Interactions** | Same as cloud processed. |
| **If Removed** | Re-run pipeline. |
| **Dependencies** | Upstream raw CSV. |

### 2.2.9 — `/models/forecast_model.joblib`

| Field | Detail |
|-------|--------|
| **Purpose** | Serialised dictionary: `{"model": LinearRegression, "feature_cols": [...], "min_date": Timestamp, "metrics": {...}}`. |
| **Why** | Avoid retraining on every API call. Load once per worker process. |
| **Interactions** | Written by `forecast.train_forecast_model()`. Read by `forecast.predict_future_costs()` (called from `routes/forecast.py`). |
| **If Removed** | `/cost-forecast` endpoint fails. Run `python scripts/train_models.py` to rebuild. |
| **Dependencies** | scikit-learn (version compatibility — joblib bundles are sklearn-version-sensitive). |

### 2.2.10 — `/models/anomaly_model.joblib`

| Field | Detail |
|-------|--------|
| **Purpose** | Serialised dictionary: `{"model": IsolationForest, "feature_cols": [...]}`. |
| **Interactions** | Written by `anomaly.train_anomaly_model()`. Read by `anomaly.detect_anomalies()` (called from `/anomalies` and from `engine.detect_recent_anomalies()`). |
| **If Removed** | `/anomalies` endpoint + anomaly recommendations fail. |

### 2.2.11 — `/models/license_classifier.joblib`

| Field | Detail |
|-------|--------|
| **Purpose** | Serialised dictionary: `{"model": LogisticRegression, "scaler": StandardScaler, "feature_cols": [...], "metrics": {...}}`. |
| **Interactions** | Written by `license_classifier.train_license_classifier()`. Read by `predict_revoke_candidates()` (called from `engine.detect_unused_licenses()`). |
| **If Removed** | SaaS revoke recommendations vanish from `/recommendations`. |

### 2.2.12 — `/scripts/generate_data.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Probabilistically generate `cloud_usage.csv` and `saas_usage.csv` with planted-but-not-labelled waste. |
| **Why** | Production data is private; synthetic data lets the ML actually *work* (anomalies hide in noise) instead of memorising hand-coded labels. |
| **Key constructs** | `INSTANCE_CATALOG` (13 instance types with INR pricing), `BEHAVIOR_PRIORS_BY_ENV` (probability-of-waste varies by env), `_seasonality_multiplier()` (month-end spikes, weekend dips, Indian-festival lull), `_generate_anomalies()` (4–8 random multi-day cost bursts). |
| **Interactions** | Writes `data/raw/cloud_usage.csv`, `data/raw/saas_usage.csv`. |
| **If Removed** | Reproducibility breaks for new contributors. |
| **Dependencies** | `numpy`, `pandas`. Seeds `RNG_SEED = 42` so a single run is reproducible — but each new RUN injects different anomalies because the same seed re-randomises every call internally. |

### 2.2.13 — `/scripts/run_pipeline.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Sequential ETL runner: cloud pipeline → SaaS pipeline. |
| **Why** | Single entry point for cron/Airflow/GitHub Actions. |
| **Key methods** | `run_cloud_pipeline()`, `run_saas_pipeline()`, `main()` (returns exit code 0/1 for shell). |
| **Interactions** | Imports `src.pipeline.{ingest, clean, transform}`. Reads `data/raw/`. Writes `data/processed/`. |
| **If Removed** | Cron job has nothing to call. Models cannot be retrained on fresh data. |
| **Dependencies** | `src/pipeline/*`, `src/utils/logger`. Adds project root to `sys.path` so absolute imports work. |

### 2.2.14 — `/scripts/train_models.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Train all three ML models from the processed CSVs. |
| **Why** | Daily retrain absorbs new patterns + fights model drift. Cheap (<1s total). |
| **Key methods** | `main()` — reads both processed CSVs, calls each model's `train_*()`. |
| **Interactions** | Reads `data/processed/`. Writes `models/`. |
| **If Removed** | Models become stale. The bundled `.joblib` files would still serve until manually retrained. |
| **Dependencies** | `src.ml.{forecast, anomaly, license_classifier}`. |

### 2.2.15 — `/src/__init__.py`

Empty file. Marks `src/` as a Python package so `from src.api.main import app` works. **If removed**, every absolute import in the project breaks.

### 2.2.16 — `/src/api/__init__.py`, `/src/api/routes/__init__.py`, etc.

All empty. Same purpose — package markers.

### 2.2.17 — `/src/api/main.py`

| Field | Detail |
|-------|--------|
| **Purpose** | FastAPI application root: creates `app`, configures CORS, mounts routers, declares `/`, `/health`, attaches `lifespan` context manager. |
| **Key constants** | `app = FastAPI(title=..., version="0.1.0", lifespan=lifespan)`. |
| **CORS** | `allow_origins=["*"]`, `allow_methods=["GET"]`. Tightened in production to the dashboard's exact origin. |
| **Routers** | Mounts `routes.forecast.router`, `routes.anomalies.router`, `routes.recommendations.router`. |
| **APIs exposed** | `GET /` (welcome JSON), `GET /health` (HealthResponse model). |
| **If Removed** | The whole API ceases to exist. |
| **Dependencies** | `fastapi`, `src.api.routes.*`, `src.api.schemas`, `src.utils.logger`. |

### 2.2.18 — `/src/api/dependencies.py`

| Field | Detail |
|-------|--------|
| **Purpose** | LRU-cached DataFrame loaders shared by every route. |
| **Why** | Without caching, every request re-reads 49,000+ row CSVs from disk → 50ms+ wasted. With `@lru_cache(maxsize=1)`, first request warms the cache, all subsequent calls return in microseconds. |
| **Methods** | `get_cloud_data()`, `get_saas_data()`, `clear_cache()` (used in tests / after fresh ETL). |
| **Migration hook** | This is the **only file** you'd rewrite to swap CSV for Postgres. |
| **If Removed** | Every route fails with ImportError. |
| **Dependencies** | `pandas`, `functools.lru_cache`. |

### 2.2.19 — `/src/api/schemas.py`

| Field | Detail |
|-------|--------|
| **Purpose** | The API's **contract** — every request shape and every response shape. |
| **Models defined** | `ForecastPoint`, `ForecastResponse`, `AnomalyItem`, `AnomalyResponse`, `RecommendationItem`, `RecommendationsSummary`, `RecommendationsResponse`, `HealthResponse`. |
| **Why Pydantic** | Validates incoming queries automatically (`422` on bad input), auto-generates Swagger UI, gives downstream code real types instead of `dict`. |
| **If Removed** | All routes break — they declare `response_model=` referencing these classes. |
| **Dependencies** | `pydantic`. |

### 2.2.20 — `/src/api/routes/forecast.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Mount `GET /cost-forecast?days_ahead=N`. |
| **Validation** | `days_ahead: int = Query(30, ge=1, le=180)` — FastAPI auto-returns 422 on out-of-range. |
| **Flow** | Load cached cloud data → `forecast.predict_future_costs(df, days_ahead)` → build response. |
| **Error handling** | `FileNotFoundError` (no joblib) → 503 ; generic exception → 500 with logged stack trace. |
| **If Removed** | Cost trends page in dashboard fails. |
| **Dependencies** | `src.api.dependencies`, `src.ml.forecast`, `src.api.schemas`. |

### 2.2.21 — `/src/api/routes/anomalies.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Mount `GET /anomalies` — returns *all* anomalies in the dataset, oldest first. |
| **Flow** | Cached cloud data → `anomaly_model.detect_anomalies(df)` → format response. |
| **Error handling** | Same pattern as forecast. |
| **If Removed** | Anomalies dashboard page fails. |

### 2.2.22 — `/src/api/routes/recommendations.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Mount `GET /recommendations?top_n=&category=&severity=`. |
| **Filtering semantics** | Summary KPIs are computed over the **unfiltered** set so toggling filters doesn't make KPIs jump. Filters apply to the returned list only. |
| **Flow** | Cached cloud + SaaS → `engine.build_all_recommendations()` → `engine.summarize()` → optional category/severity filter → top_n slice → response. |
| **If Removed** | The whole recommendations dashboard collapses. |
| **Dependencies** | `src.api.dependencies`, `src.recommendations.engine`. |

### 2.2.23 — `/src/dashboard/app.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Streamlit **landing page** — title, health-check banner, 4 KPI metrics, two breakdown bar charts, top-5 expandable cards, sidebar hint. |
| **Key calls** | `fetch_health()`, `fetch_recommendations(top_n=500)`, `fetch_forecast(days_ahead=30)`. |
| **sys.path hack** | Streamlit doesn't add project root to `sys.path` by default — line 24 inserts it so `from src...` imports work. |
| **If Removed** | Streamlit cannot start. |
| **Dependencies** | `streamlit`, `pandas`, `src.dashboard.api_client`. |

### 2.2.24 — `/src/dashboard/api_client.py`

| Field | Detail |
|-------|--------|
| **Purpose** | The **only** module that talks to the FastAPI service. Wraps every endpoint with `@st.cache_data(ttl=60)` so a CFO clicking around doesn't trigger 50 redundant calls. |
| **Configuration** | `API_BASE_URL = os.getenv("FINOPS_API_URL", "http://localhost:8000")`. |
| **Error UX** | On ConnectionError shows a friendly `❌ Cannot reach the FinOps API…` banner via `st.error()` then halts execution with `st.stop()`. |
| **Migration hook** | Add auth headers in `_get()` and you've authenticated every page. |
| **If Removed** | Every dashboard page breaks. |

### 2.2.25 — `/src/dashboard/pages/1_📊_Cost_Trends.py`

| Field | Detail |
|-------|--------|
| **Purpose** | Forecast slider (7–90 days, step 7) + 3 KPI metrics + line chart + collapsible raw data table + model-limitation caveat. |
| **Streamlit page convention** | File name leading number controls sidebar order; emoji is rendered in the sidebar. |
| **If Removed** | Cost trends tab vanishes from sidebar (other pages unaffected). |

### 2.2.26 — `/src/dashboard/pages/2_🚨_Anomalies.py`

| Field | Detail |
|-------|--------|
| **Purpose** | 3 KPI metrics (days scored, anomalies detected, anomaly rate) + bar chart of anomalous days + expandable card per anomaly with cost / CPU / hours / weekend tag. |
| **Empty-state UX** | `st.success("✅ No anomalies detected…")` + `st.stop()`. |

### 2.2.27 — `/src/dashboard/pages/3_💡_Recommendations.py`

| Field | Detail |
|-------|--------|
| **Purpose** | The "do this list" — sidebar category + severity dropdowns + top-N slider + filtered KPI bar + expandable recommendation cards + CSV download button. |
| **CSV export** | Encodes UTF-8 with full reason/action text. |

### 2.2.28 — `/src/ml/forecast.py`

See Section 4.4 / Section 12 for deep dive. Trains `LinearRegression` on time features (`day_of_week`, `day_of_month`, `month`, `is_weekend`). Uses **time-aware** train/test split (last 20% chronologically as test) to avoid future-leak. Winsorises top 5% of training target (`y_train.clip(upper=cap)`) so spike days don't pull the regression line up.

### 2.2.29 — `/src/ml/anomaly.py`

Trains `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)` on daily aggregates (`daily_cost_inr`, `daily_avg_cpu`, `daily_hours`, `is_weekend`). Unsupervised — no labels, no train/test split.

### 2.2.30 — `/src/ml/license_classifier.py`

Trains `LogisticRegression(max_iter=1000)` with `StandardScaler` on features (`logins_last_30d`, `active_days_last_30d`, `days_since_last_login`, `monthly_cost_inr`). Uses **stratified** train/test split. Labels prefer the `truly_unused` ground-truth column; falls back to weak-supervision rule if missing.

### 2.2.31 — `/src/pipeline/ingest.py`

Schema-validated CSV reader. Defines `CLOUD_REQUIRED_COLS` and `SAAS_REQUIRED_COLS`. Throws `FileNotFoundError` if path missing, `ValueError` with diff if schema mismatched.

### 2.2.32 — `/src/pipeline/clean.py`

Cleaning rules:
- Drop exact duplicates (cloud) / drop on `(user_id, tool)` composite key (SaaS).
- Coerce date columns with `errors="coerce"` (NaT for bad).
- Coerce numeric columns with `errors="coerce"` (NaN for bad).
- Per-instance median fill for `cpu_utilization_avg` (1% telemetry-gap rate); fall back to 0.0.
- Clip negative `cost_inr` to 0 with warning.
- Lowercase + strip `region`, `environment`, `instance_type`.

### 2.2.33 — `/src/pipeline/transform.py`

Feature engineering. See Section 4.3 for column-by-column logic. Critically, **idle definition**: `is_idle_candidate = (avg_cpu < 5) AND (hours_running >= 20)`. **`daily_waste_inr`** = `cost_inr` if idle else `0.0`.

### 2.2.34 — `/src/recommendations/schema.py`

Pydantic `Recommendation` model (id, category, severity, title, reason, action, monthly_savings_inr, annual_savings_inr, confidence, entity, metadata). `severity_from_savings(monthly)`: high≥₹50k, medium≥₹10k, else low.

### 2.2.35 — `/src/recommendations/engine.py`

Four detectors + orchestrator:
- `detect_idle_instances(cloud_df)` — rule.
- `detect_rightsize_candidates(cloud_df)` — rule.
- `detect_unused_licenses(saas_df, threshold=0.7)` — ML.
- `detect_recent_anomalies(cloud_df, lookback_days=14)` — ML.
- `build_all_recommendations()` — unions + sorts by (severity, -annual_savings, -confidence).
- `summarize()` — totals, counts by severity, counts by category.

### 2.2.36 — `/src/utils/logger.py`

`get_logger(name)` → returns a `logging.Logger` with INFO level, `%(asctime)s %(levelname)s %(name)s: %(message)s` format, `sys.stdout` handler, `propagate=False`. Idempotent — re-calling with the same name returns the same logger without adding duplicate handlers.

---

# SECTION 3 — FRONTEND DEEP ANALYSIS (Streamlit Dashboard)

## 3.1 Frontend Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  STREAMLIT MULTI-PAGE APP                                        │
│  Entry point: streamlit run src/dashboard/app.py                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  app.py (landing)                                          │ │
│  │   ├── set_page_config(layout="wide")                        │ │
│  │   ├── Health banner ── fetch_health()                       │ │
│  │   ├── KPI tiles ── fetch_recommendations(top_n=500)         │ │
│  │   ├── Forecast tile ── fetch_forecast(days_ahead=30)        │ │
│  │   ├── 2 bar charts (by_category, by_severity)               │ │
│  │   └── Top 5 expanders                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Auto-discovered pages (sidebar):                                │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐       │
│  │ 1_📊_Cost…     │ │ 2_🚨_Anomalies │ │ 3_💡_Reco…     │       │
│  └────────────────┘ └────────────────┘ └────────────────┘       │
│                                                                  │
│  Shared service module:                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  api_client.py                                              │ │
│  │   ├── _get(path, params) — requests.get + timeout + errors │ │
│  │   ├── fetch_health()       @st.cache_data(ttl=60)          │ │
│  │   ├── fetch_forecast(N)    @st.cache_data(ttl=60)          │ │
│  │   ├── fetch_anomalies()    @st.cache_data(ttl=60)          │ │
│  │   └── fetch_recommendations(category, severity, top_n)     │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## 3.2 Component Hierarchy

Streamlit doesn't have a "component" abstraction in the React sense — every page is a top-to-bottom Python script that runs end-to-end on every rerun. The closest unit of reuse is **functions in `api_client.py`** + **st.cache_data** decoration.

```
Page Tree
└── app.py (landing)
    ├── st.set_page_config           ← must be first call
    ├── st.title + st.caption
    ├── Health banner block
    ├── KPI row (st.columns(4))
    ├── Charts row (st.columns(2))
    │   ├── Left: by_category bar chart
    │   └── Right: by_severity bar chart
    └── Top 5 (for rec in top5: st.expander(...))
└── pages/1_📊_Cost_Trends.py
    ├── st.slider (forecast horizon)
    ├── KPI row (st.columns(3))
    ├── st.line_chart
    └── st.expander (raw data table) + st.info caveat
└── pages/2_🚨_Anomalies.py
    ├── KPI row (st.columns(3))
    ├── st.bar_chart (anomalous days)
    └── for anomaly: st.expander with 3-column metric grid
└── pages/3_💡_Recommendations.py
    ├── Sidebar: 2× st.selectbox + st.slider
    ├── KPI row (st.columns(4))
    ├── for rec: st.expander → st.columns([2,1])
    └── st.download_button (CSV export)
```

## 3.3 Routing System

Streamlit **auto-discovers** any `.py` file under `pages/` and adds it to the sidebar in **filename order**. Convention used here:

- `1_📊_Cost_Trends.py` → "📊 Cost Trends" appears first.
- `2_🚨_Anomalies.py` → "🚨 Anomalies" appears second.
- `3_💡_Recommendations.py` → "💡 Recommendations" appears third.

The leading number determines ordering; the emoji and underscore-separated name become the human-readable label. Filename `__init__.py` is excluded.

There is no programmatic router. Navigation = user clicking sidebar entries.

## 3.4 State Management

Streamlit's execution model: **the script reruns top-to-bottom on every interaction**. State management options:

1. **`st.cache_data(ttl=60)`** — function memoisation across reruns. Used aggressively in `api_client.py` to avoid hammering the API on every slider tick.
2. **`st.session_state`** — *not used* in this project; everything is stateless except for the cache.
3. **Sidebar widgets** — return their current value on every rerun; that's the "state" each page reads.

## 3.5 API Integration Flow

```
User interaction in browser
    │
    ▼
Streamlit rerun (whole page script re-executes)
    │
    ▼
api_client.fetch_X(args)
    ├── If args were called before within last 60s:
    │     └── return cached dict
    └── Else:
          ├── requests.get(API_BASE_URL + path, params=…, timeout=10)
          ├── On ConnectionError → st.error + st.stop
          ├── On HTTPError → st.error + st.stop
          ├── On Timeout → st.error + st.stop
          └── On success → resp.raise_for_status; return resp.json()
```

## 3.6 Authentication Flow

**v0.1.0: none.** Future: see Section 14. Recommended flow (planned):
1. Streamlit `st.text_input(type="password")` POSTs to `/auth/token`.
2. JWT stored in `st.session_state["token"]`.
3. `api_client._get()` adds `Authorization: Bearer <token>` header.

## 3.7 Form Handling

The dashboard is read-only — there are no forms in v0.1.0. The closest equivalent is:
- `st.selectbox("Category", ...)` and `st.selectbox("Severity", ...)` in recommendations sidebar.
- `st.slider("Forecast horizon (days)", min=7, max=90, value=30, step=7)`.
- `st.slider("Max items", 5, 200, 50, step=5)`.

Each widget reruns the script on change → `api_client.fetch_recommendations(...)` is called with new args → response renders.

## 3.8 Validation Logic

All validation happens server-side via Pydantic + FastAPI's `Query(ge=…, le=…)`. The frontend trusts these constraints (slider min/max already prevents out-of-range input from reaching the API).

## 3.9 Error Handling

`api_client._get()` is the single funnel:

```python
try:
    resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()
except requests.exceptions.ConnectionError:
    msg = f"Cannot reach the FinOps API at {API_BASE_URL}. Is uvicorn running?"
except requests.exceptions.HTTPError as e:
    msg = f"API returned {e.response.status_code}: {e.response.text}"
except requests.exceptions.Timeout:
    msg = f"API call to {url} timed out after {REQUEST_TIMEOUT_S}s"

st.error(f"❌ {msg}")
st.stop()                            # halt the page render
raise RuntimeError(msg)              # safety net so callers don't see None
```

## 3.10 Reusable Components

None in the React sense. Reuse is via `api_client` functions and pandas DataFrames passed to `st.dataframe` / `st.bar_chart` / `st.line_chart`.

## 3.11 Styling Architecture

- No CSS file. Streamlit's default theme is used.
- Wide-layout: `st.set_page_config(layout="wide")` on every page.
- Severity emojis: `{"high":"🔴", "medium":"🟡", "low":"🟢"}`.
- Currency formatting: f-strings with `f"₹{x:,.0f}"`.

## 3.12 Build Configuration

Streamlit has no build step — it runs the `.py` file directly.

Optional production config in `~/.streamlit/config.toml` (not committed):
```toml
[server]
port = 8501
headless = true
enableCORS = false

[browser]
gatherUsageStats = false
```

## 3.13 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FINOPS_API_URL` | Base URL of the FastAPI service | `http://localhost:8000` |

Set with `export FINOPS_API_URL=https://api.finops.internal` before running `streamlit run`.

## 3.14 Performance Optimizations

| Optimization | Implementation | Effect |
|--------------|----------------|--------|
| API call memoisation | `@st.cache_data(ttl=60)` on every `fetch_X()` | Page renders feel instant once cache is warm |
| Aggressive `top_n=500` on landing | Single API call drives 4 KPI tiles | Avoids 4 separate round-trips |
| Lazy expanders | `st.expander(expanded=False)` | Detail markdown only renders if user opens |
| API-side summary stats | `engine.summarize()` runs on the API, not in the browser | Sub-50ms KPI computation |

## 3.15 Rendering Flow

```
1. User hits http://localhost:8501
2. Streamlit boots, executes app.py top-to-bottom
3. st.set_page_config (must be first)
4. Header (st.title, st.caption)
5. Health banner ── fetch_health()
6. KPI tiles  ── fetch_recommendations(top_n=500), fetch_forecast(30)
7. Charts row
8. Top 5 expanders
9. Footer caption
10. (Streamlit handles WebSocket push of all rendered widgets to browser)
11. User clicks sidebar "Cost Trends"
12. Streamlit unloads app.py, loads pages/1_📊_Cost_Trends.py top-to-bottom
13. Same pattern: fetch_forecast(days_ahead=slider.value), render chart
14. User moves slider → script reruns → cache lookup → if expired, refetch
```

## 3.16 Important Hooks/Functions

| Function | File | Role |
|----------|------|------|
| `_get(path, params)` | `api_client.py` | Generic HTTP GET with error funnel |
| `fetch_health()` | `api_client.py` | `GET /health`, 60s cache |
| `fetch_forecast(days_ahead)` | `api_client.py` | `GET /cost-forecast?days_ahead=N`, 60s cache |
| `fetch_anomalies()` | `api_client.py` | `GET /anomalies`, 60s cache |
| `fetch_recommendations(category, severity, top_n)` | `api_client.py` | `GET /recommendations?…`, 60s cache |

## 3.17 Component-by-Component Inventory

### Component: Landing-Page KPI Tiles (`app.py`, lines 63–85)

| Field | Detail |
|-------|--------|
| **Purpose** | Top-of-page metric strip — Total Recommendations, Potential Monthly Savings, Potential Annual Savings (+ high-severity delta), Forecasted Next 30 Days |
| **Props** | None — pure render |
| **State variables** | `recs`, `summary`, `forecast` (Python locals, not session_state) |
| **Lifecycle** | Executes top-to-bottom on every rerun |
| **API calls** | `fetch_recommendations(top_n=500)`, `fetch_forecast(days_ahead=30)` |
| **Backend dependency** | `/recommendations`, `/cost-forecast` |

### Component: Top-5 Expanders (`app.py`, lines 119–140)

| Field | Detail |
|-------|--------|
| **Purpose** | The "act on these Monday morning" list — 5 highest-savings recommendations |
| **Props** | `recs["recommendations"][:5]` from `/recommendations` |
| **User interaction** | Click expander → markdown reason/action + metric tiles render |
| **Backend dependency** | `/recommendations` |

### Component: Cost Trends Slider + Chart (`pages/1_…`)

| Field | Detail |
|-------|--------|
| **Purpose** | Interactive forecast horizon control + line chart |
| **State** | `days_ahead` from slider |
| **API calls** | `fetch_forecast(days_ahead=days_ahead)` |
| **Render** | `st.line_chart(df.set_index("date")["predicted_cost_inr"], height=400)` |

### Component: Anomalies Cards (`pages/2_…`)

| Field | Detail |
|-------|--------|
| **Purpose** | Per-anomaly metric cards |
| **API calls** | `fetch_anomalies()` |
| **Empty state** | `st.success("✅ No anomalies…")` + `st.stop()` |

### Component: Recommendations Filters + CSV (`pages/3_…`)

| Field | Detail |
|-------|--------|
| **Purpose** | The FinOps analyst's daily workspace |
| **Props** | `category_options`, `severity_options`, `top_n` |
| **API calls** | `fetch_recommendations(category, severity, top_n)` |
| **CSV export** | `df_export.to_csv(index=False).encode("utf-8")` → `st.download_button` |

---

# SECTION 4 — BACKEND DEEP ANALYSIS (FastAPI + ML + Pipeline)

## 4.1 Backend Architecture

Three logical layers + an orchestrator:

```
┌──────────────────────────────────────────────────────────────────────┐
│ API LAYER       │  FastAPI app, routers, Pydantic schemas             │
│                 │  src/api/{main, dependencies, schemas, routes/*}    │
├──────────────────────────────────────────────────────────────────────┤
│ ENGINE LAYER    │  Rule + ML detectors, unified Recommendation model  │
│                 │  src/recommendations/{engine, schema}               │
├──────────────────────────────────────────────────────────────────────┤
│ ML LAYER        │  Three trained models + train/predict helpers       │
│                 │  src/ml/{forecast, anomaly, license_classifier}     │
├──────────────────────────────────────────────────────────────────────┤
│ PIPELINE LAYER  │  ETL (ingest → clean → transform)                   │
│                 │  src/pipeline/{ingest, clean, transform}            │
├──────────────────────────────────────────────────────────────────────┤
│ UTILS           │  src/utils/logger                                    │
└──────────────────────────────────────────────────────────────────────┘
```

## 4.2 Layered Architecture (Request-Response Flow)

```
Request: GET /recommendations?top_n=10&severity=high
    │
    ▼
[FastAPI/uvicorn process]
    │
    ▼
[CORS middleware]
    │
    ▼
[Routing: APIRouter prefix=/recommendations]
    │
    ▼
[Validation: Query(ge=1, le=500), category? severity?]
    │
    ▼
[Handler: get_recommendations()]
    │
    ├─── dependencies.get_cloud_data() ─── lru_cache → pd.DataFrame
    │
    ├─── dependencies.get_saas_data()  ─── lru_cache → pd.DataFrame
    │
    ├─── engine.build_all_recommendations(cloud_df, saas_df)
    │      ├── detect_idle_instances(cloud_df)       (rule)
    │      ├── detect_rightsize_candidates(cloud_df) (rule)
    │      ├── detect_unused_licenses(saas_df)       (ML — joblib)
    │      └── detect_recent_anomalies(cloud_df)     (ML — joblib)
    │
    ├─── engine.summarize(all_recs)
    │
    ├─── Apply optional category filter
    ├─── Apply optional severity filter
    └─── Slice [:top_n]
    │
    ▼
[Response model: RecommendationsResponse]
    │
    ▼
[FastAPI JSON serialiser]
    │
    ▼
Response: 200 OK {summary: {...}, recommendations: [...]}
```

## 4.3 Pipeline Layer Deep Dive

### `src/pipeline/ingest.py`

```python
CLOUD_REQUIRED_COLS = {"date", "instance_id", "instance_type", "region",
                       "environment", "cpu_utilization_avg",
                       "cpu_utilization_max", "hours_running", "cost_inr"}
SAAS_REQUIRED_COLS  = {"user_id", "employee_name", "department", "tool",
                       "license_type", "monthly_cost_inr", "logins_last_30d",
                       "active_days_last_30d", "last_login_date", "assigned_date"}
```

**Method `_read_csv(path, required_cols)`:**
1. Check file exists → `FileNotFoundError`.
2. `pd.read_csv(path)`.
3. Diff `required_cols - set(df.columns)` → `ValueError("missing required columns: [...]")` with full diagnostic.
4. Log row count.

**Methods `load_cloud_usage(path=None)` / `load_saas_usage(path=None)`** — thin wrappers with default paths under `data/raw/`.

### `src/pipeline/clean.py`

`clean_cloud_usage(df)`:
| Step | Code | Why |
|------|------|-----|
| 1. Dedup | `df = df.drop_duplicates()` | Generator deliberately injects 50 duplicates |
| 2. Date parse | `pd.to_datetime(df["date"], errors="coerce")` | NaT for unparseable; drop those |
| 3. Numeric coerce | `pd.to_numeric(..., errors="coerce")` on 4 cols | Survive garbage strings |
| 4. String normalize | `.str.strip().str.lower()` on region/env/type | "US-EAST-1" → "us-east-1" |
| 5. Null fill | `.groupby("instance_id").transform(lambda s: s.fillna(s.median()))` | Per-instance median preserves per-instance baseline |
| 6. Fallback | `.fillna(0.0)` | Edge case: an instance with all-NaN CPU |
| 7. Cost clip | `.clip(lower=0)` | Negative costs (refunds) treated as 0 |

`clean_saas_usage(df)`:
| Step | Code |
|------|------|
| Dedup on `(user_id, tool)` composite key | `df.drop_duplicates(subset=["user_id", "tool"])` |
| Date parse on `last_login_date`, `assigned_date` | `pd.to_datetime(..., errors="coerce")` |
| Numeric int coerce on cost + login counts | `.fillna(0).astype(int)` |
| String strip on department, tool, license_type | `.astype(str).str.strip()` |

### `src/pipeline/transform.py`

`transform_cloud_usage(df)`:
| Output Column | Logic |
|---------------|-------|
| `day_of_week` | `df["date"].dt.dayofweek` (0=Mon, 6=Sun) |
| `month` | `df["date"].dt.month` |
| `is_weekend` | `(day_of_week >= 5).astype(int)` |
| `utilization_band` | Custom band: <5 idle, <20 low, <70 normal, else high |
| `is_idle_candidate` | `(cpu_avg < 5) & (hours_running >= 20)` |
| `daily_waste_inr` | `cost_inr` if idle_candidate else `0.0` |

`transform_saas_usage(df, today=None)`:
| Output Column | Logic |
|---------------|-------|
| `has_ever_logged_in` | `last_login_date.notna()` |
| `days_since_last_login` | `(today - last_login).dt.days`; NaT → 999 |
| `usage_category` | `unused` if 0 logins; `low` if <3 active days; else `active` |
| `annual_cost_inr` | `monthly_cost_inr * 12` |
| `is_recommendation_candidate` | `usage_category in {"unused", "low"}` |

## 4.4 ML Layer Deep Dive

### `src/ml/forecast.py`

**Trainer `train_forecast_model(df)`:**

```python
FEATURE_COLS = ["day_of_week", "day_of_month", "month", "is_weekend"]
```

1. `_build_features(df)` aggregates per-instance rows to daily totals.
2. Time-aware split — last 20% chronologically is test.
3. **Winsorise training target** — `y_train = y_train.clip(upper=y_train.quantile(0.95))`. Reason: spike days bias the regression line up if left in; the forecaster is a *baseline* predictor and the anomaly detector handles spikes.
4. Fit `LinearRegression().fit(X_train, y_train)`.
5. Compute MAE, R², MAPE on the (un-winsorised) test set.
6. Persist `{"model": …, "feature_cols": …, "min_date": …, "metrics": {...}}` to `models/forecast_model.joblib`.

**Predictor `predict_future_costs(df, days_ahead)`:**

1. Load joblib bundle.
2. Build feature rows for the next `days_ahead` calendar days.
3. `model.predict(features)`.
4. `.clip(lower=0)` — costs cannot be negative even if the linear trend is downward.
5. Return `DataFrame[date, predicted_cost_inr]`.

### `src/ml/anomaly.py`

**Trainer `train_anomaly_model(df)`:**

```python
ANOMALY_FEATURE_COLS = ["daily_cost_inr", "daily_avg_cpu",
                        "daily_hours", "is_weekend"]
CONTAMINATION = 0.05
```

1. Aggregate per-instance rows to daily summary (sum of cost, mean of CPU, sum of hours).
2. Add `is_weekend`.
3. Fit `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)`.
4. Score training data, count flags. Persist.

**Predictor `detect_anomalies(df)`:**

1. Load model.
2. Re-aggregate.
3. `model.decision_function(X)` → continuous anomaly score (lower = more anomalous).
4. `model.predict(X) == -1` → boolean flag (sklearn convention: outlier = -1).
5. Return only the anomalous rows, sorted by date, rounded for API neatness.

### `src/ml/license_classifier.py`

```python
LICENSE_FEATURE_COLS = ["logins_last_30d", "active_days_last_30d",
                        "days_since_last_login", "monthly_cost_inr"]
```

**Label source `_create_labels(df)`:**

```python
if "truly_unused" in df.columns:
    return df["truly_unused"].astype(int)
return (
    (df["logins_last_30d"] == 0) |
    ((df["active_days_last_30d"] <= 1) & (df["days_since_last_login"] > 30))
).astype(int)
```

Prefers the ground-truth `truly_unused` column emitted by the data generator. Falls back to a deterministic weak-supervision rule for backward compatibility with legacy datasets.

**Trainer `train_license_classifier(df)`:**

1. Build labels.
2. **Stratified** train/test split (20%) — preserves class balance.
3. `StandardScaler.fit_transform(X_train)`. Without scaling, `monthly_cost_inr` (1000s) would dominate `logins_last_30d` (10s).
4. `LogisticRegression(max_iter=1000, random_state=42).fit(X_train_scaled, y_train)`.
5. Compute AUC, classification report.
6. Persist `{model, scaler, feature_cols, metrics}`.

**Predictor `predict_revoke_candidates(df, threshold=0.5)`:**

1. Load bundle, transform features through the saved scaler.
2. `predict_proba(X)[:, 1]` → revoke probability.
3. Filter rows where probability ≥ threshold, sort descending.

## 4.5 Recommendation Engine Deep Dive

### `src/recommendations/schema.py`

```python
HIGH_THRESHOLD = 50_000
MEDIUM_THRESHOLD = 10_000

def severity_from_savings(monthly_savings_inr: float) -> Severity:
    if monthly_savings_inr >= HIGH_THRESHOLD:    return "high"
    if monthly_savings_inr >= MEDIUM_THRESHOLD:  return "medium"
    return "low"
```

`class Recommendation(BaseModel)`:
- `id` — unique key (e.g. `rec_idle_i-prod-0001`)
- `category` — Literal of 4
- `severity` — Literal of 3
- `title`, `reason`, `action` — human-readable
- `monthly_savings_inr`, `annual_savings_inr` — financial impact
- `confidence: float = Field(ge=0.0, le=1.0)` — rule = 1.0, ML = `predict_proba`
- `entity` — instance id / user id / date
- `metadata: dict` — extension bag

### `src/recommendations/engine.py`

**`detect_idle_instances(cloud_df)`** — rule-based:
1. Filter to last 30 days.
2. Per-instance aggregate: `avg_cpu`, `total_cost`, `idle_days = sum(is_idle_candidate)`, `total_days`.
3. Compute `idle_ratio = idle_days / total_days`.
4. Keep where `idle_ratio >= 0.8 AND avg_cpu < 5`.
5. Emit one Recommendation per match.
6. Confidence fixed at `1.0` (rule).

**`detect_rightsize_candidates(cloud_df)`** — rule-based:
1. Last 30 days, per-instance avg CPU + total cost.
2. Keep where `5 <= avg_cpu < 20` AND `instance_type != "t3.medium"` (smallest tier — can't downsize further).
3. Monthly savings = `total_cost * 0.5` (going one tier smaller ≈ halves price).
4. Confidence `0.8` — rightsizing always needs load-test validation.

**`detect_unused_licenses(saas_df, threshold=0.7)`** — ML-based:
1. Call `license_classifier.predict_revoke_candidates(df, threshold=0.7)`.
2. Build a reason string that varies if `logins_last_30d == 0` vs >0.
3. Confidence = the model's `revoke_probability`.

**`detect_recent_anomalies(cloud_df, lookback_days=14)`** — ML-based:
1. Call `anomaly_model.detect_anomalies(df)`.
2. Filter to last 14 days.
3. Monthly/annual savings set to `0.0` (an anomaly is a *diagnostic*, not a fix).
4. Confidence = `min(1.0, abs(anomaly_score) * 5)` — heuristic conversion from sklearn's continuous score to 0–1.

**`build_all_recommendations(cloud_df, saas_df)`** — orchestrator:
1. Union all four detector outputs.
2. Sort by `(SEVERITY_ORDER[r.severity], -r.annual_savings_inr, -r.confidence)`.
3. Log total count.

**`summarize(recs)`** — pure aggregation, returns `dict` ready to JSON-serialise.

## 4.6 API Layer Deep Dive

### `src/api/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("FinOps API starting up")
    yield
    log.info("FinOps API shutting down")

app = FastAPI(
    title="AI FinOps Platform API",
    description="Cost forecasting, anomaly detection, and savings recommendations...",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

app.include_router(forecast.router)
app.include_router(anomalies.router)
app.include_router(recommendations.router)
```

`@app.get("/")` — landing JSON with endpoint list.
`@app.get("/health")` — checks 3 joblib files + processed CSV mtime → `HealthResponse(status, models_loaded, data_freshness)`.

### `src/api/dependencies.py`

```python
@lru_cache(maxsize=1)
def get_cloud_data() -> pd.DataFrame:
    path = PROCESSED_DIR / "cloud_usage_processed.csv"
    if not path.exists():
        raise FileNotFoundError(f"... Run scripts/run_pipeline.py first.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df
```

The `lru_cache` is **per-process** — important for multi-worker uvicorn deployment.

### `src/api/schemas.py`

Pydantic v2 BaseModel classes. Every numerical field is `float`; dates are `datetime.date`. Booleans (`is_weekend`) are real `bool`. The `metadata: dict = {}` default allows free-form extension without breaking the contract.

## 4.7 Middleware / Interceptors

- **CORSMiddleware** — only middleware in v0.1.0. Configured open-handed (`allow_origins=["*"]`) for dev.
- Recommended additions (Section 14): request-ID middleware, prometheus middleware, auth middleware.

## 4.8 Authentication & Authorization

Not implemented in v0.1.0. See Section 7.

## 4.9 Security Implementation

| Concern | v0.1.0 Status |
|---------|---------------|
| HTTPS | Out of scope — handled by reverse proxy in production |
| Input validation | ✅ Pydantic + `Query(ge=, le=)` |
| SQL injection | ✅ N/A — no SQL in v0.1.0 |
| XSS | ✅ Streamlit auto-escapes by default |
| CSRF | ⚠️ Not applicable to GET-only API |
| Rate limiting | ❌ Not implemented |
| AuthN/AuthZ | ❌ Not implemented |

## 4.10 Exception Handling

Per-route pattern:
```python
try:
    ... heavy lifting ...
except FileNotFoundError as e:
    raise HTTPException(status_code=503, detail=str(e))
except Exception:
    log.exception("...")
    raise HTTPException(status_code=500, detail="...")
```
- `503 Service Unavailable` for missing data/models (operator should run `run_pipeline.py` + `train_models.py`).
- `500 Internal Server Error` for everything else, with full stack trace logged via `log.exception`.
- `422 Unprocessable Entity` auto-returned by FastAPI on bad query types.

## 4.11 Logging

`src/utils/logger.get_logger(name)` is the only logger factory.

Format: `[YYYY-MM-DD HH:MM:SS] INFO  module.name: message`

Examples:
```
[2026-05-28 02:00:14] INFO  pipeline: === CLOUD PIPELINE START ===
[2026-05-28 02:00:14] INFO  src.pipeline.ingest: Loaded 49,150 rows from cloud_usage.csv
[2026-05-28 02:00:14] INFO  src.pipeline.clean: Dropped 50 duplicate cloud rows
[2026-05-28 02:00:15] INFO  src.pipeline.transform: Transformed cloud: 49,100 rows | idle rows = 7,512 | est. waste = Rs.482,310.50
```

## 4.12 Validation

- **API boundary** — Pydantic + `Query`.
- **Pipeline boundary** — `CLOUD_REQUIRED_COLS` / `SAAS_REQUIRED_COLS` set-diff in `_read_csv`.
- **Internal** — none (trusting our own modules).

## 4.13 Configuration Management

- Hardcoded constants live next to the code that uses them (`HIGH_THRESHOLD`, `CONTAMINATION = 0.05`, etc.).
- The only env var is `FINOPS_API_URL` (read in `api_client.py`).
- A real config system (`pydantic-settings` or `dynaconf`) is in the roadmap.

## 4.14 Dependency Injection

FastAPI's `Depends()` is **not used**. Each route directly imports `get_cloud_data` / `get_saas_data` from `dependencies.py`. Tests can inject by patching the cache or calling `clear_cache()`.

## 4.15 Microservice Communication

**v0.1.0 is a monolith** — there are no microservices. The dashboard ↔ API split is an HTTP boundary, not a microservice boundary (no service discovery, no message queue).

## 4.16 API Gateway Logic

None. uvicorn handles ingress directly. In production you'd front with nginx / AWS ALB / GCP Cloud Run.

## 4.17 Service Discovery

None. URLs are hardcoded with env-var override.

## 4.18 Async Processing

FastAPI is async-capable, but all route handlers in this project are synchronous (`def`, not `async def`). Reason: the workload is pandas / joblib / sklearn, all of which are CPU-bound + GIL-bound. Async syntax wouldn't help. uvicorn handles concurrency by running multiple sync workers.

## 4.19 Thread Handling

Single-threaded per worker. Use `--workers N` (production) to parallelise.

## 4.20 Transaction Management

N/A — no database in v0.1.0. CSV writes in the pipeline are not transactional but are atomic at the OS level (pandas writes to a temp + renames, broadly).

## 4.21 Backend File-by-File Summary (Methods → Inputs → Outputs)

| File | Method | Inputs | Outputs | Side Effects |
|------|--------|--------|---------|--------------|
| `pipeline/ingest.py` | `load_cloud_usage(path=None)` | optional Path | `pd.DataFrame` (validated schema) | reads CSV, logs |
| `pipeline/ingest.py` | `load_saas_usage(path=None)` | optional Path | `pd.DataFrame` | reads CSV, logs |
| `pipeline/clean.py` | `clean_cloud_usage(df)` | raw cloud df | cleaned df | logs |
| `pipeline/clean.py` | `clean_saas_usage(df)` | raw SaaS df | cleaned df | logs |
| `pipeline/transform.py` | `transform_cloud_usage(df)` | cleaned cloud df | df + 6 new cols | logs |
| `pipeline/transform.py` | `transform_saas_usage(df, today=None)` | cleaned SaaS df | df + 5 new cols | logs |
| `ml/forecast.py` | `train_forecast_model(df)` | processed cloud df | metrics dict | writes `forecast_model.joblib` |
| `ml/forecast.py` | `predict_future_costs(df, days_ahead=30)` | processed cloud df, int | `DataFrame[date, predicted_cost_inr]` | reads joblib |
| `ml/anomaly.py` | `train_anomaly_model(df)` | processed cloud df | metrics dict | writes `anomaly_model.joblib` |
| `ml/anomaly.py` | `detect_anomalies(df)` | processed cloud df | df of anomalous days | reads joblib |
| `ml/license_classifier.py` | `train_license_classifier(df)` | processed SaaS df | metrics dict | writes `license_classifier.joblib` |
| `ml/license_classifier.py` | `predict_revoke_candidates(df, threshold=0.5)` | processed SaaS df, float | df of candidates | reads joblib |
| `recommendations/engine.py` | `detect_idle_instances(cloud_df)` | cloud df | `List[Recommendation]` | logs |
| `recommendations/engine.py` | `detect_rightsize_candidates(cloud_df)` | cloud df | `List[Recommendation]` | logs |
| `recommendations/engine.py` | `detect_unused_licenses(saas_df, threshold=0.7)` | SaaS df, float | `List[Recommendation]` | calls joblib |
| `recommendations/engine.py` | `detect_recent_anomalies(cloud_df, lookback_days=14)` | cloud df, int | `List[Recommendation]` | calls joblib |
| `recommendations/engine.py` | `build_all_recommendations(cloud_df, saas_df)` | both dfs | sorted `List[Recommendation]` | logs |
| `recommendations/engine.py` | `summarize(recs)` | List | summary dict | — |
| `api/dependencies.py` | `get_cloud_data()` | — | cached df | reads CSV (first call) |
| `api/dependencies.py` | `get_saas_data()` | — | cached df | reads CSV (first call) |
| `api/dependencies.py` | `clear_cache()` | — | — | invalidates lru_cache |

---

# SECTION 5 — DATABASE / DATA LAYER DOCUMENTATION

## 5.1 Current State: Filesystem as Database

v0.1.0 uses **CSV files as the source of truth**:

```
data/raw/cloud_usage.csv           ← "source system" extract (49,000 rows)
data/raw/saas_usage.csv            ← "source system" extract (3,100 rows)
data/processed/cloud_usage_processed.csv  ← ETL output (read by API)
data/processed/saas_usage_processed.csv   ← ETL output (read by API)
```

This is by design: the dependency stub for the real database (`psycopg2-binary`, `sqlalchemy`) is already pinned in `requirements.txt`, and `dependencies.py` is the single file that hides the swap.

## 5.2 Logical ER Diagram (As-If Postgres)

```
┌───────────────────────────────┐           ┌──────────────────────────┐
│  cloud_usage (fact)           │           │  instances (dim)         │
│ ───────────────────────────── │           │ ──────────────────────── │
│  PK  (date, instance_id)      │     ┌──┐  │  PK  instance_id         │
│      date            DATE     │ ◀───┤FK├──┤      instance_type       │
│      instance_id     VARCHAR  │     └──┘  │      region              │
│      cpu_utilization_avg NUM  │           │      environment         │
│      cpu_utilization_max NUM  │           │      launched_date       │
│      hours_running   INT      │           │      terminated_date     │
│      cost_compute_inr NUM     │           └──────────────────────────┘
│      cost_storage_inr NUM     │
│      cost_transfer_inr NUM    │
│      cost_other_inr  NUM      │
│      cost_inr        NUM      │
└───────────────────────────────┘

┌───────────────────────────────┐           ┌──────────────────────────┐
│  saas_usage (fact)            │           │  employees (dim)         │
│ ───────────────────────────── │           │ ──────────────────────── │
│  PK  (user_id, tool)          │     ┌──┐  │  PK  user_id             │
│      user_id         VARCHAR  │ ◀───┤FK├──┤      employee_name       │
│      tool            VARCHAR  │     └──┘  │      department          │
│      license_type    VARCHAR  │           └──────────────────────────┘
│      monthly_cost_inr NUM     │
│      logins_last_30d INT      │           ┌──────────────────────────┐
│      active_days_last_30d INT │           │  saas_catalog (dim)      │
│      last_login_date DATE     │     ┌──┐  │ ──────────────────────── │
│      assigned_date   DATE     │ ◀───┤FK├──┤  PK  tool                │
│      truly_unused    BOOL     │     └──┘  │      base_cost           │
└───────────────────────────────┘           │      primary_dept_list   │
                                            └──────────────────────────┘

┌─────────────────────────────────────────┐
│  recommendations (output)               │
│ ─────────────────────────────────────── │
│  PK  id                                 │
│      category   ENUM                    │
│      severity   ENUM                    │
│      title      TEXT                    │
│      reason     TEXT                    │
│      action     TEXT                    │
│      monthly_savings_inr NUM            │
│      annual_savings_inr  NUM            │
│      confidence NUM (0..1)              │
│      entity     VARCHAR                 │
│      metadata   JSONB                   │
│      created_at TIMESTAMP               │
└─────────────────────────────────────────┘
```

## 5.3 All Tables (Logical View)

### Table: `cloud_usage` (raw fact)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `date` | DATE | NOT NULL | Day of the observation |
| `instance_id` | VARCHAR(50) | NOT NULL | e.g. `i-prod-0001` |
| `instance_type` | VARCHAR(50) | NOT NULL | e.g. `m5.4xlarge` |
| `region` | VARCHAR(50) | NOT NULL | e.g. `ap-south-1` |
| `environment` | VARCHAR(20) | NOT NULL | `prod`/`dev`/`staging`/`test` |
| `cpu_utilization_avg` | NUMERIC(5,2) | NULL OK | 0–100 |
| `cpu_utilization_max` | NUMERIC(5,2) | NOT NULL | 0–100 |
| `hours_running` | INT | NOT NULL | 0–24 |
| `cost_compute_inr` | NUMERIC(12,2) | ≥0 | |
| `cost_storage_inr` | NUMERIC(12,2) | ≥0 | |
| `cost_transfer_inr` | NUMERIC(12,2) | ≥0 | |
| `cost_other_inr` | NUMERIC(12,2) | ≥0 | |
| `cost_inr` | NUMERIC(12,2) | ≥0 | total |
| **PK** | (date, instance_id) | | composite |

### Table: `cloud_usage_processed` (transformed)

Adds: `day_of_week INT`, `month INT`, `is_weekend INT`, `utilization_band VARCHAR(10)`, `is_idle_candidate BOOL`, `daily_waste_inr NUMERIC`.

### Table: `saas_usage` (raw fact)

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | VARCHAR | e.g. `u-00001` |
| `employee_name` | VARCHAR | display string |
| `department` | VARCHAR | Sales/Eng/HR/etc |
| `tool` | VARCHAR | Salesforce/Slack/Jira/… |
| `license_type` | VARCHAR | Standard/Premium/Enterprise |
| `monthly_cost_inr` | NUMERIC | |
| `logins_last_30d` | INT | |
| `active_days_last_30d` | INT | |
| `last_login_date` | DATE | NULL if never |
| `assigned_date` | DATE | |
| `truly_unused` | BOOL/INT | ground truth |
| **PK** | (user_id, tool) | composite |

### Table: `saas_usage_processed` (transformed)

Adds: `has_ever_logged_in BOOL`, `days_since_last_login INT`, `usage_category VARCHAR`, `annual_cost_inr NUMERIC`, `is_recommendation_candidate BOOL`.

## 5.4 Indexes (Recommended for Postgres Migration)

```sql
CREATE INDEX idx_cloud_date              ON cloud_usage_processed(date);
CREATE INDEX idx_cloud_instance_date     ON cloud_usage_processed(instance_id, date);
CREATE INDEX idx_cloud_idle              ON cloud_usage_processed(is_idle_candidate) WHERE is_idle_candidate;
CREATE INDEX idx_saas_user_tool          ON saas_usage_processed(user_id, tool);
CREATE INDEX idx_saas_reco_candidate     ON saas_usage_processed(is_recommendation_candidate);
```

## 5.5 Query Flow (As-If SQL)

The Python aggregations that would map to SQL:

**Idle detection** (currently pandas):
```sql
SELECT
    instance_id, instance_type, region, environment,
    AVG(cpu_utilization_avg) AS avg_cpu,
    SUM(cost_inr)            AS total_cost,
    SUM(CAST(is_idle_candidate AS INT)) AS idle_days,
    COUNT(*)                 AS total_days,
    SUM(CAST(is_idle_candidate AS INT))::FLOAT / COUNT(*) AS idle_ratio
FROM cloud_usage_processed
WHERE date >= (SELECT MAX(date) FROM cloud_usage_processed) - INTERVAL '30 days'
GROUP BY instance_id, instance_type, region, environment
HAVING SUM(CAST(is_idle_candidate AS INT))::FLOAT / COUNT(*) >= 0.8
   AND AVG(cpu_utilization_avg) < 5;
```

**Anomaly aggregation** (currently pandas):
```sql
SELECT date,
       SUM(cost_inr) AS daily_cost_inr,
       AVG(cpu_utilization_avg) AS daily_avg_cpu,
       SUM(hours_running) AS daily_hours,
       EXTRACT(DOW FROM date) >= 5 AS is_weekend
FROM cloud_usage_processed
GROUP BY date
ORDER BY date;
```

## 5.6 ORM Mapping (Planned)

```python
# When migrating, add src/db/models.py with SQLAlchemy ORM:
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase): pass

class CloudUsage(Base):
    __tablename__ = "cloud_usage_processed"
    date         = Column(Date, primary_key=True)
    instance_id  = Column(String(50), primary_key=True)
    # ...
```

## 5.7 Migration Flow (Planned)

1. Stand up Postgres 16.
2. Apply DDL (auto-generated from the SQLAlchemy models via Alembic).
3. Backfill: `df.to_sql("cloud_usage_processed", engine, if_exists="append")` once.
4. Switch `pipeline/run_pipeline.py` to write into Postgres instead of `.csv`.
5. Rewrite `api/dependencies.py`:
   ```python
   @lru_cache(maxsize=1)
   def get_cloud_data() -> pd.DataFrame:
       return pd.read_sql("SELECT * FROM cloud_usage_processed", engine)
   ```

## 5.8 Sample Records

**`cloud_usage.csv` row 1**:
```
date=2026-02-19, instance_id=i-prod-0105, instance_type=m5.4xlarge,
region=us-east-1, environment=prod, cpu_utilization_avg=55.57,
cpu_utilization_max=75.2, hours_running=24, cost_compute_inr=1728.0,
cost_storage_inr=400.0, cost_transfer_inr=122.34, cost_other_inr=21.41,
cost_inr=2271.75
```

**`saas_usage.csv` row 1**:
```
user_id=u-00001, employee_name=Employee 1, department=Engineering,
tool=Salesforce, license_type=Enterprise, monthly_cost_inr=28800.0,
logins_last_30d=48, active_days_last_30d=13, last_login_date=2026-05-20,
assigned_date=2025-08-30, truly_unused=0
```

## 5.9 Per-Table Service Usage

| Table | Used By | CRUD |
|-------|---------|------|
| `cloud_usage` (raw) | pipeline (Read) | R |
| `cloud_usage_processed` | API (R via cache), engine (R), forecast (R), anomaly (R), train_models (R) | C/R (C = pipeline writes, R = everywhere else) |
| `saas_usage` (raw) | pipeline (R) | R |
| `saas_usage_processed` | API (R), engine.detect_unused_licenses (R), license_classifier (R), train_models (R) | C/R |

---

# SECTION 6 — API DOCUMENTATION (Swagger-Style)

OpenAPI auto-generated at `http://localhost:8000/docs`. Below is the human-readable equivalent.

## 6.1 Endpoint: `GET /`

| Field | Value |
|-------|-------|
| **URL** | `/` |
| **Method** | GET |
| **Purpose** | Friendly landing page — returns service name and endpoint list |
| **Request body** | none |
| **Query params** | none |
| **Headers** | none required |
| **Auth** | none (v0.1.0) |
| **Tags** | `meta` |

**Response 200 OK:**
```json
{
  "service": "AI FinOps Platform",
  "docs_url": "/docs",
  "endpoints": ["/cost-forecast", "/anomalies", "/recommendations", "/health"]
}
```

## 6.2 Endpoint: `GET /health`

| Field | Value |
|-------|-------|
| **URL** | `/health` |
| **Method** | GET |
| **Purpose** | Liveness + readiness probe for load balancers / k8s |
| **Auth** | none |
| **Tags** | `meta` |
| **Response model** | `HealthResponse` |

**Response 200 OK (when healthy):**
```json
{
  "status": "ok",
  "models_loaded": {
    "forecast": true,
    "anomaly": true,
    "classifier": true
  },
  "data_freshness": "2026-05-28T02:13:42"
}
```

**Response 200 OK (when degraded):**
```json
{
  "status": "degraded",
  "models_loaded": {"forecast": false, "anomaly": true, "classifier": true},
  "data_freshness": null
}
```

**Execution flow:**
1. Check `models/forecast_model.joblib` exists.
2. Check `models/anomaly_model.joblib` exists.
3. Check `models/license_classifier.joblib` exists.
4. Stat `data/processed/cloud_usage_processed.csv` — return mtime as ISO 8601.
5. `status = "ok"` iff all 3 models AND cloud_csv exist; else `"degraded"`.

## 6.3 Endpoint: `GET /cost-forecast`

| Field | Value |
|-------|-------|
| **URL** | `/cost-forecast` |
| **Method** | GET |
| **Purpose** | Predict daily cloud cost for next N days |
| **Auth** | none |
| **Tags** | `forecast` |

**Query params:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| `days_ahead` | int | 30 | 1 ≤ x ≤ 180 | Forecast horizon |

**Validation rules:**
- `days_ahead < 1` → 422 `{"detail": [{"type": "greater_than_equal", ...}]}`
- `days_ahead > 180` → 422

**Response 200 OK:**
```json
{
  "days_ahead": 30,
  "total_predicted_cost_inr": 4523890.55,
  "average_daily_cost_inr": 150796.35,
  "forecast": [
    {"date": "2026-05-29", "predicted_cost_inr": 152340.12},
    {"date": "2026-05-30", "predicted_cost_inr": 148210.05},
    "..."
  ]
}
```

**Error responses:**
- **503 Service Unavailable** — `forecast_model.joblib` missing.
- **500 Internal Server Error** — `model.predict` raised.

**Internal execution flow:**
1. `get_cloud_data()` — cached df.
2. `forecast.predict_future_costs(df, days_ahead)`:
   a. `joblib.load("forecast_model.joblib")`.
   b. Build feature rows for `last_date + 1` to `last_date + days_ahead`.
   c. `model.predict(features)` → np.array.
   d. `.clip(lower=0).round(2)`.
3. Pack into `ForecastPoint[]` + totals.

**Database operations triggered:** None (cached). On first request: 1 CSV read.

## 6.4 Endpoint: `GET /anomalies`

| Field | Value |
|-------|-------|
| **URL** | `/anomalies` |
| **Method** | GET |
| **Purpose** | Returns days flagged anomalous by IsolationForest, chronological order |
| **Auth** | none |
| **Tags** | `anomalies` |

**Query params:** none.

**Response 200 OK:**
```json
{
  "total_days_scored": 365,
  "anomalies_detected": 19,
  "anomalies": [
    {
      "date": "2025-09-12",
      "daily_cost_inr": 245312.55,
      "daily_avg_cpu": 78.4,
      "daily_hours": 3600,
      "is_weekend": false,
      "anomaly_score": -0.1234
    }
  ]
}
```

**Error responses:**
- 503 if `anomaly_model.joblib` or processed CSV is missing.
- 500 on internal error.

**Internal execution flow:**
1. `get_cloud_data()` — cached.
2. `anomaly.detect_anomalies(df)`:
   a. Load joblib.
   b. Aggregate per-day.
   c. `model.decision_function(X)` + `model.predict(X) == -1`.
   d. Filter, sort, round.
3. Build `AnomalyItem[]`.

## 6.5 Endpoint: `GET /recommendations`

| Field | Value |
|-------|-------|
| **URL** | `/recommendations` |
| **Method** | GET |
| **Purpose** | Unified savings recommendations (rules + ML) with optional filters |
| **Auth** | none |
| **Tags** | `recommendations` |

**Query params:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| `top_n` | int | 50 | 1 ≤ x ≤ 500 | Max items returned |
| `category` | str? | null | `cloud_idle` / `cloud_rightsize` / `saas_revoke` / `cloud_anomaly` | Filter to one category |
| `severity` | str? | null | `high` / `medium` / `low` | Filter to one severity |

**Response 200 OK:**
```json
{
  "summary": {
    "total_recommendations": 712,
    "total_monthly_savings_inr": 4035782.50,
    "total_annual_savings_inr": 48429390.00,
    "by_severity": {"high": 23, "medium": 156, "low": 533},
    "by_category": {
      "cloud_idle": 89,
      "cloud_rightsize": 12,
      "saas_revoke": 597,
      "cloud_anomaly": 14
    }
  },
  "recommendations": [
    {
      "id": "rec_idle_i-prod-0042",
      "category": "cloud_idle",
      "severity": "high",
      "title": "Stop idle prod instance i-prod-0042",
      "reason": "Average CPU was 1.2% over the last 30 days (idle on 30/30 days). ...",
      "action": "Stop or terminate i-prod-0042 in the us-east-1 region.",
      "monthly_savings_inr": 72000.00,
      "annual_savings_inr": 864000.00,
      "confidence": 1.0,
      "entity": "i-prod-0042",
      "metadata": {
        "instance_type": "m5.2xlarge",
        "region": "us-east-1",
        "environment": "prod",
        "avg_cpu_last_30d": 1.2
      }
    }
  ]
}
```

**Important semantics:** `summary` is computed over the *unfiltered* set; the filter only affects `recommendations[]`. This keeps the KPI tiles stable when the user toggles filters.

**Internal execution flow:**
1. Validate params.
2. `get_cloud_data()`, `get_saas_data()` (cached).
3. `engine.build_all_recommendations(cloud_df, saas_df)`:
   - `detect_idle_instances(cloud_df)` — rule.
   - `detect_rightsize_candidates(cloud_df)` — rule.
   - `detect_unused_licenses(saas_df)` — ML, threshold 0.7.
   - `detect_recent_anomalies(cloud_df, 14)` — ML.
   - Sort.
4. `engine.summarize(all_recs)`.
5. Apply category filter (if any).
6. Apply severity filter (if any).
7. Slice `[:top_n]`.
8. Pack `RecommendationsResponse`.

---

# SECTION 7 — AUTHENTICATION & SECURITY

## 7.1 v0.1.0 Status

**No authentication is implemented.** This was a deliberate scope decision for v0.1.0:
- The dataset is synthetic, so there's nothing to protect.
- All endpoints are GET-only and idempotent.
- The deploy target is "localhost" — no public exposure.

## 7.2 Recommended Login Flow (v0.2 plan)

```
1. User POSTs /auth/login {"username":"...","password":"..."}
2. API queries `users` table; bcrypt-checks password hash
3. On success: issue JWT signed with HS256, exp=24h
4. Streamlit stores JWT in st.session_state
5. api_client._get() adds Authorization: Bearer <token> header
6. FastAPI dependency `Depends(verify_jwt)` validates exp/signature on every route
```

## 7.3 Recommended Registration Flow

Out of scope — users are provisioned by IT via Active Directory / Okta SCIM.

## 7.4 JWT / Session Handling (Planned)

- **Algorithm:** HS256 with 256-bit secret in `JWT_SECRET` env var.
- **Claims:** `sub`, `email`, `role`, `iat`, `exp`.
- **Refresh strategy:** stateless 24h tokens; reissue via `/auth/refresh`.
- **Storage:** Streamlit `st.session_state["token"]` — never in localStorage of a browser context Streamlit doesn't control.

## 7.5 Password Encryption

Use `passlib[bcrypt]` with cost factor 12. Never store plaintext, never store reversible encryption.

```python
from passlib.context import CryptContext
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_ctx.hash(plain)
ok = pwd_ctx.verify(plain, hashed)
```

## 7.6 Authorization Flow (Planned)

| Role | `/health` | `/cost-forecast` | `/anomalies` | `/recommendations` |
|------|-----------|------------------|--------------|--------------------|
| `analyst` | ✓ | ✓ | ✓ | ✓ |
| `manager` | ✓ | ✓ | ✓ (own dept only) | ✓ (own dept only) |
| `cfo` | ✓ | ✓ | ✓ | ✓ |
| `engineer` | ✓ | — | — | — |

Enforce with a FastAPI dependency:
```python
def require_role(role: str):
    def dependency(token: str = Depends(verify_jwt)):
        claims = decode(token)
        if claims["role"] != role:
            raise HTTPException(403)
        return claims
    return dependency
```

## 7.7 Token Lifecycle (Planned)

- Issue → 24h.
- Refresh window: last 1h of token life.
- Revocation: short list of blacklisted JTIs in Redis (set with TTL = remaining token life).

## 7.8 Security Vulnerabilities Handled

| Vulnerability | Status | Mitigation |
|---------------|--------|------------|
| Schema attack (CSV with extra cols) | ✅ | `_read_csv` validates required cols, ignores extras |
| Invalid type (non-numeric `cost`) | ✅ | `pd.to_numeric(errors="coerce")` + null clean |
| SQL injection | N/A | No SQL in v0.1.0 |
| Server crash on bad input | ✅ | Pydantic + try/except + HTTPException |
| Path traversal | ✅ | All paths derived from `PROJECT_ROOT` |
| Unbounded query | ✅ | `top_n` capped at 500, `days_ahead` at 180 |
| DoS via huge response | ✅ | Same caps |
| Negative cost rows | ✅ | `.clip(lower=0)` in clean step |

## 7.9 CORS Handling

```python
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])
```

**Dev:** open `*`.
**Prod:** restrict to `["https://finops.your-company.com"]`. Lock `allow_methods` to only what's used.

## 7.10 CSRF / XSS / SQL-Injection Protection

| Vector | Defence |
|--------|---------|
| **CSRF** | Not applicable — GET-only, no cookies, no state-changing endpoints |
| **XSS** | Streamlit auto-HTML-escapes content; no `unsafe_allow_html` in this project |
| **SQL injection** | Not applicable; future Postgres migration must use SQLAlchemy parameterised queries (`bindparam`, never f-strings) |

## 7.11 Secure API Practices Checklist

- [x] Validation via Pydantic
- [x] Numeric bounds on query params
- [x] Logged exceptions (`log.exception`)
- [x] No secrets in code (env vars planned)
- [ ] HTTPS termination (deploy with nginx)
- [ ] Rate limiting (`slowapi` planned)
- [ ] Request-ID middleware
- [ ] Prometheus metrics
- [ ] Audit log of who-saw-what

---

# SECTION 8 — COMPLETE EXECUTION FLOW

## 8.1 Cold-Start Workflow (First-Time Setup)

```
1. Developer clones repo
2. python -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. python scripts/generate_data.py
     ├── Creates data/raw/cloud_usage.csv (~49,000 rows)
     └── Creates data/raw/saas_usage.csv  (~3,100 rows)
6. python scripts/run_pipeline.py
     ├── ingest.load_cloud_usage()    ✓ schema-validated
     ├── clean.clean_cloud_usage()    ✓ dedup, types, nulls
     ├── transform.transform_cloud_usage()  ✓ 6 new features
     └── writes data/processed/cloud_usage_processed.csv
     ├── ingest.load_saas_usage()
     ├── clean.clean_saas_usage()
     ├── transform.transform_saas_usage()
     └── writes data/processed/saas_usage_processed.csv
7. python scripts/train_models.py
     ├── forecast.train_forecast_model()         → forecast_model.joblib
     ├── anomaly.train_anomaly_model()           → anomaly_model.joblib
     └── license_classifier.train_license_classifier() → license_classifier.joblib
8. Terminal 1: uvicorn src.api.main:app --port 8000
     ├── lifespan: log "FinOps API starting up"
     ├── routers mounted
     └── ready to accept GET requests
9. Terminal 2: streamlit run src/dashboard/app.py
     ├── opens http://localhost:8501
     ├── auto-detects pages/*.py
     └── ready for user
```

## 8.2 Dashboard Landing-Page Flow (Click-to-Render)

```
User opens http://localhost:8501
    │
    ▼
Streamlit boots, executes src/dashboard/app.py top-to-bottom
    │
    ▼
st.set_page_config(layout="wide")
    │
    ▼
st.title + st.caption render
    │
    ▼
health = fetch_health()
    │
    ├─── api_client._get("/health")
    │      └── requests.get("http://localhost:8000/health", timeout=10)
    │           │
    │           ▼
    │      FastAPI worker receives GET /health
    │           ├── routes.main.health() executes
    │           ├── checks models/*.joblib exist
    │           ├── stats data/processed/cloud_usage_processed.csv
    │           └── returns HealthResponse JSON
    │      resp.json() → dict
    │
    ▼
if health["status"] == "ok": st.success(...) else st.warning(...)
    │
    ▼
recs = fetch_recommendations(top_n=500)
    │
    ├─── (60s cache miss) GET /recommendations?top_n=500
    │      ├── routes.recommendations.get_recommendations()
    │      ├── get_cloud_data() ── lru_cache miss → pd.read_csv
    │      ├── get_saas_data()  ── lru_cache miss → pd.read_csv
    │      ├── engine.build_all_recommendations(cloud_df, saas_df)
    │      │     ├── detect_idle_instances (~150ms)
    │      │     ├── detect_rightsize_candidates (~100ms)
    │      │     ├── detect_unused_licenses (~80ms, ML)
    │      │     └── detect_recent_anomalies (~50ms, ML)
    │      ├── engine.summarize(all_recs)
    │      └── return RecommendationsResponse JSON
    │      (~500ms first call, ~5ms subsequent)
    │
    ▼
forecast = fetch_forecast(days_ahead=30)
    │
    ├─── GET /cost-forecast?days_ahead=30
    │      ├── get_cloud_data() ── cache hit
    │      ├── forecast.predict_future_costs(df, 30)
    │      │     ├── joblib.load("forecast_model.joblib") (~10ms first time)
    │      │     ├── build features for 30 future days
    │      │     └── model.predict (~1ms)
    │      └── return ForecastResponse
    │
    ▼
4 KPI tiles render (st.columns(4))
    │
    ▼
2 bar charts render (st.columns(2) → st.bar_chart)
    │
    ▼
Top 5 expanders render (for rec in recs["recommendations"][:5])
    │
    ▼
Footer caption
    │
    ▼
[Streamlit WebSocket-pushes the rendered page to the browser]
```

## 8.3 Cost-Trends Slider Interaction

```
User drags slider from 30 → 90 days
    │
    ▼
Streamlit fires "ws value change" event
    │
    ▼
Streamlit reruns pages/1_📊_Cost_Trends.py top-to-bottom
    │
    ▼
days_ahead = 90 (new slider value)
    │
    ▼
forecast = fetch_forecast(days_ahead=90)
    │
    ├── @st.cache_data(ttl=60) — different arg, cache MISS
    │
    └── GET /cost-forecast?days_ahead=90
         └── (forecast logic as above with 90 future days)
    │
    ▼
KPI tiles refresh with new totals
    │
    ▼
Line chart redraws (st.line_chart re-renders)
    │
    ▼
Raw data table refreshes (collapsed expander)
```

## 8.4 Recommendations Filter Interaction

```
User changes "Severity" dropdown to "High only"
    │
    ▼
Page rerun
    │
    ▼
selected_severity_label = "High only"
severity_options[selected_severity_label] = "high"
    │
    ▼
data = fetch_recommendations(category=None, severity="high", top_n=50)
    │
    ├── @st.cache_data(ttl=60) — different args, MISS
    │
    └── GET /recommendations?top_n=50&severity=high
         ├── (full engine run — same as before)
         ├── summary = ALL recs (not filtered)
         ├── filter to severity=high
         └── return top 50 high-severity items
    │
    ▼
KPI tiles refresh (note: summary is over UNFILTERED set)
    │
    ▼
Expander cards rebuild with new list
    │
    ▼
CSV download button refreshes with filtered set
```

## 8.5 Daily Cron Execution (Production)

```
02:00 IST (system clock)
    │
    ▼
cron triggers: cd /opt/finops && /opt/finops/.venv/bin/python scripts/run_pipeline.py
    │
    ▼
run_pipeline.main()
    │
    ├── run_cloud_pipeline()
    │     ├── log "=== CLOUD PIPELINE START ==="
    │     ├── ingest.load_cloud_usage() — reads cloud_usage.csv
    │     │     ├── if file missing → FileNotFoundError → exit 1
    │     │     ├── if schema mismatch → ValueError → exit 1
    │     │     └── log "Loaded 49,150 rows"
    │     ├── clean.clean_cloud_usage(df)
    │     │     ├── drop_duplicates → "Dropped 50 duplicates"
    │     │     ├── coerce dates / numerics
    │     │     ├── per-instance median fill nulls
    │     │     └── clip negative costs
    │     ├── transform.transform_cloud_usage(df)
    │     │     ├── add day_of_week, month, is_weekend
    │     │     ├── add utilization_band
    │     │     ├── add is_idle_candidate
    │     │     └── add daily_waste_inr
    │     ├── df.to_csv("cloud_usage_processed.csv", index=False)
    │     └── log "=== CLOUD PIPELINE DONE ==="
    │
    └── run_saas_pipeline()
          ├── ingest → clean → transform (same pattern)
          └── log "=== SAAS PIPELINE DONE ==="
    │
    ▼
return 0 (success) or 1 (caught exception logged via log.exception)
    │
    ▼
[wait 1 hour]
    │
    ▼
03:00 IST
    │
    ▼
cron triggers: python scripts/train_models.py
    │
    ▼
train_models.main()
    │
    ├── read cloud_usage_processed.csv
    ├── read saas_usage_processed.csv
    │
    ├── forecast.train_forecast_model(cloud)
    │     ├── aggregate to daily
    │     ├── time-aware split
    │     ├── winsorise y_train
    │     ├── fit LinearRegression
    │     ├── compute MAE, R², MAPE
    │     └── joblib.dump → forecast_model.joblib
    │
    ├── anomaly.train_anomaly_model(cloud)
    │     ├── daily aggregate
    │     ├── fit IsolationForest(n_estimators=100, contamination=0.05)
    │     └── joblib.dump → anomaly_model.joblib
    │
    └── license_classifier.train_license_classifier(saas)
          ├── _create_labels (prefer truly_unused)
          ├── stratified split
          ├── StandardScaler.fit_transform
          ├── fit LogisticRegression
          ├── compute AUC + classification report
          └── joblib.dump → license_classifier.joblib
    │
    ▼
return 0 — models are fresh for the next 24 hours
```

---

# SECTION 9 — DEVOPS & DEPLOYMENT

## 9.1 Build Process

There is **no compile step** — Python is interpreted. The "build" is:
1. `python -m venv .venv`
2. `pip install -r requirements.txt`
3. `python scripts/generate_data.py` (one-time, dev only)
4. `python scripts/run_pipeline.py`
5. `python scripts/train_models.py`

## 9.2 CI/CD Pipeline (Recommended)

```yaml
# .github/workflows/ci.yml  (not yet committed)
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.14" }
      - run: pip install -r requirements.txt
      - run: python scripts/generate_data.py
      - run: python scripts/run_pipeline.py
      - run: python scripts/train_models.py
      - run: python -c "from src.api.main import app; print(app.routes)"
      - run: pytest -q  # when tests exist
```

## 9.3 Docker Setup (Recommended)

**Dockerfile.api:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Dockerfile.dashboard:**
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
ENV FINOPS_API_URL=http://api:8000
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 9.4 Docker Compose (Recommended)

```yaml
version: "3.9"
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
      - ./models:/app/models

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports: ["8501:8501"]
    environment:
      FINOPS_API_URL: http://api:8000
    depends_on: [api]

  cron:
    build:
      context: .
      dockerfile: Dockerfile.api
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    entrypoint: ["sh", "-c"]
    command: >
      "echo '0 2 * * * cd /app && python scripts/run_pipeline.py >> /var/log/pipeline.log 2>&1' > /etc/crontabs/root &&
       echo '0 3 * * * cd /app && python scripts/train_models.py >> /var/log/train.log 2>&1' >> /etc/crontabs/root &&
       crond -f"
```

## 9.5 Kubernetes (Plan)

- `Deployment` for `api` with `replicas: 2`.
- `Deployment` for `dashboard` with `replicas: 1` (Streamlit is single-user-per-process by design).
- `Service` of type `ClusterIP` for both, exposed via `Ingress`.
- `CronJob` for `run_pipeline` (02:00) and `train_models` (03:00).
- `ConfigMap` for `FINOPS_API_URL`.
- `PersistentVolumeClaim` for `data/` and `models/`.

## 9.6 Environment Configuration

| Environment | Detail |
|-------------|--------|
| **dev** (local) | uvicorn `--reload`, streamlit default, CSV in `data/`, joblib in `models/` |
| **staging** | Docker Compose, fake-but-prod-shaped data |
| **prod** | Kubernetes, real CUR data, Postgres-backed |

## 9.7 Production Deployment Checklist

- [ ] HTTPS termination (nginx / ALB)
- [ ] Auth (JWT)
- [ ] Postgres migration
- [ ] Rate limiting (`slowapi`)
- [ ] Prometheus metrics
- [ ] Sentry on exceptions
- [ ] Backup of `models/` (S3)
- [ ] CDN for Streamlit static assets (or replace dashboard with React)

## 9.8 Cloud Services

Recommended (AWS-flavoured):
- **ECS Fargate** or **EKS** for containers.
- **RDS Postgres** for processed data.
- **S3** for raw data ingest + model artefact storage.
- **EventBridge** (cron) for pipeline + train scheduling.
- **CloudWatch Logs** for app logs.
- **Secrets Manager** for JWT secret + DB password.

## 9.9 Nginx / Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name finops.your-company.com;
    ssl_certificate     /etc/letsencrypt/live/.../fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";   # Streamlit needs WebSockets
    }
}
```

## 9.10 SSL Setup

Use Let's Encrypt + certbot:
```bash
certbot --nginx -d finops.your-company.com
```

## 9.11 Scaling Strategy

| Bottleneck | Solution |
|-----------|----------|
| Single uvicorn worker | `--workers 4` (or autoscale on CPU) |
| CSV re-reads per worker | Single LRU per worker — fine until ~10MB CSVs |
| 10MB+ data | Switch to Postgres + connection pool |
| Anomaly engine cold start | Pre-warm joblib in lifespan |
| Streamlit single-user | Spawn multiple replicas behind sticky sessions |
| Pipeline runtime > cron window | Move to Airflow with retries + alerts |

## 9.12 Monitoring / Logging

| Concern | Tool |
|---------|------|
| App logs | `stdout` → CloudWatch Logs / Loki |
| Metrics | Prometheus + Grafana (add `starlette-prometheus`) |
| Errors | Sentry SDK |
| Uptime | Better Uptime / Pingdom on `/health` |
| Pipeline failures | EventBridge → SNS → email |

## 9.13 Secrets Management

- Dev: `.env` file (gitignored).
- Prod: AWS Secrets Manager / Vault.
- Loaded into env vars at container start, never written to disk in plaintext.

---

# SECTION 10 — CONFIGURATION & ENVIRONMENT VARIABLES

## 10.1 Current Variables

| Variable | Purpose | Example | Security | Related Service |
|----------|---------|---------|----------|-----------------|
| `FINOPS_API_URL` | Base URL the Streamlit dashboard uses to call the FastAPI service | `http://localhost:8000` (dev), `https://finops.internal/api` (prod) | Public; safe to log | dashboard → api |

## 10.2 Planned Variables (for v0.2+)

| Variable | Purpose | Example | Security |
|----------|---------|---------|----------|
| `DATABASE_URL` | Postgres connection string | `postgresql://user:pwd@host:5432/finops` | **Secret** — never commit |
| `JWT_SECRET` | HS256 signing key | `64-char-random-hex` | **Critical secret** |
| `JWT_EXPIRY_HOURS` | Token TTL | `24` | Non-secret |
| `LOG_LEVEL` | Logger verbosity | `INFO` / `DEBUG` | Non-secret |
| `SENTRY_DSN` | Exception reporting | `https://...@sentry.io/...` | Mildly secret |
| `S3_MODELS_BUCKET` | Where to push trained joblibs | `finops-models-prod` | Non-secret |
| `AWS_REGION` | For S3/Secrets/CloudWatch | `ap-south-1` | Non-secret |
| `CONTAMINATION` | IsolationForest tunable | `0.05` | Non-secret |
| `HIGH_THRESHOLD_INR` | Severity threshold | `50000` | Non-secret |
| `MEDIUM_THRESHOLD_INR` | Severity threshold | `10000` | Non-secret |

## 10.3 `.env` Template (Future)

```dotenv
# .env  (DO NOT COMMIT — covered by .gitignore *.env)
FINOPS_API_URL=http://localhost:8000
DATABASE_URL=postgresql://finops:finops@localhost:5432/finops
JWT_SECRET=changeme_in_prod_64_hex_chars
JWT_EXPIRY_HOURS=24
LOG_LEVEL=INFO
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```
(`python-dotenv` already in `requirements.txt`.)

---

# SECTION 11 — DEPENDENCIES & LIBRARIES

## 11.1 Direct Dependencies

### `pandas>=2.1`
- **Why used:** all data manipulation — read CSV, groupby, transform, merge.
- **Alternatives:** Polars (faster, smaller ecosystem), Dask (distributed but overkill).
- **Internal role:** powering ETL pipeline + all engine aggregations.
- **Risk:** memory-bound at >5GB datasets — eventual switch to Polars or Dask warranted.

### `numpy>=1.26`
- **Why used:** RNG in data generator, math in ML feature engineering.
- **Alternatives:** none viable — it's the substrate for pandas + sklearn.
- **Risk:** API breaking changes (NumPy 2.0 deprecated several aliases). Pinning `>=1.26` keeps us on the modern API.

### `openpyxl>=3.1`
- **Why used:** declared for future `.xlsx` ingest (e.g. uploaded by users via dashboard).
- **Currently unused** in any module — kept as a forward-looking pin.
- **Risk:** dead weight if ingestion stays CSV-only.

### `scikit-learn>=1.4`
- **Why used:** `LinearRegression`, `IsolationForest`, `LogisticRegression`, `StandardScaler`, `train_test_split`, `roc_auc_score`, `classification_report`, `mean_absolute_error`, `r2_score`.
- **Alternatives:** XGBoost (better accuracy, less interpretable), PyTorch (overkill for tabular).
- **Internal role:** entire ML layer.
- **Risk:** joblib format changes across sklearn versions — pin tighter in prod.

### `fastapi>=0.110`
- **Why used:** REST API framework.
- **Alternatives:** Flask (no async / no auto-docs), Django (heavyweight).
- **Internal role:** `src/api/`.
- **Risk:** v1.0 stabilisation is recent — keep an eye on breaking changes.

### `uvicorn[standard]>=0.27`
- **Why used:** ASGI server for FastAPI.
- **Alternatives:** Hypercorn (similar, smaller adoption), Daphne.
- **Internal role:** entry point for serving the API.
- **`[standard]`** brings in `uvloop`, `httptools`, `websockets`, `watchfiles` — production-grade extras.

### `pydantic>=2.6`
- **Why used:** data model validation.
- **Alternatives:** dataclasses (no validation), marshmallow (slower API).
- **Internal role:** all request/response models + `Recommendation`.

### `streamlit>=1.32`
- **Why used:** Python-only dashboard.
- **Alternatives:** Dash (more verbose), React+Plotly (requires full frontend skillset).
- **Internal role:** `src/dashboard/`.
- **Limitation:** single-user-per-process under load. Mitigation: multiple replicas + sticky sessions.

### `plotly>=5.19`
- **Why used:** interactive charts (currently `st.bar_chart` / `st.line_chart` cover needs — plotly is an upgrade path for richer interactions).
- **Alternatives:** matplotlib (static), altair (declarative but limited).

### `psycopg2-binary>=2.9`
- **Why used:** Postgres driver — currently unused, pinned for the planned migration.
- **Alternatives:** `asyncpg` (async, faster).

### `sqlalchemy>=2.0`
- **Why used:** ORM for the planned Postgres migration.
- **Alternatives:** Tortoise (smaller ecosystem), raw psycopg2 (no abstraction).

### `python-dotenv>=1.0`
- **Why used:** `.env` loader.
- **Internal role:** read env vars in local development.

## 11.2 Transitive Dependencies (Notable)

| Library | Pulled in by | Used For |
|---------|--------------|----------|
| `requests` | streamlit's recommended HTTP client | API calls in `api_client.py` |
| `joblib` | scikit-learn | model serialisation |
| `starlette` | fastapi | HTTP primitives |
| `httptools`, `uvloop`, `websockets`, `watchfiles` | `uvicorn[standard]` | production performance |

## 11.3 Why No Test Framework?

`pytest` is **not** in `requirements.txt` for v0.1.0 — the project ships without an automated test suite. This is a deliberate scope choice (the data generator + manual `python scripts/run_pipeline.py` is the "test"). Adding pytest is a roadmap item — see Section 14.

---

# SECTION 12 — IMPORTANT ALGORITHMS & LOGIC

## 12.1 Algorithm 1 — Synthetic Data Generation (Probabilistic, Not Hand-Labeled)

**File:** `scripts/generate_data.py`.

**Goal:** Plant realistic waste in the data WITHOUT giving the ML a deterministic label leak.

**Cloud generator (`generate_cloud_usage`):**
1. Build a fleet of `n_instances` (150 default) with:
   - **Environment** sampled from weighted choices (`prod:0.45, dev:0.25, staging:0.15, test:0.15`).
   - **Behaviour** sampled conditional on env. Prod is mostly normal; dev/test have far more idle and zombie.
   - **Lifetime**: 70% live the whole window; 20% launched midway; 10% terminate early.
   - **Instance type**: weighted toward smaller boxes (pyramid-shaped fleet).
   - **Baseline CPU**: drawn around a per-behaviour mean (e.g. idle: 1–4%, zombie: 2–6%, rightsize: 8–18%, normal: 35–65%).
2. For each (day × instance):
   - Apply `_seasonality_multiplier(date)`: month-end spike, weekend dip, festival lull.
   - Compute compute/storage/transfer/other costs.
3. Plant 4–8 anomalies at random dates with random magnitudes (2.5×–8× multiplier on compute + transfer for 1–3 days, hitting 1–18 instances).
4. Inject 1% missing-CPU (`NaN`) telemetry-gap rows.
5. Inject 50 duplicate rows so the dedup step has something to do.

**Why this matters:** The IsolationForest can't memorise "anomaly = day 87" because day 87 is different on every generator run. Models have to actually *find* the signal.

**SaaS generator (`generate_saas_usage`):**
1. For each of 1500 employees, draw 1–4 tools assigned.
2. Compute `p_truly_unused` based on whether the user's department typically uses the tool (8% if match, 40% if mismatch).
3. Draw `truly_unused` from Bernoulli(p_truly_unused).
4. Generate **noisy observable signals**:
   - If `truly_unused`: 85% chance of 0–2 logins, 15% chance of an accidental burst (3–7 logins).
   - If not `truly_unused`: 90% chance of steady use, 10% chance of a quiet month (mimics PTO/leave).
5. Write `truly_unused` as a ground-truth column the classifier trains against.

## 12.2 Algorithm 2 — ETL Cleaning

**File:** `src/pipeline/clean.py`.

**Steps in `clean_cloud_usage`:**
1. **Drop duplicates** — `df.drop_duplicates()` on all columns.
2. **Parse dates** — `pd.to_datetime(errors="coerce")` (bad → NaT); drop NaT rows.
3. **Coerce numerics** — `pd.to_numeric(errors="coerce")` on cpu_avg, cpu_max, hours_running, cost_inr.
4. **Normalise strings** — `.astype(str).str.strip().str.lower()` on region, environment, instance_type.
5. **Per-instance median fill** — for `cpu_utilization_avg`:
   ```python
   df["cpu_utilization_avg"] = df.groupby("instance_id")["cpu_utilization_avg"]\
                                  .transform(lambda s: s.fillna(s.median()))
   ```
   Falls back to 0.0 for instances with all-NaN CPU.
6. **Clip negative costs** — `.clip(lower=0)`.

**Why per-instance median (not global median)?** A `p3.8xlarge` GPU box and a `t3.medium` baseline differ by 100× in CPU pattern. The global median would corrupt both.

## 12.3 Algorithm 3 — Feature Engineering

**File:** `src/pipeline/transform.py`.

| Feature | Logic | Why |
|---------|-------|-----|
| `is_idle_candidate` | `(cpu_avg < 5) AND (hours_running >= 20)` | Idle = paying for hours, not using them |
| `daily_waste_inr` | `cost_inr` if idle else `0.0` | Material for "potential savings" KPI |
| `utilization_band` | `<5: idle, <20: low, <70: normal, else high` | For human-readable categorisation |
| `days_since_last_login` | `(today - last_login_date).dt.days`; NaT → 999 | Continuous feature for the classifier; 999 is the "never logged in" sentinel |
| `is_recommendation_candidate` | `usage_category in {unused, low}` | Pre-filter for the engine |

## 12.4 Algorithm 4 — Cost Forecasting

**File:** `src/ml/forecast.py`.

**Train:**
1. Aggregate rows → daily totals.
2. Build features: `day_of_week`, `day_of_month`, `month`, `is_weekend`.
3. **Time-aware split** (NOT random) — last 20% chronologically is test:
   ```python
   split_idx = int(len(daily) * 0.8)
   X_train = X.iloc[:split_idx]; X_test = X.iloc[split_idx:]
   ```
   Random split would let "future" leak into "past" — a classic time-series mistake.
4. **Winsorise training target** — clip top 5% of `y_train` to the 95th percentile:
   ```python
   cap = y_train.quantile(0.95)
   y_train = y_train.clip(upper=cap)
   ```
   Spike days bias the linear model upward; the *anomaly detector* handles spikes.
5. `LinearRegression().fit(X_train, y_train)`.
6. Compute MAE, R², MAPE on the (un-winsorised) test set.
7. `joblib.dump`.

**Predict:**
1. Load joblib.
2. Build feature rows for `last_date + 1` ... `last_date + days_ahead`.
3. `model.predict(features).clip(lower=0)`.

**Why so simple?** Three reasons:
- Linear regression is a **strong baseline** — anything fancier (Prophet, XGBoost, LSTM) must outperform this to justify its operational complexity.
- Each coefficient maps to a human-readable effect ("being a weekend reduces cost by ₹X") — explainable to finance.
- Sub-millisecond training and inference.

## 12.5 Algorithm 5 — Anomaly Detection (Isolation Forest)

**File:** `src/ml/anomaly.py`.

**How Isolation Forest works (1-paragraph mental model):**
Builds a forest of random binary trees. Each tree splits randomly on a feature. The **path length to isolate a point** is the metric — outliers separate quickly (short paths), normals take many splits (long paths). No distribution assumption, native multivariate.

**Pipeline:**
1. Aggregate to one row per day: `daily_cost_inr` (sum), `daily_avg_cpu` (mean), `daily_hours` (sum), `is_weekend` (bool).
2. `IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit(X)`.
3. `decision_function(X)` → continuous score (lower = more anomalous).
4. `predict(X) == -1` → boolean flag.

**Why no train/test split?** It's unsupervised — there are no labels, just feature space.

**Why 5% contamination?** Empirically tuned. Higher → too noisy. Lower → misses real spikes.

## 12.6 Algorithm 6 — License Classifier (Logistic Regression)

**File:** `src/ml/license_classifier.py`.

**Why logistic regression?**
- Binary output is the natural fit.
- Coefficients are interpretable (a positive `logins_last_30d` coef means *more logins → less likely revoke* — sanity check).
- `predict_proba` returns calibrated probabilities — the engine sorts by these and surfaces the most-confident revokes.
- Robust on small data (≈3,100 rows).

**Label source:** Prefer the data generator's `truly_unused` ground-truth column (noisy, realistic). Fall back to a deterministic rule for legacy datasets.

**Training pipeline:**
1. `_create_labels(df)` → `y`.
2. `train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)` — stratified to preserve class balance.
3. `StandardScaler.fit_transform(X_train)` — without it, `monthly_cost_inr` (1000s) would dominate `logins_last_30d` (10s).
4. `LogisticRegression(max_iter=1000, random_state=42).fit(X_train_scaled, y_train)`.
5. Compute AUC (typically ~0.95), full classification report.
6. Persist `{model, scaler, feature_cols, metrics}`.

**Prediction:** transform features through the *saved* scaler (never refit at predict time) → `predict_proba(X)[:, 1]` → filter ≥ threshold (default 0.7 in the engine).

## 12.7 Algorithm 7 — Unified Recommendation Engine

**File:** `src/recommendations/engine.py`.

**Steps in `build_all_recommendations`:**
1. Run 4 detectors in series:
   - `detect_idle_instances` (rule, last 30d, idle_ratio ≥ 0.8 AND avg_cpu < 5).
   - `detect_rightsize_candidates` (rule, 5 ≤ avg_cpu < 20 AND not smallest tier).
   - `detect_unused_licenses` (ML, threshold 0.7).
   - `detect_recent_anomalies` (ML, last 14 days).
2. Concatenate into one `List[Recommendation]`.
3. Sort by:
   ```python
   key=lambda r: (SEVERITY_ORDER[r.severity], -r.annual_savings_inr, -r.confidence)
   ```
   - Highest severity first.
   - Within severity, highest annual savings first.
   - Tie-break on confidence.
4. Log total.

**Severity rule:**
- `monthly_savings ≥ ₹50,000` → high.
- `monthly_savings ≥ ₹10,000` → medium.
- else → low.

**Why combine rules and ML?**
- Rules are explainable, audit-friendly, fast.
- ML catches edge cases the rules miss.
- Together: deterministic for the easy 80%, ML for the messy 20%.

## 12.8 Algorithm 8 — Severity Sorting (Stable Across Filters)

The summary stats are computed over the **unfiltered** set, then the filter is applied. Why?
- Toggling "severity=high" should not change "Total Recommendations: 712" to "Total Recommendations: 23" — that's confusing.
- Filters affect which items are shown, not the macro KPIs.

---

# SECTION 13 — RECREATING THE PROJECT FROM SCRATCH

## 13.1 Software Requirements

| Tool | Version | Why |
|------|---------|-----|
| Python | 3.14.x | Pinned to the documented stack |
| pip | bundled | Dependency install |
| git | latest | Version control |
| (optional) Docker | 24+ | Container deployment |
| (optional) Postgres | 16 | When migrating off CSV |

## 13.2 Step-by-Step Installation

```bash
# 1. Clone (or create fresh)
git clone https://github.com/YOURUSERNAME/AI_IT_OPTIMIZATION.git
cd AI_IT_OPTIMIZATION

# 2. Create the virtual environment
python -m venv .venv

# 3. Activate
.venv\Scripts\activate          # Windows PowerShell / cmd
# or
source .venv/bin/activate       # macOS / Linux

# 4. Install dependencies
pip install -r requirements.txt
```

## 13.3 Project Skeleton From Empty Folder

If you've truly lost the codebase, recreate the folder tree:
```bash
mkdir -p data/raw data/processed models scripts \
         src/api/routes src/dashboard/pages src/ml \
         src/pipeline src/recommendations src/utils

touch src/__init__.py src/api/__init__.py src/api/routes/__init__.py \
      src/dashboard/__init__.py src/dashboard/pages/__init__.py \
      src/pipeline/__init__.py src/recommendations/__init__.py \
      src/utils/__init__.py
```

Then create each file per Section 2 of this doc (every file is fully described).

## 13.4 Database / Data Setup

**v0.1.0 has no database**. Run the data generator:
```bash
python scripts/generate_data.py
```
Expect:
- `data/raw/cloud_usage.csv` (~49,000 rows)
- `data/raw/saas_usage.csv` (~3,100 rows)

## 13.5 Backend Setup

```bash
python scripts/run_pipeline.py
# → data/processed/cloud_usage_processed.csv
# → data/processed/saas_usage_processed.csv

python scripts/train_models.py
# → models/forecast_model.joblib
# → models/anomaly_model.joblib
# → models/license_classifier.joblib

uvicorn src.api.main:app --port 8000 --reload
# → http://localhost:8000/docs
```

Verify:
```bash
curl http://localhost:8000/health
curl 'http://localhost:8000/cost-forecast?days_ahead=7'
curl 'http://localhost:8000/recommendations?top_n=5&severity=high'
```

## 13.6 Frontend Setup

```bash
# In a second terminal (with .venv activated)
streamlit run src/dashboard/app.py
# → opens http://localhost:8501 in browser
```

## 13.7 Environment Configuration

For local dev, no env vars are required. For non-default API URL:
```bash
export FINOPS_API_URL=http://10.0.0.50:8000   # macOS/Linux
$env:FINOPS_API_URL = "http://10.0.0.50:8000" # Windows PowerShell
```

## 13.8 Running Locally

```
Terminal 1: uvicorn src.api.main:app --port 8000 --reload
Terminal 2: streamlit run src/dashboard/app.py
Browser:    http://localhost:8501
```

## 13.9 Running a Production Build

```bash
# API (4 workers, no reload, bound to all interfaces)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Dashboard (production mode)
streamlit run src/dashboard/app.py --server.address=0.0.0.0 --server.port=8501

# Schedule daily refresh (Linux cron, IST = UTC+5:30)
30 20 * * * cd /opt/finops && /opt/finops/.venv/bin/python scripts/run_pipeline.py >> /var/log/finops_pipeline.log 2>&1
30 21 * * * cd /opt/finops && /opt/finops/.venv/bin/python scripts/train_models.py  >> /var/log/finops_train.log 2>&1
```

## 13.10 Common Issues & Debugging

| Symptom | Probable Cause | Fix |
|---------|----------------|-----|
| `FileNotFoundError: cloud_usage.csv` | Skipped data generation | `python scripts/generate_data.py` |
| `503 Service Unavailable` from API | Pipeline never ran | `python scripts/run_pipeline.py` |
| `503` mentioning `.joblib` | Models not trained | `python scripts/train_models.py` |
| `Cannot reach the FinOps API at http://localhost:8000` | uvicorn isn't running, or wrong port | Start uvicorn; verify with `curl /health` |
| Streamlit "ModuleNotFoundError: No module named 'src'" | Streamlit's CWD vs sys.path | Already fixed via `sys.path.insert(...)` in `app.py` & each page; if you copy a page elsewhere, replicate that hack |
| `ValueError: missing required columns: [...]` | Schema drift in source CSV | Regenerate or update `CLOUD_REQUIRED_COLS` |
| Slow first request, fast later | LRU cache warming | Expected behaviour |
| Forecast predicts negative cost | Linear extrapolation downward | Already `.clip(lower=0)`-ed |
| Anomaly model flags too many days | `CONTAMINATION` too high | Lower to `0.03` in `src/ml/anomaly.py` |
| Classifier returns 0 candidates | Threshold too strict | Lower `threshold` arg from `0.7` to `0.5` in `engine.detect_unused_licenses` |

---

# SECTION 14 — IMPROVEMENTS & SCALABILITY

## 14.1 Current Limitations

1. **No authentication.** Anyone with network access reads all financial data.
2. **CSV is not a database.** Concurrent writes are not safe; queries are O(n) full scans.
3. **No automated tests.** Manual `run_pipeline.py` is the smoke test.
4. **Single-machine training.** Won't scale beyond ~1M rows.
5. **No model versioning.** Today's model overwrites yesterday's; no rollback.
6. **No request tracing / metrics.** Debugging a slow request is grep-the-log archaeology.
7. **Dashboard is single-tenant.** Streamlit doesn't isolate state between concurrent users well.
8. **Linear regression has known limitations** — won't catch non-linear seasonality, won't model new-instance arrivals.
9. **License classifier may overfit to per-tool prior** — adding tool/department one-hot could help.
10. **No alerts.** Anomaly detection runs in batch; no Slack/email push.

## 14.2 Bottlenecks

| Bottleneck | Measurement | Fix |
|------------|-------------|-----|
| First `/recommendations` call ≈ 500ms | LRU miss + 4 detectors | Pre-warm cache in `lifespan` |
| Re-train on full year of data every night | O(n) | Incremental retrain (last 90 days) |
| Pandas groupby on 50k rows | ~150ms | Polars; or aggregate in SQL |
| Streamlit re-render on every slider tick | full page rerun | Use `st.fragment` (Streamlit ≥1.33) to scope reruns |

## 14.3 Scalability Improvements

| Improvement | Lift |
|-------------|------|
| Move processed data to Postgres + indexes | 10–100× faster queries |
| `uvicorn --workers N` behind ALB | Linear throughput scaling |
| Replace CSV ingest with Kafka stream | True real-time vs batch |
| Cache `engine.build_all_recommendations` result for 5 min | 100× faster repeat calls |
| Use `ProcessPoolExecutor` for parallel detectors | 4× engine speedup |

## 14.4 Security Improvements

1. JWT auth + role-based access.
2. HTTPS termination at nginx.
3. Rate limiting (`slowapi`).
4. Audit log: who-saw-what-when.
5. Secrets in Vault / AWS Secrets Manager.
6. DAST + SAST in CI.

## 14.5 Performance Improvements

1. Pre-warm LRU cache in `lifespan`.
2. Switch to Polars where pandas is slow.
3. Persist engine output to a cache (Redis) with 1h TTL.
4. Async DB driver (`asyncpg`) when migrating.
5. CDN for Streamlit static assets.

## 14.6 Architecture Improvements

1. Split into 3 microservices: `pipeline`, `ml-train`, `api`.
2. Add a message bus (Kafka/SQS) between ingestion and ETL.
3. Adopt a feature store (Feast) so train and serve see identical features.
4. Wrap detectors as plugins (each in its own file in `engine/detectors/`).
5. Use Airflow for the pipeline DAG with proper retries + dependencies.

## 14.7 Enterprise-Level Enhancements

1. **Multi-tenancy** — segregate data per company.
2. **SSO via SAML/OIDC** (Okta).
3. **Audit trail** — append-only event log.
4. **GDPR / SOC2 compliance** — data residency, encryption at rest.
5. **A/B test new model versions** — shadow new model in parallel for 7 days before flipping traffic.
6. **Email/Slack actionable alerts** — high-severity anomalies push to channels.
7. **Auto-remediation hooks** — for `cloud_idle` recommendations, generate a one-click Terraform PR.
8. **Cost benchmark vs peers** — anonymised industry comparisons.

---

# SECTION 15 — INTERVIEW PREPARATION

## 15.1 Complete Project Explanation (60-Second Pitch)

> "I built an end-to-end FinOps platform that automatically identifies cloud and SaaS waste. It's a Python stack: an ETL pipeline that ingests, cleans, and feature-engineers cost telemetry; three machine-learning models (linear regression for cost forecasting, isolation forest for anomaly detection, logistic regression for license-revoke classification); a unified recommendation engine combining rules and ML; a FastAPI service exposing four endpoints; and a Streamlit dashboard. On a typical synthetic dataset it identifies around ₹4.8 Cr of potential annual SaaS savings and ~7,500 idle instance-days. The whole pipeline runs nightly via cron in production."

## 15.2 Architecture Explanation (3-minute deep dive)

> "It's a 4-layer architecture. At the bottom, the pipeline layer reads raw CSV — designed to swap to Postgres via a single-file change in `dependencies.py`. The ML layer trains three sklearn models and persists them as joblib bundles. The recommendation engine sits above and combines rules and ML — idle and rightsize are rule-based for explainability, while license revoke and recent anomalies are ML-based for nuance. The API layer is FastAPI with Pydantic schemas and an `lru_cache` over data loaders so we only hit disk on first request. The presentation layer is Streamlit; every page talks to the API through a single `api_client.py`, which means we change one file to add auth or switch backends. The whole thing runs as two processes — uvicorn on 8000, streamlit on 8501 — but is k8s-ready with stateless workers."

## 15.3 Feature Explanation (per stakeholder)

- **To a CFO:** "It tells you exactly how much money you're leaving on the table this month — broken down by Stop This Instance, Revoke This License, Investigate This Day."
- **To an Engineering Manager:** "It flags days when one of your team's services blew through its budget — so you catch a runaway job within 24 hours instead of finding it on the bill 30 days later."
- **To a Data Scientist:** "Three sklearn models with proper time-aware splits, stratified sampling, and StandardScaler. Forecast uses winsorised training targets. Classifier trains against a noisy ground-truth label so it can't memorise."
- **To a Backend Engineer:** "FastAPI + Pydantic, LRU-cached loaders, all routes return 503 if data is missing and 500 with logged stack traces on real errors. CORS-locked to GET-only."

## 15.4 Challenges Faced & How Solved

1. **"The ML kept rediscovering its own labels."**
   - *Problem:* Old classifier trained on `logins_last_30d == 0` while also using it as a feature → AUC ~1.0 — too good to be true.
   - *Fix:* Introduced `truly_unused` ground truth in the data generator with realistic noise (15% of unused users had an accidental login; 10% of needed users had a quiet month). Classifier had to learn through the noise. AUC settled at ~0.95 with realistic precision/recall.

2. **"Cost forecast drifted upward."**
   - *Problem:* Anomaly days in training pulled the regression line up; forecast over-estimated.
   - *Fix:* Winsorised the training target — `y_train.clip(upper=y_train.quantile(0.95))`. Forecaster predicts baseline; anomaly detector handles spikes.

3. **"API was slow on every refresh."**
   - *Problem:* Each request re-read 50k rows from CSV.
   - *Fix:* `@lru_cache(maxsize=1)` over `get_cloud_data()` + `get_saas_data()`. First request: 50ms. Every subsequent: <1ms.

4. **"Streamlit imports failed."**
   - *Problem:* Streamlit doesn't put the project root on `sys.path`.
   - *Fix:* `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))` at the top of `app.py` and each page.

5. **"Filtering KPIs jumped on every selectbox change."**
   - *Problem:* Computing summary over the *filtered* set made the KPI tiles flicker.
   - *Fix:* Compute summary over unfiltered; filter only the displayed list.

## 15.5 Tradeoffs

| Decision | Tradeoff Chosen | Tradeoff Rejected |
|----------|-----------------|-------------------|
| CSV vs Postgres | CSV — fastest to ship, swap-ready | Postgres — slower start |
| Linear regression for forecast | Explainable + cheap | XGBoost — more accurate but opaque |
| LRU cache (in-memory) | Sub-ms reads | Redis — extra dep, no benefit at single-node scale |
| Open CORS | Frictionless dev | Locked-down origin — better security but blocks rapid iteration |
| Streamlit | Python-only UI | React+Plotly — best UX but doubles tech surface |
| sklearn (not PyTorch) | Tabular ML doesn't need deep models | PyTorch — overkill |
| Rule + ML hybrid | Explainable + nuanced | Pure ML — black-box, hard for finance to trust |

## 15.6 Why These Technologies?

- **FastAPI** over Flask: async-native, auto-Swagger, Pydantic-tight. Saves weeks of boilerplate.
- **Streamlit** over React: I'm a backend/ML engineer first; Streamlit gave me a real dashboard in one day.
- **sklearn** over PyTorch: the workload is tabular regression/classification — deep learning is the wrong hammer.
- **Pandas** over Polars: ecosystem maturity. I'll switch when data exceeds 5GB.
- **joblib** over pickle: faster on NumPy arrays, sklearn-recommended.
- **uvicorn** over gunicorn+sync: FastAPI is async-native; uvicorn is its reference server.

## 15.7 Scenario-Based Questions

**Q: "How would you handle a 100× scale-up in data?"**
> "First, move processed data to Postgres with indexes on `date` and `(instance_id, date)` — that turns 'read 50k rows' into 'read 30 days × 150 instances = 4,500 rows' with sub-10ms latency. Second, switch the pipeline to Polars or Spark — the groupby/transform pattern parallelises trivially. Third, train models on a sliding 90-day window instead of full year — keeps train time bounded. Fourth, partition `recommendations` output by `team` so each engineering manager only sees their slice."

**Q: "A user reports a recommendation is wrong. How do you debug?"**
> "First, check `metadata` on the rec — it includes the input features the detector used. Second, query the processed CSV / Postgres for that entity to see if the underlying telemetry is wrong (a Datadog agent crashed?). Third, if features look right, look at the model's `predict_proba` to see how confident it was — low confidence means the threshold needs tuning, high confidence means there's actually a labelling issue."

**Q: "How do you prevent the cost forecast from drifting?"**
> "Three lines of defence. First, the time-aware train/test split makes drift visible — if MAE grows month over month, the model is drifting. Second, daily retrain absorbs recent patterns. Third, in production I'd add a 'shadow model' running last month's checkpoint in parallel and alerting if predictions diverge by >20%."

**Q: "Walk me through what happens when a user clicks 'Download CSV'."**
> "The `Recommendations` page builds a pandas DataFrame from the in-memory `recs` list — that data was fetched by `fetch_recommendations()` (cached for 60s). `df.to_csv(index=False).encode("utf-8")` produces bytes. `st.download_button(data=csv, file_name="finops_recommendations.csv", mime="text/csv")` registers a download. Streamlit serves the bytes via a generated URL on click. No server-side state."

**Q: "Why no async route handlers?"**
> "All my workload is CPU-bound — pandas/joblib/sklearn. Async would just add complexity without throughput. uvicorn parallelises via `--workers N` for that."

**Q: "How does the recommendation engine prioritise?"**
> "Three-key sort: severity bucket first, annual savings descending, confidence descending as tiebreaker. Severity is derived from monthly savings — ≥₹50k high, ≥₹10k medium, else low. So the top of the list is always 'biggest high-confidence wins first'."

**Q: "What's the failure mode if `models/anomaly_model.joblib` is corrupted?"**
> "`joblib.load` raises a generic exception. `routes/anomalies.py` catches it via the broad `except Exception` and returns 500 with the stack trace logged. `routes/recommendations.py` would also fail because `engine.detect_recent_anomalies` calls into the same model — but only that detector. I could make the engine resilient by wrapping each detector in try/except so a failed detector emits zero recs instead of failing the whole list."

**Q: "If you had one more week, what would you add?"**
> "Pytest suite + GitHub Actions CI + JWT auth. In that order. Tests because the codebase is now too big to manually verify; CI to catch regressions; auth because v0.1 is open and shouldn't be in production."

## 15.8 HR-Style Questions

**Q: "What did you learn building this?"**
> "How to design for change — every architectural decision was 'what's the smallest swap to upgrade?' That mindset led to `dependencies.py` (one file to swap CSV → Postgres), `api_client.py` (one file to add auth), and `lifespan` (one place to pre-warm caches)."

**Q: "What's the part you're proudest of?"**
> "The data generator. Most ML projects show models hitting 99% on data that was secretly hand-labelled. I deliberately built noise into the ground truth — the classifier has to learn through realistic ambiguity, and I think that makes the AUC of 0.95 actually mean something."

**Q: "Where did you ask for help?"**
> "I researched proper time-series train/test splits before deciding on the 80/20 chronological split — easy mistake to randomly split and silently leak future into past."

**Q: "How do you handle disagreement with a stakeholder?"**
> "I show them the data. For example, the CFO might think a recommendation is wrong; I'd open the metadata, show them the 30-day CPU history, and the model's confidence. If the data backs the model, the case closes itself. If the data is bad, that's a different fix."

## 15.9 Technical Cross-Questions

**Q: "Why `lru_cache(maxsize=1)` and not `maxsize=None`?"**
> "There's exactly one cloud DataFrame and one SaaS DataFrame; no key-based variation. `maxsize=1` makes the intent explicit and prevents future contributors from accidentally caching every variant of an argument."

**Q: "Why round costs to 2 decimals before returning from the API?"**
> "Visual neatness in the dashboard + smaller JSON payloads. Internally we keep full precision until the very last serialisation."

**Q: "Pydantic v2 — what's different from v1 that mattered?"**
> "Faster validation (Rust-backed), stricter types by default, and `model_dump()` replaces `.dict()`. `engine.py` uses `r.model_dump()` to convert `Recommendation` → dict for the API response."

**Q: "Why `random_state=42` everywhere?"**
> "Reproducibility. Same data → same model → same predictions. 42 is the conventional choice; could be any integer."

**Q: "Stratified vs random split for the classifier?"**
> "Class imbalance — `truly_unused` rate is ~22%. Random splits could under-represent the minority class in test. Stratified keeps the test set proportional."

**Q: "Why `confidence=1.0` for rule-based detectors?"**
> "The rule is deterministic. If `idle_ratio >= 0.8 AND avg_cpu < 5` holds, there's no probability — it just is. I might revisit this for the dashboard: a fixed 1.0 makes rule-based items always sort top, which is what we want."

## 15.10 Strong Resume Description

> **AI IT Optimization — FinOps Platform** (Python · FastAPI · scikit-learn · Streamlit)
>
> Designed and built an end-to-end data engineering + ML platform that automatically identifies cloud and SaaS spending waste. Engineered a 3-stage ETL pipeline (ingest, clean, transform) with schema validation, per-instance median null fill, and feature engineering. Trained three sklearn models — linear regression with winsorised target for daily cost forecasting (MAE within 8%), isolation forest with 5% contamination for multivariate anomaly detection, logistic regression with StandardScaler for SaaS license revoke classification (AUC ≈ 0.95). Built a unified recommendation engine combining rule-based detectors (idle, rightsize) with ML-based detectors (revoke, anomaly), exposed via a FastAPI service with Pydantic schemas, LRU-cached data loaders, and auto-generated Swagger documentation. Shipped a Streamlit dashboard with category/severity filters, interactive forecast slider, CSV export, and 60-second client-side caching. Identified ~₹4.8 Cr potential annual SaaS savings and ~7,500 idle instance-days on a representative 365-day dataset.

---

# APPENDIX A — FILE-TO-MODULE DEPENDENCY MAP

```
generate_data.py (script)
   └── (stdlib only: random, datetime, pathlib) + numpy + pandas

run_pipeline.py (script)
   ├── src.pipeline.ingest
   │     └── src.utils.logger
   ├── src.pipeline.clean
   │     └── src.utils.logger
   └── src.pipeline.transform
         └── src.utils.logger

train_models.py (script)
   ├── src.ml.forecast
   │     └── sklearn.linear_model, sklearn.metrics, sklearn.model_selection
   ├── src.ml.anomaly
   │     └── sklearn.ensemble
   └── src.ml.license_classifier
         └── sklearn.linear_model, sklearn.metrics, sklearn.model_selection, sklearn.preprocessing

src/api/main.py
   ├── src.api.routes.forecast
   │     ├── src.api.dependencies
   │     ├── src.api.schemas
   │     └── src.ml.forecast
   ├── src.api.routes.anomalies
   │     ├── src.api.dependencies
   │     ├── src.api.schemas
   │     └── src.ml.anomaly
   ├── src.api.routes.recommendations
   │     ├── src.api.dependencies
   │     ├── src.api.schemas
   │     └── src.recommendations.engine
   │           ├── src.recommendations.schema
   │           ├── src.ml.license_classifier
   │           └── src.ml.anomaly
   └── src.api.schemas (HealthResponse)

src/dashboard/app.py
   └── src.dashboard.api_client
         └── (HTTP) → src/api/main.py
src/dashboard/pages/*.py
   └── src.dashboard.api_client
```

# APPENDIX B — GLOSSARY

| Term | Definition |
|------|------------|
| **AUC** | Area Under the ROC Curve. 1.0 = perfect classifier, 0.5 = random. |
| **Contamination** | Isolation Forest's expected outlier fraction. We set 0.05. |
| **CUR** | Cost Usage Report — AWS's detailed billing export. |
| **FinOps** | "Financial Operations" — DevOps for cloud spend. |
| **Idle ratio** | Idle days / total days in the last 30. |
| **Isolation Forest** | Unsupervised anomaly detector using random tree path lengths. |
| **Joblib** | Pickle-like serialiser optimised for NumPy arrays. |
| **LRU cache** | Least-Recently-Used cache; here used as "memoise this function". |
| **MAE** | Mean Absolute Error. |
| **MAPE** | Mean Absolute Percentage Error. |
| **Pydantic** | Python data validation library; substrate of FastAPI. |
| **Right-sizing** | Downgrading an over-provisioned instance. |
| **Stratified split** | Train/test split preserving class proportions. |
| **Winsorise** | Cap extreme values at a percentile to reduce their influence. |
| **Zombie instance** | Running but doing nothing useful. |

---

*End of Documentation. Approx. word count: ~21,000. Approx. PDF page count: ~80 at standard A4 11pt.*

*Maintained by: Yathish Shetty. Last reviewed: 2026-05-28.*
