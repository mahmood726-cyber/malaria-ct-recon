"""P03 sensitivity analysis — restrict to uncomplicated P. falciparum subset.

Per spec §4 of 2026-05-03-methods-paper-design.md. Indication filter rules:

INCLUDE if any condition contains 'falciparum' OR 'uncomplicated malaria'.
EXCLUDE if any condition contains 'severe', 'complicated', 'vivax-only',
'ovale-only', 'malariae-only', 'prevention', 'chemoprevention', 'mda',
'iptp', or 'vaccine'.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import duckdb
import pandas as pd

from malaria_ct_recon import aact, config
from malaria_ct_recon import corpus as corpus_mod
from malaria_ct_recon.corpus import Corpus
from pilots import p01_p03_year_trajectories as yt

_INCLUDE_RX = re.compile(r"\b(falciparum|uncomplicated\s+malaria)\b", re.IGNORECASE)
_EXCLUDE_RX = re.compile(
    r"\b(severe|complicated|vivax-only|ovale-only|malariae-only|"
    r"prevention|chemoprevention|mda|iptp|vaccine)\b",
    re.IGNORECASE,
)


def is_uncomplicated_falciparum(conditions: Iterable[str]) -> bool:
    """Apply the §4 indication filter to a per-trial set of condition strings."""
    conditions = [str(c) for c in conditions if c is not None]
    if any(_EXCLUDE_RX.search(c) for c in conditions):
        return False
    return any(_INCLUDE_RX.search(c) for c in conditions)


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    p03_per_trial = yt._p03_per_trial(con, corpus)
    cond = aact.table(con, "conditions")
    cond_by_trial = (
        cond[cond["nct_id"].astype(str).isin(p03_per_trial["nct_id"])]
        .groupby("nct_id")["name"]
        .apply(list)
    )
    keep = cond_by_trial[cond_by_trial.apply(is_uncomplicated_falciparum)].index.tolist()
    subset = p03_per_trial[p03_per_trial["nct_id"].isin(keep)].copy()
    g = subset.groupby("year").agg(n=("nct_id", "count"), k=("pcr_corrected", "sum"))
    g["rate"] = g.apply(lambda r: (r["k"] / r["n"]) if r["n"] > 0 else float("nan"), axis=1)
    return g.reset_index().sort_values("year").reset_index(drop=True)


def main() -> int:
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    df = run(con=con, corpus=c)
    out = Path("pilots/results/p03_sensitivity.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    n_total, k_total = int(df["n"].sum()), int(df["k"].sum())
    print(f"p03_sensitivity OK: n_subset={n_total}, k_subset={k_total}, rate={k_total/max(n_total,1):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
