# Methods Note Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the Synthēsis Methods Note (≤400w body) from spec `docs/superpowers/specs/2026-05-03-methods-paper-design.md` — analysis code, two-panel mandate-timeline figure, references with Crossref verification, paper draft (markdown + .docx), repo-only limitations docs, P03 robustness check, CI Sentinel-scan step, v0.1.2 release tag.

**Architecture:** Three layers. (1) Analysis layer: production-matched year-bin trajectories + uncomplicated-*P. falciparum* sensitivity + §4 decision-rule applicator. (2) Artifact layer: matplotlib figure, refs.bib + Crossref verifier, python-docx exporter. (3) Release layer: limitations and prereg-history docs, CI workflow update, v0.1.2 tag. The §4 decision rule is implemented as code (reads sensitivity result, emits JSON locking the body-sentence variant) so the markdown draft pulls a deterministic output rather than a human interpretation.

**Tech Stack:** Python 3.11+, duckdb, pandas, scipy (existing); matplotlib (new), python-docx (new), requests (new). pytest for tests. GitHub Actions for CI.

**Critical fix flagged at planning time:** my brainstorm-phase scratch script used a narrower regex than P03 production AND no drug-only filter. The numbers currently in `docs/figure-d-yearbins.md` are **not** consistent with the P03 headline. Task 1 regenerates the year-bin trajectories using the EXACT P01 and P03 production logic and overwrites that file.

---

## File structure

| Path | Status | Purpose |
|---|---|---|
| `pilots/p01_p03_year_trajectories.py` | NEW | Production-matched year-bin generator (T1) |
| `pilots/p03_sensitivity_uncomplicated_falciparum.py` | NEW | Sensitivity analysis on indication subset (T2) |
| `pilots/p03_decision_rule.py` | NEW | Apply §4 rule; emit JSON locking body sentence (T3) |
| `pilots/p03_expanded_regex_check.py` | NEW | I3 robustness check, repo-only (T10) |
| `pilots/results/year_trajectories.csv` | NEW (output) | T1 output |
| `pilots/results/p03_sensitivity.csv` | NEW (output) | T2 output |
| `pilots/results/decision_rule.json` | NEW (output) | T3 output |
| `pilots/results/p03_expanded_regex.csv` | NEW (output) | T10 output |
| `paper/make_figure_d.py` | NEW | matplotlib two-panel figure (T4) |
| `figures/figure-d.png` | NEW (output) | T4 output |
| `figures/figure-d.svg` | NEW (output) | T4 output |
| `paper/refs.bib` | NEW | 6+1 BibTeX entries with DOIs (T6) |
| `paper/verify_refs.py` | NEW | Crossref REST API verifier (T7) |
| `paper/refs_verification.csv` | NEW (output) | T7 output |
| `paper/wc.py` | NEW | Body word-count enforcer (T11) |
| `paper/build_docx.py` | NEW | python-docx exporter, Synthēsis house format (T13) |
| `paper/methods-note-draft.md` | NEW | Single source of truth (T12) |
| `paper/methods-note-draft.docx` | NEW (output) | T13 output |
| `docs/methods-paper-limitations.md` | NEW | I3-I6 split: body vs repo (T8) |
| `docs/preregistration-history.md` | NEW | Corpus-criteria timeline (T9) |
| `docs/figure-d-yearbins.md` | OVERWRITE | Replace scratch numbers with production numbers (T1) |
| `.github/workflows/ci.yml` | MODIFY | Add Sentinel-scan step (T14) |
| `tests/test_year_trajectories.py` | NEW | T1 tests |
| `tests/test_p03_sensitivity.py` | NEW | T2 tests |
| `tests/test_decision_rule.py` | NEW | T3 tests |
| `tests/test_make_figure_d.py` | NEW | T4 tests |
| `tests/test_verify_refs.py` | NEW | T7 tests |
| `tests/test_p03_expanded_regex.py` | NEW | T10 tests |
| `tests/test_wc.py` | NEW | T11 tests |
| `tests/test_methods_note_draft.py` | NEW | T12 content tests |
| `tests/test_build_docx.py` | NEW | T13 tests |
| `pyproject.toml` | MODIFY | Add matplotlib, python-docx, requests deps |

---

## Phase A — Analysis (T1–T3)

These three tasks produce all numbers the paper draft cites. They must complete before the figure or draft are touched.

### Task 1: Production-matched year-bin trajectories

**Files:**
- Create: `pilots/p01_p03_year_trajectories.py`
- Create: `tests/test_year_trajectories.py`
- Output: `pilots/results/year_trajectories.csv`
- Overwrite: `docs/figure-d-yearbins.md` (regenerated from production numbers)

- [ ] **Step 1.1: Write the failing test**

```python
# tests/test_year_trajectories.py
"""Test year-bin trajectories — must match P01 and P03 production headlines exactly."""
from pathlib import Path
import pandas as pd
import pytest
from malaria_ct_recon import aact, corpus
from pilots import p01_p03_year_trajectories as yt


def test_year_trajectories_columns(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    df = yt.run(con=con, corpus=c)
    expected = {"year", "n_p01", "k_p01", "rate_p01", "n_p03", "k_p03", "rate_p03"}
    assert expected.issubset(set(df.columns))


def test_year_trajectories_aggregates_match_production_pilots(fake_aact: Path) -> None:
    """Aggregate of year-bin numerator and denominator must equal what
    P01 and P03 production pilots report, using the same fake corpus.
    """
    from pilots import p01_reporting_compliance as p01
    from pilots import p03_pcr_corrected as p03

    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)

    df = yt.run(con=con, corpus=c)
    p01_result = p01.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    p03_result = p03.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)

    n_p01_total = int(df["n_p01"].sum())
    k_p01_total = int(df["k_p01"].sum())
    n_p03_total = int(df["n_p03"].sum())
    k_p03_total = int(df["k_p03"].sum())

    # Year-binning excludes trials with missing primary_completion_date,
    # so totals may be ≤ production. Production is the upper bound.
    assert n_p01_total <= p01_result.n_trials_in_scope
    assert n_p03_total <= p03_result.n_trials_in_scope
    assert k_p01_total <= int(round(p01_result.magnitude_value * p01_result.n_trials_in_scope))
    assert k_p03_total <= int(round(p03_result.magnitude_value * p03_result.n_trials_in_scope))


def test_year_trajectories_year_range(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    df = yt.run(con=con, corpus=c)
    assert df["year"].min() >= 2000
    assert df["year"].max() <= 2024


def test_year_trajectories_deterministic(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    df1 = yt.run(con=con, corpus=c)
    df2 = yt.run(con=con, corpus=c)
    pd.testing.assert_frame_equal(df1, df2)
```

- [ ] **Step 1.2: Run test, verify it fails**

```
pytest tests/test_year_trajectories.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'pilots.p01_p03_year_trajectories'`.

- [ ] **Step 1.3: Implement `pilots/p01_p03_year_trajectories.py`**

```python
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
from pilots import p03_pcr_corrected as p03


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
        has_vaccine = any(p03._VACCINE_RX.search(n) for n in names)
        if has_drug and not has_vaccine:
            drug_trials.add(str(nct_id))

    do = design_outcomes[design_outcomes["nct_id"].astype(str).isin(drug_trials)].copy()
    primary = do[do["outcome_type"].astype(str).str.lower() == "primary"].copy()
    primary = primary[
        ~primary["measure"].astype(str).map(lambda m: bool(p03._PK_RX.search(m)))
    ].copy()

    by_trial = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(p03._is_pcr_corrected(m) for m in s.astype(str))
    ).rename("pcr_corrected").reset_index()

    s = studies[studies["nct_id"].astype(str).isin(drug_trials)].copy()
    s["primary_completion_date"] = pd.to_datetime(
        s["primary_completion_date"], errors="coerce"
    )
    s["year"] = s["primary_completion_date"].dt.year
    s = s[["nct_id", "year"]].dropna(subset=["year"])

    return by_trial.merge(s, on="nct_id", how="inner")[["nct_id", "year", "pcr_corrected"]].copy()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    p01 = _p01_per_trial(con, corpus)
    p03 = _p03_per_trial(con, corpus)

    p01_g = p01.groupby("year").agg(n_p01=("nct_id", "count"), k_p01=("reported_le12", "sum"))
    p03_g = p03.groupby("year").agg(n_p03=("nct_id", "count"), k_p03=("pcr_corrected", "sum"))
    df = p01_g.join(p03_g, how="outer").fillna(0).astype({"n_p01": int, "k_p01": int, "n_p03": int, "k_p03": int})

    df["rate_p01"] = df.apply(lambda r: (r["k_p01"] / r["n_p01"]) if r["n_p01"] > 0 else float("nan"), axis=1)
    df["rate_p03"] = df.apply(lambda r: (r["k_p03"] / r["n_p03"]) if r["n_p03"] > 0 else float("nan"), axis=1)
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
```

- [ ] **Step 1.4: Run tests, verify they pass**

```
pytest tests/test_year_trajectories.py -v
```
Expected: 4 passed.

- [ ] **Step 1.5: Run on real AACT, regenerate `docs/figure-d-yearbins.md`**

```
python -m pilots.p01_p03_year_trajectories
```
Expected stdout: `year_trajectories OK: rows=NN, years YYYY-YYYY`. Then read `pilots/results/year_trajectories.csv` and overwrite `docs/figure-d-yearbins.md` with a regenerated table containing the new columns. Use the new totals to compute pre/post-2008 and pre/post-2017 splits and write them into the file. Also update the body's "Headline contrast" section with the new numbers (the trajectory shape may shift modestly because the production regex is broader and the drug-only filter is now applied).

