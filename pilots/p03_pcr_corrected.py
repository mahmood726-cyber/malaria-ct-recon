"""Pilot P03 — PCR-corrected outcome reporting.

Question: Of efficacy trials of antimalarial drugs, what fraction declare a
PCR-corrected primary outcome (distinguishes recrudescence from reinfection)?
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

PILOT_ID = "P03"
PILOT_TITLE = "PCR-corrected outcome reporting"
SCRIPT_PATH = "pilots/p03_pcr_corrected.py"

_PCR_RX = re.compile(
    r"PCR-corrected|PCR\s*adjusted|PCR-adjusted|genotypically.corrected|"
    r"genotype-corrected|molecularly.corrected",
    re.IGNORECASE,
)
_PCR_NEG_RX = re.compile(r"PCR-uncorrected|PCR\s*uncorrected", re.IGNORECASE)
_VACCINE_RX = re.compile(r"vaccine|RTS,S|R21|PfSPZ|sporozoite|CSP|MSP|AMA1", re.IGNORECASE)
_PK_RX = re.compile(r"pharmacokinetic|AUC|Cmax|drug concentration", re.IGNORECASE)


def _is_pcr_corrected(measure: str) -> bool:
    """Check if a measure is PCR-corrected.

    Returns False if PCR-uncorrected is mentioned, True if PCR-corrected pattern found.
    """
    measure = measure or ""
    if _PCR_NEG_RX.search(measure):
        return False
    return bool(_PCR_RX.search(measure))


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    t0 = time.perf_counter()
    interventions = aact.table(con, "interventions")
    design_outcomes = aact.table(con, "design_outcomes")

    # Step 1: Identify drug-only efficacy trials
    # Filter interventions to corpus trials
    in_corpus = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()

    # Group by trial and check: has DRUG intervention AND no vaccine in any intervention name
    by_trial = in_corpus.groupby("nct_id").agg({
        "intervention_type": "first",  # for filtering
        "name": lambda names: names.tolist(),  # collect all names
    })

    # A trial is drug-efficacy if:
    # - it has at least one DRUG intervention type
    # - none of its intervention names match vaccine patterns
    drug_trials = set()
    for nct_id in by_trial.index:
        row = by_trial.loc[nct_id]
        has_drug = any(
            str(t).upper() == "DRUG"
            for t in in_corpus[in_corpus["nct_id"] == nct_id]["intervention_type"].astype(str)
        )
        names_list = in_corpus[in_corpus["nct_id"] == nct_id]["name"].astype(str).tolist()
        has_vaccine = any(_VACCINE_RX.search(n) for n in names_list)

        if has_drug and not has_vaccine:
            drug_trials.add(nct_id)

    # Step 2: Find primary outcomes in drug trials
    do = design_outcomes[design_outcomes["nct_id"].astype(str).isin(drug_trials)].copy()
    primary = do[do["outcome_type"].astype(str).str.lower() == "primary"].copy()

    # Step 3: Drop PK-only outcomes
    primary = primary[
        ~primary["measure"].astype(str).map(lambda m: bool(_PK_RX.search(m)))
    ].copy()

    # Step 4: Check for PCR-corrected primary outcomes per trial
    by_trial_pcr = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(_is_pcr_corrected(m) for m in s.astype(str))
    )

    n = len(by_trial_pcr)
    k = int(by_trial_pcr.sum())

    if n == 0:
        magnitude, ci_low, ci_high = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        ci_low, ci_high = stats.wilson_ci(k, n)

    excluded = {
        "vaccine_or_no_drug": int(len(corpus.included) - len(drug_trials)),
        "no_primary_outcome": int(len(drug_trials) - n),
    }

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction",
        magnitude_ci_low=float(ci_low),
        magnitude_ci_high=float(ci_high),
        tractability_AACT_only="full",
        follow_up_potential=5,
        n_trials_excluded_for_reason=excluded,
        notes=f"{k}/{n} drug-efficacy trials report a PCR-corrected primary outcome",
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
    schema.write([result], Path("pilots/results/p03.csv"))
    print(f"P03 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
