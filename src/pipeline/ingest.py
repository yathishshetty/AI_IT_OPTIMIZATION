"""
ingest.py
---------
Stage 1 of the pipeline: EXTRACT.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

from src.utils.logger import get_logger

log = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CLOUD_REQUIRED_COLS = {
    "date", "instance_id", "instance_type", "region", "environment",
    "cpu_utilization_avg", "cpu_utilization_max", "hours_running", "cost_inr",
}
SAAS_REQUIRED_COLS = {
    "user_id", "employee_name", "department", "tool", "license_type",
    "monthly_cost_inr", "logins_last_30d", "active_days_last_30d",
    "last_login_date", "assigned_date",
}


def _read_csv(path: Path, required_cols: set) -> pd.DataFrame:
    """Generic CSV reader with schema validation."""
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    df = pd.read_csv(path)
    log.info(f"Loaded {len(df):,} rows from {path.name}")

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing)}. "
            f"Found: {sorted(df.columns)}"
        )
    return df


def load_cloud_usage(path=None) -> pd.DataFrame:
    """Load raw cloud usage CSV."""
    path = path or (RAW_DIR / "cloud_usage.csv")
    return _read_csv(path, CLOUD_REQUIRED_COLS)


def load_saas_usage(path=None) -> pd.DataFrame:
    """Load raw SaaS usage CSV."""
    path = path or (RAW_DIR / "saas_usage.csv")
    return _read_csv(path, SAAS_REQUIRED_COLS)