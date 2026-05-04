"""Pilot 0 — preflight: verify AACT snapshot, required tables, corpus size."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

from malaria_ct_recon import aact, config, corpus

REQUIRED_TABLES = [
    "studies", "conditions", "browse_conditions", "interventions",
    "sponsors", "countries", "facilities", "eligibilities",
    "design_outcomes", "id_information", "calculated_values",
]

# v0.1.4 P1-22: per-table required-column manifest. AACT renames columns
# between snapshots (cf. lessons.md "AACT column-drift across snapshots").
# Pilot code that references these columns must fail at preflight, not
# mid-run with KeyError. Keep this list minimal — only columns the pilots
# actually read.
REQUIRED_COLUMNS: dict[str, set[str]] = {
    "studies": {
        "nct_id", "overall_status", "primary_completion_date",
        "study_first_submitted_date", "start_date",
    },
    "conditions": {"nct_id", "name"},
    "browse_conditions": {"nct_id", "mesh_term"},
    "interventions": {"nct_id", "intervention_type", "name"},
    "sponsors": {"nct_id", "agency_class", "lead_or_collaborator", "name"},
    "design_outcomes": {"nct_id", "outcome_type", "measure"},
    "id_information": {"nct_id", "id_value", "id_type"},
    "calculated_values": {"nct_id", "were_results_reported",
                          "months_to_report_results"},
    "eligibilities": {"nct_id", "minimum_age", "maximum_age",
                      "criteria"},
    "countries": {"nct_id", "name"},
    "facilities": {"nct_id"},
}


@dataclass(frozen=True)
class PreflightReport:
    passed: bool
    snapshot_dir: Path
    required_tables_present: bool
    missing_tables: list[str]
    corpus_size: int
    failure_reason: str
    schema_drift: dict[str, list[str]] = field(default_factory=dict)


def run(
    snapshot_dir: Path | str | None = None,
    overrides_path: Path | str = "corpus_overrides.csv",
    expected_corpus_min: int = 2000,
    expected_corpus_max: int = 2500,
) -> PreflightReport:
    """Run preflight checks. Returns a report; caller decides exit code.

    Band 2000-2500 reflects the intentionally-broad WHO-antimalarial inclusion filter
    — see design §5. Tightening would underrepresent trials of dual-use antimalarials.
    """
    if snapshot_dir is None:
        cfg = config.load()
        snapshot_dir = cfg.snapshot_dir
    snapshot_dir = Path(snapshot_dir)

    if not snapshot_dir.is_dir():
        return PreflightReport(False, snapshot_dir, False, REQUIRED_TABLES, 0,
                               f"snapshot_dir does not exist: {snapshot_dir}")

    with aact.connect(snapshot_dir) as con:
        present = set(aact.list_tables(con))
        missing = [t for t in REQUIRED_TABLES if t not in present]
        if missing:
            return PreflightReport(False, snapshot_dir, False, missing, 0,
                                   f"required tables missing: {missing}")

        # v0.1.4 P1-22: schema-drift check
        drift: dict[str, list[str]] = {}
        for tbl, required in REQUIRED_COLUMNS.items():
            try:
                cols = set(aact.table_columns(con, tbl))
            except Exception as exc:  # noqa: BLE001
                drift[tbl] = [f"error reading columns: {exc!r}"]
                continue
            missing_cols = sorted(required - cols)
            if missing_cols:
                drift[tbl] = missing_cols
        if drift:
            return PreflightReport(False, snapshot_dir, True, [], 0,
                                   f"AACT schema drift: {drift}",
                                   schema_drift=drift)

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
