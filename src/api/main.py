"""
main.py
-------
FastAPI app entry point.

Run locally:
    uvicorn src.api.main:app --reload --port 8000

Then visit:
    http://localhost:8000/docs    ← interactive API explorer (Swagger UI)
    http://localhost:8000/redoc   ← alternate documentation
    http://localhost:8000/health  ← liveness probe

Why uvicorn?
- ASGI server (async-capable). FastAPI is async-native.
- The standard for production FastAPI deployments.
- In production you'd run: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import forecast, anomalies, recommendations
from src.api.schemas import HealthResponse
from src.utils.logger import get_logger

log = get_logger("api")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("FinOps API starting up")
    yield
    log.info("FinOps API shutting down")


app = FastAPI(
    title="AI FinOps Platform API",
    description="Cost forecasting, anomaly detection, and savings recommendations "
                "for cloud + SaaS spend.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — let the Streamlit dashboard (different port) call us in dev.
# In production, replace ["*"] with the dashboard's exact origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register routers — each route file plugs in here.
app.include_router(forecast.router)
app.include_router(anomalies.router)
app.include_router(recommendations.router)


@app.get("/", tags=["meta"])
def root():
    """Friendly landing page for anyone who hits the bare URL."""
    return {
        "service": "AI FinOps Platform",
        "docs_url": "/docs",
        "endpoints": ["/cost-forecast", "/anomalies", "/recommendations", "/health"],
    }


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    """
    Liveness + readiness probe.

    What load balancers / k8s look at to decide if this instance is healthy.
    Should be FAST and report on dependencies.
    """
    models_dir = PROJECT_ROOT / "models"
    models = {
        "forecast":   (models_dir / "forecast_model.joblib").exists(),
        "anomaly":    (models_dir / "anomaly_model.joblib").exists(),
        "classifier": (models_dir / "license_classifier.joblib").exists(),
    }

    processed_dir = PROJECT_ROOT / "data" / "processed"
    cloud_csv = processed_dir / "cloud_usage_processed.csv"
    freshness = None
    if cloud_csv.exists():
        mtime = datetime.fromtimestamp(cloud_csv.stat().st_mtime)
        freshness = mtime.isoformat(timespec="seconds")

    overall = "ok" if all(models.values()) and cloud_csv.exists() else "degraded"
    return HealthResponse(status=overall, models_loaded=models, data_freshness=freshness)


