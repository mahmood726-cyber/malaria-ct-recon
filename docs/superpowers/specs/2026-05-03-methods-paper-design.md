# Methods Paper Design — malaria-ct-recon Synthēsis Methods Note

**Date:** 2026-05-03
**Author:** Mahmood Ahmad (solo)
**Target journal:** Synthēsis (Methods Note format, ≤400 words)
**Repo state at design time:** master `6dc9704`, v0.1.1 shipped, AACT 2026-04-12 frozen
**Brainstorm transcript:** session of 2026-05-02 / 2026-05-03

This document is the locked design spec for a Synthēsis Methods Note derived from the malaria-ct-recon 10-pilot reconnaissance. It is written **before** the additional sensitivity analysis and figure-generation code is run, by deliberate design — see §4 "Pre-commit decision rule".

---

## 1. Title

> **Two reporting mandates, opposite directions: undercompliance trajectories in 2,277 registered malaria trials**

Twelve words; carries the thesis (divergent trajectories) and the scope (n = 2,277 registered malaria trials). Synthēsis house style favours short descriptive titles; this one trades 4 extra words for citation-pull.

## 2. Thesis & framing

**Thesis (one sentence):**
> Two regulatory mandates governing reporting of registered malaria trials — FDAAA results-posting and WHO PCR-correction declaration — are both undercomplied with by an order of magnitude on ClinicalTrials.gov, and have been moving in opposite directions since enactment: FDAAA results-posting compliance has risen from 4.0% to 14.5% across the FDAAA Final Rule (2017), while WHO PCR-correction declaration in primary outcomes has fallen from 5.8% pre-2008 to 2.6% post-2008.

**Framing arc (4 beats):**
1. ClinicalTrials.gov is the primary public registry for malaria trials; two regulatory mandates govern what trialists must report (FDAAA results-posting; WHO PCR-correction declaration).
2. We audited n = 2,277 registered malaria trials (AACT snapshot 2026-04-12) for compliance with each mandate.
3. Compliance is ~10× below target for both — and the trajectories diverge.
4. Full reconnaissance (10 pilots) is open at the repo + dashboard for community follow-up.

## 3. Word budget

| Beat | Words | Content |
|---|---|---|
| Question (1 sentence) | ~30 | Are registered malaria trials reporting compliant with FDAAA and WHO PCR-correction? |
| Methods (3 sentences) | ~90 | AACT 2026-04-12; corpus = 2,277; P01/P03 definitions; Wilson CIs; year-bins by primary completion; sensitivity on uncomplicated-falciparum subset for P03; LLM disclosure half-clause ("no LLM in extraction; regex-only") |
| Results (4 sentences) | ~110 | P01 7.6% [6.3, 9.1] of 1,420; P03 2.8% [2.0, 3.9] of 1,276; FDAAA trajectory (4.0% → 14.5% across 2017); WHO trajectory (5.8% → 2.6% across 2008); sensitivity-subset result (placeholder until run; pre-committed decision rule in §4) |
| Interpretation (2 sentences) | ~50 | FDAAA enforcement appears to have moved the needle slowly; the WHO 2008 mandate has not. Divergence implies enforcement architecture matters more than mandate text. |
| Limitations (1 sentence) | ~30 | P03 regex is a lower bound; decline partly confounded by malaria-portfolio shift toward chemoprevention/MDA, partly addressed by sensitivity analysis. |
| Framework plug (1 sentence) | ~25 | Repo URL + dashboard. |
| Figure caption | ~50 | Two-panel timeline (described in §5). Counted separately by Synthēsis. |
| **Body subtotal** | ~335 | |
| Slack | ~65 | Reserved for copy-edit + referee response. |
| **Pre-edit draft total** | ~400 (body) + 50 (caption) | Trimmed to ≤400 body. |

Pre-edit draft target: ~360w body so the published version lands at ≤400w after journal copy-edit.

