"""Test P09 — geographic transmission heterogeneity probe."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p09_geographic as p09


def test_p09_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p09.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P09"
    assert result.pilot_type == "tractability_probe"
    assert result.tractability_AACT_only == "none"
    assert "MAP" in result.notes


def test_p09_returns_valid_result(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p09.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert isinstance(result, schema.PilotResult)
    assert result.n_trials_in_scope > 0
    assert 1 <= result.follow_up_potential <= 5
    # Tractability probe should have NaN magnitude
    import math
    assert math.isnan(result.magnitude_value)
    assert math.isnan(result.magnitude_ci_low)
    assert math.isnan(result.magnitude_ci_high)


def test_p09_includes_country_distribution(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p09.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    # Fixture has countries table with Tanzania, Kenya, Mozambique, Ghana, Cambodia, Brazil, US, Zambia
    # For malaria trials (6 total) we should see multi-country distribution
    assert "top10_countries" in result.notes
    assert "multi_country_trials" in result.notes
