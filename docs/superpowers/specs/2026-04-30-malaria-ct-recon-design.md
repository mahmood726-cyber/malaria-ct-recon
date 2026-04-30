# Malaria CT.gov Reconnaissance — Design

**Date:** 2026-04-30
**Author:** Mahmood
**Status:** Draft v1 — pending user review
**Repo:** `github.com/mahmood726-cyber/malaria-ct-recon` (to be created)
**Snapshot:** AACT pipe-delimited TXT export, frozen at `D:/AACT-storage/AACT/2026-04-12/`

---

## 1. Goal

A 10-pilot reconnaissance sprint over malaria trials in CT.gov to identify the 1–2 strongest sources of bias in malaria efficacy meta-analyses. Pilots feed three deliverables:

1. **Methods paper** — 10-issue audit of malaria CT.gov data quality (BMJ Global Health or Trials).
2. **Focused atlas** — top 1–2 pilot winners grown into a full atlas (CSV + dashboard + Synthēsis Methods Note).
3. **Opportunistic E156** — a 156-word micro-paper for Synthēsis, contingent on whether the headline of the top pilot fits cleanly in 156 words. Not committed upfront.

**Implementation-plan scope:** the implementation plan that follows this design covers ONLY the sprint (preflight + 10 pilots + dashboard + v0.1.0 tag). The methods paper, focused atlas, and opportunistic E156 each get their own subsequent design + plan once the sprint signal-table is in hand.

## 2. Why this is groundbreaking

Five reasons:

- **No prior systematic data-quality audit of malaria trials in CT.gov exists.** Cross-disease audits (e.g., FDAAA compliance, outcome switching) treat malaria as a small subgroup. A targeted audit can isolate malaria-specific failure modes invisible at the cross-disease level.
- **Most malaria trials are non-FDA-regulated.** FDAAA results-posting law applies only to FDA-regulated drugs/devices in trials with at least one US site. Most malaria trials run entirely in sub-Saharan Africa or SE Asia on WHO-prequalified (not FDA-regulated) drugs, so FDAAA exemption is the default. The actual CT.gov results-posting rate for this population is unaudited. Note: this is distinct from the trial-to-publication linkage rate (~63.6% cross-disease, per TrialScout/medRxiv 2026.03.15) — results-posting and publication are separate compliance regimes.
- **The malaria endpoint space is genuinely heterogeneous.** At least 6 disjoint primary-endpoint families. Cochrane MAs that pool across families produce nonsense, but no one has quantified how often this happens.
- **The resistance landscape changed under existing MAs.** K13 mutations (~2008) made artemisinin-era trials non-exchangeable with pre-K13 trials of the same drug. MAs that ignore this give wrong answers.
- **PCR-corrected outcome reporting is WHO-mandated but uncompliance is unaudited.** Without genotyping, "treatment failure" rate mechanically inflates because reinfection is misclassified as recrudescence.

## 3. Scope

**In scope:**
- 10 pilots over the AACT 2026-04-12 snapshot
- Methods paper (10-issue audit) — drafting after pilots conclude
- One focused atlas on the top pilot(s) — built after paper draft
- Opportunistic E156 if the headline is sharp enough

**Out of scope:**
- PACTR, ICTRP, ISRCTN, ANZCTR scrapers (cross-registry coverage flagged as data-untractable)
- MAP project transmission-intensity rasters (geographic heterogeneity flagged as data-untractable)
- WWARN molecular-resistance data (resistance pilot uses temporal proxy only)
- Live malaria-MA engine (cardiosynth-style)
- RapidMeta-style screening UI for malaria
- Vivax-vs-falciparum methodology audit (dropped — well-known issue, no surprise potential; vivax trials remain in corpus)
- Vector-control cluster-RCT design-effect audit (dropped — not malaria-specific; vector-control trials remain in corpus)

## 4. The 10 pilots

Pilots P01–P10 are numbered for the paper. Each pilot is a single Python script that reads from frozen AACT TXT files and writes one CSV row to `pilots/results/<pilot>.csv`.