## 4. Sensitivity analysis (new analytical work)

**Restriction:** drug-efficacy trials for treatment of uncomplicated *Plasmodium falciparum* malaria.

**Indication filter rules (operationalised):**
- INCLUDE if `conditions` table contains "*falciparum*" OR "uncomplicated malaria" (case-insensitive substring match)
- EXCLUDE if any condition includes: "severe", "complicated", "vivax-only", "ovale-only", "malariae-only", "prevention", "chemoprevention", "MDA", "IPTp", "vaccine"
- Carry over P03's existing drug-efficacy filter (no vaccine; drug intervention present)

**Pre-commit decision rule** (this is the integrity move; written into the spec **before** the analysis is run):

| Sensitivity result on uncomplicated-*P. falciparum* subset | Body sentence stance |
|---|---|
| Post-2008 decline persists with Δ ≤ −2 percentage points | Body retains: "the decline is not solely a portfolio-shift artefact." |
| Decline attenuates to −2 < Δ < 0 pp | Body softens: "the decline is partially attributable to portfolio shift but persists within the uncomplicated-*P. falciparum* subset." |
| Decline disappears (Δ ≈ 0) or reverses (Δ > 0) | Body pivots to honest disclosure: "the apparent decline is largely explained by portfolio shift; within indications where PCR-correction applies, compliance has been flat at ~5% throughout." |

**Why this matters:** the rule eliminates analyst degrees of freedom. The paper either lands the original thesis cleanly or pivots to a more limited but more defensible claim. Either path is reviewer-defensible. Without the rule, this becomes a P-hacking risk.

## 5. Figure D — two-panel mandate-timeline

**Layout:** two side-by-side panels in a single PNG/SVG figure, ~7" wide × ~3" tall.

**Panel 1 (left) — FDAAA results-posting compliance**
- x: primary completion year, 2004–2024
- y: % completed trials with results posted within 12 months, range 0–25%
- Line + 95% Wilson CI ribbon, year-by-year point estimates
- Years with n < 10: thinner line / lighter ribbon (low-precision flag)
- Vertical dashed line at **2017** (FDAAA Final Rule); annotated "Final Rule"
- Plain-text annotation in panel corner: "Pre-2017: 4.0% · Post-2017: 14.5%"
- No horizontal target line on plot; "target near-100%" appears in caption only

**Panel 2 (right) — WHO PCR-correction declaration in primary outcome**
- x: primary completion year, 2004–2024
- y: % drug-efficacy trials declaring PCR-correction in primary outcome, range 0–10%
- Line + 95% Wilson CI ribbon
- Vertical dashed line at **2008** (WHO 2008 mandate); annotated "WHO 2008"
- Plain-text annotation in panel corner: "Pre-2008: 5.8% · Post-2008: 2.6%"
- No horizontal target line; "target near-100%" caption only

**Caption (~50w):**
> Compliance trajectories with two reporting mandates among registered malaria trials (n = 2,277, AACT 2026-04-12). **Left:** results-posting within 12 months of primary completion (P01); FDAAA Final Rule (2017) marked. **Right:** PCR-correction declaration in primary outcome (P03); WHO 2008 mandate marked. Note differing y-axes. Ribbons = pointwise Wilson 95% CIs; years with n < 10 lightened.

**Differing-y-axes justification:** P01 ranges 0–23%, P03 ranges 0–7%. A shared axis would visually flatten P03's trajectory and lose the declining-trend story. Caption flags this explicitly.

**Implementation:**
- `paper/make_figure_d.py`: matplotlib (existing dep); reads from AACT 2026-04-12 directly (single source of truth) and writes `figures/figure-d.png` + `figures/figure-d.svg`.
- Both raster and vector outputs committed.
- Deterministic (pure aggregation; no seed).

## 6. Limitations split: body vs repo

