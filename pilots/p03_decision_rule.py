"""§4 decision-rule applicator — locks the body sentence variant deterministically.

Reads the P03 sensitivity CSV; computes the pre-/post-mandate rates within the
uncomplicated-falciparum subset; applies the decision rule; emits a JSON report
that the markdown draft (paper/methods-note-draft.md) consumes.

This is the integrity move: the body sentence is now a function of the data,
not the writer's interpretation.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PERSIST_SENTENCE = (
    "the decline is not solely a portfolio-shift artefact: it persists within "
    "the uncomplicated-falciparum subset where PCR-correction is unambiguously relevant."
)
ATTENUATE_SENTENCE = (
    "within the uncomplicated-falciparum subset the same direction holds but the "
    "small pre-mandate sample renders the within-subset trend inconclusive."
)
# Note: spec §4 originally said "flat at ~5% throughout"; we drop the speculative
# "~5%" because the body_sentence is consumed verbatim by T12, and a hardcoded
# rate would contradict Figure D if DISAPPEAR ever fires with a different rate.
# DISAPPEAR did not fire on the AACT 2026-04-12 data (band=attenuates), so this
# is currently moot, but the documented divergence preserves the integrity claim.
# v0.1.3: ATTENUATE_SENTENCE rewritten to drop the unsupported "persists" claim
# (Fisher p=0.06 in the n_pre=27 subset; CIs overlap). See review-findings.md P0-3.
DISAPPEAR_SENTENCE = (
    "the apparent decline is largely explained by portfolio shift; within indications "
    "where PCR-correction applies, compliance has been flat throughout."
)

SMALL_N_THRESHOLD = 50  # pre-mandate sample below this triggers the safety net


def apply(*, pre_rate: float, post_rate: float, pre_n: int, post_n: int) -> dict:
    """Apply the decision rule to determine the body sentence variant.

    Args:
        pre_rate: failure rate before the mandate.
        post_rate: failure rate after the mandate.
        pre_n: sample size before the mandate.
        post_n: sample size after the mandate.

    Returns:
        A dict with keys:
        - band: one of "persists", "attenuates", "disappears"
        - delta_pp: absolute change in percentage points
        - pre_rate: input pre-mandate rate
        - post_rate: input post-mandate rate
        - pre_n: input pre-mandate sample size
        - post_n: input post-mandate sample size
        - body_sentence: the locked body sentence variant
        - notes: optional interpretation notes
    """
    delta_pp = (post_rate - pre_rate) * 100.0
    notes = ""
    if pre_n < SMALL_N_THRESHOLD:
        band = "attenuates"
        sentence = ATTENUATE_SENTENCE
        notes = (
            f"small pre-mandate sample (n={pre_n} < {SMALL_N_THRESHOLD}); "
            "decision rule defaulted to 'attenuates' as the conservative interpretation."
        )
    elif delta_pp <= -2.0:
        band = "persists"
        sentence = PERSIST_SENTENCE
    elif delta_pp < 0.0:
        band = "attenuates"
        sentence = ATTENUATE_SENTENCE
    else:
        band = "disappears"
        sentence = DISAPPEAR_SENTENCE
    return {
        "band": band,
        "delta_pp": delta_pp,
        "pre_rate": pre_rate,
        "post_rate": post_rate,
        "pre_n": pre_n,
        "post_n": post_n,
        "body_sentence": sentence,
        "notes": notes,
    }


def from_csv(csv_path: Path, out_path: Path, mandate_year: int = 2009) -> dict:
    """Read the sensitivity CSV and apply the decision rule.

    Args:
        csv_path: path to the sensitivity CSV.
        out_path: path to write the decision JSON.
        mandate_year: the year the mandate took effect (default 2009 — WHO
            *Methods for Surveillance of Antimalarial Drug Efficacy*; this
            replaces the OTS-anchored §4 spec value of 2008. Divergence
            documented in outputs/extraction_audit.md.

    Returns:
        The decision rule payload dict.

    Raises:
        ValueError: if the post-mandate bucket is empty (no data >= mandate_year).
    """
    df = pd.read_csv(csv_path)
    pre = df[df["year"] < mandate_year]
    post = df[df["year"] >= mandate_year]
    pre_n, pre_k = int(pre["n"].sum()), int(pre["k"].sum())
    post_n, post_k = int(post["n"].sum()), int(post["k"].sum())
    if post_n == 0:
        raise ValueError("post-mandate bucket is empty; cannot apply decision rule")
    pre_rate = (pre_k / pre_n) if pre_n > 0 else 0.0
    post_rate = (post_k / post_n) if post_n > 0 else 0.0
    payload = apply(pre_rate=pre_rate, post_rate=post_rate, pre_n=pre_n, post_n=post_n)
    payload["mandate_year"] = mandate_year
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    """Read real sensitivity output and apply decision rule."""
    payload = from_csv(
        Path("pilots/results/p03_sensitivity.csv"),
        Path("pilots/results/decision_rule.json"),
        mandate_year=2009,
    )
    print(f"decision_rule OK: band={payload['band']}, delta={payload['delta_pp']:+.2f}pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
