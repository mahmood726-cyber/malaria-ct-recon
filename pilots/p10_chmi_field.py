"""Pilot P10 — CHMI vs field-trial mixing.

Of malaria-vaccine trials, what fraction are Controlled Human Malaria Infection
(CHMI) studies? CHMI uses a different efficacy endpoint (time to parasitemia
after sporozoite challenge) than field trials. Pooling CHMI + field VE estimates
without stratification conflates endpoint types.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P10"
PILOT_TITLE = "CHMI vs field-trial mixing"
SCRIPT_PATH = "pilots/p10_chmi_field.py"

_VACCINE_RX = re.compile(
    r"vaccine|RTS,S|R21|PfSPZ|sporozoite|CSP|MSP|AMA1|Mosquirix", re.IGNORECASE
)
_CHMI_RX = re.compile(
    r"sporozoite challenge|controlled human malaria infection|CHMI|"
    r"non-immune.*challenge|PfSPZ Challenge|infection model",
    re.IGNORECASE,
)


def _is_chmi(intervention_name: str, eligibility_criteria: str) -> bool:
    """Check if a trial is CHMI based on intervention name and eligibility criteria."""
    blob = f"{intervention_name or ''} {eligibility_criteria or ''}"
    return bool(_CHMI_RX.search(blob))


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
    elig = aact.table(con, "eligibilities")

    # Filter interventions to trials in corpus
    iv = interventions[interventions["nct_id"].astype(str).isin(corpus.included)]

    # Identify vaccine trials
    vaccine_trials = iv[
        iv["name"].astype(str).map(lambda n: bool(_VACCINE_RX.search(n)))
    ]
    vaccine_nct = set(vaccine_trials["nct_id"].astype(str).unique())

    # Merge with eligibility criteria and identify CHMI
    blob = vaccine_trials.merge(
        elig[["nct_id", "criteria"]], on="nct_id", how="left"
    )

    # Build a dict of nct_id -> is_chmi
    chmi_dict = {}
    for nct_id in vaccine_nct:
        group = blob[blob["nct_id"] == nct_id]
        is_chmi = any(
            _is_chmi(n, c)
            for n, c in zip(
                group["name"].astype(str), group["criteria"].fillna("").astype(str)
            )
        )
        chmi_dict[nct_id] = is_chmi

    chmi_count = sum(1 for v in chmi_dict.values() if v)

    n = int(len(vaccine_nct))
    k = int(chmi_count)
    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(k, n)

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction_of_vaccine_trials_chmi",
        magnitude_ci_low=float(lo),
        magnitude_ci_high=float(hi),
        tractability_AACT_only="full",
        # follow_up_potential=4: real risk for malaria-vaccine MAs that pool
        # CHMI + field VE estimates without distinguishing endpoints.
        follow_up_potential=4,
        n_trials_excluded_for_reason={"non_vaccine": int(len(corpus.included) - n)},
        notes=f"{k}/{n} malaria-vaccine trials are CHMI",
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
        schema.write([result], Path("pilots/results/p10.csv"))
        print(f"P10 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
