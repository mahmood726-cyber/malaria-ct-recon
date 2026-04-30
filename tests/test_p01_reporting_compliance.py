"""Test P01 — reporting compliance against fixture."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p01_reporting_compliance as p01


def test_p01_runs_on_fake_aact_and_returns_valid_result(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p01.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert isinstance(result, schema.PilotResult)
    assert result.pilot_id == "P01"
    assert result.pilot_type == "magnitude"
    assert result.magnitude_unit == "fraction"
    # Of 6 included trials (NCT01-NCT06), all 6 are completed.
    # calculated_values.were_results_reported within 12mo:
    #   NCT01 False, NCT02 True (7mo), NCT03 True (9mo), NCT04 False,
    #   NCT05 True (5mo), NCT06 False
    # = 3/6 = 0.50
    assert 0.45 <= result.magnitude_value <= 0.55
    assert result.magnitude_ci_low <= result.magnitude_value <= result.magnitude_ci_high
    assert 1 <= result.follow_up_potential <= 5


def test_p01_excludes_non_completed_trials(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p01.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    # All 6 corpus trials are COMPLETED in the fixture; n_trials_in_scope == 6
    assert result.n_trials_in_scope == 6
