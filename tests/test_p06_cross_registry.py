"""Test P06 — cross-registry coverage probe."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p06_cross_registry as p06


def test_p06_runs_on_fake_aact(fake_aact: Path) -> None:
    """Test P06 runs on minimal fake AACT and returns valid tractability_probe result."""
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p06.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)

    assert result.pilot_id == "P06"
    assert result.pilot_type == "tractability_probe"
    assert result.tractability_AACT_only == "partial"
    assert "cross_registered_count" in result.notes


def test_p06_registry_pattern_recognition() -> None:
    """Test registry ID pattern recognition."""
    assert p06._registry_kind("ISRCTN12345678") == "ISRCTN"
    assert p06._registry_kind("PACTR201509001234567") == "PACTR"
    assert p06._registry_kind("RBR-abc123") == "RBR"
    assert p06._registry_kind("ACTRN12612345678") == "ANZCTR"
    assert p06._registry_kind("NCT01234567") is None
    assert p06._registry_kind("EUDRA-2010-001234") == "EUCTR"
    assert p06._registry_kind("U1111-1234-5678") == "WHO_UTN"
    assert p06._registry_kind("DRKS00123456") == "DRKS"
    assert p06._registry_kind("CTRI/2020/01/023456") == "CTRI"
    assert p06._registry_kind("ChiCTR2020000123") == "ChiCTR"
    assert p06._registry_kind("JPRN-UMIN000012345") == "JPRN"


def test_p06_registry_pattern_case_insensitive() -> None:
    """Test registry pattern recognition is case-insensitive."""
    assert p06._registry_kind("isrctn12345678") == "ISRCTN"
    assert p06._registry_kind("pactr201509001234567") == "PACTR"


def test_p06_registry_unknown() -> None:
    """Test unknown/invalid registry IDs return None."""
    assert p06._registry_kind("") is None
    assert p06._registry_kind("UNKNOWN12345") is None
    assert p06._registry_kind("XYZ-123") is None
