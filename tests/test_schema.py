"""Tests for PilotResult schema + CSV writer."""
import csv
import json
from pathlib import Path

import pytest

from malaria_ct_recon import schema


def make_result(**overrides) -> schema.PilotResult:
    base = dict(
        pilot_id="P01", pilot_title="Reporting compliance", pilot_type="magnitude",
        n_trials_in_scope=1342, magnitude_value=0.31, magnitude_unit="fraction",
        magnitude_ci_low=0.28, magnitude_ci_high=0.34,
        tractability_AACT_only="full", follow_up_potential=4,
        n_trials_excluded_for_reason={"missing_completion_date": 12},
        notes="31% of completed malaria trials post results within 12mo",
        script_path="pilots/p01_reporting_compliance.py", script_sha256="abc123",
        aact_snapshot="2026-04-12", seed=20260430, wall_clock_seconds=4.2,
    )
    base.update(overrides)
    return schema.PilotResult(**base)


def test_pilot_result_serialises_to_csv_row(tmp_path: Path) -> None:
    schema.write([make_result()], tmp_path / "p01.csv")
    rows = list(csv.DictReader((tmp_path / "p01.csv").open(encoding="utf-8")))
    assert rows[0]["pilot_id"] == "P01"
    assert json.loads(rows[0]["n_trials_excluded_for_reason"]) == {"missing_completion_date": 12}


def test_tractability_probe_allows_nan_magnitude(tmp_path: Path) -> None:
    r = make_result(pilot_id="P06", pilot_type="tractability_probe",
                    magnitude_value=float("nan"), magnitude_ci_low=float("nan"),
                    magnitude_ci_high=float("nan"), magnitude_unit="")
    schema.write([r], tmp_path / "p06.csv")
    rows = list(csv.DictReader((tmp_path / "p06.csv").open(encoding="utf-8")))
    assert rows[0]["magnitude_value"] == ""


def test_invalid_pilot_type_raises() -> None:
    with pytest.raises(ValueError, match="pilot_type"):
        make_result(pilot_type="invalid")


def test_follow_up_potential_clamped_1_to_5() -> None:
    with pytest.raises(ValueError, match="follow_up_potential"):
        make_result(follow_up_potential=0)
    with pytest.raises(ValueError, match="follow_up_potential"):
        make_result(follow_up_potential=6)


def test_aggregate_writes_master_table(tmp_path: Path) -> None:
    rs = [make_result(), make_result(pilot_id="P02", pilot_title="Endpoint chaos")]
    schema.write(rs, tmp_path / "signal-table.csv")
    rows = list(csv.DictReader((tmp_path / "signal-table.csv").open(encoding="utf-8")))
    assert [r["pilot_id"] for r in rows] == ["P01", "P02"]
