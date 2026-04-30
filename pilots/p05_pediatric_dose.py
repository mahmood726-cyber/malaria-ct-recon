"""Pilot P05 — Pediatric dose fragmentation.

Question: For the 5 most-frequent antimalarial intervention names in the corpus
(by trial count), how many distinct dose strings exist per drug-age-band cell?
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P05"
PILOT_TITLE = "Pediatric dose fragmentation"
SCRIPT_PATH = "pilots/p05_pediatric_dose.py"


def _parse_age_to_years(s: str) -> float | None:
    """Convert age string (e.g. '6 Months', '18 Years') to years as a float.

    Returns None if the string is N/A, NA, empty, or unparseable.
    """
    if s is None or str(s).strip().upper() in {"N/A", "NA", ""}:
        return None
    m = re.match(r"(\d+(?:\.\d+)?)\s*(Year|Years|Month|Months|Week|Weeks|Day|Days)", str(s), re.IGNORECASE)
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2).lower()
    if unit.startswith("year"):
        return val
    if unit.startswith("month"):
        return val / 12.0
    if unit.startswith("week"):
        return val / 52.0
    return val / 365.0


def _age_band(min_age: str, max_age: str) -> str:
    """Classify trial age eligibility into pediatric bands + adult.

    Returns: "under_5y", "5_to_11y", "12_to_17y", "adult", "mixed", "unknown"
    """
    lo = _parse_age_to_years(min_age)
    hi = _parse_age_to_years(max_age)
    if lo is None and hi is None:
        return "unknown"
    if lo is None:
        lo = 0
    if hi is None:
        hi = 200
    # Check for clean fit in single band (no overlap across boundaries)
    if hi < 5:
        return "under_5y"
    if lo >= 5 and hi <= 11:
        return "5_to_11y"
    if lo >= 12 and hi <= 17:
        return "12_to_17y"
    if lo >= 18:
        return "adult"
    return "mixed"


def _drug_key(name: str) -> str:
    """Canonicalise drug name to a standardised form.

    Returns the full combination name if identifiable, else the first word lowercased.
    """
    n = (name or "").lower()
    for stem in [
        "artemether-lumefantrine",
        "dihydroartemisinin-piperaquine",
        "artesunate-mefloquine",
        "artesunate-amodiaquine",
        "sulfadoxine-pyrimethamine",
        "tafenoquine",
        "primaquine",
    ]:
        if stem in n or all(part in n for part in stem.split("-")):
            return stem
    return n.split()[0] if n else "unknown"


def _sha256_self() -> str:
    """Return the SHA256 hash of this file's contents."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    """Run P05 pediatric dose fragmentation analysis.

    Identifies the 5 most-frequent antimalarial drugs (by trial count) in the corpus.
    For each drug and age band, counts the number of distinct dose strings.
    Returns the mean distinct dose count per drug-age-band cell.

    Args:
        con: DuckDB connection to AACT snapshot
        corpus: Corpus of included trials (by NCT ID)
        aact_snapshot: Label for the AACT snapshot (for metadata)
        seed: Random seed for bootstrap CI

    Returns:
        PilotResult with magnitude = mean distinct doses per drug × age band cell
    """
    t0 = time.perf_counter()
    interventions = aact.table(con, "interventions")
    eligibilities = aact.table(con, "eligibilities")

    # Filter interventions to corpus and canonicalise drug names
    iv = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()
    iv["drug"] = iv["name"].astype(str).map(_drug_key)

    # Select top 5 drugs by trial count
    top5 = iv.groupby("drug")["nct_id"].nunique().sort_values(ascending=False).head(5).index.tolist()
    iv_top5 = iv[iv["drug"].isin(top5)]

    # Classify age bands from eligibility criteria
    eligibilities["age_band"] = [
        _age_band(lo, hi)
        for lo, hi in zip(eligibilities["minimum_age"].astype(str), eligibilities["maximum_age"].astype(str))
    ]

    # Merge interventions with age band info
    merged = iv_top5.merge(eligibilities[["nct_id", "age_band"]], on="nct_id")

    # Count distinct dose strings per (drug, age_band) cell
    distinct_per_cell = merged.groupby(["drug", "age_band"])["name"].nunique()

    if len(distinct_per_cell) == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = float(distinct_per_cell.mean())
        # Bootstrap CI on the mean of distinct counts per cell
        boot_lo, boot_hi = stats.bootstrap_ci(
            np.asarray(distinct_per_cell.values, dtype=float),
            np.mean,
            n_resamples=1000,
            seed=seed,
        )
        lo, hi = float(boot_lo), float(boot_hi)

    excluded = {
        "not_top5_drug": int(len(corpus.included) - merged["nct_id"].nunique()),
    }

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(merged["nct_id"].nunique()),
        magnitude_value=magnitude,
        magnitude_unit="mean_distinct_doses_per_drug_age_band",
        magnitude_ci_low=lo,
        magnitude_ci_high=hi,
        tractability_AACT_only="full",
        follow_up_potential=3,
        n_trials_excluded_for_reason=excluded,
        notes=f"top5={top5}; {len(distinct_per_cell)} drug × age cells; mean distinct dose strings={magnitude:.2f}",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    """Run P05 against the configured AACT snapshot."""
    from malaria_ct_recon import config, corpus as corpus_mod

    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p05.csv"))
    print(f"P05 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
