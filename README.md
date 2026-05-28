# AI IT Optimization — FinOps Platform

A data engineering and machine learning project that automatically identifies
cloud and SaaS waste using an ETL pipeline and three ML models.

---

## 💡 What It Found

(Numbers below are illustrative — they regenerate every time you re-run the
data generator, because anomalies and behaviours are drawn from probability
distributions rather than hard-coded.)

- **~₹6 Cr/year** total cloud spend under analysis
- **~₹4.8 Cr/year** potential SaaS savings
- **~7,500 idle instance-days** identified across the fleet
- **~700 "truly unused" licenses** flagged by the classifier (out of ~3,100)
- **19 anomalous days** auto-detected (planted at random dates each run)

---

## 🏗️ Project Structure

```
AI_IT_OPTIMIZATION/
├── data/
│   ├── raw/                        # Source CSV files (regenerable)
│   └── processed/                  # Pipeline output
├── src/
│   ├── pipeline/
│   │   ├── ingest.py               # Extract — reads & validates CSVs
│   │   ├── clean.py                # Clean — dedup, fix types, fill nulls
│   │   └── transform.py            # Transform — feature engineering
│   ├── ml/
│   │   ├── forecast.py             # Cost forecasting model
│   │   ├── anomaly.py              # Anomaly detection model
│   │   └── license_classifier.py   # License revoke/keep classifier
│   ├── recommendations/
│   │   ├── schema.py               # Recommendation Pydantic model + severity rules
│   │   └── engine.py               # Unified rules + ML detectors
│   ├── api/                        # FastAPI service
│   │   ├── main.py                 # App + lifespan
│   │   ├── dependencies.py         # Cached data loaders
│   │   ├── schemas.py              # API Pydantic models
│   │   └── routes/                 # /cost-forecast, /anomalies, /recommendations
│   ├── dashboard/                  # Streamlit dashboard
│   │   ├── app.py                  # Landing page
│   │   ├── api_client.py           # Single point of contact with the API
│   │   └── pages/                  # Cost trends, anomalies, recommendations
│   └── utils/
│       └── logger.py
├── scripts/
│   ├── generate_data.py            # Synthetic data generator (probabilistic)
│   ├── run_pipeline.py             # ETL entry point
│   └── train_models.py             # ML training entry point
├── models/
│   ├── forecast_model.joblib
│   ├── anomaly_model.joblib
│   └── license_classifier.joblib
└── requirements.txt
```

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/AI_IT_OPTIMIZATION.git
cd AI_IT_OPTIMIZATION
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate synthetic source data
```bash
python scripts/generate_data.py
```
Re-run this any time you want a fresh dataset — anomalies and behaviours
are drawn from probability distributions so the planted "waste" looks
different on every run.

### 5. Run the ETL pipeline
```bash
python scripts/run_pipeline.py
```

### 6. Train the ML models
```bash
python scripts/train_models.py
```

### 7. Start the API and dashboard (in two terminals)
```bash
# Terminal 1 — FastAPI backend
uvicorn src.api.main:app --port 8000

# Terminal 2 — Streamlit dashboard
streamlit run src/dashboard/app.py
```

---

## 📊 Pipeline Output (typical run)

| Metric | Value |
|--------|-------|
| Raw cloud rows | ~49,000 |
| After dedup | ~49,000 |
| Idle instance-days (CPU < 5%, idle ≥ 80% of last 30d) | ~7,500 |
| Cloud spend analysed (365 days) | ~₹6 Cr |
| SaaS licenses analysed | ~3,100 |
| Truly-unused licenses (ground truth) | ~700 (≈22%) |
| Zero-login licenses (observable) | ~250 |
| Potential annual saving | ~₹4.8 Cr |

---

## 🤖 ML Models

| Model | Algorithm | Purpose | Notes |
|-------|-----------|---------|-------|
| Cost Forecaster | Linear Regression | Predicts daily cloud spend | Time-aware split; deliberately a simple baseline. Random anomalies and seasonality mean it has real noise to fight — useful for benchmarking richer models. |
| Anomaly Detector | Isolation Forest (unsupervised, 5% contamination) | Flags abnormal cost days | Anomalies are planted at random dates each run, so the model has to actually find them rather than memorize calendar dates. |
| License Classifier | Logistic Regression | Scores licenses for cancellation | Trained against a `truly_unused` ground-truth label that is NOT a deterministic function of the input features. AUC typically ~0.95 with realistic precision/recall trade-off. |

### Why the classifier feels honest now

Earlier versions trained on a label derived from `logins_last_30d == 0` while
also feeding `logins_last_30d` as a feature — essentially handing the model
the answer key. The current generator emits a `truly_unused` flag (the
"would an admin actually revoke this in 90 days?" signal) with realistic
noise: ~10% of truly-needed users still had a quiet month, ~15% of truly-
unused users still logged in once or twice. The classifier sees this noise
and has to learn through it.

---

## 📈 Project Status

- [x] ETL pipeline — ingest, clean, transform
- [x] ML layer — forecasting, anomaly detection, classification
- [x] Unified recommendation engine (rules + ML)
- [x] FastAPI layer — `/cost-forecast`, `/anomalies`, `/recommendations`, `/health`
- [x] Streamlit dashboard with cost trends, anomalies, and filterable recommendations
- [x] Realistic synthetic data generator (probabilistic behaviours, random anomalies, ground-truth labels)

---

## 🛠️ Tech Stack

- Python 3.14
- Pandas
- Scikit-learn
- Matplotlib
- OpenPyXL

---

## ⏰ Production Scheduling

Designed to run daily via cron at 2 AM IST:
```
30 20 * * * cd /path/to/project && python scripts/run_pipeline.py
```

---

## 👤 Author

Yathish — [LinkedIn](https://linkedin.com/in/yourprofile)
