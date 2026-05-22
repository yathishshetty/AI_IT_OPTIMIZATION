"""
dependencies.py
---------------
Shared loaders used by every route.

KEY PERFORMANCE PATTERN:
    @lru_cache means each CSV is read from disk EXACTLY ONCE per process.
    On every subsequent request, we return the cached DataFrame.

    Without caching: every request = re-read 1,350 rows = 50ms+ wasted.
    With caching:    first request = 50ms, all others = 0.001ms.

In production you'd swap the @lru_cache for a real DB query (Postgres / Redshift).
That's also a great interview point: "I designed the loader as a single function
so swapping CSV → Postgres is a one-file change."
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@lru_cache(maxsize=1)
def get_cloud_data() -> pd.DataFrame:
    """Load processed cloud usage. Cached for the life of the process."""
    path = PROCESSED_DIR / "cloud_usage_processed.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Processed cloud data not found at {path}. "
            f"Run scripts/run_pipeline.py first."
        )
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


@lru_cache(maxsize=1)
def get_saas_data() -> pd.DataFrame:
    """Load processed SaaS usage. Cached."""
    path = PROCESSED_DIR / "saas_usage_processed.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Processed SaaS data not found at {path}. "
            f"Run scripts/run_pipeline.py first."
        )
    df = pd.read_csv(path)
    return df


def clear_cache() -> None:
    """Useful for tests or when the pipeline produces fresh data."""
    get_cloud_data.cache_clear()
    get_saas_data.cache_clear()