| # | Pilot | Question | AACT tables | Type |
|---|---|---|---|---|
| P01 | Reporting compliance | What fraction of completed malaria trials post results to CT.gov within 12mo, stratified by FDA-regulated status? | studies, calculated_values, sponsors | Magnitude |
| P02 | Endpoint-family chaos | How many distinct primary-endpoint families exist in the malaria corpus, and what fraction of trials mix families? | design_outcomes, outcomes | Magnitude |
| P03 | PCR-corrected outcome reporting | What fraction of efficacy trials report PCR-genotyping for recrudescence-vs-reinfection distinction? | design_outcomes, outcomes, brief_summaries | Magnitude (text-mining) |
| P04 | Resistance-era pooling | Distribution of trial start_date for ACT-class interventions by country; identify pre-K13 (≤2008) vs post-K13 (≥2015) trials of the same drug | studies, interventions, countries | Magnitude |
| P05 | Pediatric dose fragmentation | For the 5 most-frequent antimalarial intervention names in the corpus (ranked by trial count), count distinct intervention dose strings stratified by enrolled age band (<5y, 5–11y, 12–17y, ≥18y per `eligibilities.minimum_age`/`maximum_age`) | interventions, eligibilities | Magnitude |
| P06 | Cross-registry coverage | Of malaria trials with `id_information.id_value` matching PACTR/ISRCTN patterns, what fraction *also* have a CT.gov registration? | id_information, studies | Tractability probe (AACT-only ceiling) |
| P07 | Sponsor classification | What fraction of malaria trials have a PDP sponsor (MMV, PATH MVI, Sanaria, FIND, DNDi, Aeras) misclassified as "OTHER" by AACT's `agency_class`? | sponsors | Magnitude |
| P08 | Retrospective registration | Of malaria trials, what fraction have `start_date < first_received_date` (registered after starting)? Stratified pre-2007 vs post-2007 | studies | Magnitude |
| P09 | Geographic transmission heterogeneity | Distribution of trial site countries; flag MAs that mix high-transmission (sub-Saharan Africa) and low-transmission (SE Asia) sites for the same intervention | facilities, countries | Tractability probe (AACT-only ceiling) |
| P10 | CHMI vs field mixing | Identify CHMI (controlled human malaria infection) trials by intervention/eligibility text; compute fraction of malaria-vaccine MAs at risk of pooling CHMI + field trials | interventions, eligibilities, brief_summaries | Magnitude |

**Two pilots (P06, P09) are tractability probes**, not magnitude probes. Their "result" is "AACT alone cannot answer this; the data lives in PACTR / MAP project." Recording this is itself a finding for the methods paper — it bounds what AACT can and cannot tell us about malaria trial quality.

**Pilot sub-filters:** several pilots apply additional filters within the corpus. Each pilot script declares its sub-filter and reports `n_trials_in_scope` (denominator after sub-filtering) plus `n_trials_excluded_for_reason`. Examples:

- P03 (PCR-corrected reporting) restricts to *efficacy* trials of antimalarial drugs (excludes vaccines, PK studies, vector control, and diagnostics)
- P04 (resistance-era pooling) restricts to artemisinin-class-containing interventions
- P05 (pediatric dose fragmentation) restricts to the top-5 antimalarials by trial count
- P10 (CHMI vs field mixing) identifies CHMI trials by intervention/eligibility text patterns and reports the malaria-vaccine-trial subset

The full corpus (~1,300–1,500 trials) is the denominator only for pilots P01, P02, P07, P08 (and the tractability probes P06, P09).

## 5. Inclusion filter

Defining "malaria trial" needs an actual algorithm — `condition LIKE '%malaria%'` over-includes (HIV+malaria co-condition trials where malaria is incidental) and under-includes (trials labelled only by drug name like "artemether-lumefantrine pharmacokinetics").

**Inclusion algorithm:**
```
INCLUDE trial if ANY of:
  (a) conditions.name matches /malaria|plasmodium|falciparum|vivax|ovale|malariae|knowlesi/i
  (b) browse_conditions.mesh_term IN {"Malaria", "Malaria, Falciparum", "Malaria, Vivax",
       "Malaria, Cerebral", "Plasmodium falciparum", "Plasmodium vivax"}
  (c) interventions.name matches one of the WHO-listed antimalarials:
       /artemether|artesunate|artemisinin|lumefantrine|amodiaquine|piperaquine|
        mefloquine|chloroquine|primaquine|tafenoquine|quinine|sulfadoxine|
        pyrimethamine|atovaquone|proguanil|dihydroartemisinin|artefenomel|
        ferroquine|RTS,S|R21|PfSPZ|Mosquirix|MSP|AMA1|CSP/i

EXCLUDE trial if:
  - It matches inclusion (a) on a string like "anti-malarial diet" / "malaria-endemic
    region" used incidentally, AND has no malaria-specific MeSH term, AND no
    antimalarial intervention. (Implementation: keep all trials passing inclusion;
    flag for manual review any whose ONLY match is a substring inside a longer phrase
    in the conditions.name field. Exclusion list lives in corpus_overrides.csv.)

Manual override: corpus_overrides.csv lists explicit include/exclude NCT IDs for
edge cases discovered during pilots. Both lists are version-controlled and
auditable. No silent drops.
```

