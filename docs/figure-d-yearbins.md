# Figure D — year-binned trajectory data

Regenerated 2026-05-02 from `pilots/p01_p03_year_trajectories.py` (production-matched logic). AACT snapshot 2026-04-12, malaria corpus n=2,277. Year range shown: 2004–2024 (the CSV `pilots/results/year_trajectories.csv` contains all years 1992–2035; years outside 2004–2024 have very small n or are future estimated dates and are excluded from the figure).

Aggregate check: year-bins (2004–2024) sum to P01 n=1,226 k=106 (production: 1,420/108); P03 n=1,031 k=30 (production: 1,276/36). Shortfall = trials with missing primary_completion_date, as expected (year-bins ≤ production, constraint satisfied).

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

Pre-2017 / post-2017 split: 4.0% (27/683) / 14.5% (79/543) (Δ +10.6 pp).
Pre-2008 / post-2008 split: 1.0% (1/97) / 9.3% (105/1129) (Δ +8.3 pp).

## P03 — PCR-correction declared in primary outcome by year

```
year  n     k    rate
2004    1    0   0.000
2005   16    1   0.062
2006   13    2   0.154
2007   29    1   0.034
2008   29    3   0.103
2009   33    3   0.091
2010   35    1   0.029
2011   27    0   0.000
2012   53    3   0.057
2013   47    1   0.021
2014   52    2   0.038
2015   63    2   0.032
2016   63    1   0.016
2017   37    2   0.054
2018   40    2   0.050
2019   43    1   0.023
2020  172    2   0.012
2021   95    0   0.000
2022   76    1   0.013
2023   45    0   0.000
2024   62    2   0.032
```

Pre-2008 / post-2008 split: 6.8% (4/59) / 2.7% (26/972) (Δ −4.1 pp; DOWN after WHO mandate).
Pre-2010 / post-2010 split: 8.3% (10/121) / 2.2% (20/910) (Δ −6.1 pp).
Pre-2017 / post-2017 split: 4.3% (20/461) / 1.8% (10/570) (Δ −2.6 pp).

## Headline contrast (for body)

P01 (FDAAA): rose from 4.0 % [2.7, 5.7] pre-2017 to 14.5 % [11.8, 17.8] post-2017 (Fisher p < 0.001) — enforcement-driven improvement.
P03 (WHO 2009 PCR-correction): fell from 8.1 % [4.0, 15.9] pre-2009 to 2.3 % [1.6, 3.5] post-2009 (Fisher p = 0.008) — declining despite the operational guideline.

(v0.1.3 amended the WHO cutoff from 2008 → 2009 because the 2008 doc is a technical genotyping monograph, not the operational protocol. v0.1.4 narrowed the P03 denominator from 1,276 → 1,270 by excluding drug+device combo trials. Both changes documented in `preregistration-history.md`.)

Note: P03 year-bin denominators differ from the scratch script because this version applies the production drug-only filter (excludes vaccine trials, trials with no primary outcomes in design_outcomes) and uses the full production PCR regex (_PCR_RX). The scratch script used a narrower regex and no drug-only filter. The "decline after WHO mandate" direction is unchanged; magnitudes shift modestly.

## Caveats to disclose

1. **P03 regex undercount.** Current regex `PCR-corrected|PCR adjusted|PCR-adjusted|genotypically.corrected|genotype-corrected|molecularly.corrected` misses phrasings like "PCR-confirmed", "PCR-distinguished". The 2.8% headline and the year-trajectory are both lower bounds. Underdetection only strengthens the gap.
2. **P03 portfolio shift confound.** Some of the post-2010 decline reflects the malaria portfolio shifting toward MDA / IPTp / chemoprevention / vaccine trials where PCR-correction is irrelevant (no recurrent infection to distinguish from new infection). The decline within indications-where-PCR-correction-applies may be smaller; year-binning does not control for this.
3. **Wilson CIs are pointwise; no time-series model is fit.** The trajectories are descriptive.
4. **Primary-outcome text only.** PCR-correction declared in secondary outcomes or methods sections only would be missed.
5. **Missing primary_completion_date.** Year-bins exclude ~12–14% of trials (194 P01 trials, 245 P03 trials) due to missing dates; aggregate year-bin totals are therefore lower bounds of the production headline denominators.

## Plot recipe (for implementation)

Two-panel figure, side-by-side. Each panel:
- x-axis: primary completion year, 2004–2024
- y-axis: compliance rate (0–25% range covers both panels)
- bars or line+ribbon for point estimate + Wilson 95% CI per year
- vertical dashed line at mandate year (P01: 2017 FDAAA Final Rule; P03: 2009 WHO operational protocol)
- horizontal reference at "expected ≥X%" (annotated, not modelled — both mandates target near-100%)

Years with n < 10 should be visually de-emphasised (faded fill or thinner ribbon) to flag low precision.
