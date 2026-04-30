"""Pilot P04 — Resistance-era pooling.

Question: Of artemisinin-class trials, what fraction of (drug × country) cells
span the K13 boundary (≤2008 vs ≥2015)?
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P04"
PILOT_TITLE = "Resistance-era pooling"
SCRIPT_PATH = "pilots/p04_resistance_era.py"

_ARTEMISININ_RX = re.compile(
    r"artemether|artesunate|artemisinin|dihydroartemisinin|DHA-piperaquine",
    re.IGNORECASE,
)


def _canonical_drug(name: str) -> str:
    """Canonicalise drug name to a standardised form."""
    n = (name or "").lower()
    if "lumefantrine" in n and ("artemether" in n or "al " in n):
        return "artemether-lumefantrine"
    if "piperaquine" in n and ("dihydroartemisinin" in n or "dha" in n):
        return "dihydroartemisinin-piperaquine"
    if "mefloquine" in n and "artesunate" in n:
        return "artesunate-mefloquine"
    if "amodiaquine" in n and "artesunate" in n:
        return "artesunate-amodiaquine"
    if "amodiaquine" in n and "sulfadoxine" in n:
        return "sulfadoxine-pyrimethamine-amodiaquine"
    # Default: extract first word lowercased
    return n.split()[0] if n else "unknown"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    """Run P04 resistance-era pooling analysis.

    Identifies artemisinin-class trials in the corpus, groups by (drug, country),
    and counts what fraction of cells have both pre-K13 (≤2008) and post-K13 (≥2015)
    trials, indicating pooling across resistance eras.
    """
    t0 = time.perf_counter()
    studies = aact.table(con, "studies")
    interventions = aact.table(con, "interventions")
    countries = aact.table(con, "countries")

    # Filter studies to corpus
    in_corpus = studies[studies["nct_id"].astype(str).isin(corpus.included)].copy()
    in_corpus["start_year"] = pd.to_datetime(in_corpus["start_date"], errors="coerce").dt.year

    # Filter interventions to artemisinin-class, corpus-only
    art_iv = interventions[
        (interventions["nct_id"].astype(str).isin(corpus.included))
        & (interventions["name"].astype(str).map(lambda n: bool(_ARTEMISININ_RX.search(n))))
    ].copy()
    art_iv["drug"] = art_iv["name"].astype(str).map(_canonical_drug)

    # Merge to get start_year and country
    merged = art_iv.merge(
        in_corpus[["nct_id", "start_year"]],
        on="nct_id"
    ).merge(
        countries.rename(columns={"name": "country"}),
        on="nct_id"
    )

    # Classify trials into eras
    merged["era"] = merged["start_year"].map(
        lambda y: (
            "pre_K13" if y is not None and y <= 2008
            else ("post_K13" if y is not None and y >= 2015 else "between")
        )
    )

    # Group by (drug, country) and collect eras in each cell
    cells = merged.groupby(["drug", "country"])["era"].apply(set)
    # Filter out cells with only "between" era (need at least one pre or post)
    cells_with_data = cells[cells.map(lambda s: bool(s - {"between"}))]
    n_cells = len(cells_with_data)
    # Count cells spanning both pre and post K13
    spanning = (cells_with_data.map(lambda s: {"pre_K13", "post_K13"}.issubset(s))).sum()

    if n_cells == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = spanning / n_cells
        lo, hi = stats.wilson_ci(int(spanning), int(n_cells))

    excluded = {
        "non_artemisinin": int(len(corpus.included) - merged["nct_id"].nunique()),
    }

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(merged["nct_id"].nunique()),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction_of_drug_country_cells",
        magnitude_ci_low=float(lo),
        magnitude_ci_high=float(hi),
        tractability_AACT_only="full",
        follow_up_potential=5,
        n_trials_excluded_for_reason=excluded,
        notes=f"{int(spanning)}/{n_cells} drug × country cells span the pre/post-K13 boundary",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod

    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p04.csv"))
    print(f"P04 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
