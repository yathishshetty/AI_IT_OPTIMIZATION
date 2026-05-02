"""
transform.py
------------
Stage 2 (part 2): TRANSFORM.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from datetime import datetime

from src.utils.logger import get_logger

log = get_logger(__name__)


def transform_cloud_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Add features derived from cleaned cloud usage data."""
    df = df.copy()

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    def _band(cpu: float) -> str:
        if cpu < 5:
            return "idle"
        if cpu < 20:
            return "low"
        if cpu < 70:
            return "normal"
        return "high"

    df["utilization_band"] = df["cpu_utilization_avg"].apply(_band)

    df["is_idle_candidate"] = (
        (df["cpu_utilization_avg"] < 5) & (df["hours_running"] >= 20)
    )

    df["daily_waste_inr"] = np.where(df["is_idle_candidate"], df["cost_inr"], 0.0)

    log.info(
        f"Transformed cloud: {len(df):,} rows | "
        f"idle rows = {df['is_idle_candidate'].sum()} | "
        f"est. waste = Rs.{df['daily_waste_inr'].sum():,.2f}"
    )
    return df


def transform_saas_usage(df: pd.DataFrame, today=None) -> pd.DataFrame:
    """Add features for SaaS license analysis."""
    df = df.copy()
    today = today or pd.Timestamp.today().normalize()

    df["has_ever_logged_in"] = df["last_login_date"].notna()
    df["days_since_last_login"] = (today - df["last_login_date"]).dt.days
    df["days_since_last_login"] = df["days_since_last_login"].fillna(999).astype(int)

    def _category(row) -> str:
        if row["logins_last_30d"] == 0:
            return "unused"
        if row["active_days_last_30d"] < 3:
            return "low"
        return "active"

    df["usage_category"] = df.apply(_category, axis=1)
    df["annual_cost_inr"] = df["monthly_cost_inr"] * 12
    df["is_recommendation_candidate"] = df["usage_category"].isin(["unused", "low"])

    log.info(
        f"Transformed SaaS: {len(df):,} rows | "
        f"reco candidates = {df['is_recommendation_candidate'].sum()} | "
        f"potential annual savings = "
        f"Rs.{df.loc[df['is_recommendation_candidate'], 'annual_cost_inr'].sum():,.2f}"
    )
    return df