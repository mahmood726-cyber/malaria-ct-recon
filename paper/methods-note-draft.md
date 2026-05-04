---
title: "Two reporting requirements, opposite directions: undercompliance trajectories in 2,277 registered malaria trials"
author: "Mahmood Ahmad"
affiliation: "Royal Free Hospital, London"
orcid: "0009-0003-7781-4478"
target: "Synthēsis Methods Note"
---

# Two reporting requirements, opposite directions: undercompliance trajectories in 2,277 registered malaria trials

**Question.** Do malaria trials registered on ClinicalTrials.gov comply with two reporting requirements — the FDAAA (Food and Drug Administration Amendments Act 2007 §801) results-posting mandate [2] and WHO PCR-correction declaration in primary outcomes [3]?

**Methods.** AACT (Aggregate Analysis of ClinicalTrials.gov) snapshot of 2026-04-12 [1]; n = 2,277 registered malaria trials. P01 = fraction of completed trials posting results within 12 months of primary completion. P03 = fraction of drug-efficacy trials whose primary-outcome text declares PCR-correction; strict regex (explicit phrasing) plus broad regex covering ACPR, recrudescence-vs-reinfection, and msp1/msp2/glurp genotyping. Wilson 95 % CIs [5]; year-bins 2004–2024 (NaT dropouts: P01 10.1 %, P03 6.7 %); pre/post Fisher tests; sensitivity on uncomplicated-*P. falciparum* [6]. No LLM; regex-only.

**Results.** Compliance is below target for both mandates: P01 = 7.6 % [6.3, 9.1] of 1,420 completed trials; P03 = 2.8 % [2.0, 3.8] strict / 7.5 % [6.2, 9.1] broad of 1,270 drug-efficacy trials. Trajectories diverge across enactment years: FDAAA results-posting rose from 4.0 % [2.7, 5.7] pre-2017 to 14.5 % [11.8, 17.8] post-2017 (Final Rule, Fisher p < 0.001), while WHO PCR-correction declaration fell from 8.1 % [4.0, 15.9] pre-2009 to 2.3 % [1.6, 3.5] post-2009 (Fisher p = 0.008). Sensitivity on uncomplicated-*P. falciparum* (n = 162) gave pre-2009 19.2 % [8.5, 37.9] (n_pre = 26) vs post-2009 6.6 % [3.5, 12.1] (Fisher p = 0.05); within the uncomplicated-falciparum subset the same direction holds but the small pre-mandate sample renders the within-subset trend inconclusive.

**Interpretation.** FDAAA enforcement moved the needle measurably across nearly two decades; the WHO methodological standard did not. Malaria-specific FDAAA compliance still trails the cross-disease benchmark [4] by roughly threefold, consistent with audit infrastructure — not mandate text alone — being the active ingredient.

**Limitations.** P03 strict regex is a lower bound; broad (ACPR-inclusive) is upper. WHO cutoff = 2009 (operational protocol); 2008 yields p = 0.08. The post-2009 decline is partially confounded by portfolio shift toward chemoprevention and mass drug administration (MDA). P01 measures CT.gov results-posting (≠ peer-reviewed publication). Trials registered only in PACTR/CTRI/ISRCTN are outside this corpus.

**Data availability.** Code, AACT 2026-04-12 corpus manifest, and signal table at `github.com/mahmood726-cyber/malaria-ct-recon`; framework HEAD `26a3fb0` preregistered 2026-04-30; design spec preregistered via OpenTimestamps Bitcoin anchor 2026-05-03 (commit `535fa2e`). Full 10-pilot reconnaissance and dashboard are open at the same URL.

<!-- figure-caption-begin -->
**Figure 1.** Compliance trajectories with two reporting requirements among registered malaria trials (n = 2,277, AACT 2026-04-12). **Left:** results-posting within 12 months of primary completion (P01); FDAAA Final Rule (2017) marked. **Right:** PCR-correction declaration in primary outcome (P03, strict regex); WHO 2009 marked. Differing y-axes. Ribbons: pointwise Wilson 95 % CIs; n < 10 shown as open circles.
<!-- figure-caption-end -->

**Conflicts of interest.** None.

**Funding.** None. Personal time.

## References

1. Tasneem A, et al. The Database for Aggregate Analysis of ClinicalTrials.gov (AACT). PLoS ONE 2012;7(3):e33677. doi:10.1371/journal.pone.0033677
2. U.S. Department of Health and Human Services. Clinical Trials Registration and Results Information Submission (Final Rule, 42 CFR Part 11). Federal Register 2017;81(183):64981–65157. Implements FDAAA 2007 §801, Pub. L. 110-85.
3. World Health Organization. Methods for Surveillance of Antimalarial Drug Efficacy. Geneva: WHO; 2009.
4. DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet 2020;395:361–9. doi:10.1016/S0140-6736(19)33220-9
5. Wilson EB. Probable inference, the law of succession, and statistical inference. J Am Stat Assoc 1927;22:209–12. doi:10.1080/01621459.1927.10502953
6. World Health Organization. Guidelines for the Treatment of Malaria, 3rd ed. Geneva: WHO; 2015.
