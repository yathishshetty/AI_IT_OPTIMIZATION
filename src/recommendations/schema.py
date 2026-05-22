"""schema.py — Recommendation data model shared by the engine and the API."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

Category = Literal["cloud_idle", "cloud_rightsize", "saas_revoke", "cloud_anomaly"]
Severity = Literal["high", "medium", "low"]

# Monthly-savings thresholds (INR) used to bucket recommendations by severity.
HIGH_THRESHOLD = 50_000
MEDIUM_THRESHOLD = 10_000


def severity_from_savings(monthly_savings_inr: float) -> Severity:
    if monthly_savings_inr >= HIGH_THRESHOLD:
        return "high"
    if monthly_savings_inr >= MEDIUM_THRESHOLD:
        return "medium"
    return "low"


class Recommendation(BaseModel):
    id: str
    category: Category
    severity: Severity
    title: str
    reason: str
    action: str
    monthly_savings_inr: float
    annual_savings_inr: float
    confidence: float = Field(ge=0.0, le=1.0)
    entity: str
    metadata: dict = Field(default_factory=dict)
