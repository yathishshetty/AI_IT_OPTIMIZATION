"""
clean.py
--------
Stage 2 (part 1): CLEAN.
"""
from __future__ import annotations
import pandas as pd
import numpy as np

from src.utils.logger import get_logger

log = get_logger(__name__)


def clean_cloud_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw cloud usage data."""
    df = df.copy()
    n_in = len(df)

    df = df.drop_duplicates()
    log.info(f"Dropped {n_in - len(df)} duplicate cloud rows")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        bad = df["date"].isna().sum()
        log.warning(f"{bad} rows had unparseable dates - dropping them")
        df = df.dropna(subset=["date"])

    numeric_cols = ["cpu_utilization_avg", "cpu_utilization_max",
                    "hours_running", "cost_inr"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["region", "environment", "instance_type"]:
        df[col] = df[col].astype(str).str.strip().str.lower()

    nulls_before = df["cpu_utilization_avg"].isna().sum()
    df["cpu_utilization_avg"] = df.groupby("instance_id")["cpu_utilization_avg"]\
                                  .transform(lambda s: s.fillna(s.median()))
    df["cpu_utilization_avg"] = df["cpu_utilization_avg"].fillna(0.0)
    log.info(f"Filled {nulls_before} null CPU values using per-instance medians")

    bad_cost = (df["cost_inr"] < 0).sum()
    if bad_cost:
        log.warning(f"Found {bad_cost} rows with negative cost - clipping to 0")
        df["cost_inr"] = df["cost_inr"].clip(lower=0)

    log.info(f"Cleaned cloud rows: {n_in} -> {len(df)}")
    return df


def clean_saas_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw SaaS usage data."""
    df = df.copy()
    n_in = len(df)

    df = df.drop_duplicates(subset=["user_id", "tool"])
    log.info(f"Dropped {n_in - len(df)} duplicate (user, tool) rows")

    df["last_login_date"] = pd.to_datetime(df["last_login_date"], errors="coerce")
    df["assigned_date"] = pd.to_datetime(df["assigned_date"], errors="coerce")

    for col in ["monthly_cost_inr", "logins_last_30d", "active_days_last_30d"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["department", "tool", "license_type"]:
        df[col] = df[col].astype(str).str.strip()

    log.info(f"Cleaned SaaS rows: {n_in} -> {len(df)}")
    return df