"""Pilot P02 — Endpoint-family chaos.

Question: Of malaria trials with >=2 outcomes (any type), what fraction span
distinct endpoint families?
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

PILOT_ID = "P02"
PILOT_TITLE = "Endpoint-family chaos"
SCRIPT_PATH = "pilots/p02_endpoint_chaos.py"

# Family classifiers ordered by specificity:
# vaccine_VE first (catches "Time to ... parasitemia ... challenge" before
# the parasitological regex would match "parasitemia"), then transmission,
# severe, PK, parasitological, clinical.
_FAMILY_PATTERNS = [
    ("vaccine_VE", re.compile(r"vaccine efficacy|protective efficacy|time to.*parasitemia.*challenge|sporozoite challenge", re.I)),
    ("transmission", re.compile(r"gametocyte|mosquito infectivity|transmission|infectivity to mosquito", re.I)),
    ("severe", re.compile(r"severe malaria|cerebral malaria|mortality|death", re.I)),
    ("PK", re.compile(r"pharmacokinetic|AUC|Cmax|clearance.*plasma|drug concentration", re.I)),
    ("parasitological", re.compile(r"\bACPR\b|adequate clinical and parasitological response|PCR-corrected|parasitaem|parasitem|parasite clearance|recrudescence|recurrent parasit", re.I)),
    ("clinical", re.compile(r"clinical malaria|fever clearance|incidence of clinical|symptomatic malaria episode", re.I)),
]


def _classify(measure: str) -> str:
    for fam, rx in _FAMILY_PATTERNS:
        if rx.search(measure or ""):
            return fam
    return "other"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    t0 = time.perf_counter()
    do = aact.table(con, "design_outcomes")
    do = do[do["nct_id"].astype(str).isin(corpus.included)].copy()
    do["family"] = do["measure"].astype(str).map(_classify)

    by_trial = do.groupby("nct_id")["family"].apply(lambda s: set(s) - {"other"})
    by_trial = by_trial[by_trial.map(len) >= 1]  # exclude trials with only "other"
    n = len(by_trial)
    mixed = (by_trial.map(len) >= 2).sum()

    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = mixed / n
        lo, hi = stats.wilson_ci(int(mixed), int(n))

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction",
        magnitude_ci_low=float(lo),
        magnitude_ci_high=float(hi),
        tractability_AACT_only="full",
        follow_up_potential=5,
        n_trials_excluded_for_reason={"only_other_family": int(len(do["nct_id"].unique()) - n)},
        notes=f"{int(mixed)}/{n} malaria trials span >=2 endpoint families",
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
        schema.write([result], Path("pilots/results/p02.csv"))
        print(f"P02 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