**In paper body (one sentence, ~30w):**
> P03's regex captures only "PCR-corrected/correction/adjusted" phrasings and is a lower bound; the post-2008 decline is partially confounded by the malaria portfolio's shift toward chemoprevention/MDA, partly addressed by the uncomplicated-*P. falciparum* sensitivity analysis (Figure 1 caption note).

**In repo only (`docs/methods-paper-limitations.md`):**
- **I3 — P03 expanded-regex check.** Re-run P03 with regex covering "PCR-confirmed", "genotyping-corrected", "PCR-distinguished". Report Δ vs. headline 2.8% in the repo.
- **I4 — Preregistration sequence disclosure.** Corpus inclusion criteria were widened pre-OTS-stamp. Document timestamps in `docs/preregistration-history.md`. Cited from the paper's data-availability statement.
- **I5 — CI Sentinel-scan step.** Add Sentinel pre-push BLOCK gate to the repo's CI workflow. Separate v0.1.2 task; not visible in the paper.
- **I6 — P05 caveat.** Top-5 includes placebo + HCQ; documented in `docs/extraction_audit.md`. Mentioned in the paper only if a referee asks about other pilots.

## 7. References (Vancouver, ≤7)

| # | Citation | Purpose |
|---|---|---|
| 1 | Tasneem A, et al. *The Database for Aggregate Analysis of ClinicalTrials.gov (AACT)*. PLoS ONE 2012;7(3):e33677. | AACT data source |
| 2 | 42 CFR Part 11 (FDAAA Final Rule, 2017); Food and Drug Administration Amendments Act of 2007, Pub. L. 110-85 §801. | FDAAA mandate |
| 3 | World Health Organization. *Methods and Techniques for Clinical Trials on Antimalarial Drug Efficacy: Genotyping to Identify Parasite Populations.* Geneva: WHO; 2008. | WHO PCR-correction mandate |
| 4 | DeVito NJ, Bacon S, Goldacre B. *Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study.* Lancet 2020;395:361–9. | Cross-disease FDAAA baseline (~63% comparator) |
| 5 | Wilson EB. *Probable inference, the law of succession, and statistical inference.* JASA 1927;22:209–12. | CI method |
| 6 | World Health Organization. *Guidelines for the Treatment of Malaria* (3rd ed.). Geneva: WHO; 2015. | Defines uncomplicated *P. falciparum* indication |
| 7 (optional) | Bhatt S, et al. *The effect of malaria control on Plasmodium falciparum in Africa between 2000 and 2015.* Nature 2015;526:207–11. | Portfolio-shift context (drop if word budget tight) |

**DOI verification requirement:** every reference must be Crossref-resolved before submission. Per the portfolio's "LLM citation misattribution ~4%" rule, eyeball validation is insufficient. Implementation plan must include a `paper/refs.bib` + a verification script that runs Crossref lookup on each entry.

**DeVito 2020 fallback:** if a referee challenges the 2020 cross-disease baseline as outdated, swap-in candidate is the FDAAA TrialsTracker dashboard's current 2024-era number (verify at submission time).

## 8. Authorship & disclosures

- **Authors:** Mahmood Ahmad (solo).
- **Affiliation:** Royal Free Hospital, London.
- **ORCID:** 0009-0003-7781-4478.
- **Editorial board COI:** none — author retired from Synthēsis editorial board on 2026-04-20 (pre-dates this submission). No COI statement needed beyond standard.
- **Funding:** none. Personal time.
- **LLM disclosure:** body methods sentence includes "no LLM used in extraction; regex-only." This is a true claim about P01 and P03 specifically; the broader 10-pilot reconnaissance (P02, etc.) does use the local sha256-pinned gemma2:9b model — but those pilots are not in the body.
- **Data availability:** code at `github.com/mahmood726-cyber/malaria-ct-recon`; AACT snapshot 2026-04-12; framework HEAD `26a3fb0` preregistered 2026-04-30; design spec (this document) preregistered via OTS Bitcoin anchor on commit-and-stamp date.

