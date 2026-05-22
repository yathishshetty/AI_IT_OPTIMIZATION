"""
api_client.py
-------------
Single place that knows how to talk to the FastAPI service.

Why isolate this?
- Every page in /pages calls these functions, not requests.get directly.
- If we move the API to a different host or add auth headers,
  we change ONE file.
- Easy to mock for tests.
- @st.cache_data avoids hammering the API on every UI redraw.
"""
from __future__ import annotations
import os
import requests
import streamlit as st

# Configurable via env var, defaults to localhost.
# In production you'd point this at the deployed service URL.
API_BASE_URL = os.getenv("FINOPS_API_URL", "http://localhost:8000")

# Tunable; 5s is generous for a local API, tight for prod.
REQUEST_TIMEOUT_S = 10


def _get(path: str, params: dict | None = None) -> dict:
    """Generic GET helper with friendly error handling."""
    url = f"{API_BASE_URL}{path}"
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_S)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        msg = (
            f"Cannot reach the FinOps API at {API_BASE_URL}. "
            f"Is uvicorn running? Try: `uvicorn src.api.main:app --port 8000`"
        )
    except requests.exceptions.HTTPError as e:
        msg = f"API returned {e.response.status_code}: {e.response.text}"
    except requests.exceptions.Timeout:
        msg = f"API call to {url} timed out after {REQUEST_TIMEOUT_S}s"

    # st.error + st.stop only halt execution inside a live Streamlit runtime;
    # raise so callers never receive None and crash with a cryptic KeyError.
    st.error(f"❌ {msg}")
    st.stop()
    raise RuntimeError(msg)


# ----- Cached wrappers -----
# ttl=60 = cached for 60 seconds. Good enough for a dashboard that
# refreshes occasionally; you don't want a CFO clicking the chart and
# triggering 50 API calls.
@st.cache_data(ttl=60)
def fetch_health() -> dict:
    return _get("/health")


@st.cache_data(ttl=60)
def fetch_forecast(days_ahead: int = 30) -> dict:
    return _get("/cost-forecast", params={"days_ahead": days_ahead})


@st.cache_data(ttl=60)
def fetch_anomalies() -> dict:
    return _get("/anomalies")


@st.cache_data(ttl=60)
def fetch_recommendations(
    category: str | None = None,
    severity: str | None = None,
    top_n: int = 50,
) -> dict:
    params: dict = {"top_n": top_n}
    if category:
        params["category"] = category
    if severity:
        params["severity"] = severity
    return _get("/recommendations", params=params)