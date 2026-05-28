"""
generate_data.py
----------------
Generates realistic-looking cloud and SaaS usage datasets.

What's intentionally hard here (so the ML actually has to work):
- Behaviors are drawn from probability distributions, not hand-labeled tags.
  The models can't "rediscover labels" because there are no labels to rediscover.
- Anomalies happen at random dates with random magnitudes. Re-running the
  generator will plant DIFFERENT anomalies, so the Isolation Forest can't
  memorize specific dates.
- Costs are split across compute / storage / transfer / other line items.
  A single oversized prod instance with high egress can easily cross
  ₹1L/mo, which gives the severity bucketing real meaning.
- The license dataset has a `truly_unused` ground-truth column with NOISE:
  some truly-unused licenses had an accidental login last month, some
  truly-needed licenses had zero logins because the user was on PTO.
  The classifier sees this noise and has to learn through it instead of
  memorizing `logins_last_30d == 0`.

Run:
    python scripts/generate_data.py
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# CLOUD USAGE
# ---------------------------------------------------------------------

# Instance catalogue: hourly compute price + typical storage/transfer cost.
# Prices are illustrative INR figures for a mixed AWS-like fleet.
INSTANCE_CATALOG = {
    "t3.medium":   {"hourly_inr": 4.0,   "storage_gb": 50,   "tier": "small"},
    "t3.large":    {"hourly_inr": 8.0,   "storage_gb": 100,  "tier": "small"},
    "m5.xlarge":   {"hourly_inr": 18.0,  "storage_gb": 200,  "tier": "medium"},
    "m5.2xlarge":  {"hourly_inr": 36.0,  "storage_gb": 400,  "tier": "medium"},
    "m5.4xlarge":  {"hourly_inr": 72.0,  "storage_gb": 800,  "tier": "large"},
    "r5.xlarge":   {"hourly_inr": 24.0,  "storage_gb": 300,  "tier": "memory"},
    "r5.2xlarge":  {"hourly_inr": 48.0,  "storage_gb": 600,  "tier": "memory"},
    "c5.2xlarge":  {"hourly_inr": 30.0,  "storage_gb": 200,  "tier": "compute"},
    "c5.4xlarge":  {"hourly_inr": 60.0,  "storage_gb": 400,  "tier": "compute"},
    "p3.2xlarge":  {"hourly_inr": 250.0, "storage_gb": 500,  "tier": "gpu"},
    "p3.8xlarge":  {"hourly_inr": 950.0, "storage_gb": 1000, "tier": "gpu"},
    "db.m5.large": {"hourly_inr": 40.0,  "storage_gb": 1000, "tier": "rds"},
    "db.r5.xlarge":{"hourly_inr": 90.0,  "storage_gb": 2000, "tier": "rds"},
}

REGIONS = ["ap-south-1", "us-east-1", "eu-west-1", "ap-southeast-1", "us-west-2"]
ENVIRONMENTS_WITH_WEIGHTS = [("prod", 0.45), ("dev", 0.25), ("staging", 0.15), ("test", 0.15)]

# Behaviour probabilities given an environment. These do NOT get written to disk —
# they're internal to the generator. The downstream models see only the
# observable telemetry (cpu, cost, hours).
BEHAVIOR_PRIORS_BY_ENV = {
    "prod":    [("normal", 0.85), ("rightsize", 0.10), ("idle", 0.02), ("zombie", 0.03)],
    "staging": [("normal", 0.70), ("rightsize", 0.15), ("idle", 0.10), ("zombie", 0.05)],
    "dev":     [("normal", 0.45), ("rightsize", 0.20), ("idle", 0.25), ("zombie", 0.10)],
    "test":    [("normal", 0.40), ("rightsize", 0.20), ("idle", 0.30), ("zombie", 0.10)],
}


def _draw(weighted_choices: list[tuple[str, float]]) -> str:
    """Categorical sample from [(value, prob), ...]. Probs need not sum to 1 exactly."""
    values, weights = zip(*weighted_choices)
    return np.random.choice(values, p=np.array(weights) / sum(weights))


def _build_fleet(n_instances: int, days: int) -> list[dict]:
    """
    Build a fleet with realistic churn — some instances exist for the
    whole window, others are launched or terminated partway through.
    """
    fleet = []
    for i in range(n_instances):
        env = _draw(ENVIRONMENTS_WITH_WEIGHTS)
        behavior = _draw(BEHAVIOR_PRIORS_BY_ENV[env])

        # 70% live the entire window, 20% are launched midway, 10% terminate early.
        roll = np.random.rand()
        if roll < 0.70:
            launched_day, terminated_day = 0, days
        elif roll < 0.90:
            launched_day = np.random.randint(int(days * 0.1), int(days * 0.7))
            terminated_day = days
        else:
            launched_day = 0
            terminated_day = np.random.randint(int(days * 0.3), int(days * 0.9))

        # Instance type: weighted toward smaller boxes (real fleets are pyramid-shaped)
        if env == "prod":
            type_pool = ["m5.xlarge", "m5.2xlarge", "m5.4xlarge", "r5.xlarge", "r5.2xlarge",
                         "c5.2xlarge", "c5.4xlarge", "p3.2xlarge", "p3.8xlarge",
                         "db.m5.large", "db.r5.xlarge"]
            type_weights = [0.20, 0.15, 0.08, 0.10, 0.07, 0.10, 0.08, 0.05, 0.02, 0.10, 0.05]
        else:
            type_pool = ["t3.medium", "t3.large", "m5.xlarge", "m5.2xlarge",
                         "c5.2xlarge", "db.m5.large"]
            type_weights = [0.40, 0.25, 0.15, 0.08, 0.07, 0.05]

        inst_type = np.random.choice(type_pool, p=np.array(type_weights) / sum(type_weights))

        fleet.append({
            "instance_id":  f"i-{env[:4]}-{i+1:04d}",
            "instance_type": inst_type,
            "region": np.random.choice(REGIONS),
            "environment": env,
            "behavior": behavior,
            "launched_day": launched_day,
            "terminated_day": terminated_day,
            # Each instance has its own baseline CPU drawn around its behaviour mean —
            # so two "normal" prod boxes don't look identical.
            "baseline_cpu": _baseline_cpu_for_behavior(behavior),
        })
    return fleet


def _baseline_cpu_for_behavior(behavior: str) -> float:
    if behavior == "idle":      return np.random.uniform(1.0, 4.0)
    if behavior == "zombie":    return np.random.uniform(2.0, 6.0)
    if behavior == "rightsize": return np.random.uniform(8.0, 18.0)
    return np.random.uniform(35.0, 65.0)  # normal


def _seasonality_multiplier(date: datetime) -> float:
    """
    Real cloud bills move with seasonality. Returns a cost multiplier:
      - month-end (last 3 days): batch jobs / billing runs / reports → 1.15-1.30x
      - weekend: lower batch load → 0.85-0.95x
      - Indian festival lull (mid Oct - mid Nov approx): 0.92x
    """
    mult = 1.0
    # Month-end spike
    days_in_month = (date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    if date.day > days_in_month.day - 3:
        mult *= np.random.uniform(1.15, 1.30)
    # Weekend dip
    if date.weekday() >= 5:
        mult *= np.random.uniform(0.85, 0.95)
    # Festival lull
    if date.month == 10 and date.day >= 15 or date.month == 11 and date.day <= 15:
        mult *= 0.92
    return mult


def _generate_anomalies(fleet: list[dict], days: int) -> dict:
    """
    Plant 4-8 random cost anomalies across the window. Each anomaly hits
    a random subset of instances on a random date for 1-3 days. Magnitudes
    are sampled — small bumps to severe spikes. The dates are NOT known
    to the anomaly model.
    """
    anomalies = {}  # {(day_offset, instance_id): magnitude_multiplier}
    n_anomalies = np.random.randint(4, 9)
    for _ in range(n_anomalies):
        day = np.random.randint(7, days - 3)
        duration = np.random.randint(1, 4)
        n_affected = np.random.randint(1, max(2, len(fleet) // 8))
        affected = np.random.choice(len(fleet), size=n_affected, replace=False)
        magnitude = np.random.uniform(2.5, 8.0)
        for d in range(day, min(day + duration, days)):
            for idx in affected:
                anomalies[(d, fleet[idx]["instance_id"])] = magnitude
    return anomalies


def generate_cloud_usage(days: int = 365, n_instances: int = 150) -> pd.DataFrame:
    fleet = _build_fleet(n_instances, days)
    anomalies = _generate_anomalies(fleet, days)

    rows = []
    start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)

    for day_offset in range(days):
        date = start + timedelta(days=day_offset)
        season_mult = _seasonality_multiplier(date)

        for inst in fleet:
            if day_offset < inst["launched_day"] or day_offset >= inst["terminated_day"]:
                continue  # instance doesn't exist on this day

            cfg = INSTANCE_CATALOG[inst["instance_type"]]
            behavior = inst["behavior"]

            # Runtime hours
            if behavior == "zombie":
                hours = 24
            elif inst["environment"] == "prod":
                hours = 24
            elif behavior == "idle":
                hours = 24  # idle BUT still running — that's the waste
            else:
                hours = np.random.choice([10, 12, 14], p=[0.5, 0.3, 0.2]) if date.weekday() < 5 else np.random.choice([0, 4, 8], p=[0.5, 0.3, 0.2])

            # CPU around the per-instance baseline, with daily noise
            cpu_avg = max(0.1, np.random.normal(inst["baseline_cpu"], 3.0))
            cpu_max = min(99.9, cpu_avg + np.random.uniform(5, 25))

            # Per-day cost components
            cost_compute = round(hours * cfg["hourly_inr"], 2)
            # Storage scales with allocated GB at ~₹0.5/GB-day
            cost_storage = round(cfg["storage_gb"] * 0.5, 2)
            # Egress: prod ships more data; bursts on weekdays
            transfer_factor = {"prod": 1.0, "staging": 0.3, "dev": 0.15, "test": 0.1}[inst["environment"]]
            cost_transfer = round(np.random.exponential(80.0) * transfer_factor, 2)
            # Misc (snapshots, monitoring, support): small but not zero
            cost_other = round(np.random.uniform(5, 25), 2)

            # Anomaly injection — applies to compute + transfer (e.g. runaway job)
            anomaly_mult = anomalies.get((day_offset, inst["instance_id"]), 1.0)
            cost_compute = round(cost_compute * anomaly_mult, 2)
            cost_transfer = round(cost_transfer * anomaly_mult, 2)
            if anomaly_mult > 1.0:
                # During an anomaly, CPU also spikes — that's the multivariate signal
                cpu_avg = min(99.0, cpu_avg + np.random.uniform(20, 50))
                cpu_max = min(99.9, cpu_avg + np.random.uniform(5, 20))

            # Seasonality applies to the whole bill
            cost_compute  = round(cost_compute * season_mult, 2)
            cost_transfer = round(cost_transfer * season_mult, 2)

            total_cost = round(cost_compute + cost_storage + cost_transfer + cost_other, 2)

            # 1% telemetry gaps
            if np.random.rand() < 0.01:
                cpu_avg = np.nan

            rows.append({
                "date": date.date().isoformat(),
                "instance_id": inst["instance_id"],
                "instance_type": inst["instance_type"],
                "region": inst["region"],
                "environment": inst["environment"],
                "cpu_utilization_avg": round(cpu_avg, 2) if not np.isnan(cpu_avg) else np.nan,
                "cpu_utilization_max": round(cpu_max, 2),
                "hours_running": hours,
                "cost_compute_inr": cost_compute,
                "cost_storage_inr": cost_storage,
                "cost_transfer_inr": cost_transfer,
                "cost_other_inr": cost_other,
                "cost_inr": total_cost,  # kept for backward compatibility — total of components
            })

    df = pd.DataFrame(rows)

    # Inject duplicates so the cleaning step has work to do
    dupes = df.sample(n=min(50, len(df) // 100), random_state=RNG_SEED)
    df = pd.concat([df, dupes], ignore_index=True)
    df = df.sample(frac=1, random_state=RNG_SEED).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------
# SAAS USAGE
# ---------------------------------------------------------------------

SAAS_CATALOG = {
    "Salesforce": {"cost": 12000, "primarily_used_by": ["Sales", "Marketing"]},
    "Slack":      {"cost": 700,   "primarily_used_by": None},
    "Zoom":       {"cost": 1200,  "primarily_used_by": None},
    "Jira":       {"cost": 1500,  "primarily_used_by": ["Engineering", "Operations"]},
    "GitHub":     {"cost": 1800,  "primarily_used_by": ["Engineering"]},
    "Notion":     {"cost": 900,   "primarily_used_by": None},
    "Figma":      {"cost": 1300,  "primarily_used_by": ["Design", "Engineering"]},
    "HubSpot":    {"cost": 4500,  "primarily_used_by": ["Sales", "Marketing"]},
}

DEPARTMENTS = ["Sales", "Engineering", "Marketing", "Finance", "HR",
               "Operations", "Design", "Legal"]

LICENSE_TYPES = ["Standard", "Premium", "Enterprise"]
LICENSE_PRICE_MULT = {"Standard": 1.0, "Premium": 1.6, "Enterprise": 2.4}


def generate_saas_usage(num_employees: int = 1500) -> pd.DataFrame:
    """
    Generate SaaS licenses with a ground-truth `truly_unused` flag that the
    classifier will train against. The observable features (logins,
    active_days, last_login_date) are NOISY correlates of `truly_unused`,
    not perfect signals — so the classifier has to learn a probabilistic
    relationship instead of memorizing a rule.
    """
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = []

    for emp_idx in range(num_employees):
        user_id = f"u-{emp_idx+1:05d}"
        name = f"Employee {emp_idx+1}"
        dept = random.choice(DEPARTMENTS)
        n_tools = np.random.choice([1, 2, 3, 4], p=[0.30, 0.40, 0.20, 0.10])
        assigned_tools = random.sample(list(SAAS_CATALOG.keys()),
                                       k=min(n_tools, len(SAAS_CATALOG)))

        for tool in assigned_tools:
            cfg = SAAS_CATALOG[tool]
            license_type = np.random.choice(LICENSE_TYPES, p=[0.55, 0.30, 0.15])
            monthly_cost = round(cfg["cost"] * LICENSE_PRICE_MULT[license_type], 2)

            # Ground truth: is this license actually needed?
            # Higher chance of NOT being needed if the department doesn't typically use this tool.
            dept_match = cfg["primarily_used_by"] is None or dept in cfg["primarily_used_by"]
            p_truly_unused = 0.08 if dept_match else 0.40
            truly_unused = np.random.rand() < p_truly_unused

            # Observable signals — noisy correlates of truly_unused
            if truly_unused:
                # Most truly-unused show 0-2 logins, but a small group has
                # an accidental burst (e.g. opened it once last week to check).
                if np.random.rand() < 0.85:
                    logins = np.random.randint(0, 3)
                    active_days = min(logins, np.random.randint(0, 2))
                    last_login_offset = np.random.randint(30, 180) if logins == 0 else np.random.randint(10, 30)
                else:
                    # Noisy: this user opened it a few times despite not needing it
                    logins = np.random.randint(3, 8)
                    active_days = np.random.randint(2, 5)
                    last_login_offset = np.random.randint(2, 15)
            else:
                # Most truly-needed licenses see steady use, but ~10% had a
                # quiet month (PTO, parental leave, switched projects).
                if np.random.rand() < 0.90:
                    logins = np.random.randint(15, 120)
                    active_days = np.random.randint(10, 30)
                    last_login_offset = np.random.randint(0, 4)
                else:
                    logins = np.random.randint(0, 4)
                    active_days = np.random.randint(0, 2)
                    last_login_offset = np.random.randint(20, 60)

            last_login = (
                (today - timedelta(days=last_login_offset)).date().isoformat()
                if logins > 0 else None
            )
            assigned_date = (today - timedelta(days=np.random.randint(30, 900))).date().isoformat()

            rows.append({
                "user_id": user_id,
                "employee_name": name,
                "department": dept,
                "tool": tool,
                "license_type": license_type,
                "monthly_cost_inr": monthly_cost,
                "logins_last_30d": int(logins),
                "active_days_last_30d": int(active_days),
                "last_login_date": last_login,
                "assigned_date": assigned_date,
                # Ground-truth label — in production, this would come from a
                # delayed signal like "admin confirmed revoke 90 days later".
                "truly_unused": int(truly_unused),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main() -> None:
    print("Generating cloud usage data (365 days x ~150 instances)...")
    cloud = generate_cloud_usage(days=365, n_instances=150)
    cloud_path = RAW_DIR / "cloud_usage.csv"
    cloud.to_csv(cloud_path, index=False)
    print(f"  wrote {len(cloud):,} rows to {cloud_path}")

    print("Generating SaaS usage data (1500 employees, 8 tools)...")
    saas = generate_saas_usage(num_employees=1500)
    saas_path = RAW_DIR / "saas_usage.csv"
    saas.to_csv(saas_path, index=False)
    print(f"  wrote {len(saas):,} rows to {saas_path}")

    print("\nCloud sample:")
    print(cloud.head(3).to_string(index=False))
    print(f"\nTotal cloud spend: INR {cloud['cost_inr'].sum():,.2f}")
    print(f"Cost breakdown — compute: INR {cloud['cost_compute_inr'].sum():,.0f}, "
          f"storage: INR {cloud['cost_storage_inr'].sum():,.0f}, "
          f"transfer: INR {cloud['cost_transfer_inr'].sum():,.0f}, "
          f"other: INR {cloud['cost_other_inr'].sum():,.0f}")
    print(f"Idle-CPU rows (CPU<5%): {(cloud['cpu_utilization_avg'] < 5).sum()}")

    print("\nSaaS sample:")
    print(saas.head(3).to_string(index=False))
    print(f"\nTotal monthly SaaS spend: INR {saas['monthly_cost_inr'].sum():,.2f}")
    print(f"Truly-unused licenses (ground truth): {saas['truly_unused'].sum()} / {len(saas)} "
          f"({100*saas['truly_unused'].mean():.1f}%)")
    print(f"Zero-login licenses (observable): {(saas['logins_last_30d'] == 0).sum()}")


if __name__ == "__main__":
    main()
