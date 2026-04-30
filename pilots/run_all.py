"""Master orchestrator: run preflight, then all 10 pilots, then write signal-table.csv."""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema
from pilots import (
    preflight,
    p01_reporting_compliance,
    p02_endpoint_chaos,
    p03_pcr_corrected,
    p04_resistance_era,
    p05_pediatric_dose,
    p06_cross_registry,
    p07_sponsor_pdp,
    p08_retro_registration,
    p09_geographic,
    p10_chmi_field,
)

PILOTS = [
    p01_reporting_compliance, p02_endpoint_chaos, p03_pcr_corrected,
    p04_resistance_era, p05_pediatric_dose, p06_cross_registry,
    p07_sponsor_pdp, p08_retro_registration, p09_geographic, p10_chmi_field,
]


def run(
    snapshot_dir: Path,
    snapshot_label: str,
    overrides_path: Path,
    out_path: Path,
    seed: int,
    expected_corpus_min: int = 2000,
    expected_corpus_max: int = 2500,
) -> int:
    pre = preflight.run(snapshot_dir=snapshot_dir, overrides_path=overrides_path,
                        expected_corpus_min=expected_corpus_min,
                        expected_corpus_max=expected_corpus_max)
    if not pre.passed:
        raise RuntimeError(f"preflight failed: {pre.failure_reason}")

    from malaria_ct_recon import corpus as corpus_mod
    con = aact.open(snapshot_dir)
    c = corpus_mod.build(con, overrides_path=overrides_path)

    results = []
    for mod in PILOTS:
        r = mod.run(con=con, corpus=c, aact_snapshot=snapshot_label, seed=seed)
        results.append(r)
        print(f"{r.pilot_id} OK: {r.notes}", file=sys.stderr)

    schema.write(results, out_path)
    return len(results)


def main() -> int:
    from malaria_ct_recon import config
    cfg = config.load()
    n = run(
        snapshot_dir=cfg.snapshot_dir,
        snapshot_label=cfg.snapshot_label,
        overrides_path=Path("corpus_overrides.csv"),
        out_path=Path("dashboard/data/signal-table.csv"),
        seed=20260430,
    )
    print(f"run_all OK: wrote {n} pilot rows to dashboard/data/signal-table.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
