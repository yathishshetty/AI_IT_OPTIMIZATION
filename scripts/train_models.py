"""
train_models.py
---------------
Trains all ML models from the processed data files.
Run after run_pipeline.py.

Typical schedule:
    02:00  cron → run_pipeline.py    (build today's processed data)
    03:00  cron → train_models.py    (retrain with fresh data)

Why retrain daily?
- New patterns emerge (new instances, new SaaS users).
- Drift: models trained on Jan data degrade by April.
- It's cheap (these models train in <1s).

In a serious shop you'd add: model versioning, A/B testing the new
vs old model, automatic rollback if metrics drop. v1 doesn't need that.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.ml import forecast, anomaly, license_classifier
from src.utils.logger import get_logger

log = get_logger("train")

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> int:
    try:
        cloud = pd.read_csv(PROCESSED_DIR / "cloud_usage_processed.csv")
        saas  = pd.read_csv(PROCESSED_DIR / "saas_usage_processed.csv")

        log.info("--- Training cost forecaster ---")
        forecast.train_forecast_model(cloud)

        log.info("--- Training anomaly detector ---")
        anomaly.train_anomaly_model(cloud)

        log.info("--- Training license classifier ---")
        license_classifier.train_license_classifier(saas)

        log.info("All models trained successfully")
        return 0
    except Exception as e:
        log.exception(f"Training failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())