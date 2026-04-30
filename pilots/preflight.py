"""Pilot 0 — preflight: verify AACT snapshot, required tables, corpus size."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from malaria_ct_recon import aact, config, corpus

REQUIRED_TABLES = [
    "studies", "conditions", "browse_conditions", "interventions",
    "sponsors", "countries", "facilities", "eligibilities",
    "design_outcomes", "id_information", "calculated_values",
]


@dataclass(frozen=True)
class PreflightReport:
    passed: bool
    snapshot_dir: Path
    required_tables_present: bool
    missing_tables: list[str]
    corpus_size: int
    failure_reason: str


def run(
    snapshot_dir: Path | str | None = None,
    overrides_path: Path | str = "corpus_overrides.csv",
    expected_corpus_min: int = 1200,
    expected_corpus_max: int = 1600,
) -> PreflightReport:
    """Run preflight checks. Returns a report; caller decides exit code."""
    if snapshot_dir is None:
        cfg = config.load()
        snapshot_dir = cfg.snapshot_dir
    snapshot_dir = Path(snapshot_dir)

    if not snapshot_dir.is_dir():
        return PreflightReport(False, snapshot_dir, False, REQUIRED_TABLES, 0,
                               f"snapshot_dir does not exist: {snapshot_dir}")

    con = aact.open(snapshot_dir)
    present = set(aact.list_tables(con))
    missing = [t for t in REQUIRED_TABLES if t not in present]
    if missing:
        return PreflightReport(False, snapshot_dir, False, missing, 0,
                               f"required tables missing: {missing}")

    try:
        c = corpus.build(con, overrides_path=overrides_path)
    except Exception as exc:
        return PreflightReport(False, snapshot_dir, True, [], 0,
                               f"corpus build failed: {exc!r}")

    if not (expected_corpus_min <= len(c.included) <= expected_corpus_max):
        return PreflightReport(False, snapshot_dir, True, [], len(c.included),
                               f"corpus_size {len(c.included)} outside [{expected_corpus_min}, {expected_corpus_max}]")

    return PreflightReport(True, snapshot_dir, True, [], len(c.included), "")


def main() -> int:
    report = run()
    if report.passed:
        print(f"PREFLIGHT OK: corpus_size={report.corpus_size} snapshot={report.snapshot_dir}")
        return 0
    print(f"PREFLIGHT FAIL: {report.failure_reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