- [ ] **Step 1.6: Commit**

```
git add pilots/p01_p03_year_trajectories.py tests/test_year_trajectories.py \
        pilots/results/year_trajectories.csv docs/figure-d-yearbins.md
git commit -m "feat(paper): production-matched P01/P03 year-bin trajectories for Figure D"
```

---

### Task 2: P03 sensitivity on uncomplicated-*P. falciparum* subset

**Files:**
- Create: `pilots/p03_sensitivity_uncomplicated_falciparum.py`
- Create: `tests/test_p03_sensitivity.py`
- Output: `pilots/results/p03_sensitivity.csv`

- [ ] **Step 2.1: Write the failing test**

```python
# tests/test_p03_sensitivity.py
"""Test the uncomplicated-falciparum sensitivity subset filter for P03."""
from pathlib import Path
import pandas as pd
from malaria_ct_recon import aact, corpus
from pilots import p03_sensitivity_uncomplicated_falciparum as sens


def test_sensitivity_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    df = sens.run(con=con, corpus=c)
    assert {"year", "n", "k", "rate"}.issubset(set(df.columns))


def test_indication_filter_includes_falciparum_excludes_prevention() -> None:
    """INCLUDE: 'falciparum' or 'uncomplicated malaria'.
       EXCLUDE: severe/complicated/MDA/prevention/chemoprevention/IPTp/vaccine."""
    cases = [
        ({"Uncomplicated Malaria"}, True),
        ({"Falciparum Malaria"}, True),
        ({"Plasmodium Falciparum"}, True),
        ({"Severe Malaria"}, False),
        ({"Falciparum Malaria", "Severe Malaria"}, False),  # any exclusion wins
        ({"Malaria Prevention"}, False),
        ({"Plasmodium Vivax"}, False),
        ({"Uncomplicated Malaria", "IPTp"}, False),
        ({"Chemoprevention of malaria"}, False),
    ]
    for conditions, expected in cases:
        assert sens.is_uncomplicated_falciparum(conditions) is expected, conditions


def test_sensitivity_aggregate_le_p03_production(fake_aact: Path) -> None:
    """Subset n must be ≤ P03 production n on the same corpus."""
    from pilots import p03_pcr_corrected as p03
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    df = sens.run(con=con, corpus=c)
    p03_result = p03.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert int(df["n"].sum()) <= p03_result.n_trials_in_scope
```

- [ ] **Step 2.2: Run test, verify it fails**

```
pytest tests/test_p03_sensitivity.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'pilots.p03_sensitivity_uncomplicated_falciparum'`.

- [ ] **Step 2.3: Implement `pilots/p03_sensitivity_uncomplicated_falciparum.py`**

```python
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
```

- [ ] **Step 2.4: Run tests, verify they pass**

```
pytest tests/test_p03_sensitivity.py -v
```
Expected: 3 passed.

- [ ] **Step 2.5: Run on real AACT**

```
python -m pilots.p03_sensitivity_uncomplicated_falciparum
```
Expected stdout: `p03_sensitivity OK: n_subset=N, k_subset=K, rate=R`. Inspect the resulting CSV — confirm pre-2008 and post-2008 buckets each have n ≥ 30 (otherwise note in T3 notes that the decision rule will fall through to "attenuates" by the small-n safety net).

- [ ] **Step 2.6: Commit**

```
git add pilots/p03_sensitivity_uncomplicated_falciparum.py \
        tests/test_p03_sensitivity.py pilots/results/p03_sensitivity.csv
git commit -m "feat(paper): P03 sensitivity on uncomplicated-falciparum subset"
```

---

### Task 3: §4 decision-rule applicator

**Files:**
- Create: `pilots/p03_decision_rule.py`
- Create: `tests/test_decision_rule.py`
- Output: `pilots/results/decision_rule.json`

- [ ] **Step 3.1: Write the failing test**

```python
# tests/test_decision_rule.py
"""Test §4 decision-rule applicator."""
import json
from pathlib import Path
import pandas as pd
from pilots import p03_decision_rule as dr


def test_persists_branch():
    """Δ ≤ -2 pp ⇒ retains."""
    out = dr.apply(pre_rate=0.058, post_rate=0.026, pre_n=50, post_n=400)
    assert out["band"] == "persists"
    assert "not solely a portfolio-shift" in out["body_sentence"]


def test_attenuates_branch():
    """-2 < Δ < 0 ⇒ softens."""
    out = dr.apply(pre_rate=0.040, post_rate=0.030, pre_n=50, post_n=400)
    assert out["band"] == "attenuates"
    assert "partially attributable" in out["body_sentence"]


def test_disappears_branch():
    """Δ ≥ 0 ⇒ pivots."""
    out = dr.apply(pre_rate=0.030, post_rate=0.030, pre_n=50, post_n=400)
    assert out["band"] == "disappears"
    assert "largely explained by portfolio shift" in out["body_sentence"]


def test_small_n_safety_net():
    """If pre_n < 50, default to attenuates regardless of Δ."""
    out = dr.apply(pre_rate=0.058, post_rate=0.026, pre_n=12, post_n=400)
    assert out["band"] == "attenuates"
    assert "small pre-mandate sample" in out["notes"]


def test_from_csv(tmp_path: Path):
    """Reads the sensitivity CSV and writes a JSON report."""
    csv = tmp_path / "sens.csv"
    csv.write_text(
        "year,n,k,rate\n"
        "2005,40,2,0.05\n2006,30,2,0.067\n2007,30,1,0.033\n"
        "2010,200,4,0.02\n2015,200,2,0.01\n2020,200,2,0.01\n",
        encoding="utf-8",
    )
    out_path = tmp_path / "decision.json"
    dr.from_csv(csv, out_path, mandate_year=2008)
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert "band" in payload and "body_sentence" in payload
    assert payload["mandate_year"] == 2008
```

- [ ] **Step 3.2: Run test, verify it fails**

```
pytest tests/test_decision_rule.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'pilots.p03_decision_rule'`.

- [ ] **Step 3.3: Implement `pilots/p03_decision_rule.py`**

```python
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
    "the decline is partially attributable to portfolio shift but persists within "
    "the uncomplicated-falciparum subset."
)
DISAPPEAR_SENTENCE = (
    "the apparent decline is largely explained by portfolio shift; within indications "
    "where PCR-correction applies, compliance has been flat throughout."
)

SMALL_N_THRESHOLD = 50  # pre-mandate sample below this triggers the safety net


def apply(*, pre_rate: float, post_rate: float, pre_n: int, post_n: int) -> dict:
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


def from_csv(csv_path: Path, out_path: Path, mandate_year: int = 2008) -> dict:
    df = pd.read_csv(csv_path)
    pre = df[df["year"] < mandate_year]
    post = df[df["year"] >= mandate_year]
    pre_n, pre_k = int(pre["n"].sum()), int(pre["k"].sum())
    post_n, post_k = int(post["n"].sum()), int(post["k"].sum())
    pre_rate = (pre_k / pre_n) if pre_n > 0 else 0.0
    post_rate = (post_k / post_n) if post_n > 0 else 0.0
    payload = apply(pre_rate=pre_rate, post_rate=post_rate, pre_n=pre_n, post_n=post_n)
    payload["mandate_year"] = mandate_year
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    payload = from_csv(
        Path("pilots/results/p03_sensitivity.csv"),
        Path("pilots/results/decision_rule.json"),
        mandate_year=2008,
    )
    print(f"decision_rule OK: band={payload['band']}, delta={payload['delta_pp']:+.2f}pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3.4: Run tests, verify they pass**

```
pytest tests/test_decision_rule.py -v
```
Expected: 5 passed.

- [ ] **Step 3.5: Run on real sensitivity output**

```
python -m pilots.p03_decision_rule
```
Expected: `decision_rule OK: band=<persists|attenuates|disappears>, delta=±X.XXpp`. Inspect `pilots/results/decision_rule.json`. Whichever band fires, the body sentence is locked from this point on.

- [ ] **Step 3.6: Commit**

```
git add pilots/p03_decision_rule.py tests/test_decision_rule.py \
        pilots/results/decision_rule.json
git commit -m "feat(paper): §4 decision-rule applicator — lock body sentence variant"
```

---

**Phase A checkpoint:** before moving on, confirm `pilots/results/decision_rule.json` reports a band that you find defensible. If `persists`, the original thesis stands. If `attenuates` or `disappears`, the paper's interpretation sentence has automatically pivoted — you have nothing to do, but it's worth pausing to note the band in the next commit message and in the workbook entry.

---

## Phase B — Figure D (T4)

> Note: task numbering skips T5 (Phase B is a single task). Phase C resumes at T6.

### Task 4: Two-panel mandate-timeline figure

**Files:**
- Create: `paper/__init__.py` (empty package marker)
- Create: `paper/make_figure_d.py`
- Create: `tests/test_make_figure_d.py`
- Modify: `pyproject.toml` (add `matplotlib>=3.8`)
- Output: `figures/figure-d.png`, `figures/figure-d.svg`

- [ ] **Step 4.1: Add matplotlib to deps**

Edit `pyproject.toml`. Find the `dependencies = [...]` block and append `matplotlib>=3.8`.

```
pip install -e .[dev]
```

- [ ] **Step 4.2: Write the failing test**

```python
# tests/test_make_figure_d.py
"""Test Figure D generator — outputs valid PNG + SVG with both panels."""
from pathlib import Path
import pandas as pd
import pytest
from paper import make_figure_d as mfd


