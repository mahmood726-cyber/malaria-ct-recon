"""Test P03 expanded-regex robustness check."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p03_pcr_corrected as p03prod
from pilots import p03_expanded_regex_check as p03exp


def test_expanded_pattern_matches_more_than_production():
    """Expanded pattern should match new phrases that production misses."""
    cases = [
        "PCR-confirmed recrudescence",
        "genotyping-corrected outcome",
        "PCR-distinguished new infection from recrudescence",
        "parasitologically corrected ACPR",
    ]
    for s in cases:
        assert p03exp._is_pcr_corrected_expanded(s), f"Expanded should match: {s}"
        assert not p03prod._is_pcr_corrected(s), f"Production should NOT match: {s}"


def test_expanded_still_excludes_uncorrected():
    """Expanded pattern should still reject PCR-uncorrected."""
    assert not p03exp._is_pcr_corrected_expanded("PCR-uncorrected ACPR")


def test_expanded_includes_production_phrasings():
    """Anything the production pattern catches, the expanded one must catch too."""
    cases = [
        "PCR-corrected ACPR day 28",
        "ACPR (PCR-adjusted)",
        "Genotypically-corrected treatment failure",
        "molecularly corrected recurrence",
    ]
    for s in cases:
        assert p03exp._is_pcr_corrected_expanded(s), f"Expanded should match: {s}"


def test_runs_on_fake_aact(fake_aact: Path):
    """Test that the expanded check runs end-to-end on fake AACT."""
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    out = p03exp.run(con=con, corpus=c)
    assert {"variant", "n", "k", "rate"} <= set(out.columns)
    # Expanded ≥ production by construction.
    prod = out[out["variant"] == "production"].iloc[0]
    expd = out[out["variant"] == "expanded"].iloc[0]
    assert expd["k"] >= prod["k"], (
        f"Expanded count ({expd['k']}) should be >= production ({prod['k']})"
    )
