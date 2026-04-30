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
