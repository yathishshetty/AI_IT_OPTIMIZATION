"""
anomaly.py
----------
Detects unusual cost / usage days using Isolation Forest.

Why Isolation Forest (not Z-score, not DBSCAN)?
- Z-score assumes normal distribution & one column. Real cost data
  is right-skewed (a few huge days) and we care about MULTIVARIATE
  weirdness (cost is high AND CPU is high AND it's a weekend).
- Isolation Forest works by building random trees and seeing how
  quickly each point gets isolated. Outliers separate fast → low
  "path length" → flagged. No distribution assumption.

What we feed it:
- daily_cost_inr     — total spend that day
- daily_avg_cpu      — average utilization across the fleet
- daily_hours        — total compute hours
- is_weekend         — context feature: weekends usually cost less
                       so a high-cost weekend is more anomalous

Why no labels? Because nobody hand-labels "this day was weird".
Anomaly detection is fundamentally an UNSUPERVISED problem.
"""
from __future__ import annotations
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from src.utils.logger import get_logger

log = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

ANOMALY_FEATURE_COLS = ["daily_cost_inr", "daily_avg_cpu",
                        "daily_hours", "is_weekend"]
# 5% of days = anomalies. Tunable. Higher = more noise, lower = miss things.
CONTAMINATION = 0.05


def _build_daily_features(df: pd.DataFrame) -> pd.DataFrame:
    """Roll up to one row per day with the features Isolation Forest needs."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date").agg(
        daily_cost_inr=("cost_inr", "sum"),
        daily_avg_cpu=("cpu_utilization_avg", "mean"),
        daily_hours=("hours_running", "sum"),
    ).reset_index()
    daily["is_weekend"] = (daily["date"].dt.dayofweek >= 5).astype(int)
    return daily


def train_anomaly_model(df: pd.DataFrame) -> dict:
    """
    Train Isolation Forest on daily aggregates.
    No train/test split — unsupervised models train on everything.
    """
    daily = _build_daily_features(df)
    X = daily[ANOMALY_FEATURE_COLS]

    model = IsolationForest(
        n_estimators=100,
        contamination=CONTAMINATION,    # expected fraction of outliers
        random_state=42,
    )
    model.fit(X)

    # Score the training data so we can report what was found
    daily["anomaly_score"] = model.decision_function(X)        # higher = more normal
    daily["is_anomaly"] = (model.predict(X) == -1)             # -1 = outlier in sklearn

    n_anom = daily["is_anomaly"].sum()
    log.info(f"Anomaly model trained: flagged {n_anom}/{len(daily)} days "
             f"({100*n_anom/len(daily):.1f}%)")

    out = MODELS_DIR / "anomaly_model.joblib"
    joblib.dump({"model": model, "feature_cols": ANOMALY_FEATURE_COLS}, out)
    log.info(f"Saved anomaly model to {out}")

    return {"days_scored": len(daily), "anomalies_detected": int(n_anom)}


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score every day in the dataset and return only the anomalies,
    sorted by date. Each row carries enough context for the API.
    """
    bundle = joblib.load(MODELS_DIR / "anomaly_model.joblib")
    model, cols = bundle["model"], bundle["feature_cols"]

    daily = _build_daily_features(df)
    daily["anomaly_score"] = model.decision_function(daily[cols])
    daily["is_anomaly"] = (model.predict(daily[cols]) == -1)

    anom = daily[daily["is_anomaly"]].copy()
    anom = anom.sort_values("date")
    # Round for API neatness
    anom["daily_cost_inr"] = anom["daily_cost_inr"].round(2)
    anom["daily_avg_cpu"] = anom["daily_avg_cpu"].round(2)
    anom["anomaly_score"] = anom["anomaly_score"].round(4)
    return anom[["date", "daily_cost_inr", "daily_avg_cpu",
                 "daily_hours", "is_weekend", "anomaly_score"]]