"""
generate_data.py
----------------
Generates realistic-looking cloud and SaaS usage datasets with
planted inefficiencies, so the rest of the platform has something
meaningful to detect.

Run:
    python scripts/generate_data.py
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Reproducibility
RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

# Paths relative to this file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# CLOUD USAGE
# ---------------------------------------------------------------------
def generate_cloud_usage(days: int = 90) -> pd.DataFrame:
    instance_types = {
        "t3.medium":  {"hourly_inr": 4.0,  "size": "small"},
        "t3.large":   {"hourly_inr": 8.0,  "size": "medium"},
        "m5.xlarge":  {"hourly_inr": 18.0, "size": "large"},
        "m5.2xlarge": {"hourly_inr": 36.0, "size": "xlarge"},
        "r5.xlarge":  {"hourly_inr": 24.0, "size": "memory"},
    }

    instances = [
        ("i-prod-001", "m5.2xlarge", "ap-south-1", "prod",   "normal"),
        ("i-prod-002", "m5.xlarge",  "ap-south-1", "prod",   "normal"),
        ("i-prod-003", "m5.xlarge",  "us-east-1",  "prod",   "normal"),
        ("i-prod-004", "r5.xlarge",  "eu-west-1",  "prod",   "normal"),
        ("i-prod-005", "t3.large",   "ap-south-1", "prod",   "normal"),
        ("i-prod-006", "m5.xlarge",  "us-east-1",  "prod",   "spike"),
        ("i-stag-001", "t3.large",   "ap-south-1", "staging","normal"),
        ("i-stag-002", "t3.medium",  "us-east-1",  "staging","normal"),
        ("i-dev-001",  "t3.medium",  "ap-south-1", "dev",    "idle"),
        ("i-dev-002",  "t3.medium",  "ap-south-1", "dev",    "idle"),
        ("i-dev-003",  "t3.large",   "us-east-1",  "dev",    "zombie"),
        ("i-dev-004",  "t3.medium",  "eu-west-1",  "dev",    "normal"),
        ("i-test-001", "t3.medium",  "ap-south-1", "test",   "idle"),
        ("i-test-002", "t3.medium",  "us-east-1",  "test",   "normal"),
        ("i-ml-001",   "m5.2xlarge", "ap-south-1", "prod",   "bursty"),
    ]

    rows = []
    start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)

    for day_offset in range(days):
        date = start + timedelta(days=day_offset)
        for inst_id, inst_type, region, env, behavior in instances:
            cfg = instance_types[inst_type]

            if behavior == "zombie":
                hours = 24
            elif env == "prod":
                hours = 24
            elif behavior == "idle":
                hours = 24
            else:
                hours = 10 if date.weekday() < 5 else 4

            if behavior == "idle":
                cpu_avg = np.random.uniform(0.5, 4.5)
                cpu_max = cpu_avg + np.random.uniform(0, 5)
            elif behavior == "zombie":
                cpu_avg = np.random.uniform(1.0, 6.0)
                cpu_max = cpu_avg + np.random.uniform(0, 8)
            elif behavior == "bursty":
                cpu_avg = np.random.uniform(20, 45)
                cpu_max = np.random.uniform(80, 99)
            elif behavior == "spike" and 58 <= day_offset <= 62:
                cpu_avg = np.random.uniform(60, 90)
                cpu_max = np.random.uniform(85, 99)
                hours = 24
            else:
                cpu_avg = np.random.uniform(30, 75)
                cpu_max = cpu_avg + np.random.uniform(5, 20)

            cost_multiplier = 4 if (behavior == "spike" and 58 <= day_offset <= 62) else 1
            cost = round(hours * cfg["hourly_inr"] * cost_multiplier, 2)

            # 1% null rate to simulate telemetry gaps
            if np.random.rand() < 0.01:
                cpu_avg = np.nan

            rows.append({
                "date": date.date().isoformat(),
                "instance_id": inst_id,
                "instance_type": inst_type,
                "region": region,
                "environment": env,
                "cpu_utilization_avg": round(cpu_avg, 2) if not np.isnan(cpu_avg) else np.nan,
                "cpu_utilization_max": round(cpu_max, 2),
                "hours_running": hours,
                "cost_inr": cost,
            })

    df = pd.DataFrame(rows)

    # Inject duplicates so the cleaning step has work to do
    dupes = df.sample(n=20, random_state=RNG_SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    df = df.sample(frac=1, random_state=RNG_SEED).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------
# SAAS USAGE
# ---------------------------------------------------------------------
def generate_saas_usage(num_employees: int = 200) -> pd.DataFrame:
    departments = ["Sales", "Engineering", "Marketing", "Finance", "HR", "Operations"]
    tools = {
        "Salesforce": {"cost": 7500, "primarily_used_by": ["Sales", "Marketing"]},
        "Slack":      {"cost": 700,  "primarily_used_by": None},
        "Zoom":       {"cost": 1200, "primarily_used_by": None},
        "Jira":       {"cost": 800,  "primarily_used_by": ["Engineering", "Operations"]},
    }
    license_types = ["Standard", "Premium", "Enterprise"]

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = []

    for emp_idx in range(num_employees):
        user_id = f"u-{emp_idx+1:04d}"
        name = f"Employee {emp_idx+1}"
        dept = random.choice(departments)
        assigned_tools = random.sample(list(tools.keys()), k=random.randint(1, 3))

        for tool in assigned_tools:
            cfg = tools[tool]
            mismatch = cfg["primarily_used_by"] and dept not in cfg["primarily_used_by"]

            r = np.random.rand()
            if mismatch and r < 0.6:
                category = "unused"
            elif r < 0.25:
                category = "unused"
            elif r < 0.40:
                category = "low"
            else:
                category = "active"

            if category == "unused":
                logins = 0
                active_days = 0
                last_login = None
            elif category == "low":
                logins = np.random.randint(1, 4)
                active_days = np.random.randint(1, 3)
                last_login = (today - timedelta(days=np.random.randint(15, 60))).date().isoformat()
            else:
                logins = np.random.randint(20, 120)
                active_days = np.random.randint(15, 30)
                last_login = (today - timedelta(days=np.random.randint(0, 3))).date().isoformat()

            assigned_date = (today - timedelta(days=np.random.randint(60, 720))).date().isoformat()

            rows.append({
                "user_id": user_id,
                "employee_name": name,
                "department": dept,
                "tool": tool,
                "license_type": random.choice(license_types),
                "monthly_cost_inr": cfg["cost"],
                "logins_last_30d": logins,
                "active_days_last_30d": active_days,
                "last_login_date": last_login,
                "assigned_date": assigned_date,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main() -> None:
    print("Generating cloud usage data...")
    cloud = generate_cloud_usage(days=90)
    cloud_path = RAW_DIR / "cloud_usage.csv"
    cloud.to_csv(cloud_path, index=False)
    print(f"  wrote {len(cloud):,} rows to {cloud_path}")

    print("Generating SaaS usage data...")
    saas = generate_saas_usage(num_employees=200)
    saas_path = RAW_DIR / "saas_usage.csv"
    saas.to_csv(saas_path, index=False)
    print(f"  wrote {len(saas):,} rows to {saas_path}")

    print("\nCloud sample:")
    print(cloud.head(3).to_string(index=False))
    print(f"\nTotal cloud spend: INR {cloud['cost_inr'].sum():,.2f}")
    print(f"Idle instance candidates (CPU<5%): "
          f"{(cloud['cpu_utilization_avg'] < 5).sum()} rows")

    print("\nSaaS sample:")
    print(saas.head(3).to_string(index=False))
    print(f"\nTotal monthly SaaS spend: INR {saas['monthly_cost_inr'].sum():,.2f}")
    print(f"Unused licenses (0 logins): {(saas['logins_last_30d'] == 0).sum()}")


if __name__ == "__main__":
    main()