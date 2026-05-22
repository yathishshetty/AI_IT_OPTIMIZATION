"""
app.py
------
The FinOps dashboard entry point.

Run:
    streamlit run src/dashboard/app.py

This is the LANDING page. Streamlit auto-discovers pages/*.py
and adds them to the sidebar.

Design intent:
- Page 1 (this file)   = executive summary, headline KPIs
- Page 2 = cost trends over time + forecast chart
- Page 3 = anomalies, recent first
- Page 4 = full recommendations list with filters
"""
from __future__ import annotations
import sys
from pathlib import Path

# Streamlit puts the script's directory on sys.path, not the project root,
# so `from src...` imports fail without this. Adds project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd

from src.dashboard.api_client import (
    fetch_health,
    fetch_recommendations,
    fetch_forecast,
)

# -------- Page config (must be the FIRST Streamlit call) --------
st.set_page_config(
    page_title="AI FinOps Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------- Header --------
st.title("💰 AI FinOps Platform")
st.caption("Cloud + SaaS cost optimization powered by ML")

# -------- Health check (top banner) --------
health = fetch_health()
if health["status"] == "ok":
    st.success(f"✅ System healthy — data refreshed at {health['data_freshness']}")
else:
    st.warning(f"⚠️ System status: {health['status']} — some components may be missing")

st.divider()

# -------- Headline KPIs --------
# We pull recommendations + forecast to populate the top tiles.
recs = fetch_recommendations(top_n=500)
summary = recs["summary"]
forecast = fetch_forecast(days_ahead=30)

# st.columns lets us put metrics side by side
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Recommendations",
    f"{summary['total_recommendations']}",
    help="Open optimization opportunities across cloud and SaaS",
)
col2.metric(
    "Potential Monthly Savings",
    f"₹{summary['total_monthly_savings_inr']:,.0f}",
    help="If every recommendation is implemented",
)
col3.metric(
    "Potential Annual Savings",
    f"₹{summary['total_annual_savings_inr']:,.0f}",
    delta=f"{summary['by_severity']['high']} high-severity items",
    help="Annualized impact",
)
col4.metric(
    "Forecasted Next 30 Days",
    f"₹{forecast['total_predicted_cost_inr']:,.0f}",
    help=f"Avg ₹{forecast['average_daily_cost_inr']:,.0f}/day",
)

st.divider()

# -------- Breakdown charts --------
left, right = st.columns(2)

with left:
    st.subheader("📂 Recommendations by Category")
    cat_df = pd.DataFrame(
        list(summary["by_category"].items()),
        columns=["Category", "Count"],
    )
    cat_df = cat_df[cat_df["Count"] > 0]      # hide empty categories
    if not cat_df.empty:
        st.bar_chart(cat_df.set_index("Category"))
    else:
        st.info("No recommendations yet.")

with right:
    st.subheader("🚦 Recommendations by Severity")
    sev_df = pd.DataFrame(
        list(summary["by_severity"].items()),
        columns=["Severity", "Count"],
    )
    # Custom order: high → low
    sev_df["Severity"] = pd.Categorical(
        sev_df["Severity"], categories=["high", "medium", "low"], ordered=True,
    )
    sev_df = sev_df.sort_values("Severity")
    st.bar_chart(sev_df.set_index("Severity"))

st.divider()

# -------- Top 5 high-impact items (the "do this Monday morning" list) --------
st.subheader("🎯 Top 5 High-Impact Recommendations")
st.caption("Highest annual savings, ranked.")

top5 = recs["recommendations"][:5]
if not top5:
    st.info("No recommendations to display.")
else:
    for rec in top5:
        sev_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["severity"]]
        with st.expander(
            f"{sev_color} **{rec['title']}**  —  "
            f"Save ₹{rec['annual_savings_inr']:,.0f}/year",
            expanded=False,
        ):
            cA, cB = st.columns([3, 1])
            with cA:
                st.markdown(f"**Why:** {rec['reason']}")
                st.markdown(f"**Action:** {rec['action']}")
            with cB:
                st.metric("Monthly", f"₹{rec['monthly_savings_inr']:,.0f}")
                st.metric("Confidence", f"{rec['confidence']:.0%}")

st.divider()
st.caption(
    "👈 Use the sidebar to explore cost trends, anomalies, and the full "
    "recommendations list. Data refreshes every 60 seconds."
)