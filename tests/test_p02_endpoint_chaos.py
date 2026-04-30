"""Test P02 — endpoint-family chaos."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p02_endpoint_chaos as p02


def test_p02_classifies_endpoint_families(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p02.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P02"
    assert result.magnitude_unit == "fraction"
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p02_classify_family_function() -> None:
    assert p02._classify("PCR-corrected ACPR at day 28") == "parasitological"
    assert p02._classify("Vaccine efficacy against clinical malaria") == "vaccine_VE"
    assert p02._classify("Time to first parasitemia after challenge") == "vaccine_VE"
    assert p02._classify("Severe malaria mortality") == "severe"
    assert p02._classify("Gametocyte carriage at day 14") == "transmission"
    assert p02._classify("Pharmacokinetic AUC0-inf") == "PK"
    assert p02._classify("Clinical malaria episodes per person-year") == "clinical"
    assert p02._classify("Some random outcome") == "other"
