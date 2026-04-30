"""Pilot P09 — Geographic transmission heterogeneity (tractability probe).

AACT records site countries but NOT transmission intensity (PfPR). PfPR varies
by 2 orders of magnitude across endemic countries. The MAP project
(https://malariaatlas.org) publishes per-pixel rasters but those are external
to AACT. This pilot reports country distribution + flags the data gap.
"""
from __future__ import annotations

import hashlib
import time
from collections import Counter
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P09"
PILOT_TITLE = "Geographic transmission heterogeneity"
SCRIPT_PATH = "pilots/p09_geographic.py"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    t0 = time.perf_counter()
    countries = aact.table(con, "countries")

    # Filter to trials in corpus
    in_corpus = countries[countries["nct_id"].astype(str).isin(corpus.included)]

    # Count countries per trial
    by_country = Counter(in_corpus["name"].astype(str))
    top10 = dict(by_country.most_common(10))

    # Count multi-country trials
    multi_country = in_corpus.groupby("nct_id")["name"].nunique()
    multi_country_count = int((multi_country >= 2).sum())

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="tractability_probe",
        n_trials_in_scope=int(len(corpus.included)),
        magnitude_value=float("nan"),
        magnitude_unit="",
        magnitude_ci_low=float("nan"),
        magnitude_ci_high=float("nan"),
        tractability_AACT_only="none",
        # follow_up_potential=2: an atlas requires MAP project per-pixel rasters
        # outside AACT scope.
        follow_up_potential=2,
        n_trials_excluded_for_reason={},
        notes=f"top10_countries={top10}; multi_country_trials={multi_country_count}; "
              f"PfPR/transmission-intensity not in AACT — needs MAP project rasters "
              f"(https://malariaatlas.org)",
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
    schema.write([result], Path("pilots/results/p09.csv"))
    print(f"P09 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
