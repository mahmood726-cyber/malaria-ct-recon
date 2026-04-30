"""Test P08 — retrospective registration."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p08_retro_registration as p08


def test_p08_runs_on_fake_aact(fake_aact: Path) -> None:
    """Test P08 runs on minimal fake AACT and returns valid magnitude result."""
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p08.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P08"
    assert result.pilot_type == "magnitude"
    assert 0.0 <= result.magnitude_value <= 1.0
    # Of 6 corpus trials, only NCT01 is retro (start 2005-06 < submitted 2006-01).
    # NCT02..NCT06 all submitted before start. So 1/6 ≈ 0.167.
    assert result.n_trials_in_scope == 6
