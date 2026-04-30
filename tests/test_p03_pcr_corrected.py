"""Test P03 — PCR-corrected outcome reporting."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p03_pcr_corrected as p03


def test_p03_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p03.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P03"
    assert result.n_trials_in_scope >= 1
    assert 0.0 <= result.magnitude_value <= 1.0
    assert result.magnitude_ci_low <= result.magnitude_value <= result.magnitude_ci_high


def test_p03_pcr_pattern_matches_known_phrasings() -> None:
    assert p03._is_pcr_corrected("PCR-corrected ACPR day 28")
    assert p03._is_pcr_corrected("ACPR (PCR-adjusted) at day 42")
    assert p03._is_pcr_corrected("Genotypically-corrected treatment failure")
    assert p03._is_pcr_corrected("PCR adjusted parasitemia")
    assert p03._is_pcr_corrected("molecularly corrected recurrence")
    assert not p03._is_pcr_corrected("Day 28 ACPR")
    assert not p03._is_pcr_corrected("Time to recurrent parasitaemia (PCR-uncorrected)")
    assert not p03._is_pcr_corrected("PCR-uncorrected malaria")
