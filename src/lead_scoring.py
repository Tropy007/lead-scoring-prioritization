"""Run the SQL lead-scoring pipeline end to end with SQLite.

Usage:  python src/lead_scoring.py
Outputs: outputs/scored_leads.csv, outputs/top_50_leads.csv, outputs/kpis_by_source.csv
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"


def load_raw(con, csv_path):
    raw = pd.read_csv(csv_path)
    for col in ["has_email", "has_phone", "decision_maker_identified", "research_complete"]:
        raw[col] = raw[col].astype(int)
    raw.to_sql("raw_leads", con, index=False, if_exists="replace")


def run_pipeline(csv_path=ROOT / "data" / "synthetic_leads.csv", con=None):
    con = con or sqlite3.connect(":memory:")
    load_raw(con, csv_path)
    quality = pd.read_sql((SQL / "01_data_quality.sql").read_text(), con)
    for step in ["02_clean_leads.sql", "03_score_and_rank.sql"]:
        con.executescript((SQL / step).read_text())
    scored = pd.read_sql("SELECT * FROM scored_leads ORDER BY overall_rank", con)
    kpis = pd.read_sql((SQL / "04_kpis.sql").read_text(), con)
    return quality, scored, kpis


def priority_band(score: float) -> str:
    """Translate a 0-100 score into an action label."""
    if score >= 70:
        return "Contact this week"
    if score >= 50:
        return "Nurture"
    if score >= 30:
        return "Complete research"
    return "Deprioritize"


if __name__ == "__main__":
    quality, scored, kpis = run_pipeline()
    scored["priority"] = scored["lead_score"].apply(priority_band)
    out = ROOT / "outputs"; out.mkdir(exist_ok=True)
    scored.to_csv(out / "scored_leads.csv", index=False)
    scored.head(50).to_csv(out / "top_50_leads.csv", index=False)
    kpis.to_csv(out / "kpis_by_source.csv", index=False)
    print(quality.T.to_string(header=False))
    print(f"\nScored {len(scored)} leads; Top 50 written to outputs/top_50_leads.csv")
