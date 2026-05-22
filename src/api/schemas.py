"""
schemas.py
----------
Pydantic models = the API's contract.

Why Pydantic?
- Validates incoming requests automatically (wrong types → 422 error)
- Documents the API in /docs (Swagger UI auto-generated)
- Gives downstream code real types instead of ambiguous dicts

Convention: Request models end in `Request`, response models in `Response`.
List items get their own model (e.g. `AnomalyItem`) — never inline-define inside lists.
"""
from __future__ import annotations
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


# ----------------------------- Forecast -----------------------------
class ForecastPoint(BaseModel):
    """A single day's predicted cost."""
    date: date
    predicted_cost_inr: float


class ForecastResponse(BaseModel):
    """Response for /cost-forecast."""
    days_ahead: int
    total_predicted_cost_inr: float
    average_daily_cost_inr: float
    forecast: List[ForecastPoint]


# ----------------------------- Anomalies ----------------------------
class AnomalyItem(BaseModel):
    """A single flagged day."""
    date: date
    daily_cost_inr: float
    daily_avg_cpu: float
    daily_hours: int
    is_weekend: bool
    anomaly_score: float = Field(
        ...,
        description="Lower (more negative) = more anomalous",
    )


class AnomalyResponse(BaseModel):
    """Response for /anomalies."""
    total_days_scored: int
    anomalies_detected: int
    anomalies: List[AnomalyItem]


# -------------------------- Recommendations -------------------------
# Unified recommendation contract — one shape for cloud idle, rightsize,
# SaaS revoke, and cost anomalies. The dashboard renders against this.

class RecommendationItem(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    reason: str
    action: str
    monthly_savings_inr: float
    annual_savings_inr: float
    confidence: float
    entity: str
    metadata: dict = {}


class RecommendationsSummary(BaseModel):
    total_recommendations: int
    total_monthly_savings_inr: float
    total_annual_savings_inr: float
    by_severity: dict
    by_category: dict


class RecommendationsResponse(BaseModel):
    summary: RecommendationsSummary
    recommendations: List[RecommendationItem]


# ----------------------------- Health -------------------------------
class HealthResponse(BaseModel):
    status: str
    models_loaded: dict
    data_freshness: Optional[str] = None