"""engine.py — Recommendation engine: rules + ML detectors."""
from __future__ import annotations
from typing import List
import pandas as pd

from src.recommendations.schema import Recommendation, severity_from_savings
from src.ml import license_classifier, anomaly as anomaly_model
from src.utils.logger import get_logger

log = get_logger(__name__)


def detect_idle_instances(cloud_df: pd.DataFrame) -> List[Recommendation]:
    df = cloud_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    last_30 = df[df["date"] >= df["date"].max() - pd.Timedelta(days=30)]

    summary = (
        last_30.groupby(["instance_id", "instance_type", "region", "environment"])
        .agg(
            avg_cpu=("cpu_utilization_avg", "mean"),
            total_cost=("cost_inr", "sum"),
            idle_days=("is_idle_candidate", "sum"),
            total_days=("date", "count"),
        )
        .reset_index()
    )
    summary["idle_ratio"] = summary["idle_days"] / summary["total_days"]
    qualifying = summary[(summary["idle_ratio"] >= 0.8) & (summary["avg_cpu"] < 5)]

    recs = []
    for _, row in qualifying.iterrows():
        monthly = round(float(row["total_cost"]), 2)
        recs.append(Recommendation(
            id=f"rec_idle_{row['instance_id']}",
            category="cloud_idle",
            severity=severity_from_savings(monthly),
            title=f"Stop idle {row['environment']} instance {row['instance_id']}",
            reason=(
                f"Average CPU was {row['avg_cpu']:.1f}% over the last 30 days "
                f"(idle on {int(row['idle_days'])}/{int(row['total_days'])} days). "
                f"This instance is paid for but not doing useful work."
            ),
            action=f"Stop or terminate {row['instance_id']} in the {row['region']} region.",
            monthly_savings_inr=monthly,
            annual_savings_inr=round(monthly * 12, 2),
            confidence=1.0,
            entity=row["instance_id"],
            metadata={
                "instance_type": row["instance_type"],
                "region": row["region"],
                "environment": row["environment"],
                "avg_cpu_last_30d": round(float(row["avg_cpu"]), 2),
            },
        ))
    log.info(f"Idle detector: {len(recs)} recommendations")
    return recs


def detect_rightsize_candidates(cloud_df: pd.DataFrame) -> List[Recommendation]:
    df = cloud_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    last_30 = df[df["date"] >= df["date"].max() - pd.Timedelta(days=30)]

    summary = (
        last_30.groupby(["instance_id", "instance_type", "region", "environment"])
        .agg(avg_cpu=("cpu_utilization_avg", "mean"),
             total_cost=("cost_inr", "sum"))
        .reset_index()
    )
    qualifying = summary[
        (summary["avg_cpu"] >= 5) &
        (summary["avg_cpu"] < 20) &
        (~summary["instance_type"].isin(["t3.medium"]))
    ]

    recs = []
    for _, row in qualifying.iterrows():
        monthly_savings = round(float(row["total_cost"]) * 0.5, 2)
        recs.append(Recommendation(
            id=f"rec_rightsize_{row['instance_id']}",
            category="cloud_rightsize",
            severity=severity_from_savings(monthly_savings),
            title=f"Rightsize {row['instance_type']} instance {row['instance_id']}",
            reason=(
                f"Average CPU was only {row['avg_cpu']:.1f}% — this instance "
                f"is significantly oversized for its workload."
            ),
            action=(
                f"Downsize {row['instance_id']} from {row['instance_type']} "
                f"to one tier smaller. Validate with load test first."
            ),
            monthly_savings_inr=monthly_savings,
            annual_savings_inr=round(monthly_savings * 12, 2),
            confidence=0.8,
            entity=row["instance_id"],
            metadata={
                "current_type": row["instance_type"],
                "region": row["region"],
                "environment": row["environment"],
                "avg_cpu_last_30d": round(float(row["avg_cpu"]), 2),
            },
        ))
    log.info(f"Rightsize detector: {len(recs)} recommendations")
    return recs


