"""Generate a synthetic B2B healthcare lead list.

All records are randomly generated. No real organizations, people, or
contact details are used. The structure mirrors a typical CRM export:
messy, incomplete, and spread across several owners and sources.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
N_LEADS = 2500

ORG_TYPES = ["Hospital", "Clinic", "Medical school", "Pharmaceutical company",
             "Translation agency", "Health insurer", "Nursing school"]
SPECIALTIES = ["General", "Cardiology", "Oncology", "Pediatrics", "Nursing",
               "Pharmacy", "Radiology", "Dentistry"]
REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "Canada", "UK", "EU"]
SOURCES = ["Conference", "Website form", "LinkedIn", "Referral", "Purchased list", "Webinar"]
OWNERS = ["Owner A", "Owner B", "Owner C", "Owner D", "Owner E"]


def generate(n=N_LEADS, seed=SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    source = rng.choice(SOURCES, n, p=[0.15, 0.20, 0.20, 0.10, 0.25, 0.10])
    warm = np.isin(source, ["Referral", "Webinar", "Website form"])
    df = pd.DataFrame({
        "lead_id": [f"L{100000 + i}" for i in range(n)],
        "org_type": rng.choice(ORG_TYPES, n, p=[0.22, 0.25, 0.10, 0.10, 0.13, 0.08, 0.12]),
        "specialty": rng.choice(SPECIALTIES, n),
        "region": rng.choice(REGIONS, n, p=[0.18, 0.15, 0.14, 0.10, 0.15, 0.09, 0.10, 0.09]),
        "lead_source": source,
        "owner": rng.choice(OWNERS, n),
        "employee_count": np.round(rng.lognormal(4.5, 1.3, n)).astype(int),
        "has_email": rng.random(n) < 0.86,
        "has_phone": rng.random(n) < 0.72,
        "decision_maker_identified": rng.random(n) < np.where(warm, 0.55, 0.30),
        "website_visits_90d": rng.poisson(np.where(warm, 4.0, 1.2)),
        "email_opens_90d": rng.poisson(np.where(warm, 3.0, 0.8)),
        "days_since_last_activity": np.round(rng.exponential(np.where(warm, 25, 70))).astype(int),
        "research_complete": rng.random(n) < 0.31,
    })
    # Messy CRM realities: missing fields, inconsistent text, duplicates
    for col, rate in [("specialty", 0.08), ("region", 0.04), ("employee_count", 0.12)]:
        df.loc[rng.random(n) < rate, col] = np.nan
    messy = rng.random(n) < 0.06
    df.loc[messy, "org_type"] = df.loc[messy, "org_type"].str.upper()
    dupes = df.sample(40, random_state=seed).copy()
    return pd.concat([df, dupes], ignore_index=True)


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "synthetic_leads.csv"
    generate().to_csv(out, index=False)
    print(f"Wrote {out.name}")
