"""
routes/anomalies.py
-------------------
GET /anomalies

Returns days that were flagged as anomalous by the Isolation Forest model.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException

from src.api.dependencies import get_cloud_data
from src.api.schemas import AnomalyResponse, AnomalyItem
from src.ml import anomaly as anomaly_model
from src.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=AnomalyResponse)
def get_anomalies() -> AnomalyResponse:
    """
    Return all anomalous days detected on the current dataset.
    Sorted by date (chronological), oldest first.
    """
    try:
        df = get_cloud_data()
        anomalies_df = anomaly_model.detect_anomalies(df)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.exception("Anomaly detection failed")
        raise HTTPException(status_code=500, detail="Anomaly detection failed")

    items = [
        AnomalyItem(
            date=row["date"].date() if hasattr(row["date"], "date") else row["date"],
            daily_cost_inr=float(row["daily_cost_inr"]),
            daily_avg_cpu=float(row["daily_avg_cpu"]),
            daily_hours=int(row["daily_hours"]),
            is_weekend=bool(row["is_weekend"]),
            anomaly_score=float(row["anomaly_score"]),
        )
        for _, row in anomalies_df.iterrows()
    ]

    # Total days scored = unique dates in the cloud data
    total_days = df["date"].nunique()

    return AnomalyResponse(
        total_days_scored=int(total_days),
        anomalies_detected=len(items),
        anomalies=items,
    )