"""Test §4 decision-rule applicator."""
import json
from pathlib import Path

import pandas as pd
import pytest

from pilots import p03_decision_rule as dr


def test_persists_branch():
    """Δ ≤ -2 pp ⇒ retains."""
    out = dr.apply(pre_rate=0.058, post_rate=0.026, pre_n=50, post_n=400)
    assert out["band"] == "persists"
    assert "not solely a portfolio-shift" in out["body_sentence"]


def test_attenuates_branch():
    """-2 < Δ < 0 ⇒ softens."""
    out = dr.apply(pre_rate=0.040, post_rate=0.030, pre_n=50, post_n=400)
    assert out["band"] == "attenuates"
    assert "partially attributable" in out["body_sentence"]


def test_disappears_branch():
    """Δ ≥ 0 ⇒ pivots."""
    out = dr.apply(pre_rate=0.030, post_rate=0.030, pre_n=50, post_n=400)
    assert out["band"] == "disappears"
    assert "largely explained by portfolio shift" in out["body_sentence"]


def test_small_n_safety_net():
    """If pre_n < 50, default to attenuates regardless of Δ."""
    out = dr.apply(pre_rate=0.058, post_rate=0.026, pre_n=12, post_n=400)
    assert out["band"] == "attenuates"
    assert "small pre-mandate sample" in out["notes"]


def test_from_csv(tmp_path: Path):
    """Reads the sensitivity CSV and writes a JSON report."""
    csv = tmp_path / "sens.csv"
    csv.write_text(
        "year,n,k,rate\n"
        "2005,40,2,0.05\n2006,30,2,0.067\n2007,30,1,0.033\n"
        "2010,200,4,0.02\n2015,200,2,0.01\n2020,200,2,0.01\n",
        encoding="utf-8",
    )
    out_path = tmp_path / "decision.json"
    dr.from_csv(csv, out_path, mandate_year=2008)
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert "band" in payload and "body_sentence" in payload
    assert payload["mandate_year"] == 2008
