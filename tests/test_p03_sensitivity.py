"""Test the uncomplicated-falciparum sensitivity subset filter for P03."""
from pathlib import Path

import pandas as pd
import pytest

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