Expected corpus size: ~1,300–1,500 trials (vs CT.gov's surface count of 1,462 for `condition=malaria`).

## 6. Output schema

Each pilot writes one row to `pilots/results/<pilot>.csv` with this schema:

| Column | Type | Description |
|---|---|---|
| `pilot_id` | str | P01–P10 |
| `pilot_title` | str | Short title |
| `pilot_type` | enum | `magnitude` or `tractability_probe` |
| `n_trials_in_scope` | int | Denominator |
| `magnitude_value` | float | Primary headline number (NaN for tractability probes) |
| `magnitude_unit` | str | e.g., "fraction", "count", "ratio" |
| `magnitude_ci_low` | float | 95% CI lower (Wilson for proportions, bootstrap otherwise) |
| `magnitude_ci_high` | float | 95% CI upper |
| `tractability_AACT_only` | enum | `full`, `partial`, `none` |
| `follow_up_potential` | int | 1–5: how strong an atlas/paper the issue could grow into |
| `n_trials_excluded_for_reason` | json | `{reason: count}` audit of exclusions |
| `notes` | str | One-line interpretation |
| `script_path` | str | Relative path to pilot script |
| `script_sha256` | str | SHA256 of the pilot script at run time |
| `aact_snapshot` | str | "2026-04-12" |
| `seed` | int | RNG seed used |
| `wall_clock_seconds` | float | Pilot runtime |

Master `signal-table.csv` aggregates all 10 rows; ranked view in `dashboard/index.html`.

## 7. Tech stack

- **Language:** Python 3.11+
- **Query engine:** `duckdb` directly against AACT TXT files (no Postgres needed; duckdb reads pipe-delimited TSV natively)
- **Stats:** `scipy.stats` for Wilson CIs; `numpy` for bootstrap
- **Dashboard:** single self-contained `dashboard/index.html` with vanilla JS + inline SVG (no CDN, no build step) — same pattern as `responder-floor-atlas`
- **Tests:** `pytest`; one test per pilot asserting (a) script runs deterministically with seed, (b) output schema matches, (c) magnitude is in plausible range
- **Pre-push:** Sentinel hook installed (`python -m sentinel install-hook --repo C:/Projects/malaria-ct-recon`)
- **Pages:** GitHub Actions deploys `dashboard/` to Pages on push to master

## 8. Reproducibility contract

- AACT snapshot **frozen** at `D:/AACT-storage/AACT/2026-04-12/` for the entire sprint and paper. Do NOT pull a fresher snapshot mid-sprint; if a republication needs fresher data, re-run the full pipeline against the new snapshot and report both.
- All pilots use a fixed seed (`SEED=20260430`).
- All pilot scripts SHA256-pinned at run time and recorded in their output row.
- OTS (OpenTimestamps) timestamp committed before pilot 1 runs — same discipline as PI Atlas, Responder Floor.
- Crossref DOI on v0.1.0 tag at publication; Zenodo DOI on every numbered release.
- `pytest -q` must be 0-fail before any commit on master.
- Sentinel must report 0 BLOCK before push.

## 9. Deliverables and timing

| Artefact | Timing | Target | Status |
|---|---|---|---|
| `malaria-ct-recon` repo + 10 pilots + dashboard + v0.1.0 tag | Week 1 (5-evening target, 7-evening hard cap) | github.io Pages | Committed |
| Methods paper draft (10-issue audit) | Week 2–3 | BMJ Global Health or Trials | Committed |
| Focused atlas v0.1.0 (top 1–2 pilots grown) | Week 4–6 | Synthēsis Methods Note + dashboard | Committed |
| E156 micro-paper | Opportunistic | Synthēsis 156w | Conditional |

**Sprint hard cap:** if any pilot is taking more than 2 evenings, downgrade it to "tractable but expensive" and move on. The point of the sprint is *signal*, not *finished pilot*.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| AACT inclusion filter under- or over-includes | Manual `corpus_overrides.csv` + bootstrap-validate corpus size against CT.gov surface count (1,462) |
| No pilot produces a sharp headline | E156 doesn't ship; methods paper still ships. Acceptable. |
| Sentinel pre-push hook blocks on a P0 (e.g., hardcoded `D:/` path) | Use config file `aact_path.toml` for the snapshot location; fail-closed if not set |
| AACT snapshot has known issue (missing `studies.txt`, broken column) | Pilot 0 (preflight) verifies all required tables load and have expected columns before any other pilot runs |
| BMJ Global Health rejects | Re-target Trials, then PLOS Global Public Health, then submit to F1000 with reviewer-mediated revision |
| Scope creep into a 13th, 14th pilot | 7-evening cap + the 10 pilots are pre-registered in the OTS-timestamped commit — adding more after-the-fact requires an explicit amendment |
| Vivax/vector-control trials in corpus contaminate species- or design-specific pilot results | Each pilot script declares whether it filters them out; recorded in `n_trials_excluded_for_reason` |

## 11. Defaults locked

- **Repo:** `github.com/mahmood726-cyber/malaria-ct-recon`
- **License:** MIT (per portfolio default)
- **Branching:** trunk-based on `master`; tags for releases (`v0.1.0`, `v0.2.0`, …)
- **Dependencies:** `pyproject.toml` declares `python>=3.11`, `duckdb>=1.0`, `pandas>=2.2`, `scipy>=1.13`, `pytest>=8`, `pytest-cov`. Pin in `requirements.txt`.
- **Author block:** per `feedback_e156_authorship.md` (middle-author-only on E156, full on methods paper)
- **CI:** GitHub Actions running `pytest -q` + Sentinel scan on push

## 12. Pre-pilot preflight (Pilot 0)

Before any of P01–P10 runs, a preflight script must verify:

1. AACT snapshot path resolves (`D:/AACT-storage/AACT/2026-04-12/`)
2. All required AACT tables load with `duckdb.read_csv(..., delim='|')` and have expected columns (assertion list in `pilots/preflight.py`)
3. Inclusion filter returns a corpus of 1,200–1,600 trials (sanity range)
4. Random sample of 20 trials from the corpus survives manual eyeball check (auto-flag if any look like obvious false positives)
5. `pytest` passes
6. Sentinel returns 0 BLOCK

Preflight failure halts the sprint. This is the lessons-learned application of "Preflight external prereqs BEFORE starting a multi-task plan" — the rule that EvidenceForecast Phase-1 violated and lost 16 tasks of work to.

## 13. Open questions for user review

None. All decisions resolved during brainstorming. If user spots a gap in this design, log it here and re-version the doc.

---

## Appendix A: pilot signal-table mockup

What `signal-table.csv` will look like after the sprint (illustrative numbers, NOT a prediction):

```
pilot_id,pilot_title,pilot_type,n_trials,magnitude,unit,ci_low,ci_high,tractability,follow_up
P01,Reporting compliance,magnitude,1342,0.31,fraction,0.28,0.34,full,4
P02,Endpoint-family chaos,magnitude,1342,0.47,fraction,0.44,0.50,full,5
P03,PCR-corrected reporting,magnitude,624,0.42,fraction,0.38,0.46,full,5
P04,Resistance-era pooling,magnitude,318,0.71,fraction,0.66,0.76,full,5
P05,Pediatric dose fragmentation,magnitude,287,8.3,distinct_doses_per_drug,6.1,10.5,full,3
P06,Cross-registry coverage,tractability_probe,1342,NaN,,,,partial,2
P07,Sponsor PDP misclass,magnitude,1342,0.18,fraction,0.16,0.20,full,3
P08,Retrospective registration,magnitude,1342,0.34,fraction,0.31,0.37,full,3
P09,Geographic transmission het,tractability_probe,1342,NaN,,,,none,2
P10,CHMI vs field mixing,magnitude,84,0.27,fraction,0.18,0.36,full,4
```

The two highest `follow_up` values are the candidates to grow into the atlas. In this illustrative table, P02/P03/P04 tie at 5, suggesting an atlas combining "endpoint-family chaos" + "resistance-era pooling" — exactly the prior I bet on.
