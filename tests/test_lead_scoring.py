import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from generate_synthetic_leads import generate
from lead_scoring import run_pipeline, priority_band


def test_pipeline_removes_duplicates_and_scores_range(tmp_path):
    csv = tmp_path / "leads.csv"
    generate(n=300, seed=1).to_csv(csv, index=False)
    quality, scored, _ = run_pipeline(csv)
    assert scored["lead_id"].is_unique
    assert len(scored) == quality.loc[0, "unique_leads"]
    assert scored["lead_score"].between(0, 100).all()


def test_ranking_is_ordered_by_score(tmp_path):
    csv = tmp_path / "leads.csv"
    generate(n=300, seed=2).to_csv(csv, index=False)
    _, scored, _ = run_pipeline(csv)
    assert scored["lead_score"].is_monotonic_decreasing


def test_text_is_standardized(tmp_path):
    csv = tmp_path / "leads.csv"
    generate(n=300, seed=3).to_csv(csv, index=False)
    _, scored, _ = run_pipeline(csv)
    assert not scored["org_type"].str.isupper().any()


def test_priority_bands():
    assert priority_band(85) == "Contact this week"
    assert priority_band(55) == "Nurture"
    assert priority_band(35) == "Complete research"
    assert priority_band(10) == "Deprioritize"
