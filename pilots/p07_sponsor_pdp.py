"""Pilot P07 — Sponsor PDP misclassification.

Question: What fraction of malaria trials have a Product Development Partnership (PDP) sponsor
(MMV, PATH MVI, FIND, DNDi, Aeras, IVI, EVI, MVRC) that AACT classifies as "OTHER" rather
than its own category?

This identifies cases where PDP sponsors are misclassified in AACT's agency_class field,
which affects downstream analyses that stratify by sponsor type.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P07"
PILOT_TITLE = "Sponsor PDP misclassified as OTHER"
SCRIPT_PATH = "pilots/p07_sponsor_pdp.py"

_PDP_RX = re.compile(
    r"medicines for malaria venture|"
    r"\bMMV\b|"
    r"PATH malaria vaccine initiative|"
    r"\bMVI\b|"
    r"\bFIND\b|"
    r"\bDNDi\b|"
    r"drugs? for neglected diseases|"
    r"aeras global tb vaccine|"
    r"\baeras\b|"
    r"international vaccine institute|"
    r"\bIVI\b|"
    r"european vaccine initiative|"
    r"\bEVI\b|"
    r"malaria vaccine research center|"
    r"\bMVRC\b",
    re.IGNORECASE,
)


def _is_pdp(name: str | None) -> bool:
    """Check if a sponsor name matches a known PDP organization.

    Args:
        name: Sponsor name to check (may be None)

    Returns:
        True if the name matches a PDP pattern, False otherwise
    """
    if name is None or name == "":
        return False
    return bool(_PDP_RX.search(str(name)))


def _sha256_self() -> str:
    """Return the SHA256 hash of this file's contents."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    """Run P07 sponsor PDP misclassification pilot.

    Identifies malaria trials in the corpus that have a PDP sponsor but are
    misclassified as "OTHER" in AACT's agency_class field.

    Args:
        con: DuckDB connection to AACT snapshot
        corpus: Corpus of included trials (by NCT ID)
        aact_snapshot: Label for the AACT snapshot (for metadata)
        seed: Random seed (unused for this deterministic analysis)

    Returns:
        PilotResult with pilot_type="magnitude" reporting the fraction of
        trials with PDP sponsors that are misclassified as OTHER
    """
    t0 = time.perf_counter()

    # Load sponsors table
    sp = aact.table(con, "sponsors")

    # Filter to corpus trials with lead sponsors
    sp = sp[
        (sp["nct_id"].astype(str).isin(corpus.included))
        & (sp["lead_or_collaborator"].astype(str) == "lead")
    ].copy()

    # Identify PDP sponsors
    sp["is_pdp"] = sp["name"].astype(str).apply(_is_pdp)

    # Normalize agency_class to uppercase for comparison
    sp["agency_class"] = sp["agency_class"].astype(str).str.upper()

    # Count all lead-sponsored trials in corpus
    n = len(sp)

    # Identify PDP sponsors misclassified as OTHER
    pdp_trials = sp[sp["is_pdp"]]
    misclassified = pdp_trials[pdp_trials["agency_class"] == "OTHER"]
    k = len(misclassified)

    # Compute Wilson CI
    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(int(k), int(n))

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction_of_lead_sponsored_trials",
        magnitude_ci_low=float(lo),
        magnitude_ci_high=float(hi),
        tractability_AACT_only="full",
        # follow_up_potential=3: real but lower-priority finding;
        # PDP misclassification affects funding-class analysis but doesn't
        # directly bias clinical effect estimates.
        follow_up_potential=3,
        n_trials_excluded_for_reason={
            "no_lead_sponsor_row": int(len(corpus.included) - sp["nct_id"].nunique())
        },
        notes=f"{k}/{n} lead-sponsored trials have PDP sponsor classified as OTHER",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    """Run P07 against the configured AACT snapshot."""
    from malaria_ct_recon import config, corpus as corpus_mod

    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p07.csv"))
    print(f"P07 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
