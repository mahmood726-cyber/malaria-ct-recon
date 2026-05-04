"""Tests for the malaria-trial inclusion filter."""
from pathlib import Path

import pandas as pd
import pytest

from malaria_ct_recon import aact, corpus


def _write(tmp_path, name, df):
    df.to_csv(tmp_path / f"{name}.txt", sep="|", index=False)


def _seed(tmp_path):
    _write(tmp_path, "studies", pd.DataFrame({"nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"]}))
    _write(tmp_path, "conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
        "name": ["Plasmodium Falciparum Malaria", "Type 2 Diabetes",
                 "Anemia in malaria-endemic region", "HIV Infection", "Healthy Volunteers"],
    }))
    _write(tmp_path, "browse_conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT04"],
        "mesh_term": ["Malaria, Falciparum", "HIV Infections"],
    }))
    _write(tmp_path, "interventions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT04", "NCT05"],
        "name": ["Artemether-lumefantrine", "Artesunate", "Placebo"],
    }))


def test_build_includes_via_condition_meshterm_or_intervention(tmp_path: Path):
    _seed(tmp_path)
    overrides = tmp_path / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=overrides)
    assert "NCT01" in result.included
    assert "NCT04" in result.included      # intervention=Artesunate
    assert "NCT02" not in result.included
    assert "NCT05" not in result.included  # placebo only


def test_build_respects_exclude_override(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text("nct_id,action,reason,added_by,added_on\nNCT01,exclude,test,test,2026-04-30\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert "NCT01" not in result.included


def test_build_respects_include_override(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text("nct_id,action,reason,added_by,added_on\nNCT05,include,verified,test,2026-04-30\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert "NCT05" in result.included


def test_records_inclusion_reason(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"; ov.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert result.reason["NCT01"]


def test_load_overrides_unknown_action_raises(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text(
        "nct_id,action,reason,added_by,added_on\nNCT01,badvalue,test,test,2026-04-30\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="badvalue|Unknown action"):
        corpus.build(aact.open(tmp_path), overrides_path=ov)


# v0.1.6 P1-11: corpus_overrides audit-trail validation (v0.1.4 P2-10 hardening).

def test_load_overrides_empty_reason_raises(tmp_path: Path):
    """v0.1.4 P2-10: empty reason column must fail closed for audit trail."""
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text(
        "nct_id,action,reason,added_by,added_on\nNCT99,include,,mahmood,2026-04-30\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="empty.*reason|reason.*empty"):
        corpus.build(aact.open(tmp_path), overrides_path=ov)


def test_load_overrides_empty_added_by_raises(tmp_path: Path):
    """v0.1.4 P2-10: empty added_by column must fail closed for audit trail."""
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text(
        "nct_id,action,reason,added_by,added_on\nNCT99,include,manual review,,2026-04-30\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="empty.*added_by|added_by.*empty"):
        corpus.build(aact.open(tmp_path), overrides_path=ov)
