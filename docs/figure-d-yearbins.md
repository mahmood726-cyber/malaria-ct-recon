# Figure D — year-binned trajectory data

Stashed 2026-05-02 from `scratch_d_feasibility.py` (since deleted) for use in the Methods Note figure. AACT snapshot 2026-04-12, malaria corpus n=2,277.

## P01 — results posted within 12 months by primary completion year

```
year  n     k    rate
2004    8    0   0.000
2005   21    0   0.000
2006   27    0   0.000
2007   41    1   0.024
2008   50    2   0.040
2009   50    2   0.040
2010   48    2   0.042
2011   43    1   0.023
2012   72    2   0.028
2013   76    3   0.039
2014   67    6   0.090
2015  105    3   0.029
2016   75    5   0.067
2017   56    3   0.054
2018   61    7   0.115
2019   62   10   0.161
2020   99   15   0.152
2021   66    6   0.091
2022   82   17   0.207
2023   60    8   0.133
2024   57   13   0.228
```

Pre-2017 / post-2017 split: 4.0% / 14.5% (Δ +10.5 pp).
Pre-2008 / post-2008 split: 1.0% / 9.3% (Δ +8.3 pp).

## P03 — PCR-correction declared in primary outcome by year

```
year  n     k    rate
2004    8    0   0.000
2005   23    1   0.043
2006   28    2   0.071
2007   44    3   0.068
2008   53    3   0.057
2009   54    4   0.074
2010   60    3   0.050
2011   53    0   0.000
2012   87    4   0.046
2013   88    2   0.023
2014   87    2   0.023
2015  118    3   0.025
2016  105    2   0.019
2017   73    3   0.041
2018   75    4   0.053
2019   85    2   0.024
2020  203    2   0.010
2021  140    1   0.007
2022  140    1   0.007
2023  104    2   0.019
2024  114    4   0.035
```

Pre-2008 / post-2008 split: 5.8% / 2.6% (Δ −3.2 pp; DOWN after WHO mandate).
Pre-2010 / post-2010 split: 6.2% / 2.3% (Δ −3.9 pp).
Pre-2017 / post-2017 split: 3.6% / 2.0% (Δ −1.6 pp).

## Headline contrast (for body)

P01 (FDAAA): rose from 4.0% pre-2017 to 14.5% post — slow improvement, mandate working.
P03 (WHO 2008 PCR-correction): fell from 5.8% pre-2008 to 2.6% post — declining despite mandate.

## Caveats to disclose

1. **P03 regex undercount.** Current regex `\bpcr[\s\-]?(corrected|correction|adjusted)\b` misses phrasings like "PCR-confirmed", "genotyping-corrected", "PCR-distinguished". The 2.8% headline and the year-trajectory are both lower bounds. Underdetection only strengthens the gap.
2. **P03 portfolio shift confound.** Some of the post-2010 decline reflects the malaria portfolio shifting toward MDA / IPTp / chemoprevention / vaccine trials where PCR-correction is irrelevant (no recurrent infection to distinguish from new infection). The decline within indications-where-PCR-correction-applies may be smaller; year-binning does not control for this.
3. **Wilson CIs are pointwise; no time-series model is fit.** The trajectories are descriptive.
4. **Primary-outcome text only.** PCR-correction declared in secondary outcomes or methods sections only would be missed.

## Plot recipe (for implementation)

Two-panel figure, side-by-side. Each panel:
- x-axis: primary completion year, 2004–2024
- y-axis: compliance rate (0–25% range covers both panels)
- bars or line+ribbon for point estimate + Wilson 95% CI per year
- vertical dashed line at mandate year (P01: 2017 FDAAA Final Rule; P03: 2008 WHO mandate)
- horizontal reference at "expected ≥X%" (annotated, not modelled — both mandates target near-100%)

Years with n < 10 should be visually de-emphasised (faded fill or thinner ribbon) to flag low precision.