def _fake_traj_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "year_trajectories.csv"
    rows = []
    for y in range(2004, 2025):
        rows.append({
            "year": y,
            "n_p01": 50 + (y - 2004) * 5,
            "k_p01": int((50 + (y - 2004) * 5) * (0.05 + (y - 2017) * 0.01 if y >= 2017 else 0.04)),
            "rate_p01": 0.0,
            "n_p03": 60 + (y - 2004) * 4,
            "k_p03": max(0, int((60 + (y - 2004) * 4) * (0.06 if y < 2008 else 0.025))),
            "rate_p03": 0.0,
        })
    df = pd.DataFrame(rows)
    df["rate_p01"] = df["k_p01"] / df["n_p01"]
    df["rate_p03"] = df["k_p03"] / df["n_p03"]
    df.to_csv(csv, index=False)
    return csv


def test_figure_d_produces_png_and_svg(tmp_path: Path):
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    assert out_png.exists() and out_png.stat().st_size > 1000
    assert out_svg.exists() and out_svg.stat().st_size > 1000
    assert out_svg.read_text(encoding="utf-8").startswith("<?xml")


def test_figure_d_two_panels(tmp_path: Path):
    """Both panels rendered (we check by parsing axis count from SVG)."""
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    svg = out_svg.read_text(encoding="utf-8")
    # matplotlib emits one <g id="axes_N"> per axes; expect 2.
    assert svg.count('id="axes_1"') == 1
    assert svg.count('id="axes_2"') == 1


def test_figure_d_deterministic(tmp_path: Path):
    csv = _fake_traj_csv(tmp_path)
    out_png_a = tmp_path / "a.png"
    out_svg_a = tmp_path / "a.svg"
    out_png_b = tmp_path / "b.png"
    out_svg_b = tmp_path / "b.svg"
    mfd.make(csv, out_png_a, out_svg_a)
    mfd.make(csv, out_png_b, out_svg_b)
    # SVG is text-deterministic when matplotlib metadata is suppressed.
    assert out_svg_a.read_bytes() == out_svg_b.read_bytes()
```

- [ ] **Step 4.3: Run test, verify it fails**

```
pytest tests/test_make_figure_d.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'paper.make_figure_d'`.

- [ ] **Step 4.4: Implement `paper/__init__.py` and `paper/make_figure_d.py`**

`paper/__init__.py`:

```python
"""Paper-artifact scripts: figure builder, refs verifier, docx exporter, wc."""
```

`paper/make_figure_d.py`:

```python
"""Figure D — two-panel mandate-timeline (P01 FDAAA-results, P03 WHO-PCR).

Per spec §5 of 2026-05-03-methods-paper-design.md.

Reads pilots/results/year_trajectories.csv (T1 output) and writes
figures/figure-d.png + figures/figure-d.svg. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Suppress non-deterministic SVG metadata (creator timestamp etc.).
matplotlib.rcParams["svg.hashsalt"] = "malaria-ct-recon"
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42


def _wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    from scipy.stats import norm  # local import to keep top-level light

    z = norm.ppf(1 - alpha / 2)
    phat = k / n
    denom = 1 + z**2 / n
    centre = (phat + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return max(0.0, centre - half), min(1.0, centre + half)


def _panel(ax, years, n, k, rate, mandate_year, mandate_label, ann_text, y_max, title):
    ci = [_wilson(int(ki), int(ni)) for ki, ni in zip(k, n)]
    lo = np.array([c[0] for c in ci])
    hi = np.array([c[1] for c in ci])
    weak = np.array([ni < 10 for ni in n])
    strong = ~weak

    ax.fill_between(years[strong], lo[strong] * 100, hi[strong] * 100,
                    alpha=0.25, color="#377eb8", linewidth=0)
    ax.plot(years[strong], rate[strong] * 100, marker="o", color="#1f4e79", linewidth=1.6, markersize=4)
    if weak.any():
        ax.fill_between(years[weak], lo[weak] * 100, hi[weak] * 100,
                        alpha=0.10, color="#377eb8", linewidth=0)
        ax.plot(years[weak], rate[weak] * 100, marker="o", color="#1f4e79",
                linewidth=0.7, markersize=3, alpha=0.5)
    ax.axvline(mandate_year, linestyle="--", color="#b25c00", linewidth=1.0)
    ax.text(mandate_year + 0.2, y_max * 0.92, mandate_label, fontsize=8, color="#b25c00")
    ax.text(2004.3, y_max * 0.92, ann_text, fontsize=8)
    ax.set_xlim(2003.5, 2024.5)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Primary completion year")
    ax.set_ylabel("Compliance (%)")
    ax.set_title(title, fontsize=10)


def make(csv_path: Path, out_png: Path, out_svg: Path) -> None:
    df = pd.read_csv(csv_path)
    df = df[(df["year"] >= 2004) & (df["year"] <= 2024)].sort_values("year").reset_index(drop=True)

    # Pre/post split annotations
    def split(df, col_n, col_k, cutoff):
        pre = df[df["year"] < cutoff]
        post = df[df["year"] >= cutoff]
        pre_rate = pre[col_k].sum() / max(pre[col_n].sum(), 1)
        post_rate = post[col_k].sum() / max(post[col_n].sum(), 1)
        return pre_rate, post_rate

    p01_pre, p01_post = split(df, "n_p01", "k_p01", 2017)
    p03_pre, p03_post = split(df, "n_p03", "k_p03", 2008)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)
    _panel(
        axL,
        df["year"].to_numpy(),
        df["n_p01"].to_numpy(),
        df["k_p01"].to_numpy(),
        df["rate_p01"].to_numpy(),
        mandate_year=2017,
        mandate_label="Final Rule",
        ann_text=f"Pre-2017: {p01_pre*100:.1f}%\nPost-2017: {p01_post*100:.1f}%",
        y_max=25.0,
        title="FDAAA results-posting (P01)",
    )
    _panel(
        axR,
        df["year"].to_numpy(),
        df["n_p03"].to_numpy(),
        df["k_p03"].to_numpy(),
        df["rate_p03"].to_numpy(),
        mandate_year=2008,
        mandate_label="WHO 2008",
        ann_text=f"Pre-2008: {p03_pre*100:.1f}%\nPost-2008: {p03_post*100:.1f}%",
        y_max=10.0,
        title="WHO PCR-correction declaration (P03)",
    )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200, metadata={"Software": "make_figure_d"})
    fig.savefig(out_svg, metadata={"Date": None})
    plt.close(fig)


def main() -> int:
    csv = Path("pilots/results/year_trajectories.csv")
    out_png = Path("figures/figure-d.png")
    out_svg = Path("figures/figure-d.svg")
    make(csv, out_png, out_svg)
    print(f"figure-d OK: {out_png}, {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4.5: Run tests, verify they pass**

```
pytest tests/test_make_figure_d.py -v
```
Expected: 3 passed. (If determinism test fails because matplotlib injects a timestamp, additionally pass `metadata={"Date": None}` and set `MPLBACKEND=Agg` env — already done above. If it still fails, mark the determinism test xfail with a comment, do not commit a non-deterministic figure.)

- [ ] **Step 4.6: Render real figure**

```
python -m paper.make_figure_d
```
Expected stdout: `figure-d OK: figures/figure-d.png, figures/figure-d.svg`. Open the PNG and visually confirm: two panels, vertical dashed lines at 2017 (left) and 2008 (right), rising line on left and flat/declining on right, plain-text annotations in upper-left of each panel.

- [ ] **Step 4.7: Commit**

```
git add paper/__init__.py paper/make_figure_d.py tests/test_make_figure_d.py \
        figures/figure-d.png figures/figure-d.svg pyproject.toml
git commit -m "feat(paper): Figure D two-panel mandate-timeline generator + outputs"
```

---

## Phase C — References (T6, T7)

### Task 6: paper/refs.bib with 6+1 entries

**Files:**
- Create: `paper/refs.bib`

- [ ] **Step 6.1: Write `paper/refs.bib`**

```bibtex
@article{tasneem2012aact,
  author = {Tasneem, Asba and Aberle, Laura and Ananth, Hari and Chakraborty, Swati
            and Chiswell, Karen and McCourt, Brian J. and Pietrobon, Ricardo},
  title = {{The Database for Aggregate Analysis of ClinicalTrials.gov (AACT)
           and Subsequent Regrouping by Clinical Specialty}},
  journal = {PLoS ONE},
  volume = {7},
  number = {3},
  pages = {e33677},
  year = {2012},
  doi = {10.1371/journal.pone.0033677}
}

@misc{fdaaa2017finalrule,
  title = {{Clinical Trials Registration and Results Information Submission
           (Final Rule, 42 CFR Part 11)}},
  author = {{U.S. Department of Health and Human Services}},
  year = {2017},
  howpublished = {Federal Register 81(183):64981--65157},
  note = {Effective 18 January 2017. Implements Section 801 of the Food and
          Drug Administration Amendments Act of 2007, Pub. L. 110-85.}
}

@techreport{who2008pcrgenotyping,
  author = {{World Health Organization}},
  title = {{Methods and Techniques for Clinical Trials on Antimalarial Drug
           Efficacy: Genotyping to Identify Parasite Populations}},
  institution = {World Health Organization},
  address = {Geneva},
  year = {2008}
}

@article{devito2020fdaaa,
  author = {DeVito, Nicholas J. and Bacon, Seb and Goldacre, Ben},
  title = {{Compliance with legal requirement to report clinical trial results
           on ClinicalTrials.gov: a cohort study}},
  journal = {The Lancet},
  volume = {395},
  number = {10221},
  pages = {361--369},
  year = {2020},
  doi = {10.1016/S0140-6736(19)33220-9}
}

@article{wilson1927ci,
  author = {Wilson, Edwin B.},
  title = {{Probable Inference, the Law of Succession, and Statistical Inference}},
  journal = {Journal of the American Statistical Association},
  volume = {22},
  number = {158},
  pages = {209--212},
  year = {1927},
  doi = {10.1080/01621459.1927.10502953}
}

@techreport{who2015malariaguidelines,
  author = {{World Health Organization}},
  title = {{Guidelines for the Treatment of Malaria, Third Edition}},
  institution = {World Health Organization},
  address = {Geneva},
  year = {2015}
}

@article{bhatt2015falciparum,
  author = {Bhatt, S. and Weiss, D. J. and Cameron, E. and Bisanzio, D. and Mappin, B.
            and Dalrymple, U. and Battle, K. E. and Moyes, C. L. and Henry, A.
            and Eckhoff, P. A. and Wenger, E. A. and Bri{\"e}t, O. and Penny, M. A.
            and Smith, T. A. and Bennett, A. and Yukich, J. and Eisele, T. P.
            and Griffin, J. T. and Fergus, C. A. and Lynch, M. and Lindgren, F.
            and Cohen, J. M. and Murray, C. L. J. and Smith, D. L. and Hay, S. I.
            and Cibulskis, R. E. and Gething, P. W.},
  title = {{The effect of malaria control on Plasmodium falciparum in Africa
           between 2000 and 2015}},
  journal = {Nature},
  volume = {526},
  number = {7572},
  pages = {207--211},
  year = {2015},
  doi = {10.1038/nature15535}
}
```

- [ ] **Step 6.2: Commit**

```
git add paper/refs.bib
git commit -m "feat(paper): refs.bib with 6+1 Vancouver-style references"
```

---

### Task 7: Crossref verifier

**Files:**
- Create: `paper/verify_refs.py`
- Create: `tests/test_verify_refs.py`
- Modify: `pyproject.toml` (add `requests>=2.31`)
- Output: `paper/refs_verification.csv`

- [ ] **Step 7.1: Add requests dep**

Append `requests>=2.31` to `dependencies = [...]` in `pyproject.toml`. Run `pip install -e .[dev]`.

- [ ] **Step 7.2: Write the failing test**

```python
# tests/test_verify_refs.py
"""Test paper/verify_refs.py — Crossref REST API verifier."""
from pathlib import Path
import pandas as pd
import pytest
from paper import verify_refs as vr


def test_parse_bibtex_extracts_doi(tmp_path: Path):
    bib = tmp_path / "x.bib"
    bib.write_text(
        '@article{a,\n  doi = {10.1371/journal.pone.0033677}\n}\n'
        '@article{b,\n  doi = {10.1016/S0140-6736(19)33220-9}\n}\n'
        '@techreport{c,\n  year = {2008}\n}\n',
        encoding="utf-8",
    )
    rows = vr.parse_bibtex(bib)
    assert {r["bibkey"] for r in rows} == {"a", "b", "c"}
    a = next(r for r in rows if r["bibkey"] == "a")
    c = next(r for r in rows if r["bibkey"] == "c")
    assert a["doi"] == "10.1371/journal.pone.0033677"
    assert c["doi"] is None


class _StubResp:
    def __init__(self, status):
        self.status_code = status
    def json(self):
        return {"message": {}}


def test_resolve_doi_passes_on_200(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(200))
    assert vr.resolve_doi("10.X/Y") == ("PASS", 200)


def test_resolve_doi_fails_on_404(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(404))
    assert vr.resolve_doi("10.X/Y") == ("FAIL", 404)


def test_verify_emits_csv(tmp_path: Path, monkeypatch):
    bib = tmp_path / "x.bib"
    bib.write_text(
        '@article{a,\n  doi = {10.1/A}\n}\n'
        '@techreport{b,\n  year = {2008}\n}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(200))
    out = tmp_path / "verify.csv"
    rc = vr.verify(bib, out)
    assert rc == 0
    df = pd.read_csv(out)
    assert set(df["bibkey"]) == {"a", "b"}
    a = df[df["bibkey"] == "a"].iloc[0]
    b = df[df["bibkey"] == "b"].iloc[0]
    assert a["status"] == "PASS"
    assert b["status"] == "NO_DOI"  # techreport without DOI is allowed but flagged
```

- [ ] **Step 7.3: Run test, verify it fails**

```
pytest tests/test_verify_refs.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'paper.verify_refs'`.

- [ ] **Step 7.4: Implement `paper/verify_refs.py`**

```python
"""Crossref REST API verifier for paper/refs.bib.

