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

**Results.** Compliance is roughly an order of magnitude below target for both mandates: P01 = 7.6 % [6.3, 9.1] of 1,420 completed trials; P03 = 2.8 % [2.0, 3.9] of 1,276 drug-efficacy trials. The trajectories diverge across the two mandates' enactment years: FDAAA results-posting compliance rose from 4.0 % pre-2017 to 14.5 % post-2017 (Final Rule), while WHO PCR-correction declaration fell from 6.8 % pre-2008 to 2.7 % post-2008. A sensitivity analysis on drug-efficacy trials for uncomplicated-*P. falciparum* malaria (n = 186; pre-2008 16.0 %, post-2008 6.83 %; small pre-mandate sample n_pre = 25) found: the decline is partially attributable to portfolio shift but persists within the uncomplicated-falciparum subset.

**Interpretation.** FDAAA enforcement appears to have moved the needle slowly across nearly two decades; the WHO 2008 mandate has not. The divergence implies that audit and enforcement architecture matter more than mandate text [4].

**Limitations.** P03's regex captures only "PCR-corrected/correction/adjusted" phrasings and is a lower bound; the post-2008 decline is partially confounded by the malaria portfolio's shift toward chemoprevention/MDA [7], partly addressed by the uncomplicated-*P. falciparum* sensitivity analysis.

**Data availability.** Code, AACT 2026-04-12 corpus manifest, and signal table at `github.com/mahmood726-cyber/malaria-ct-recon`; framework HEAD `26a3fb0` preregistered 2026-04-30; design spec preregistered via OpenTimestamps Bitcoin anchor 2026-05-03 (commit `535fa2e`). Full 10-pilot reconnaissance and dashboard are open at the same URL.

<!-- figure-caption-begin -->
**Figure 1.** Compliance trajectories with two reporting mandates among registered malaria trials (n = 2,277, AACT 2026-04-12). **Left:** results-posting within 12 months of primary completion (P01); FDAAA Final Rule (2017) marked. **Right:** PCR-correction declaration in primary outcome (P03); WHO 2008 mandate marked. Note differing y-axes. Ribbons are pointwise Wilson 95 % CIs; years with n < 10 lightened.
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
