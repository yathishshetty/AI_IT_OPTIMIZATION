# AI IT Optimization — FinOps Platform

A data engineering project that automatically identifies 
cloud and SaaS waste using an ETL pipeline.

## 💡 What It Found
- **₹57,62,400/year** potential SaaS savings
- **341 idle cloud instance-days** identified
- **152 zero-login licenses** flagged for cancellation
- **₹39,552** wasted on idle dev/test servers over 90 days

## 🏗️ Project Structure

AI_IT_OPTIMIZATION/
├── data/
│   ├── raw/                  # Source CSV files
│   └── processed/            # Pipeline output
├── src/
│   ├── pipeline/
│   │   ├── ingest.py         # Extract — reads & validates CSVs
│   │   ├── clean.py          # Transform — dedup, fix types, fill nulls
│   │   └── transform.py      # Transform — feature engineering
│   └── utils/
│       └── logger.py         # Logging utility
├── scripts/
│   └── run_pipeline.py       # Pipeline entry point
└── requirements.txt

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

### 4. Run the pipeline
```bash
python scripts/run_pipeline.py
```

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

## 🛠️ Tech Stack
- Python 3.11
- Pandas
- OpenPyXL

## ⏰ Production Scheduling
Designed to run daily via cron at 2 AM IST:
30 20 * * * cd /path/to/project && python scripts/run_pipeline.py

## 👤 Author
Your Name — [LinkedIn](https://linkedin.com/in/yourprofile)