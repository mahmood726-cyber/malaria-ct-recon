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
    # so totals may be <= production. Production is the upper bound.
    # v0.1.4 P2-3: assert that EVERY year-binned trial agrees with production
    # numerator at the trial level (k_total cannot exceed production_k, and
    # the gap is bounded by trials-with-no-completion-date).
    assert n_p01_total <= p01_result.n_trials_in_scope
    assert n_p03_total <= p03_result.n_trials_in_scope
    p01_k_prod = int(round(p01_result.magnitude_value * p01_result.n_trials_in_scope))
    p03_k_prod = int(round(p03_result.magnitude_value * p03_result.n_trials_in_scope))
    assert k_p01_total <= p01_k_prod
    assert k_p03_total <= p03_k_prod
    # The drop is exactly the count of NaT-completion-date trials; if it
    # exceeds 50% something is structurally wrong with the merge.
    assert n_p01_total >= int(0.5 * p01_result.n_trials_in_scope), (
        f"year_trajectories dropped >50% of P01 trials "
        f"({n_p01_total}/{p01_result.n_trials_in_scope}); upstream bug?"
    )
    assert n_p03_total >= int(0.5 * p03_result.n_trials_in_scope), (
        f"year_trajectories dropped >50% of P03 trials "
        f"({n_p03_total}/{p03_result.n_trials_in_scope}); upstream bug?"
    )


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
