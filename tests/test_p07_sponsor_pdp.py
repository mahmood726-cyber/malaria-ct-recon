"""Test P07 — sponsor PDP misclassification."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p07_sponsor_pdp as p07


def test_p07_runs_on_fake_aact(fake_aact: Path) -> None:
    """Test P07 runs on minimal fake AACT and returns valid magnitude result."""
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p07.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P07"
    assert result.pilot_type == "magnitude"
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p07_pdp_recognition() -> None:
    """Test PDP sponsor name recognition."""
    assert p07._is_pdp("Medicines for Malaria Venture")
    assert p07._is_pdp("MMV")
    assert p07._is_pdp("PATH Malaria Vaccine Initiative")
    assert p07._is_pdp("PATH MVI")
    assert p07._is_pdp("FIND")
    assert p07._is_pdp("DNDi")
    assert p07._is_pdp("Drugs for Neglected Diseases initiative")
    assert p07._is_pdp("Aeras Global TB Vaccine Foundation")
    assert p07._is_pdp("International Vaccine Institute")
    assert p07._is_pdp("IVI")
    assert p07._is_pdp("European Vaccine Initiative")
    assert p07._is_pdp("EVI")
    assert p07._is_pdp("Malaria Vaccine Research Center")
    assert p07._is_pdp("MVRC")


def test_p07_pdp_recognition_case_insensitive() -> None:
    """Test PDP recognition is case-insensitive."""
    assert p07._is_pdp("medicines for malaria venture")
    assert p07._is_pdp("mmv")
    assert p07._is_pdp("FIND")
    assert p07._is_pdp("find")


def test_p07_non_pdp_recognition() -> None:
    """Test non-PDP sponsors are correctly identified."""
    assert not p07._is_pdp("Pfizer")
    assert not p07._is_pdp("GlaxoSmithKline")
    assert not p07._is_pdp("London School of Hygiene and Tropical Medicine")
    assert not p07._is_pdp("Sanaria Inc.")
    assert not p07._is_pdp("")
    assert not p07._is_pdp(None)
