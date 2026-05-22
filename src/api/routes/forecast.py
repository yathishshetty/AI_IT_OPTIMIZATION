"""
routes/forecast.py
------------------
GET /cost-forecast?days_ahead=30

Returns predicted daily cost for the next N days.
"""
from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException

from src.api.dependencies import get_cloud_data
from src.api.schemas import ForecastResponse, ForecastPoint
from src.ml import forecast as forecast_model
from src.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/cost-forecast", tags=["forecast"])


@router.get("", response_model=ForecastResponse)
def get_forecast(
    days_ahead: int = Query(
        30,
        ge=1,
        le=180,
        description="Number of days to forecast (1-180)",
    ),
) -> ForecastResponse:
    """Predict daily cloud cost for the next `days_ahead` days."""
    try:
        df = get_cloud_data()
        predictions = forecast_model.predict_future_costs(df, days_ahead=days_ahead)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        log.exception("Forecast prediction failed")
        raise HTTPException(status_code=500, detail="Forecast generation failed")

    points = [
        ForecastPoint(
            date=row["date"].date(),
            predicted_cost_inr=float(row["predicted_cost_inr"]),
        )
        for _, row in predictions.iterrows()
    ]
    total = float(predictions["predicted_cost_inr"].sum())
    avg = total / len(points) if points else 0.0

    return ForecastResponse(
        days_ahead=days_ahead,
        total_predicted_cost_inr=round(total, 2),
        average_daily_cost_inr=round(avg, 2),
        forecast=points,
    )