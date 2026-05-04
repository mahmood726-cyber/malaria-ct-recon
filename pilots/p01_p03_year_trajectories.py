"""Year-binned trajectories for P01 and P03, using EXACT production pilot logic.

This is the data source for Figure D. It must agree with the P01 and P03
production pilots when aggregated; we re-use their internal logic here so
there is one source of truth.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, config
from malaria_ct_recon import corpus as corpus_mod
from malaria_ct_recon.corpus import Corpus
from pilots.p03_pcr_corrected import (
    _VACCINE_RX, _PK_RX, _VECTOR_CONTROL_RX, _is_pcr_corrected,
)


def _p01_per_trial(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    """Per-trial P01 status: (nct_id, year, reported_le12)."""
    studies = aact.table(con, "studies")
    cv = aact.table(con, "calculated_values")
    in_corpus = studies[studies["nct_id"].astype(str).isin(corpus.included)]
    completed = in_corpus[in_corpus["overall_status"].astype(str) == "COMPLETED"].copy()
    completed["primary_completion_date"] = pd.to_datetime(
        completed["primary_completion_date"], errors="coerce"
    )
    completed["year"] = completed["primary_completion_date"].dt.year
    m = completed.merge(cv, on="nct_id", how="left")
    m["reported_le12"] = (
        m["were_results_reported"].fillna(False).astype(bool)
        & (pd.to_numeric(m["months_to_report_results"], errors="coerce") <= 12)
    )
    return m[["nct_id", "year", "reported_le12"]].dropna(subset=["year"]).copy()


def _p03_per_trial(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    """Per-trial P03 status: (nct_id, year, pcr_corrected).

    Re-uses the production P03 drug-only filter and PCR pattern, then attaches
    the primary completion year.
    """
    interventions = aact.table(con, "interventions")
    design_outcomes = aact.table(con, "design_outcomes")
    studies = aact.table(con, "studies")

    in_corpus = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()
    drug_trials: set[str] = set()
    for nct_id, group in in_corpus.groupby("nct_id"):
        has_drug = any(str(t).upper() == "DRUG" for t in group["intervention_type"].astype(str))
        names = group["name"].astype(str).tolist()
        has_vaccine = any(_VACCINE_RX.search(n) for n in names)
        has_vector = any(_VECTOR_CONTROL_RX.search(n) for n in names)
        if has_drug and not has_vaccine and not has_vector:
            drug_trials.add(str(nct_id))

    do = design_outcomes[design_outcomes["nct_id"].astype(str).isin(drug_trials)].copy()
    primary = do[do["outcome_type"].astype(str).str.lower() == "primary"].copy()
    primary = primary[
        ~primary["measure"].astype(str).map(lambda m: bool(_PK_RX.search(m)))
    ].copy()

    by_trial = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(_is_pcr_corrected(m) for m in s.astype(str))
    ).rename("pcr_corrected").reset_index()

    s = studies[studies["nct_id"].astype(str).isin(drug_trials)].copy()
    s["primary_completion_date"] = pd.to_datetime(
        s["primary_completion_date"], errors="coerce"
    )
    s["year"] = s["primary_completion_date"].dt.year
    s = s[["nct_id", "year"]].dropna(subset=["year"])

    return by_trial.merge(s, on="nct_id", how="inner")[["nct_id", "year", "pcr_corrected"]].copy()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    p01_df = _p01_per_trial(con, corpus)
    p03_df = _p03_per_trial(con, corpus)

    p01_g = p01_df.groupby("year").agg(
        n_p01=("nct_id", "count"),
        k_p01=("reported_le12", "sum"),
    )
    p03_g = p03_df.groupby("year").agg(
        n_p03=("nct_id", "count"),
        k_p03=("pcr_corrected", "sum"),
    )
    df = p01_g.join(p03_g, how="outer").fillna(0).astype(
        {"n_p01": int, "k_p01": int, "n_p03": int, "k_p03": int}
    )

    df["rate_p01"] = df.apply(
        lambda r: (r["k_p01"] / r["n_p01"]) if r["n_p01"] > 0 else float("nan"), axis=1
    )
    df["rate_p03"] = df.apply(
        lambda r: (r["k_p03"] / r["n_p03"]) if r["n_p03"] > 0 else float("nan"), axis=1
    )
    df = df.reset_index()
    df["year"] = df["year"].astype(int)
    return df.sort_values("year").reset_index(drop=True)


def main() -> int:
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    df = run(con=con, corpus=c)
    out = Path("pilots/results/year_trajectories.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"year_trajectories OK: rows={len(df)}, years {df['year'].min()}-{df['year'].max()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
