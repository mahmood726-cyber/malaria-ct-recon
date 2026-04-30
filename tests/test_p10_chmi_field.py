"""Test P10 — CHMI vs field-trial mixing."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p10_chmi_field as p10


def test_p10_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p10.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P10"
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p10_chmi_recognition() -> None:
    assert p10._is_chmi("PfSPZ Challenge", "Healthy non-immune adults for sporozoite challenge")
    assert p10._is_chmi("Sporozoite challenge", "")
    assert not p10._is_chmi("RTS,S/AS01", "Healthy infants 5-17 months")


def test_p10_returns_valid_result(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p10.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert isinstance(result, schema.PilotResult)
    assert result.pilot_type == "magnitude"
    assert result.tractability_AACT_only == "full"
    assert 1 <= result.follow_up_potential <= 5
    assert "chmi" in result.magnitude_unit.lower()


def test_p10_detects_chmi_in_corpus(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p10.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    # Fixture has 2 vaccine trials in corpus (NCT02: RTS,S and NCT05: PfSPZ Challenge)
    # NCT05 is CHMI, so we expect 1/2 to be CHMI
    assert result.n_trials_in_scope >= 1
    assert result.magnitude_value > 0.0  # At least one CHMI detected
    assert "CHMI" in result.notes
