"""P03 expanded-regex robustness — repo-only check (I3 mitigation).

Re-runs P03 with a broader regex covering 'PCR-confirmed', 'PCR-distinguished',
'genotyping-corrected', 'parasitologically corrected'. Reports both production
and expanded numbers in the same CSV so a reviewer can quantify the lower-bound
gap.

Not in the paper body. The paper's headline-as-lower-bound framing already
covers this.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import duckdb
import pandas as pd

from malaria_ct_recon import aact, config
from malaria_ct_recon import corpus as corpus_mod
from malaria_ct_recon.corpus import Corpus
from pilots import p03_pcr_corrected as p03prod

_PCR_EXPANDED_RX = re.compile(
    r"PCR-corrected|PCR\s*adjusted|PCR-adjusted|genotypically.corrected|"
    r"genotype-corrected|molecularly.corrected|"
    r"PCR-confirmed|PCR\s*confirmed|PCR-distinguished|"
    r"genotyping-corrected|parasitologically.corrected",
    re.IGNORECASE,
)
_PCR_NEG_RX = re.compile(r"PCR-uncorrected|PCR\s*uncorrected", re.IGNORECASE)


def _is_pcr_corrected_expanded(measure: str) -> bool:
    """Check if a measure is PCR-corrected using the expanded pattern.

    Returns False if PCR-uncorrected is mentioned, True if expanded PCR pattern found.
    """
    measure = measure or ""
    if _PCR_NEG_RX.search(measure):
        return False
    return bool(_PCR_EXPANDED_RX.search(measure))


def _count(
    con: duckdb.DuckDBPyConnection, corpus: Corpus, predicate: Callable[[str], bool]
) -> tuple[int, int]:
    """Count trials with PCR-corrected outcomes using a predicate function.

    Returns (k, n) where k = trials with matching outcome, n = total drug trials.
    """
    interventions = aact.table(con, "interventions")
    design_outcomes = aact.table(con, "design_outcomes")

    # Step 1: Identify drug-only efficacy trials
    in_corpus = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()

    drug_trials: set[str] = set()
    for nct_id in in_corpus["nct_id"].unique():
        row_group = in_corpus[in_corpus["nct_id"] == nct_id]
        has_drug = any(
            str(t).upper() == "DRUG" for t in row_group["intervention_type"].astype(str)
        )
        names_list = row_group["name"].astype(str).tolist()
        has_vaccine = any(p03prod._VACCINE_RX.search(n) for n in names_list)

        if has_drug and not has_vaccine:
            drug_trials.add(str(nct_id))

    # Step 2: Find primary outcomes in drug trials
    do = design_outcomes[design_outcomes["nct_id"].astype(str).isin(drug_trials)].copy()
    primary = do[do["outcome_type"].astype(str).str.lower() == "primary"].copy()

    # Step 3: Drop PK-only outcomes
    primary = primary[
        ~primary["measure"].astype(str).map(lambda m: bool(p03prod._PK_RX.search(m)))
    ].copy()

    # Step 4: Check for PCR-corrected primary outcomes per trial
    by_trial = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(predicate(m) for m in s.astype(str))
    )
    return int(by_trial.sum()), int(len(by_trial))


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    """Run expanded-regex check, return DataFrame with production and expanded rows."""
    rows = []
    for label, pred in (
        ("production", p03prod._is_pcr_corrected),
        ("expanded", _is_pcr_corrected_expanded),
    ):
        k, n = _count(con, corpus, pred)
        rows.append(
            {
                "variant": label,
                "n": n,
                "k": k,
                "rate": (k / n) if n > 0 else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    """Run expanded-regex check on real AACT and write results."""
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    df = run(con=con, corpus=c)
    out = Path("pilots/results/p03_expanded_regex.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    by_variant = {row["variant"]: row for _, row in df.iterrows()}
    if "production" not in by_variant or "expanded" not in by_variant:
        raise ValueError("p03_expanded_regex.run() produced unexpected empty DataFrame")
    prod = by_variant["production"]
    expd = by_variant["expanded"]
    delta_pp = (expd["rate"] - prod["rate"]) * 100
    print(
        f"p03_expanded_regex OK: production={prod['rate']:.4f} ({prod['k']}/{prod['n']}), "
        f"expanded={expd['rate']:.4f} ({expd['k']}/{expd['n']}), "
        f"delta_pp={delta_pp:+.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
