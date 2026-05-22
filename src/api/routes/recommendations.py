"""
routes/recommendations.py
-------------------------
GET /recommendations?top_n=50&category=cloud_idle&severity=high

Unified savings recommendations across cloud + SaaS, produced by the
recommendation engine (rules + ML). Supports optional category/severity
filters so the dashboard can render the same endpoint with different views.
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from src.api.dependencies import get_cloud_data, get_saas_data
from src.api.schemas import (
    RecommendationsResponse,
    RecommendationsSummary,
    RecommendationItem,
)
from src.recommendations import engine
from src.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationsResponse)
def get_recommendations(
    top_n: int = Query(50, ge=1, le=500,
                       description="Maximum number of recommendations to return"),
    category: Optional[str] = Query(
        None,
        description="Filter to one category: cloud_idle, cloud_rightsize, saas_revoke, cloud_anomaly",
    ),
    severity: Optional[str] = Query(
        None,
        description="Filter to one severity: high, medium, low",
    ),
) -> RecommendationsResponse:
    try:
        cloud_df = get_cloud_data()
        saas_df = get_saas_data()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        all_recs = engine.build_all_recommendations(cloud_df, saas_df)
    except Exception:
        log.exception("Recommendation generation failed")
        raise HTTPException(status_code=500, detail="Could not generate recommendations")

    # Summary is computed over the UNFILTERED set so KPI tiles stay stable
    # as the user toggles filters. The filtered list is what gets shown.
    summary_dict = engine.summarize(all_recs)

    filtered = all_recs
    if category:
        filtered = [r for r in filtered if r.category == category]
    if severity:
        filtered = [r for r in filtered if r.severity == severity]
    filtered = filtered[:top_n]

    return RecommendationsResponse(
        summary=RecommendationsSummary(**summary_dict),
        recommendations=[RecommendationItem(**r.model_dump()) for r in filtered],
    )
