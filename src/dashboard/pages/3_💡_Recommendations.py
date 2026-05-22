"""
Recommendations page
--------------------
The "do this list" — filterable, sortable, exportable.
This is the page a FinOps analyst will live in.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import streamlit as st

from src.dashboard.api_client import fetch_recommendations

st.set_page_config(page_title="Recommendations", page_icon="💡", layout="wide")
st.title("💡 Recommendations")
st.caption("Prioritized actions ranked by severity, then annual savings.")

# -------- Filters (sidebar) --------
st.sidebar.header("Filter")
category_options = {
    "All": None,
    "Idle cloud instances": "cloud_idle",
    "Rightsize candidates": "cloud_rightsize",
    "SaaS license revokes": "saas_revoke",
    "Cloud anomalies": "cloud_anomaly",
}
severity_options = {
    "All": None,
    "High only": "high",
    "Medium only": "medium",
    "Low only": "low",
}
selected_category_label = st.sidebar.selectbox("Category", list(category_options.keys()))
selected_severity_label = st.sidebar.selectbox("Severity", list(severity_options.keys()))
top_n = st.sidebar.slider("Max items", 5, 200, 50, step=5)

data = fetch_recommendations(
    category=category_options[selected_category_label],
    severity=severity_options[selected_severity_label],
    top_n=top_n,
)

summary = data["summary"]
recs = data["recommendations"]

# -------- KPIs for the FILTERED set --------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Items shown", summary["total_recommendations"])
c2.metric("Monthly savings", f"₹{summary['total_monthly_savings_inr']:,.0f}")
c3.metric("Annual savings", f"₹{summary['total_annual_savings_inr']:,.0f}")
c4.metric("High-severity", summary["by_severity"]["high"])

st.divider()

if not recs:
    st.info("No recommendations match the current filters.")
    st.stop()

# -------- Detail view --------
for rec in recs:
    sev_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}[rec["severity"]]
    cat_label = {
        "cloud_idle": "Idle instance",
        "cloud_rightsize": "Rightsize",
        "saas_revoke": "Revoke license",
        "cloud_anomaly": "Cost anomaly",
    }.get(rec["category"], rec["category"])

    with st.expander(
        f"{sev_color} [{cat_label}] **{rec['title']}**  "
        f"—  Save ₹{rec['annual_savings_inr']:,.0f}/yr",
    ):
        info_col, action_col = st.columns([2, 1])
        with info_col:
            st.markdown(f"**Why:** {rec['reason']}")
            st.markdown(f"**Recommended action:** {rec['action']}")
            if rec.get("metadata"):
                st.json(rec["metadata"], expanded=False)
        with action_col:
            st.metric("Monthly savings", f"₹{rec['monthly_savings_inr']:,.0f}")
            st.metric("Confidence", f"{rec['confidence']:.0%}")
            st.caption(f"ID: `{rec['id']}`")

# -------- CSV export (executives love this) --------
st.divider()
df_export = pd.DataFrame([
    {
        "ID": r["id"],
        "Category": r["category"],
        "Severity": r["severity"],
        "Title": r["title"],
        "Reason": r["reason"],
        "Action": r["action"],
        "Monthly Savings (INR)": r["monthly_savings_inr"],
        "Annual Savings (INR)": r["annual_savings_inr"],
        "Confidence": r["confidence"],
    }
    for r in recs
])
csv = df_export.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download as CSV",
    data=csv,
    file_name="finops_recommendations.csv",
    mime="text/csv",
)