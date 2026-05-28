"""
license_classifier.py
---------------------
Classifies each SaaS license as 'revoke' or 'keep' using logistic regression.

Why logistic regression?
- Output is binary — perfect fit
- Coefficients are interpretable ("logins matters most")
- predict_proba gives a confidence score the recommendation engine
  can sort by, so we surface the most-confident revokes first
- Robust on small data (we have 385 rows — a deep model would overfit)

How do we get labels?
The raw data has no 'should_revoke' column. We CREATE labels using
domain rules — this is called 'weak supervision' or 'rule-based
labeling'. In production, you'd refine these labels over time as
admins approve/reject the model's suggestions.

Our labeling rule:
    revoke = (logins_last_30d == 0) OR
             (active_days_last_30d <= 1 AND days_since_last_login > 30)

The classifier then learns these patterns AND generalizes to edge
cases the rule misses. That's the win — once trained, the model
catches "almost-unused" licenses the hand-rule wouldn't.
"""
from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.utils.logger import get_logger

log = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

# Numeric features the model learns from. We deliberately leave OUT
# things like user_id and employee_name — the model should not
# memorize people, it should learn USAGE PATTERNS.
LICENSE_FEATURE_COLS = [
    "logins_last_30d",
    "active_days_last_30d",
    "days_since_last_login",
    "monthly_cost_inr",
]


def _create_labels(df: pd.DataFrame) -> pd.Series:
    """
    Labels = ground truth.

    Preferred source is the `truly_unused` column, which the data generator
    produces as a delayed signal of whether the license is actually needed.
    It is NOT a deterministic function of the features the model trains on,
    so the classifier has to learn a noisy probabilistic relationship
    instead of memorizing a rule.

    Falls back to the old weak-supervision rule if `truly_unused` is missing
    (legacy datasets), so this code stays backward-compatible.
    """
    if "truly_unused" in df.columns:
        return df["truly_unused"].astype(int)
    return (
        (df["logins_last_30d"] == 0) |
        ((df["active_days_last_30d"] <= 1) & (df["days_since_last_login"] > 30))
    ).astype(int)


def train_license_classifier(df: pd.DataFrame) -> dict:
    """Train + persist the classifier. Returns metrics."""
    df = df.copy()
    df["label"] = _create_labels(df)

    X = df[LICENSE_FEATURE_COLS]
    y = df["label"]

    # Stratified split — preserves class balance in test set.
    # Critical when classes are imbalanced (which they often are here).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )

    # StandardScaler: logistic regression is sensitive to feature scale.
    # `monthly_cost_inr` (1000s) would otherwise dominate `logins` (10s).
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_s, y_train)

    y_pred  = model.predict(X_test_s)
    y_proba = model.predict_proba(X_test_s)[:, 1]
    auc = roc_auc_score(y_test, y_proba)

    log.info(f"Classifier AUC: {auc:.3f}")
    log.info("Classification report:\n" +
             classification_report(y_test, y_pred,
                                   target_names=["keep", "revoke"]))

    metrics = {
        "auc": round(float(auc), 3),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "positive_rate": round(float(y.mean()), 3),
    }

    out = MODELS_DIR / "license_classifier.joblib"
    joblib.dump({
        "model": model,
        "scaler": scaler,
        "feature_cols": LICENSE_FEATURE_COLS,
        "metrics": metrics,
    }, out)
    log.info(f"Saved license classifier to {out}")

    # Bonus: log feature importance (= coefficient sign + magnitude)
    coefs = dict(zip(LICENSE_FEATURE_COLS, model.coef_[0].round(3)))
    log.info(f"Model coefficients (positive => pushes toward revoke): {coefs}")

    return metrics


def predict_revoke_candidates(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Score each license. Returns the candidates whose revoke-probability
    >= threshold, sorted by confidence (most-confident first) so the
    recommendation engine can surface the easy wins.
    """
    bundle = joblib.load(MODELS_DIR / "license_classifier.joblib")
    model, scaler, cols = bundle["model"], bundle["scaler"], bundle["feature_cols"]

    df = df.copy()
    X = scaler.transform(df[cols])
    df["revoke_probability"] = model.predict_proba(X)[:, 1].round(4)
    df["revoke_recommended"] = df["revoke_probability"] >= threshold

    candidates = df[df["revoke_recommended"]].copy()
    candidates = candidates.sort_values("revoke_probability", ascending=False)
    return candidates[[
        "user_id", "employee_name", "department", "tool",
        "license_type", "monthly_cost_inr", "annual_cost_inr",
        "logins_last_30d", "days_since_last_login",
        "revoke_probability",
    ]]