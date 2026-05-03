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

### I7 — P03 sensitivity EXCLUDE-list literalism

**Concern.** The §4 sensitivity analysis EXCLUDE list is literally what spec §4
specified: `severe`, `complicated`, `vivax-only`, `ovale-only`,
`malariae-only`, `prevention`, `chemoprevention`, `mda`, `iptp`, `vaccine`.
A code review identified that this misses some real AACT condition phrasings:
"Mass Drug Administration" without the abbreviation, "Preventive treatment",
"Prophylaxis"/"Prophylactic", and bare "Plasmodium Vivax" (only the hyphenated
"vivax-only" is excluded).

**Mitigation.** Honoring the OTS-anchored spec literally is the integrity
move; expanding the EXCLUDE list post-data would defeat the pre-commit. The
small-n safety net fired on the resulting subset (pre_n=25 < 50) producing
"attenuates" — this verdict is robust to the EXCLUDE-list gaps because the
safety net is more conservative than the Δ-driven branches. A future v0.2
follow-up may add an "expanded-EXCLUDE" robustness check mirroring I3's
expanded-INCLUDE check, reported in the repo (not the body).