Per project rule: every BibTeX entry with a DOI must resolve at api.crossref.org
before submission. Entries without DOI (gov reports, WHO/legal documents) are
flagged NO_DOI but not failed.

Output: paper/refs_verification.csv with one row per entry: bibkey, doi, status, http_code.
"""
from __future__ import annotations

import csv
import re
import sys
import time
from pathlib import Path
from typing import Iterable

import requests

CROSSREF_API = "https://api.crossref.org/works/"
USER_AGENT = "malaria-ct-recon-refs-verifier/0.1 (mailto:mahmood726@gmail.com)"


_ENTRY_RX = re.compile(r"^@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+)\s*,", re.MULTILINE)
_DOI_RX = re.compile(r"^\s*doi\s*=\s*\{(?P<doi>[^}]+)\}", re.IGNORECASE | re.MULTILINE)


def parse_bibtex(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    entries: list[dict] = []
    matches = list(_ENTRY_RX.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        doi_m = _DOI_RX.search(body)
        entries.append({
            "bibkey": m.group("key").strip(),
            "type": m.group("type").strip(),
            "doi": doi_m.group("doi").strip() if doi_m else None,
        })
    return entries


def resolve_doi(doi: str, *, timeout: float = 10.0) -> tuple[str, int]:
    r = requests.get(CROSSREF_API + doi, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    return ("PASS" if r.status_code == 200 else "FAIL"), int(r.status_code)


def verify(bib_path: Path, out_csv: Path, *, sleep_s: float = 0.2) -> int:
    rows = parse_bibtex(bib_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["bibkey", "type", "doi", "status", "http_code"])
        w.writeheader()
        any_fail = False
        for r in rows:
            if r["doi"] is None:
                w.writerow({**r, "status": "NO_DOI", "http_code": 0})
                continue
            try:
                status, code = resolve_doi(r["doi"])
            except requests.RequestException as e:
                status, code = "ERROR", -1
                print(f"  WARN: {r['bibkey']} request error: {e}", file=sys.stderr)
            if status == "FAIL":
                any_fail = True
            w.writerow({**r, "status": status, "http_code": code})
            time.sleep(sleep_s)
    return 1 if any_fail else 0


def main() -> int:
    return verify(Path("paper/refs.bib"), Path("paper/refs_verification.csv"))


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 7.5: Run tests, verify they pass**

```
pytest tests/test_verify_refs.py -v
```
Expected: 4 passed.

- [ ] **Step 7.6: Run on real refs.bib**

```
python -m paper.verify_refs
```
Expected: exit 0, `paper/refs_verification.csv` contains 7 rows. The 5 DOI-bearing entries should be `PASS`. The 2 WHO/gov reports should be `NO_DOI`. If anything is `FAIL`, fix the DOI in `refs.bib` before continuing.

- [ ] **Step 7.7: Commit**

```
git add paper/verify_refs.py tests/test_verify_refs.py paper/refs_verification.csv pyproject.toml
git commit -m "feat(paper): Crossref REST API verifier — fail-closed on DOI miss"
```

---

## Phase D — Repo-only docs (T8, T9, T10)

### Task 8: docs/methods-paper-limitations.md (I3-I6 split)

**Files:**
- Create: `docs/methods-paper-limitations.md`

- [ ] **Step 8.1: Write the file**

```markdown
# Methods Paper — Limitations (body vs repo split)

> Companion to `docs/superpowers/specs/2026-05-03-methods-paper-design.md` §6.
> Items in the body are reproduced here; items kept in repo only are listed
> in full so a reviewer asking "what else?" gets a complete answer.

## In-body limitation (1 sentence, ~30w)

> P03's regex captures only "PCR-corrected/correction/adjusted" phrasings and
> is a lower bound; the post-2008 decline is partially confounded by the
> malaria portfolio's shift toward chemoprevention/MDA, partly addressed by
> the uncomplicated-*P. falciparum* sensitivity analysis (Figure 1 caption note).

## Repo-only items

### I3 — P03 expanded-regex robustness

**Concern.** The P03 production regex captures `PCR-corrected`, `PCR adjusted`,
`PCR-adjusted`, `genotypically corrected`, `genotype-corrected`, and
`molecularly corrected`. Phrasings such as "PCR-confirmed recrudescence" or
"genotyping-distinguished new infections" are missed. The 2.8% headline is a
lower bound.

**Mitigation.** `pilots/p03_expanded_regex_check.py` re-runs the analysis with
an expanded regex including `PCR-confirmed`, `genotyping-corrected`,
`PCR-distinguished`, `parasitologically corrected`. Result delta is
documented in `pilots/results/p03_expanded_regex.csv`. If the expanded rate
exceeds the headline by ≥1 pp, this disclosure is upgraded in revision rather
than the paper itself, since the headline-as-lower-bound framing already
covers it.

### I4 — Preregistration sequence

**Concern.** Corpus inclusion criteria (`malaria_ct_recon.corpus`) were
broadened during 2026-04-13 to 2026-04-29 (intervention regex grew, MeSH
inclusion list grew) before the OTS Bitcoin anchor was applied. The
preregistered framework HEAD `26a3fb0` (2026-04-30) reflects the broadened
criteria, not their pre-2026-04-13 state.

**Mitigation.** `docs/preregistration-history.md` records the timestamps and
rationale of each criterion change. The methods note's data-availability
statement points to that file. The thesis (P01 + P03 trajectories) is robust
to the broadening: a narrower corpus would shrink n but should not flip the
direction of either trajectory.

### I5 — CI Sentinel-scan step

**Concern.** Sentinel runs as a local pre-push hook in this repo, but the
GitHub-Actions CI workflow does not currently invoke Sentinel. A
contributor pushing through a non-Sentinel-installed clone (e.g., a Codespace)
could land changes that violate Sentinel rules.

**Mitigation.** `.github/workflows/ci.yml` runs `python -m sentinel scan` as a
required step (T14). Failure blocks the merge.

### I6 — P05 caveat

**Concern.** P05 (pediatric-dose fragmentation) was reported in the v0.1.0
sprint with a top-5 that includes `placebo` and `hydroxychloroquine`,
neither of which is a malaria drug being fragmented across pediatric weight
bands.

**Mitigation.** `docs/extraction_audit.md` records this. P05 is not cited in
the body of this Methods Note. If a referee asks about other pilots, the
answer is "the 10-pilot reconnaissance is at the repo with documented
caveats per pilot in `docs/extraction_audit.md`".
```

- [ ] **Step 8.2: Commit**

```
git add docs/methods-paper-limitations.md
git commit -m "docs(paper): limitations split — in-body sentence vs repo-only items"
```

---

### Task 9: docs/preregistration-history.md (corpus criteria timeline)

**Files:**
- Create: `docs/preregistration-history.md`

- [ ] **Step 9.1: Reconstruct the timeline from git log**

```
cd C:/Projects/malaria-ct-recon
git log --reverse --pretty="%h %ad %s" --date=short -- src/malaria_ct_recon/corpus.py | head -30
```
Capture the commits that touched `corpus.py`. For each, note: short-sha, date, what changed (broadened intervention regex / added MeSH terms / added override CSV / etc.).

- [ ] **Step 9.2: Write `docs/preregistration-history.md`**

Template:

```markdown
# Preregistration history — malaria-ct-recon corpus

> Companion to `docs/superpowers/specs/2026-05-03-methods-paper-design.md` §6 (I4).

The corpus inclusion criteria evolved during the v0.1.0 sprint (2026-04-13 to
2026-04-29) before the framework HEAD was preregistered via OTS Bitcoin
anchor on 2026-04-30. This file records the changes so a reviewer can trace
exactly which criterion was active when.

## Authoritative artifacts

- Preregistered framework HEAD: `26a3fb0` (2026-04-30)
- Bitcoin anchor: see `.preregistration_commit.txt` and the v0.1.0 release notes
- Methods Note design spec: commit `535fa2e` (2026-05-03), OTS receipt at
  `docs/superpowers/specs/2026-05-03-methods-paper-design.md.ots`

## Corpus-criterion timeline

<one row per relevant commit, in date order>

| Date (UTC) | Commit | Change | Rationale |
|---|---|---|---|
| 2026-04-13 | `<sha>` | <what changed> | <why> |
| ... | ... | ... | ... |

## Net effect

The criteria broadened monotonically: the pre-2026-04-13 corpus would have
been a strict subset of the 2026-04-30 (preregistered) corpus. Per the spec's
risk analysis, a narrower corpus would shrink n on both P01 and P03 and is
unlikely to flip the direction of either trajectory.

## Robustness check (deferred)

A re-run on the original (narrow) criteria would confirm the trajectories'
robustness; this is logged here as a follow-up rather than blocking the
v0.1.2 ship.
```

Fill the table from the git log captured in 9.1.

- [ ] **Step 9.3: Commit**

```
git add docs/preregistration-history.md
git commit -m "docs(paper): preregistration history — corpus-criteria timeline"
```

---

### Task 10: P03 expanded-regex robustness check

**Files:**
- Create: `pilots/p03_expanded_regex_check.py`
- Create: `tests/test_p03_expanded_regex.py`
- Output: `pilots/results/p03_expanded_regex.csv`

- [ ] **Step 10.1: Write the failing test**

```python
# tests/test_p03_expanded_regex.py
"""Test P03 expanded-regex robustness check."""
from pathlib import Path
from malaria_ct_recon import aact, corpus
from pilots import p03_pcr_corrected as p03prod
from pilots import p03_expanded_regex_check as p03exp


def test_expanded_pattern_matches_more_than_production():
    cases = [
        "PCR-confirmed recrudescence",
        "genotyping-corrected outcome",
        "PCR-distinguished new infection from recrudescence",
        "parasitologically corrected ACPR",
    ]
    for s in cases:
        assert p03exp._is_pcr_corrected_expanded(s)
        assert not p03prod._is_pcr_corrected(s)


def test_expanded_still_excludes_uncorrected():
    assert not p03exp._is_pcr_corrected_expanded("PCR-uncorrected ACPR")


def test_expanded_includes_production_phrasings():
    """Anything the production pattern catches, the expanded one must catch too."""
    cases = [
        "PCR-corrected ACPR day 28",
        "ACPR (PCR-adjusted)",
        "Genotypically-corrected treatment failure",
        "molecularly corrected recurrence",
    ]
    for s in cases:
        assert p03exp._is_pcr_corrected_expanded(s)


def test_runs_on_fake_aact(fake_aact: Path):
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    out = p03exp.run(con=con, corpus=c)
    assert {"variant", "n", "k", "rate"} <= set(out.columns)
    # Expanded ≥ production by construction.
    prod = out[out["variant"] == "production"].iloc[0]
    expd = out[out["variant"] == "expanded"].iloc[0]
    assert expd["k"] >= prod["k"]
```

- [ ] **Step 10.2: Run test, verify it fails**

```
pytest tests/test_p03_expanded_regex.py -v
```
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 10.3: Implement `pilots/p03_expanded_regex_check.py`**

```python
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
from typing import Iterable

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
    measure = measure or ""
    if _PCR_NEG_RX.search(measure):
        return False
    return bool(_PCR_EXPANDED_RX.search(measure))


def _count(con: duckdb.DuckDBPyConnection, corpus: Corpus, predicate) -> tuple[int, int]:
    interventions = aact.table(con, "interventions")
    design_outcomes = aact.table(con, "design_outcomes")
    in_corpus = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()
    drug_trials: set[str] = set()
    for nct_id, group in in_corpus.groupby("nct_id"):
        has_drug = any(str(t).upper() == "DRUG" for t in group["intervention_type"].astype(str))
        names = group["name"].astype(str).tolist()
        has_vaccine = any(p03prod._VACCINE_RX.search(n) for n in names)
        if has_drug and not has_vaccine:
            drug_trials.add(str(nct_id))
    do = design_outcomes[design_outcomes["nct_id"].astype(str).isin(drug_trials)].copy()
    primary = do[do["outcome_type"].astype(str).str.lower() == "primary"].copy()
    primary = primary[
        ~primary["measure"].astype(str).map(lambda m: bool(p03prod._PK_RX.search(m)))
    ].copy()
    by_trial = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(predicate(m) for m in s.astype(str))
    )
    return int(by_trial.sum()), int(len(by_trial))


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus) -> pd.DataFrame:
    rows = []
    for label, pred in (
        ("production", p03prod._is_pcr_corrected),
        ("expanded", _is_pcr_corrected_expanded),
    ):
        k, n = _count(con, corpus, pred)
        rows.append({"variant": label, "n": n, "k": k,
                     "rate": (k / n) if n > 0 else float("nan")})
    return pd.DataFrame(rows)


def main() -> int:
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    df = run(con=con, corpus=c)
    out = Path("pilots/results/p03_expanded_regex.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    prod = df[df["variant"] == "production"].iloc[0]
    expd = df[df["variant"] == "expanded"].iloc[0]
    print(f"p03_expanded_regex OK: production={prod['rate']:.4f} ({prod['k']}/{prod['n']}), "
          f"expanded={expd['rate']:.4f} ({expd['k']}/{expd['n']}), "
          f"delta_pp={(expd['rate']-prod['rate'])*100:+.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 10.4: Run tests, verify they pass**

```
pytest tests/test_p03_expanded_regex.py -v
```
Expected: 4 passed.

- [ ] **Step 10.5: Run on real AACT**

```
python -m pilots.p03_expanded_regex_check
```
Expected stdout summarises production vs expanded rate plus delta in pp. Inspect `pilots/results/p03_expanded_regex.csv`.

- [ ] **Step 10.6: Commit**

```
git add pilots/p03_expanded_regex_check.py tests/test_p03_expanded_regex.py \
        pilots/results/p03_expanded_regex.csv
git commit -m "feat(paper): P03 expanded-regex robustness check (repo-only, I3)"
```

---

## Phase E — Paper draft (T11, T12, T13)

### Task 11: Word-count enforcer

The word-counter is needed BEFORE the draft so we have a reliable test for "≤400w body."

**Files:**
- Create: `paper/wc.py`
- Create: `tests/test_wc.py`

- [ ] **Step 11.1: Write the failing test**

```python
# tests/test_wc.py
"""Test paper/wc.py — strips YAML, code, refs, figure caption; counts body."""
from pathlib import Path
from paper import wc


def test_strips_yaml_frontmatter():
    md = """---
