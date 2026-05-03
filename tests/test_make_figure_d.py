"""Test Figure D generator — outputs valid PNG + SVG with both panels."""
from pathlib import Path

import pandas as pd
import pytest

from paper import make_figure_d as mfd


def _fake_traj_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "year_trajectories.csv"
    rows = []
    for y in range(2004, 2025):
        rows.append({
            "year": y,
            "n_p01": 50 + (y - 2004) * 5,
            "k_p01": int((50 + (y - 2004) * 5) * (0.05 + (y - 2017) * 0.01 if y >= 2017 else 0.04)),
            "rate_p01": 0.0,
            "n_p03": 60 + (y - 2004) * 4,
            "k_p03": max(0, int((60 + (y - 2004) * 4) * (0.06 if y < 2008 else 0.025))),
            "rate_p03": 0.0,
        })
    df = pd.DataFrame(rows)
    df["rate_p01"] = df["k_p01"] / df["n_p01"]
    df["rate_p03"] = df["k_p03"] / df["n_p03"]
    df.to_csv(csv, index=False)
    return csv


def test_figure_d_produces_png_and_svg(tmp_path: Path):
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    assert out_png.exists() and out_png.stat().st_size > 1000
    assert out_svg.exists() and out_svg.stat().st_size > 1000
    assert out_svg.read_text(encoding="utf-8").startswith("<?xml")


def test_figure_d_two_panels(tmp_path: Path):
    """Both panels rendered (we check by parsing axis count from SVG)."""
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    svg = out_svg.read_text(encoding="utf-8")
    # matplotlib emits one <g id="axes_N"> per axes; expect 2.
    assert svg.count('id="axes_1"') == 1
    assert svg.count('id="axes_2"') == 1


def test_figure_d_deterministic(tmp_path: Path):
    csv = _fake_traj_csv(tmp_path)
    out_png_a = tmp_path / "a.png"
    out_svg_a = tmp_path / "a.svg"
    out_png_b = tmp_path / "b.png"
    out_svg_b = tmp_path / "b.svg"
    mfd.make(csv, out_png_a, out_svg_a)
    mfd.make(csv, out_png_b, out_svg_b)
    # SVG is text-deterministic when matplotlib metadata is suppressed.
    assert out_svg_a.read_bytes() == out_svg_b.read_bytes()
