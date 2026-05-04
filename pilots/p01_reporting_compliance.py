"""Pilot P01 — Reporting compliance.

Question: Of completed malaria trials, what fraction posted results to CT.gov
within 12 months of primary completion?
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P01"
PILOT_TITLE = "Reporting compliance"
SCRIPT_PATH = "pilots/p01_reporting_compliance.py"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    t0 = time.perf_counter()
    studies = aact.table(con, "studies")
    cv = aact.table(con, "calculated_values")

    # Restrict to corpus + completed trials
    in_corpus = studies[studies["nct_id"].astype(str).isin(corpus.included)]
    completed = in_corpus[in_corpus["overall_status"].astype(str) == "COMPLETED"]
    n_in = len(completed)

    # Join with calculated_values for were_results_reported + months_to_report_results
    merged = completed.merge(cv, on="nct_id", how="left")

    # Numerator: results reported within 12 months
    reported = merged[
        (merged["were_results_reported"].fillna(False).astype(bool))
        & (pd.to_numeric(merged["months_to_report_results"], errors="coerce") <= 12)
    ]
    k = len(reported)

    if n_in == 0:
        magnitude, ci_low, ci_high = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n_in
        ci_low, ci_high = stats.wilson_ci(k, n_in)

    excluded = {
        "not_completed": int(len(in_corpus) - len(completed)),
        "missing_calculated_values": int(merged["were_results_reported"].isna().sum()),
    }

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n_in),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction",
        magnitude_ci_low=float(ci_low),
        magnitude_ci_high=float(ci_high),
        tractability_AACT_only="full",
        follow_up_potential=4,
        n_trials_excluded_for_reason=excluded,
        notes=f"{k}/{n_in} completed malaria trials posted results within 12mo",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    with aact.connect(cfg.snapshot_dir) as con:
        c = corpus_mod.build(con)
        result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
        schema.write([result], Path("pilots/results/p01.csv"))
        print(f"P01 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
