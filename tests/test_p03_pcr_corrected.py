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


# v0.1.6 P1-7: ACPR-uncorrected / without-PCR-correction negation tests.

def test_p03_extended_negation_blocks_acpr_uncorrected() -> None:
    """v0.1.6: broaden _PCR_NEG_RX to catch ACPR-uncorrected and without-PCR phrasings."""
    assert not p03._is_pcr_corrected("ACPR-uncorrected day 28")
    assert not p03._is_pcr_corrected("ACPR (without PCR correction) at day 42")


# v0.1.6 P1-11: vector-control regex tests (covers both v0.1.4 baseline and
# v0.1.6 brand-name extensions).

def test_p03_vector_control_regex_matches_chemical_classes() -> None:
    rx = p03._VECTOR_CONTROL_RX
    assert rx.search("artemether-lumefantrine + ITN")
    assert rx.search("Insecticide-treated bednet (LLIN)")
    assert rx.search("indoor residual spraying with pyrethroid")
    assert rx.search("piperonyl butoxide / PBO net")


def test_p03_vector_control_regex_matches_brand_names() -> None:
    """v0.1.6 P1-8: brand-name vector-control trials (Olyset, Interceptor G2, etc)."""
    rx = p03._VECTOR_CONTROL_RX
    assert rx.search("Olyset Plus distribution")
    assert rx.search("Interceptor G2 net (chlorfenapyr)")
    assert rx.search("PermaNet 3.0 cluster RCT")
    assert rx.search("ATSB sugar-bait deployment")
    assert rx.search("Royal Guard net trial")


def test_p03_vector_control_regex_does_not_match_drug_only() -> None:
    """Negative space — pure-drug intervention names must not match vector-control regex."""
    rx = p03._VECTOR_CONTROL_RX
    assert not rx.search("artemether-lumefantrine")
    assert not rx.search("dihydroartemisinin-piperaquine")
    assert not rx.search("primaquine 0.25 mg/kg")
