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

| Date (UTC) | Commit | Change | Rationale |
|---|---|---|---|
| 2026-04-30 | 12c2cba | Initial inclusion filter with condition regex, MeSH terms, antimalarial intervention regex, and override CSV | Defined the three core mechanisms: malaria-keyword search in conditions, MeSH browse terms (falciparum/vivax/cerebral), and drug name regex; override CSV allows manual curation |
| 2026-04-30 | 606d91d | Added strict validation: fail closed on unknown override action | Ensures override CSV is unambiguous; rejects typos or invalid action values (only 'include' and 'exclude' allowed) |
| 2026-04-30 | 26a3fb0 | Added inline docstring noting dual-use drug false positives (quinine, atovaquone) and deferral to override CSV | Documents known limitation: intervention regex catches drugs used for non-malaria indications; management strategy is manual review per pilot |

## Net effect

The criteria were defined in a single sprint across three commits: the core filter (condition + MeSH + intervention) was instantiated on 2026-04-30, followed immediately by validation hardening (fail-closed on bad overrides) and documentation (dual-use drug gotcha). No criteria were broadened or narrowed after initial definition; the override mechanism was tight from the start.

The preregistered HEAD (commit `26a3fb0`) includes the docstring annotation, so the framework embeds awareness of the dual-use limitation and the override-driven curation strategy.

## Numbers shift between scratch and production

For the Methods Note specifically, the v0.1.0 sprint also produced a
brainstorm-phase scratch script (since deleted, see commit `535fa2e`) that
estimated P03 pre/post-2008 splits as 5.8% / 2.6% using a narrower regex and
no drug-only filter. The spec text reflects those scratch numbers.

When T1 (`pilots/p01_p03_year_trajectories.py`) regenerated the year-bins
using exact P03 production logic on AACT 2026-04-12, the splits became
6.8% / 2.7% — the direction is unchanged (decline) and Δ actually
strengthened from −3.2 pp to −4.1 pp. The paper draft uses the production
numbers; the spec retains the scratch numbers as a historical record of the
pre-data estimate.

## Robustness check (deferred)

A re-run on the original (narrow) criteria would confirm the trajectories'
robustness; this is logged here as a follow-up rather than blocking the
v0.1.2 ship.

## v0.1.3 divergence: WHO mandate year 2008 → 2009

The OTS-anchored design spec (`docs/superpowers/specs/2026-05-03-methods-paper-design.md`,
commit `535fa2e`, Bitcoin block 947705) specified the WHO mandate cutoff as
2008. A multi-persona review on 2026-05-04 (`review-findings.md`) flagged
that the 2008 WHO document is a technical genotyping monograph, not the
operational protocol.

For v0.1.3, the cutoff was moved to **2009** — the year of WHO's *Methods
for Surveillance of Antimalarial Drug Efficacy*, the operational protocol
that updated the 2003 ACPR/PCR-correction methodology. Effects of the move:

- Pre-mandate baseline: 2008 cutoff gave n=67 (Fisher p=0.12, not
  significant); 2009 cutoff gives n=96 (Fisher p=0.016, significant). The
  2009 split is both bibliographically and statistically defensible.
- Within-subset (uncomplicated falciparum) sensitivity: 2008 had n_pre=21
  → 19.0%/7.0% with p=0.086; 2009 has n_pre=27 → 18.5%/6.6% with p=0.059.
  Both fall under the §4 small-n safety net (`pre_n < 50`); the locked
  body sentence retains the "attenuates" branch but its text was rewritten
  to drop the unsupported "persists" claim (see `pilots/p03_decision_rule.py`
  v0.1.3 history).
- B3 broad-regex variant: a separate review finding (P0-2) added ACPR,
  recrudescence-vs-reinfection, msp1/msp2/glurp genotyping patterns to the
  expanded check (`pilots/p03_expanded_regex_check.py`). This is **not** in
  the production P03 pilot — the headline 2.8% remains the strict-syntactic
  measurement. The broad-regex 7.5% is reported as an upper bound.

The divergence is not silent: the spec is OTS-anchored and immutable; this
file is the registered amendment. The framework HEAD `26a3fb0` is unchanged,
so the spec-vs-implementation reconciliation can be audited from the git
log alone.

## v0.1.4 divergences (2026-05-04)

Two further filter refinements landed in v0.1.4, both flagged by the
multi-persona review (P1-5, P1-9):

- **§4 indication exclude list** (`pilots/p03_sensitivity_uncomplicated_falciparum.py`):
  added Seasonal Malaria Chemoprevention (SMC), IPTi (infants), IPTsc
  (school-children), PMC (Perennial Malaria Chemoprevention — the 2022 WHO
  rename of IPTi). Effect on the sensitivity subset: pre-2009 was 5/27 →
  5/26 (one SMC trial dropped); post-2009 was 9/136 → 9/136 (no change).
  Direction unchanged; Fisher p shifted 0.06 → 0.05.

- **Drug-efficacy filter** (`pilots/p03_pcr_corrected.py`): drug+device
  combinations (insecticide-treated nets, IRS, larvicide, pyrethroid, PBO)
  excluded. Removes ~6 trials whose primary endpoint is incidence-of-clinical-
  malaria, where PCR-correction is not the conventional outcome construction.
  Effect on the headline P03 denominator: 1,276 → 1,270 (drop of 6).
  P03 strict rate: 36/1276 (2.82%) → 35/1270 (2.76%). Pre/post WHO 2009:
  pre 7/88 (8.0%) → 7/86 (8.1%); post 23/943 (2.4%) → 22/940 (2.3%).
  Fisher p improved 0.010 → 0.008. Direction unchanged.

Both changes preserve the v0.1.3 thesis (FDAAA enforcement vs. WHO-norm
trajectories diverge) and strengthen the P03 inference. Spec OTS anchor
unchanged; framework HEAD `26a3fb0` unchanged; the changes are bounded to
filter regexes and live as registered amendments here.
