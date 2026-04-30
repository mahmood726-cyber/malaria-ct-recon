"""Test P04 — resistance-era pooling."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p04_resistance_era as p04


def test_p04_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p04.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P04"
    assert result.magnitude_unit == "fraction_of_drug_country_cells"
    assert 0.0 <= result.magnitude_value <= 1.0
    assert result.magnitude_ci_low <= result.magnitude_value <= result.magnitude_ci_high
    # After the schema change: n_trials_in_scope counts drug×country cells, not trials.
    # In the fixture, very few cells exist (the corpus is small).
    assert result.n_trials_in_scope <= 20


def test_p04_drug_canonicalisation() -> None:
    assert p04._canonical_drug("Artemether-lumefantrine 20/120mg pediatric") == "artemether-lumefantrine"
    assert p04._canonical_drug("DHA-piperaquine") == "dihydroartemisinin-piperaquine"
    assert p04._canonical_drug("Dihydroartemisinin-piperaquine MDA") == "dihydroartemisinin-piperaquine"
    assert p04._canonical_drug("Artesunate-mefloquine") == "artesunate-mefloquine"
    assert p04._canonical_drug("Tafenoquine 300mg single dose") == "tafenoquine"
