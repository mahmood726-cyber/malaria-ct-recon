"""Pilot P08 — Retrospective registration.

Question: What fraction of malaria trials have start_date < study_first_submitted_date
(registered AFTER trial started)? This is stratified pre-2007 vs post-2007 to capture
the ICMJE prospective-registration era boundary (adopted ~2005, enforced 2007+).

Retrospective registration may correlate with selective outcome reporting and
poses a threat to evidence quality.
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P08"
PILOT_TITLE = "Retrospective registration"
SCRIPT_PATH = "pilots/p08_retro_registration.py"


def _sha256_self() -> str:
    """Return the SHA256 hash of this file's contents."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    """Run P08 retrospective registration pilot.

    Identifies malaria trials in the corpus with start_date < study_first_submitted_date,
    indicating the trial began before formal registration. Stratified by era (pre-2007 vs
    post-2007) to capture ICMJE adoption.

    Args:
        con: DuckDB connection to AACT snapshot
        corpus: Corpus of included trials (by NCT ID)
        aact_snapshot: Label for the AACT snapshot (for metadata)
        seed: Random seed (unused for this deterministic analysis)

    Returns:
        PilotResult with pilot_type="magnitude" reporting the fraction of
        trials with retrospective registration, plus breakdown by era.
    """
    t0 = time.perf_counter()

    # Load studies table
    studies = aact.table(con, "studies")

    # Filter to corpus trials
    s = studies[studies["nct_id"].astype(str).isin(corpus.included)].copy()

    # Parse dates
    s["start"] = pd.to_datetime(s["start_date"], errors="coerce")
    s["submitted"] = pd.to_datetime(s["study_first_submitted_date"], errors="coerce")

    # Keep only trials with both dates
    s = s.dropna(subset=["start", "submitted"])

    # Identify retrospective registration (start < submitted)
    s["retro"] = s["start"] < s["submitted"]

    # Stratify by era (ICMJE boundary ~2007)
    s["era"] = s["start"].dt.year.map(lambda y: "pre_2007" if y < 2007 else "post_2007")

    # Compute overall counts
    n = len(s)
    k = int(s["retro"].sum())

    # Compute Wilson CI
    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(int(k), int(n))

    # Breakdown by era (for notes)
    by_era = s.groupby("era")["retro"].agg(["sum", "count"]).to_dict("index")

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction_retro_registered",
        magnitude_ci_low=float(lo),
        magnitude_ci_high=float(hi),
        tractability_AACT_only="full",
        # follow_up_potential=4: retrospective registration is a known confounder
        # for outcome-switching and selective reporting; direct threat to evidence quality.
        follow_up_potential=4,
        n_trials_excluded_for_reason={"missing_dates": int(len(corpus.included) - n)},
        notes=f"{k}/{n} retrospectively registered; by_era={by_era}",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    """Run P08 against the configured AACT snapshot."""
    from malaria_ct_recon import config, corpus as corpus_mod

    cfg = config.load()
    with aact.connect(cfg.snapshot_dir) as con:
        c = corpus_mod.build(con)
        result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
        schema.write([result], Path("pilots/results/p08.csv"))
        print(f"P08 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
