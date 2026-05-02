"""
run_pipeline.py
---------------
End-to-end pipeline runner. This is the script a scheduler (cron, Airflow,
GitHub Actions on a schedule) calls.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import ingest, clean, transform
from src.utils.logger import get_logger

log = get_logger("pipeline")

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def run_cloud_pipeline() -> None:
    log.info("=== CLOUD PIPELINE START ===")
    raw = ingest.load_cloud_usage()
    cleaned = clean.clean_cloud_usage(raw)
    transformed = transform.transform_cloud_usage(cleaned)

    out = PROCESSED_DIR / "cloud_usage_processed.csv"
    transformed.to_csv(out, index=False)
    log.info(f"Wrote {out} ({len(transformed):,} rows)")
    log.info("=== CLOUD PIPELINE DONE ===\n")


def run_saas_pipeline() -> None:
    log.info("=== SAAS PIPELINE START ===")
    raw = ingest.load_saas_usage()
    cleaned = clean.clean_saas_usage(raw)
    transformed = transform.transform_saas_usage(cleaned)

    out = PROCESSED_DIR / "saas_usage_processed.csv"
    transformed.to_csv(out, index=False)
    log.info(f"Wrote {out} ({len(transformed):,} rows)")
    log.info("=== SAAS PIPELINE DONE ===\n")


def main() -> int:
    try:
        run_cloud_pipeline()
        run_saas_pipeline()
        return 0
    except Exception as e:
        log.exception(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())