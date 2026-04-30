"""Test P05 — pediatric dose fragmentation."""
from pathlib import Path

import pandas as pd
import pytest

from malaria_ct_recon import aact, corpus
from pilots import p05_pediatric_dose as p05


def _seed_aact(tmp_path: Path) -> None:
    """Seed a minimal fake AACT with interventions and eligibilities."""
    def _write(name, df):
        df.to_csv(tmp_path / f"{name}.txt", sep="|", index=False)

    _write("studies", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
    }))
    _write("conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
        "name": ["Malaria", "Malaria", "Malaria", "Malaria", "Malaria"],
    }))
    _write("browse_conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
        "mesh_term": ["Malaria, Falciparum"] * 5,
    }))
    _write("interventions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT02", "NCT03", "NCT03", "NCT04", "NCT04", "NCT05"],
        "name": [
            "Artemether-lumefantrine 20-120 mg",
            "Artemether-lumefantrine 80-480 mg",
            "Artemether-lumefantrine 60-360 mg",
            "Dihydroartemisinin-piperaquine 16-100 mg",
            "Dihydroartemisinin-piperaquine 32-200 mg",
            "Dihydroartemisinin-piperaquine 16-100 mg",
            "Artesunate-amodiaquine 50-150 mg",
            "Artesunate-amodiaquine 100-300 mg",
            "Quinine",  # Not in top 5
        ],
    }))
    _write("eligibilities", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
        "minimum_age": ["6 Months", "5 Years", "12 Years", "18 Years", "N/A"],
        "maximum_age": ["59 Months", "11 Years", "17 Years", "65 Years", "N/A"],
    }))


def test_p05_runs_on_fake_aact(tmp_path: Path) -> None:
    """Test P05 runs on minimal fake AACT and returns valid result."""
    _seed_aact(tmp_path)
    overrides = tmp_path / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(tmp_path)
    c = corpus.build(con, overrides_path=overrides)
    result = p05.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)

    assert result.pilot_id == "P05"
    assert result.magnitude_unit == "mean_distinct_doses_per_drug_age_band"
    assert result.magnitude_value >= 1.0
    assert result.n_trials_in_scope >= 1


def test_p05_age_band_under_5() -> None:
    """Test age band classification for under-5."""
    assert p05._age_band("6 Months", "59 Months") == "under_5y"
    assert p05._age_band("0 Years", "4 Years") == "under_5y"


def test_p05_age_band_5_to_11() -> None:
    """Test age band classification for 5-11 years."""
    assert p05._age_band("5 Years", "11 Years") == "5_to_11y"
    assert p05._age_band("5 Years", "9 Years") == "5_to_11y"


def test_p05_age_band_12_to_17() -> None:
    """Test age band classification for 12-17 years."""
    assert p05._age_band("12 Years", "17 Years") == "12_to_17y"
    assert p05._age_band("12 Years", "16 Years") == "12_to_17y"


def test_p05_age_band_adult() -> None:
    """Test age band classification for adults."""
    assert p05._age_band("18 Years", "65 Years") == "adult"
    assert p05._age_band("21 Years", "N/A") == "adult"


def test_p05_age_band_unknown() -> None:
    """Test age band classification for unknown/N/A."""
    assert p05._age_band("N/A", "N/A") == "unknown"
    assert p05._age_band("NA", "NA") == "unknown"
    assert p05._age_band("", "") == "unknown"


def test_p05_age_band_mixed() -> None:
    """Test age band classification for mixed/overlapping ages."""
    assert p05._age_band("3 Years", "13 Years") == "mixed"
    assert p05._age_band("10 Years", "20 Years") == "mixed"