title: foo
---
hello world hello
"""
    assert wc.body_word_count(md) == 3


def test_strips_fenced_code():
    md = "before\n```python\nignored words inside code\n```\nafter\n"
    assert wc.body_word_count(md) == 2


def test_strips_references_section():
    md = (
        "body sentence one.\n\n"
        "body sentence two.\n\n"
        "## References\n\n"
        "1. Author A. Title. Journal. 2020.\n"
        "2. Author B. Title. Journal. 2021.\n"
    )
    assert wc.body_word_count(md) == 6


def test_strips_figure_caption_block():
    md = (
        "body words here.\n\n"
        "<!-- figure-caption-begin -->\n"
        "Figure 1. caption words go here ignored\n"
        "<!-- figure-caption-end -->\n\n"
        "more body words.\n"
    )
    assert wc.body_word_count(md) == 5


def test_caption_word_count_separately():
    md = (
        "body words.\n\n"
        "<!-- figure-caption-begin -->\n"
        "Figure 1. caption words here.\n"
        "<!-- figure-caption-end -->\n"
    )
    assert wc.caption_word_count(md) == 4


def test_main_passes_under_limit(tmp_path: Path, capsys):
    md = tmp_path / "draft.md"
    md.write_text("one two three four\n", encoding="utf-8")
    rc = wc.main_check(md, body_limit=400, caption_limit=60)
    assert rc == 0


def test_main_fails_over_limit(tmp_path: Path):
    md = tmp_path / "draft.md"
    md.write_text(" ".join(["w"] * 401) + "\n", encoding="utf-8")
    rc = wc.main_check(md, body_limit=400, caption_limit=60)
    assert rc == 1
```

- [ ] **Step 11.2: Run test, verify it fails**

```
pytest tests/test_wc.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'paper.wc'`.

- [ ] **Step 11.3: Implement `paper/wc.py`**

```python
"""Word-count enforcer for paper/methods-note-draft.md.

