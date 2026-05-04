"""Tests for preflight (Pilot 0)."""
from __future__ import annotations

from pathlib import Path

import pytest

from pilots import preflight


def test_preflight_passes_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=1, expected_corpus_max=10)
    assert report.passed is True
    assert report.corpus_size == 6  # NCT01-NCT06
    assert report.required_tables_present is True


def test_preflight_fails_when_corpus_below_min(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=100, expected_corpus_max=200)
    assert report.passed is False
    assert "corpus_size" in report.failure_reason


def test_preflight_fails_when_required_table_missing(fake_aact: Path) -> None:
    (fake_aact / "studies.txt").unlink()
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=1, expected_corpus_max=10)
    assert report.passed is False
    assert "studies" in report.failure_reason


# v0.1.6 P1-11: schema-drift branch coverage (v0.1.4 P1-22 hardening).

def test_preflight_detects_schema_drift(fake_aact: Path) -> None:
    """v0.1.4 P1-22: missing required columns must fail preflight closed."""
    # Drop the start_date column from studies.txt (a required column for p04/p08).
    studies = fake_aact / "studies.txt"
    lines = studies.read_text(encoding="utf-8").splitlines(keepends=True)
    header_cols = lines[0].rstrip("\n").split("|")
    if "start_date" in header_cols:
        idx = header_cols.index("start_date")
        new_header = "|".join(c for i, c in enumerate(header_cols) if i != idx) + "\n"
        new_data = []
        for line in lines[1:]:
            cells = line.rstrip("\n").split("|")
            new_data.append("|".join(c for i, c in enumerate(cells) if i != idx) + "\n")
        studies.write_text(new_header + "".join(new_data), encoding="utf-8")
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=1, expected_corpus_max=10)
    assert report.passed is False
    assert "schema drift" in report.failure_reason
    assert "studies" in report.schema_drift
    assert "start_date" in report.schema_drift["studies"]
