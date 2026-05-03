# AI IT Optimization — FinOps Platform

A data engineering and machine learning project that automatically identifies
cloud and SaaS waste using an ETL pipeline and three ML models.

---

## 💡 What It Found

- **₹57,62,400/year** potential SaaS savings
- **341 idle cloud instance-days** identified
- **152 zero-login licenses** flagged for cancellation
- **₹39,552** wasted on idle dev/test servers over 90 days
- **April 2nd cost spike** automatically detected by anomaly model

---

## 🏗️ Project Structure

```
AI_IT_OPTIMIZATION/
├── data/
│   ├── raw/                        # Source CSV files
│   └── processed/                  # Pipeline output
├── src/
│   ├── pipeline/
│   │   ├── ingest.py               # Extract — reads & validates CSVs
│   │   ├── clean.py                # Clean — dedup, fix types, fill nulls
│   │   └── transform.py            # Transform — feature engineering
│   ├── utils/
│   │   └── logger.py               # Logging utility
│   └── ml/
│       ├── forecast.py             # Cost forecasting model
│       ├── anomaly.py              # Anomaly detection model
│       └── license_classifier.py  # License revoke/keep classifier
├── scripts/
│   ├── run_pipeline.py             # ETL entry point
│   └── train_models.py            # ML training entry point
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

### 4. Run the ETL pipeline
```bash
python scripts/run_pipeline.py
```

### 5. Train the ML models
```bash
python scripts/train_models.py
```

---

## 📊 Pipeline Output

| Metric | Value |
|--------|-------|
| Raw cloud rows | 1,370 |
| After dedup | 1,350 |
| Idle instance-days | 341 |
| Cloud waste (90 days) | ₹39,552 |
| SaaS licenses analysed | 385 |
| Zero-login licenses | 152 |
| Potential annual saving | ₹57,62,400 |

---

## 🤖 ML Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| Cost Forecaster | Linear Regression | Predicts daily cloud spend |
| Anomaly Detector | Isolation Forest | Flags abnormal cost days |
| License Classifier | Logistic Regression | Scores licenses for cancellation |

---

## 📈 Project Status

- [x] ETL pipeline — ingest, clean, transform
- [x] ML layer — forecasting, anomaly detection, classification
- [ ] FastAPI layer — REST endpoints for all three models
- [ ] Streamlit dashboard

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