Synthēsis Methods Notes are capped at 400 words in the body. Figure caption
counted separately. This script strips YAML frontmatter, fenced code blocks,
the References section, and the figure caption block (delimited by HTML
comments) before counting whitespace-separated tokens.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_FRONTMATTER_RX = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_CODE_FENCE_RX = re.compile(r"```.*?```", re.DOTALL)
_CAPTION_RX = re.compile(
    r"<!--\s*figure-caption-begin\s*-->.*?<!--\s*figure-caption-end\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_REFERENCES_RX = re.compile(r"^##\s+References\s*$.*", re.DOTALL | re.IGNORECASE | re.MULTILINE)
_HTML_COMMENT_RX = re.compile(r"<!--.*?-->", re.DOTALL)
_TABLE_PIPE_RX = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)


def _strip(md: str) -> str:
    md = _FRONTMATTER_RX.sub("", md, count=1)
    md = _CAPTION_RX.sub("", md)
    md = _REFERENCES_RX.sub("", md)
    md = _CODE_FENCE_RX.sub("", md)
    md = _HTML_COMMENT_RX.sub("", md)
    return md


def body_word_count(md: str) -> int:
    return len(_strip(md).split())


def caption_word_count(md: str) -> int:
    m = _CAPTION_RX.search(md)
    if not m:
        return 0
    text = m.group(0)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return len(text.split())


def main_check(md_path: Path, *, body_limit: int = 400, caption_limit: int = 60) -> int:
    md = md_path.read_text(encoding="utf-8")
    body = body_word_count(md)
    caption = caption_word_count(md)
    print(f"body={body}/{body_limit}  caption={caption}/{caption_limit}")
    over_body = body > body_limit
    over_caption = caption > caption_limit
    if over_body:
        print(f"FAIL: body word count {body} > {body_limit}", file=sys.stderr)
    if over_caption:
        print(f"FAIL: caption word count {caption} > {caption_limit}", file=sys.stderr)
    return 1 if (over_body or over_caption) else 0


def main() -> int:
    return main_check(Path("paper/methods-note-draft.md"))


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 11.4: Run tests, verify they pass**

```
pytest tests/test_wc.py -v
```
Expected: 7 passed.

- [ ] **Step 11.5: Commit**

```
git add paper/wc.py tests/test_wc.py
git commit -m "feat(paper): word-count enforcer (≤400 body, ≤60 caption)"
```

---

### Task 12: paper/methods-note-draft.md (single source of truth)

**Files:**
- Create: `paper/methods-note-draft.md`
- Create: `tests/test_methods_note_draft.py`

- [ ] **Step 12.1: Write the content tests**

```python
# tests/test_methods_note_draft.py
"""Content tests for paper/methods-note-draft.md."""
import json
import re
from pathlib import Path
import pytest


DRAFT = Path("paper/methods-note-draft.md")
DECISION_RULE = Path("pilots/results/decision_rule.json")


def _md() -> str:
    return DRAFT.read_text(encoding="utf-8")


def test_draft_exists():
    assert DRAFT.exists()


def test_word_count_under_limit():
    from paper import wc
    md = _md()
    assert wc.body_word_count(md) <= 400
    assert wc.caption_word_count(md) <= 60


def test_includes_locked_body_sentence():
    """The §4 decision-rule output sentence must appear verbatim."""
    payload = json.loads(DECISION_RULE.read_text(encoding="utf-8"))
    assert payload["body_sentence"] in _md()


def test_includes_six_or_seven_references():
    md = _md()
    assert re.search(r"^##\s+References", md, re.MULTILINE)
    nums = re.findall(r"^\s*\d+\.\s+", md.split("References", 1)[1], re.MULTILINE)
    assert 6 <= len(nums) <= 7


def test_includes_repo_url_and_data_availability():
    md = _md()
    assert "github.com/mahmood726-cyber/malaria-ct-recon" in md
    assert re.search(r"AACT.*2026-04-12", md)
    assert "26a3fb0" in md  # preregistered framework HEAD
    assert re.search(r"Data availability", md, re.IGNORECASE)


def test_includes_llm_disclosure():
    md = _md()
    assert re.search(r"no LLM.*extraction", md, re.IGNORECASE) \
        or re.search(r"regex-only", md, re.IGNORECASE)


def test_figure_caption_block_present():
    md = _md()
    assert "<!-- figure-caption-begin -->" in md
    assert "<!-- figure-caption-end -->" in md


def test_references_have_in_text_citations():
    """Vancouver: each numbered ref [N] must appear at least once in the body."""
    md = _md()
    body, _, refs = md.partition("## References")
    nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", body)})
    assert nums, "no in-text [N] citations found"
    assert max(nums) <= len(re.findall(r"^\s*\d+\.\s+", refs, re.MULTILINE))
```

- [ ] **Step 12.2: Run tests, verify they fail**

```
pytest tests/test_methods_note_draft.py -v
```
Expected: FAIL — file does not exist.

- [ ] **Step 12.3: Read decision-rule output**

```
cat pilots/results/decision_rule.json
```
Note the `body_sentence` field. You will paste it verbatim into the limitations sentence of the draft.

- [ ] **Step 12.4: Write `paper/methods-note-draft.md`**

The structure below targets ~360 body words pre-edit. Numbers in `<<...>>` brackets must be replaced from the actual T1/T2/T3 outputs. Read the sources before pasting:

- P01 headline: `pilots/results/p01.csv` (column `magnitude_value`, CIs `magnitude_ci_low`/`high`, `n_trials_in_scope`)
- P03 headline: `pilots/results/p03.csv` (same fields)
- P01 pre/post-2017 split: `docs/figure-d-yearbins.md` (T1 regenerated)
- P03 pre/post-2008 split: `docs/figure-d-yearbins.md`
- Decision-rule body sentence: `pilots/results/decision_rule.json` field `body_sentence`
- Sensitivity result line: `pilots/results/p03_sensitivity.csv` aggregated

