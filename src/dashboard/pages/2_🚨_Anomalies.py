"""
Anomalies page
--------------
Lists days flagged by the Isolation Forest model. Each gets a
quick description and the context that triggered the flag.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import streamlit as st

from src.dashboard.api_client import fetch_anomalies

st.set_page_config(page_title="Anomalies", page_icon="🚨", layout="wide")
st.title("🚨 Cost & Usage Anomalies")
st.caption("Days flagged as unusual by the Isolation Forest model. "
           "Investigate these to catch runaway workloads early.")

data = fetch_anomalies()

# -------- KPIs --------
c1, c2, c3 = st.columns(3)
c1.metric("Days scored", data["total_days_scored"])
c2.metric("Anomalies detected", data["anomalies_detected"])
rate = (data["anomalies_detected"] / data["total_days_scored"] * 100
        if data["total_days_scored"] else 0)
c3.metric("Anomaly rate", f"{rate:.1f}%")

if not data["anomalies"]:
    st.success("✅ No anomalies detected in the current dataset.")
    st.stop()

# -------- Anomaly chart --------
df = pd.DataFrame(data["anomalies"])
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

st.subheader("Anomalous Days — Cost View")
# Use a bar chart so each spike stands out visually
st.bar_chart(df.set_index("date")["daily_cost_inr"], height=300)

# -------- Details list --------
st.subheader("Anomaly Details")
for _, row in df.iterrows():
    weekend_tag = "🌅 Weekend" if row["is_weekend"] else "💼 Weekday"
    with st.expander(
        f"📅 {row['date'].strftime('%Y-%m-%d')}  ({weekend_tag})  "
        f"—  ₹{row['daily_cost_inr']:,.2f}",
    ):
        a, b, c = st.columns(3)
        a.metric("Daily cost", f"₹{row['daily_cost_inr']:,.2f}")
        b.metric("Avg CPU", f"{row['daily_avg_cpu']:.1f}%")
        c.metric("Total hours", f"{int(row['daily_hours'])}h")
        st.caption(
            f"Anomaly score: **{row['anomaly_score']:.4f}** "
            f"(more negative = more anomalous). "
            f"Investigate runaway workloads, mis-scaled prod traffic, "
            f"or test environments that weren't torn down."
        )