## 9. Submission workflow

1. Spec written + committed + pushed (this commit).
2. Spec OTS-stamped; receipt `.ots` committed + pushed.
3. User review of spec (per brainstorming skill); approval gate.
4. Invoke writing-plans skill → produce implementation plan covering: paper/refs.bib + Crossref verification, paper/make_figure_d.py, sensitivity analysis (uncomplicated-*P. falciparum* subset), `docs/methods-paper-limitations.md`, `docs/preregistration-history.md`, P03 expanded-regex check, paper draft in .docx (Synthēsis house format), CI Sentinel-scan step.
5. Implementation phase produces all artifacts including the .docx draft.
6. Pre-commit decision rule from §4 evaluated against actual sensitivity result; body sentence locked.
7. Final draft DOI-checked for references; word-count to ≤400 body confirmed.
8. v0.2.0 tag at submission readiness; second OTS stamp on the v0.2.0 commit.
9. Synthēsis OJS submission (5-step wizard; .docx A4 1.5spc 11-pt Calibri / 12-pt TNR).
10. On acceptance: Crossref DOI minted by Synthēsis; repo `CITATION.cff` updated.

## 10. Out of scope for this Methods Note

- All other 8 pilots (P02, P04–P10) — reserved for future atlas papers.
- A full empirical paper at BMJ Global Health / Malaria Journal — out of scope; this Methods Note is scaffolding for that future paper, not a substitute.
- Replication on a non-AACT dataset (WHO ICTRP, ISRCTN, PACTR) — out of scope per P06 finding (only ~1% of malaria trials show cross-registry IDs in AACT).
- Formal time-series modelling of the trajectories (segmented regression / interrupted time series) — out of scope; the current descriptive trajectories are sufficient for the thesis. A future paper could fit ITS.

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Sensitivity analysis kills the headline (Δ ≈ 0 case in §4) | §4 pre-commit decision rule pivots the body cleanly; paper still ships. |
| Reviewer challenges DeVito 2020 as outdated baseline | §7 fallback: swap to FDAAA TrialsTracker 2024 number. |
| Reviewer asks for time-series model | §10: out of scope by design; offer in revision if needed. |
| Reviewer flags two-y-axis figure | §5 caption already discloses; defensive in advance. |
| Reviewer asks why other 8 pilots are excluded | §10: out of scope by design; framework plug + repo URL covers community access. |
| OTS calendar reachability fails at stamp time | Retry from a non-sandboxed shell; if persistent, document in `docs/preregistration-history.md` and use a non-OTS hash-witness (e.g., post the SHA256 to a public commit message on a dated branch). |
| Word budget overrun in draft | §3 reserves 65w slack; copy-edit pass to trim. |
| P03 regex undercount discovered post-publication | I3 expanded-regex check in repo (§6) provides corrective number; correction or post-publication note can cite it. |

## 12. Implementation handoff

This spec is the input to writing-plans. The plan must produce:

1. `paper/refs.bib` + `paper/verify_refs.py` (Crossref lookup) + verification CSV
2. `paper/make_figure_d.py` + `figures/figure-d.png` + `figures/figure-d.svg`
3. `pilots/p03_sensitivity_uncomplicated_falciparum.py` — runs the §4 sensitivity analysis; emits result CSV
4. `docs/methods-paper-limitations.md` — §6 body-vs-repo limitations split
5. `docs/preregistration-history.md` — §6 I4 timeline
6. `pilots/p03_expanded_regex_check.py` — §6 I3 robustness check (NOT in body; for repo only)
7. `paper/methods-note-draft.docx` — Synthēsis house format
8. `paper/methods-note-draft.md` — markdown source for the .docx (single source of truth)
9. CI workflow update: Sentinel pre-push scan step
10. v0.1.2 tag once items 1–9 merge; v0.2.0 tag at submission readiness
11. Two OTS stamps: one on this spec (now), one on v0.2.0 (at submission).