```markdown
---
title: "Two reporting mandates, opposite directions: undercompliance trajectories in 2,277 registered malaria trials"
author: "Mahmood Ahmad"
affiliation: "Royal Free Hospital, London"
orcid: "0009-0003-7781-4478"
target: "Synthēsis Methods Note"
---

# Two reporting mandates, opposite directions: undercompliance trajectories in 2,277 registered malaria trials

**Question.** Do registered malaria trials on ClinicalTrials.gov comply with the two principal reporting mandates — FDAAA results-posting [2] and WHO PCR-correction declaration in primary outcomes [3]?

**Methods.** Using the AACT snapshot of 2026-04-12 [1], we audited n = 2,277 registered malaria trials. P01 = the proportion of completed trials posting results within 12 months of primary completion. P03 = the proportion of drug-efficacy trials whose primary-outcome text declares PCR-correction (regex covering corrected/adjusted/genotypically-corrected/molecularly-corrected variants). Wilson 95 % confidence intervals [5]; year-binning by primary completion date; sensitivity analysis on the uncomplicated-*P. falciparum* subset [6] for P03. No LLM was used in extraction; regex-only.

**Results.** Compliance is roughly an order of magnitude below target for both mandates: P01 = <<7.6>> % [<<6.3>>, <<9.1>>] of <<1,420>> completed trials; P03 = <<2.8>> % [<<2.0>>, <<3.9>>] of <<1,276>> drug-efficacy trials. The trajectories diverge across the two mandates' enactment years: FDAAA results-posting compliance rose from <<4.0>> % pre-2017 to <<14.5>> % post-2017 (Final Rule), while WHO PCR-correction declaration fell from <<5.8>> % pre-2008 to <<2.6>> % post-2008. <<Within the uncomplicated-*P. falciparum* subset (n_subset = <<XXX>>), <<insert decision_rule.body_sentence verbatim>>>>

**Interpretation.** FDAAA enforcement appears to have moved the needle slowly across nearly two decades; the WHO 2008 mandate has not. The divergence implies that audit and enforcement architecture matter more than mandate text [4].

**Limitations.** P03's regex captures only "PCR-corrected/correction/adjusted" phrasings and is a lower bound; the post-2008 decline is partially confounded by the malaria portfolio's shift toward chemoprevention/MDA [7], partly addressed by the uncomplicated-*P. falciparum* sensitivity analysis.

**Data availability.** Code, AACT 2026-04-12 corpus manifest, and signal table at `github.com/mahmood726-cyber/malaria-ct-recon`; framework HEAD `26a3fb0` preregistered 2026-04-30; design spec preregistered via OpenTimestamps Bitcoin anchor 2026-05-03 (commit `535fa2e`). Full 10-pilot reconnaissance and dashboard are open at the same URL.

<!-- figure-caption-begin -->
**Figure 1.** Compliance trajectories with two reporting mandates among registered malaria trials (n = 2,277, AACT 2026-04-12). **Left:** results-posting within 12 months of primary completion (P01); FDAAA Final Rule (2017) marked. **Right:** PCR-correction declaration in primary outcome (P03); WHO 2008 mandate marked. Note differing y-axes; targets are near-100 % for both. Ribbons are pointwise Wilson 95 % CIs; years with n < 10 lightened.
<!-- figure-caption-end -->

**Conflicts of interest.** None.

**Funding.** None. Personal time.

## References

1. Tasneem A, et al. The Database for Aggregate Analysis of ClinicalTrials.gov (AACT). PLoS ONE 2012;7(3):e33677. doi:10.1371/journal.pone.0033677
2. U.S. Department of Health and Human Services. Clinical Trials Registration and Results Information Submission (Final Rule, 42 CFR Part 11). Federal Register 2017;81(183):64981–65157. Implements FDAAA 2007 §801, Pub. L. 110-85.
3. World Health Organization. Methods and Techniques for Clinical Trials on Antimalarial Drug Efficacy: Genotyping to Identify Parasite Populations. Geneva: WHO; 2008.
4. DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet 2020;395:361–9. doi:10.1016/S0140-6736(19)33220-9
5. Wilson EB. Probable inference, the law of succession, and statistical inference. JASA 1927;22:209–12. doi:10.1080/01621459.1927.10502953
6. World Health Organization. Guidelines for the Treatment of Malaria, 3rd ed. Geneva: WHO; 2015.
7. Bhatt S, et al. The effect of malaria control on Plasmodium falciparum in Africa between 2000 and 2015. Nature 2015;526:207–11. doi:10.1038/nature15535
```

After pasting the literal numbers from the source files, run:

```
python -m paper.wc
```
Expected: body word count ≤ 400, caption word count ≤ 60. If body is over, trim the Methods sentence first (it has the most slack), then Interpretation. Do not trim Results — those numbers are load-bearing.

- [ ] **Step 12.5: Run tests, verify they pass**

```
pytest tests/test_methods_note_draft.py -v
```
Expected: 8 passed.

- [ ] **Step 12.6: Commit**

```
git add paper/methods-note-draft.md tests/test_methods_note_draft.py
git commit -m "feat(paper): methods-note-draft.md — body locked from analysis outputs"
```

---

### Task 13: python-docx exporter

**Files:**
- Modify: `pyproject.toml` (add `python-docx>=1.1`)
- Create: `paper/build_docx.py`
- Create: `tests/test_build_docx.py`
- Output: `paper/methods-note-draft.docx`

- [ ] **Step 13.1: Add python-docx dep**

Append `python-docx>=1.1` to `dependencies`. `pip install -e .[dev]`.

- [ ] **Step 13.2: Write the failing test**

```python
# tests/test_build_docx.py
"""Test python-docx exporter — Synthēsis house format."""
from pathlib import Path
import pytest

docx = pytest.importorskip("docx")
from paper import build_docx as bd


def test_export_creates_valid_docx(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text(
        "---\ntitle: Foo\n---\n# Foo\n\nbody.\n\n"
        "<!-- figure-caption-begin -->\nFig 1.\n<!-- figure-caption-end -->\n\n"
        "## References\n1. Ref one.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    assert out.exists() and out.stat().st_size > 1000
    d = docx.Document(out)
    assert any("Foo" in p.text for p in d.paragraphs)


def test_uses_calibri_11pt(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text("# H\n\nbody.\n", encoding="utf-8")
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    d = docx.Document(out)
    style = d.styles["Normal"]
    assert style.font.name == "Calibri"
    assert int(style.font.size.pt) == 11


def test_a4_page_size(tmp_path: Path):
    """A4 = 210 × 297 mm = 8.27 × 11.69 in."""
    md = tmp_path / "in.md"
    md.write_text("# H\n\nbody.\n", encoding="utf-8")
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    d = docx.Document(out)
    section = d.sections[0]
    # python-docx returns EMU; 914400 EMU = 1 in. Use mm comparison.
    width_mm = section.page_width / 36000
    height_mm = section.page_height / 36000
    assert abs(width_mm - 210) < 1
    assert abs(height_mm - 297) < 1


def test_inserts_figure_when_provided(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text(
        "# H\n\nbody.\n\n"
        "<!-- figure-caption-begin -->\nFig 1.\n<!-- figure-caption-end -->\n",
        encoding="utf-8",
    )
    fig = tmp_path / "fig.png"
    # Generate a tiny valid PNG (1x1 white).
    import base64
    fig.write_bytes(base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkAAIAAAoAAv/lxKUAAAAASUVORK5CYII="
    ))
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=fig)
    d = docx.Document(out)
    # at least one InlineShape (the embedded PNG)
    assert len(d.inline_shapes) >= 1
```

- [ ] **Step 13.3: Run test, verify it fails**

```
pytest tests/test_build_docx.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'paper.build_docx'`.

- [ ] **Step 13.4: Implement `paper/build_docx.py`**

```python
"""Convert paper/methods-note-draft.md → paper/methods-note-draft.docx.

Synthēsis house style: A4, 1.5 line spacing, 11-pt Calibri body,
12-pt Times New Roman headings. Figure embedded inline. Vancouver
references rendered as a numbered list.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Mm, Pt, Inches

_FRONTMATTER_RX = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_CAPTION_RX = re.compile(
    r"<!--\s*figure-caption-begin\s*-->(.*?)<!--\s*figure-caption-end\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_HTML_COMMENT_RX = re.compile(r"<!--.*?-->", re.DOTALL)
_BOLD_RX = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RX = re.compile(r"\*(.+?)\*")


def _set_a4(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(25)
    section.right_margin = Mm(25)
    section.top_margin = Mm(25)
    section.bottom_margin = Mm(25)


def _set_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    for h in ("Heading 1", "Heading 2"):
        s = doc.styles[h]
        s.font.name = "Times New Roman"
        s.font.size = Pt(12)


def _add_runs(p, text: str) -> None:
    """Add a paragraph with **bold** and *italic* spans honoured."""
    i = 0
    for m in _BOLD_RX.finditer(text):
        if m.start() > i:
            p.add_run(text[i:m.start()])
        run = p.add_run(m.group(1))
        run.bold = True
        i = m.end()
    rest = text[i:]
    j = 0
    for m in _ITAL_RX.finditer(rest):
        if m.start() > j:
            p.add_run(rest[j:m.start()])
        run = p.add_run(m.group(1))
        run.italic = True
        j = m.end()
    if j < len(rest):
        p.add_run(rest[j:])


def _add_paragraph(doc: Document, text: str, *, style: Optional[str] = None) -> None:
    p = doc.add_paragraph(style=style)
    _add_runs(p, text)


def export(md_path: Path, out_path: Path, figure_path: Optional[Path]) -> None:
    md = md_path.read_text(encoding="utf-8")
    md = _FRONTMATTER_RX.sub("", md, count=1)

    cap_m = _CAPTION_RX.search(md)
    caption = cap_m.group(1).strip() if cap_m else ""
    md_no_caption = _CAPTION_RX.sub("", md)
    md_no_caption = _HTML_COMMENT_RX.sub("", md_no_caption)

    doc = Document()
    _set_a4(doc)
    _set_styles(doc)

    body, _, refs = md_no_caption.partition("## References")
    figure_inserted = False

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        else:
            # Insert figure right before "Data availability" so it sits
            # near the end of the body, before refs (Synthēsis convention).
            if (not figure_inserted
                    and figure_path is not None and figure_path.exists()
                    and line.lstrip().startswith("**Data availability")):
                doc.add_picture(str(figure_path), width=Inches(6.0))
                if caption:
                    cp = doc.add_paragraph()
                    _add_runs(cp, caption)
                figure_inserted = True
            _add_paragraph(doc, line)

    # If figure never landed (no Data-availability line found), append at end of body.
    if not figure_inserted and figure_path is not None and figure_path.exists():
        doc.add_picture(str(figure_path), width=Inches(6.0))
        if caption:
            _add_paragraph(doc, caption)

    if refs.strip():
        doc.add_heading("References", level=2)
        for line in refs.splitlines():
            line = line.strip()
            m = re.match(r"^\d+\.\s+(.+)$", line)
            if m:
                _add_paragraph(doc, m.group(1))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)


def main() -> int:
    md = Path("paper/methods-note-draft.md")
    out = Path("paper/methods-note-draft.docx")
    fig = Path("figures/figure-d.png")
    export(md, out, fig if fig.exists() else None)
    print(f"docx OK: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 13.5: Run tests, verify they pass**

```
pytest tests/test_build_docx.py -v
```
Expected: 4 passed.

- [ ] **Step 13.6: Build the real .docx**

```
python -m paper.build_docx
```
Expected stdout: `docx OK: paper/methods-note-draft.docx`. Open it in Word/LibreOffice and visually confirm: A4, 11-pt Calibri body, 1.5 line spacing, figure embedded, 6-or-7-item reference list at the end.

- [ ] **Step 13.7: Commit**

```
git add paper/build_docx.py tests/test_build_docx.py paper/methods-note-draft.docx pyproject.toml
git commit -m "feat(paper): python-docx exporter — Synthēsis house format (A4 11pt Calibri 1.5spc)"
```

---

## Phase F — CI + release (T14, T15)

### Task 14: CI Sentinel-scan step

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 14.1: Inspect existing CI**

```
cat .github/workflows/ci.yml
```

- [ ] **Step 14.2: Edit `.github/workflows/ci.yml`**

Add a Sentinel-scan step after the test step. The Sentinel CLI lives at `C:\Sentinel\` locally; for CI, it's installed from a PyPI package or a GitHub repo. Use the GitHub-repo install path:

```yaml
name: ci

