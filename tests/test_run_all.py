"""Test the master run_all orchestrator."""
from pathlib import Path

import pandas as pd
import pytest

from pilots import run_all


def test_run_all_produces_signal_table(fake_aact: Path, tmp_path: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    out = tmp_path / "signal-table.csv"
    n = run_all.run(snapshot_dir=fake_aact, snapshot_label="2026-04-12",
                    overrides_path=overrides, out_path=out, seed=20260430,
                    expected_corpus_min=1, expected_corpus_max=10)
    assert n == 10
    df = pd.read_csv(out)
    assert len(df) == 10
    expected_ids = [f"P0{i}" if i < 10 else f"P{i}" for i in range(1, 11)]
    assert sorted(df["pilot_id"].tolist()) == sorted(expected_ids)
    assert df["pilot_type"].isin(["magnitude", "tractability_probe"]).all()


def test_run_all_aborts_if_preflight_fails(tmp_path: Path) -> None:
    """tmp_path has no AACT files → preflight should fail."""
    out = tmp_path / "signal-table.csv"
    overrides = tmp_path / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="preflight"):
        run_all.run(snapshot_dir=tmp_path, snapshot_label="x",
                    overrides_path=overrides, out_path=out, seed=1,
                    expected_corpus_min=1, expected_corpus_max=10)


# v0.1.6 P1-11: per-pilot resilience test (v0.1.4 P1-23 hardening).

def test_run_all_continues_when_one_pilot_raises(
    fake_aact: Path, tmp_path: Path, monkeypatch
) -> None:
    """v0.1.4 P1-23: one pilot raising must not kill the whole run.

    Successful pilots' results are still written; the failure is reported
    via stderr.
    """
    # Patch P05 to raise — verify the other 9 still complete.
    from pilots import p05_pediatric_dose

    def boom(*args, **kwargs):
        raise RuntimeError("simulated P05 failure")

    monkeypatch.setattr(p05_pediatric_dose, "run", boom)

    out = tmp_path / "signal-table.csv"
    overrides = fake_aact / "ov.csv"
    overrides.write_text(
        "nct_id,action,reason,added_by,added_on\n", encoding="utf-8"
    )
    n = run_all.run(
        snapshot_dir=fake_aact, snapshot_label="2026-04-12",
        overrides_path=overrides, out_path=out, seed=20260430,
        expected_corpus_min=1, expected_corpus_max=10,
    )
    assert n == 9, f"expected 9 successes (P05 failed), got {n}"
    df = pd.read_csv(out)
    assert "P05" not in df["pilot_id"].tolist()
    assert len(df) == 9