def detect_unused_licenses(saas_df: pd.DataFrame, threshold: float = 0.7) -> List[Recommendation]:
    candidates = license_classifier.predict_revoke_candidates(saas_df, threshold=threshold)

    recs = []
    for _, row in candidates.iterrows():
        monthly = float(row["monthly_cost_inr"])
        if row["logins_last_30d"] == 0:
            evidence = "logged in 0 times in the last 30 days"
        else:
            evidence = (
                f"logged in only {int(row['logins_last_30d'])} times in 30 days, "
                f"last login {int(row['days_since_last_login'])} days ago"
            )

        recs.append(Recommendation(
            id=f"rec_revoke_{row['user_id']}_{row['tool']}",
            category="saas_revoke",
            severity=severity_from_savings(monthly),
            title=f"Revoke {row['tool']} license for {row['employee_name']}",
            reason=(
                f"{row['employee_name']} ({row['department']}) has a "
                f"{row['license_type']} {row['tool']} license but {evidence}. "
                f"ML model confidence: {row['revoke_probability']:.0%}."
            ),
            action=(
                f"Revoke {row['tool']} license for user {row['user_id']}. "
                f"Confirm with their manager first if the license is enterprise-tier."
            ),
            monthly_savings_inr=round(monthly, 2),
            annual_savings_inr=round(float(row["annual_cost_inr"]), 2),
            confidence=float(row["revoke_probability"]),
            entity=row["user_id"],
            metadata={
                "tool": row["tool"],
                "department": row["department"],
                "license_type": row["license_type"],
                "logins_last_30d": int(row["logins_last_30d"]),
                "days_since_last_login": int(row["days_since_last_login"]),
            },
        ))
    log.info(f"Revoke detector: {len(recs)} recommendations")
    return recs


def detect_recent_anomalies(cloud_df: pd.DataFrame, lookback_days: int = 14) -> List[Recommendation]:
    anomalies_df = anomaly_model.detect_anomalies(cloud_df)
    if anomalies_df.empty:
        return []
    anomalies_df["date"] = pd.to_datetime(anomalies_df["date"])
    cutoff = pd.to_datetime(cloud_df["date"]).max() - pd.Timedelta(days=lookback_days)
    recent = anomalies_df[anomalies_df["date"] >= cutoff]

    recs = []
    for _, row in recent.iterrows():
        cost = float(row["daily_cost_inr"])
        recs.append(Recommendation(
            id=f"rec_anomaly_{row['date'].date().isoformat()}",
            category="cloud_anomaly",
            severity=severity_from_savings(cost),
            title=f"Cost anomaly detected on {row['date'].date()}",
            reason=(
                f"Daily cost was ₹{cost:,.2f} with average CPU "
                f"{row['daily_avg_cpu']:.1f}% — flagged as unusual by the anomaly model "
                f"(score: {row['anomaly_score']:.3f})."
            ),
            action=(
                "Investigate which workloads ran on this date. Common causes: a "
                "runaway batch job, mis-scaled prod traffic, or an over-provisioned "
                "dev environment that should have been torn down."
            ),
            monthly_savings_inr=0.0,
            annual_savings_inr=0.0,
            confidence=min(1.0, abs(float(row["anomaly_score"])) * 5),
            entity=row["date"].date().isoformat(),
            metadata={
                "daily_cost_inr": cost,
                "daily_avg_cpu": float(row["daily_avg_cpu"]),
                "anomaly_score": float(row["anomaly_score"]),
            },
        ))
    log.info(f"Recent anomaly detector: {len(recs)} recommendations")
    return recs


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_all_recommendations(cloud_df: pd.DataFrame, saas_df: pd.DataFrame) -> List[Recommendation]:
    all_recs = []
    all_recs += detect_idle_instances(cloud_df)
    all_recs += detect_rightsize_candidates(cloud_df)
    all_recs += detect_unused_licenses(saas_df)
    all_recs += detect_recent_anomalies(cloud_df)

    all_recs.sort(
        key=lambda r: (
            SEVERITY_ORDER[r.severity],
            -r.annual_savings_inr,
            -r.confidence,
        )
    )
    log.info(f"Built {len(all_recs)} total recommendations")
    return all_recs


def summarize(recs: List[Recommendation]) -> dict:
    return {
        "total_recommendations": len(recs),
        "total_monthly_savings_inr": round(sum(r.monthly_savings_inr for r in recs), 2),
        "total_annual_savings_inr": round(sum(r.annual_savings_inr for r in recs), 2),
        "by_severity": {
            "high":   sum(1 for r in recs if r.severity == "high"),
            "medium": sum(1 for r in recs if r.severity == "medium"),
            "low":    sum(1 for r in recs if r.severity == "low"),
        },
        "by_category": {
            cat: sum(1 for r in recs if r.category == cat)
            for cat in ["cloud_idle", "cloud_rightsize", "saas_revoke", "cloud_anomaly"]
        },
    }