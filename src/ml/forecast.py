"""
forecast.py
-----------
Predicts future daily cloud cost using linear regression with
engineered time features.

Why linear regression?
- Explainable to finance teams (each coefficient = a clear effect)
- Fast to train, easy to ship
- Strong baseline — anything fancier (Prophet, XGBoost, LSTM) must
  outperform this to be worth the operational complexity

What we DON'T do (and why):
- We don't fit on instance-level cost. Too noisy. We aggregate
  to daily total cost first — that's the question the CFO asks.
- We don't use raw dates as features. Models can't learn from
  pandas timestamps. We extract: day_of_week, day_of_month,
  month, days_since_start (the trend signal).
"""
from __future__ import annotations
from datetime import timedelta
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from src.utils.logger import get_logger

log = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = ["days_since_start", "day_of_week", "day_of_month",
                "month", "is_weekend"]


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate to daily total cost and add time features.
    The aggregation step is critical — forecasting per-instance is
    a different (much harder) problem.
    """
    daily = df.groupby("date", as_index=False)["cost_inr"].sum()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    daily["days_since_start"] = (daily["date"] - daily["date"].min()).dt.days
    daily["day_of_week"]  = daily["date"].dt.dayofweek
    daily["day_of_month"] = daily["date"].dt.day
    daily["month"]        = daily["date"].dt.month
    daily["is_weekend"]   = (daily["day_of_week"] >= 5).astype(int)
    return daily


def train_forecast_model(df: pd.DataFrame) -> dict:
    """
    Train a linear regression on daily cost.
    Returns metrics + persists the trained model to disk.
    """
    daily = _build_features(df)
    X, y = daily[FEATURE_COLS], daily["cost_inr"]

    # Time-aware split: the LAST 20% is our test set, never random.
    # Why? Random split lets future leak into training — a classic mistake.
    split_idx = int(len(daily) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2  = r2_score(y_test, y_pred)
    mape = (np.abs((y_test - y_pred) / y_test)).mean() * 100

    metrics = {
        "mae_inr": round(float(mae), 2),
        "r2": round(float(r2), 3),
        "mape_pct": round(float(mape), 2),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }
    log.info(f"Forecast model trained: {metrics}")

    # Persist for the API to load later. joblib > pickle for sklearn.
    out = MODELS_DIR / "forecast_model.joblib"
    joblib.dump({"model": model, "feature_cols": FEATURE_COLS,
                 "min_date": daily["date"].min(), "metrics": metrics}, out)
    log.info(f"Saved forecast model to {out}")

    return metrics


def predict_future_costs(df: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
    """
    Predict the next `days_ahead` daily costs.
    Loads the persisted model so the API doesn't retrain on each call.
    """
    bundle = joblib.load(MODELS_DIR / "forecast_model.joblib")
    model = bundle["model"]
    min_date = bundle["min_date"]

    daily = _build_features(df)
    last_date = daily["date"].max()

    # Build feature rows for the future window
    future = pd.DataFrame({
        "date": [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    })
    future["days_since_start"] = (future["date"] - min_date).dt.days
    future["day_of_week"]  = future["date"].dt.dayofweek
    future["day_of_month"] = future["date"].dt.day
    future["month"]        = future["date"].dt.month
    future["is_weekend"]   = (future["day_of_week"] >= 5).astype(int)

    future["predicted_cost_inr"] = model.predict(future[FEATURE_COLS])
    # Cost can never be negative — clip. Linear models can predict <0
    # if the trend is downward, which is mathematically valid but
    # business-nonsensical.
    future["predicted_cost_inr"] = future["predicted_cost_inr"].clip(lower=0).round(2)

    return future[["date", "predicted_cost_inr"]]