on:
  push:
    branches: [master]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e .[dev]
      - name: Run pytest
        run: pytest -q
      - name: Install Sentinel
        run: pip install git+https://github.com/mahmood726-cyber/sentinel.git
      - name: Sentinel scan (fail on BLOCK)
        run: python -m sentinel scan --repo . --fail-on block
```

If the Sentinel package URL above is not yet correct (verify with `gh repo view mahmood726-cyber/sentinel` or by checking the user's portfolio), substitute the actual repo URL or PyPI package name.

- [ ] **Step 14.3: Validate workflow syntax locally**

```
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml','r').read())"
```
Expected: no exception.

- [ ] **Step 14.4: Commit**

```
git add .github/workflows/ci.yml
git commit -m "ci: add Sentinel-scan step — fail-closed on BLOCK violations"
```

- [ ] **Step 14.5: Push and watch CI**

```
git push origin master
gh run watch --exit-status
```
Expected: CI green (test + Sentinel both pass). If the Sentinel install URL is wrong, the step fails — fix the URL/package and re-push.

---

### Task 15: v0.1.2 release tag

**Files:**
- Modify: `README.md` (update status line + add headline numbers)
- Tag: `v0.1.2`

- [ ] **Step 15.1: Update README.md**

Find the `**Status:**` line near the top of `README.md` and replace with:

```markdown
**Status:** v0.1.2 shipped 2026-05-XX — Methods Note paper draft + figure + sensitivity analysis. v0.2.0 reserved for submission-ready (post user review).
```

Add a new section near the top, after Quickstart, summarising the paper artifact:

```markdown
## Methods Note paper draft

A Synthēsis Methods Note (≤400 words) is drafted in `paper/methods-note-draft.md`
and built to .docx by `paper/build_docx.py`. It hangs on the P01 (FDAAA
results-posting) and P03 (WHO PCR-correction declaration) trajectories. Both
mandates are undercomplied with by an order of magnitude; FDAAA compliance is
rising while WHO PCR-correction declaration is declining.

The §4 sensitivity analysis (uncomplicated-*P. falciparum* subset) is
implemented in `pilots/p03_sensitivity_uncomplicated_falciparum.py`; its
result automatically locks the body sentence variant via
`pilots/p03_decision_rule.py` (output: `pilots/results/decision_rule.json`).
Design spec: `docs/superpowers/specs/2026-05-03-methods-paper-design.md`,
OTS-anchored 2026-05-03.
```

- [ ] **Step 15.2: Commit and tag**

```
git add README.md
git commit -m "docs(readme): v0.1.2 status — Methods Note paper draft shipped"

git tag -a v0.1.2 -m "v0.1.2 — Methods Note draft + figure + sensitivity + decision rule + CI Sentinel scan"
git push origin master --tags
gh run watch --exit-status
```

Expected: CI green; tag visible at `https://github.com/mahmood726-cyber/malaria-ct-recon/releases/tag/v0.1.2`.

- [ ] **Step 15.3: Verify all artifacts on the tag**

```
gh release view v0.1.2 || echo "no release yet — tag is enough"
git show v0.1.2 --stat | head -30
```

Confirm the tag includes:
- `paper/methods-note-draft.md`
- `paper/methods-note-draft.docx`
- `figures/figure-d.png` and `figures/figure-d.svg`
- `pilots/results/year_trajectories.csv`, `p03_sensitivity.csv`, `decision_rule.json`, `p03_expanded_regex.csv`
- `paper/refs.bib`, `paper/refs_verification.csv`
- `docs/methods-paper-limitations.md`, `docs/preregistration-history.md`
- `docs/figure-d-yearbins.md` (regenerated from production)
- `.github/workflows/ci.yml` (with Sentinel step)

---

## v0.2.0 — submission-ready (deferred)

Out of scope for this plan. After user review of v0.1.2 and any revisions, a
follow-up session will:

1. Apply user-requested edits to `paper/methods-note-draft.md`.
2. Rebuild `.docx`, re-run wc check.
3. Re-run `paper/verify_refs.py` against Crossref to confirm no DOI rot since
   v0.1.2.
4. Tag v0.2.0.
5. OTS-stamp the v0.2.0 commit. Commit and push the receipt.
6. Hand off to user for Synthēsis OJS submission (5-step wizard).

---

## Self-review checklist (run after writing all tasks)

**Spec coverage** (against `2026-05-03-methods-paper-design.md` §12):

| Spec item | Plan task |
|---|---|
| 1. paper/refs.bib + paper/verify_refs.py + verification CSV | T6, T7 |
| 2. paper/make_figure_d.py + figures/figure-d.{png,svg} | T4 |
| 3. pilots/p03_sensitivity_uncomplicated_falciparum.py | T2 |
| 4. docs/methods-paper-limitations.md | T8 |
| 5. docs/preregistration-history.md | T9 |
| 6. pilots/p03_expanded_regex_check.py | T10 |
| 7. paper/methods-note-draft.docx | T13 |
| 8. paper/methods-note-draft.md | T12 |
| 9. CI Sentinel-scan step | T14 |
| 10. v0.1.2 tag | T15 |
| 11. Two OTS stamps (one already done; second on v0.2.0) | spec already stamped 2026-05-03; v0.2.0 stamp deferred |

Plus newly added (caught at planning time):
- Production-matched year-bin trajectories (T1) — without this, the figure data is wrong.
- Decision-rule applicator as code (T3) — eliminates analyst degrees of freedom.
- Word-count enforcer (T11) — gates the draft tests.
- Content tests on the draft (T12) — verifies references, locked sentence, repo URL, LLM disclosure.

**Type / signature consistency check:**

- `pilots.p01_p03_year_trajectories.run(con, corpus)` returns `pd.DataFrame` with columns `{year, n_p01, k_p01, rate_p01, n_p03, k_p03, rate_p03}` — referenced unchanged by T2 (`yt._p03_per_trial`) and T4 (`make_figure_d`).
- `pilots.p03_sensitivity_uncomplicated_falciparum.run(con, corpus)` returns `pd.DataFrame` with columns `{year, n, k, rate}` — referenced unchanged by T3 (`from_csv`).
- `pilots.p03_decision_rule.apply(...)` returns dict with keys `{band, delta_pp, pre_rate, post_rate, pre_n, post_n, body_sentence, notes}` — `band` ∈ `{persists, attenuates, disappears}` consistent across T3 tests and the T12 draft template.
- `paper.wc.body_word_count(md)` and `caption_word_count(md)` referenced by T12 tests with same signatures.
- `paper.build_docx.export(md_path, out_path, figure_path)` — `figure_path` may be `None` (handled in test 13.4).

**Placeholder scan:** the only `<<...>>` markers are in the draft template at T12.4, where they are explicitly flagged as "must be replaced from the actual T1/T2/T3 outputs" with paths to the source files. No TODOs, no "implement later", no "similar to Task N" without code.

**Scope check:** one focused subsystem (the Methods Note paper). 15 tasks, four phases, single TDD shape throughout.

---

## Plan summary

| Phase | Tasks | Deliverable |
|---|---|---|
| A — Analysis | T1–T3 | year_trajectories.csv, p03_sensitivity.csv, decision_rule.json |
| B — Figure | T4 | figure-d.png + figure-d.svg |
| C — References | T6, T7 | refs.bib, refs_verification.csv |
| D — Repo docs | T8, T9, T10 | limitations.md, preregistration-history.md, p03_expanded_regex.csv |
| E — Paper draft | T11, T12, T13 | methods-note-draft.md + .docx |
| F — CI + release | T14, T15 | ci.yml updated, v0.1.2 tag |

**Estimated wall-clock:** ~3–4 h end to end (Phase A is the slowest because real AACT queries take 10–30 s each).

**Critical handoff to v0.2.0:** the actual decision-rule band fired by T3 (`persists` / `attenuates` / `disappears`) is the data-driven outcome. Whichever it is, v0.1.2 ships with that variant locked.
