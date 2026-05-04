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


def test_figure_d_empty_csv_raises(tmp_path: Path):
    """Empty CSV (or all rows outside 2004–2024) should fail closed, not crash."""
    csv = tmp_path / "empty.csv"
    csv.write_text(
        "year,n_p01,k_p01,rate_p01,n_p03,k_p03,rate_p03\n",
        encoding="utf-8",
    )
    out_png = tmp_path / "x.png"
    out_svg = tmp_path / "x.svg"
    with pytest.raises(ValueError, match="No rows in year range"):
        mfd.make(csv, out_png, out_svg)


def test_figure_d_dashboard_in_sync_with_figures():
    """v0.1.5 P0-A: dashboard/figure-d.{png,svg} must be byte-identical to figures/.

    GitHub Pages publishes dashboard/, so any drift between figures/ and
    dashboard/ leaks v0.1.3-era numbers to the public site. Caught a real
    drift in the v0.1.4 review.
    """
    import hashlib
    repo = Path(__file__).parent.parent
    pairs = [
        (repo / "figures" / "figure-d.png", repo / "dashboard" / "figure-d.png"),
        (repo / "figures" / "figure-d.svg", repo / "dashboard" / "figure-d.svg"),
    ]
    for src, dst in pairs:
        if not src.exists():
            pytest.skip(f"{src} not present (fresh clone before run); skipping")
        assert dst.exists(), f"{dst} missing — run `python -m paper.make_figure_d`"
        src_md5 = hashlib.md5(src.read_bytes()).hexdigest()
        dst_md5 = hashlib.md5(dst.read_bytes()).hexdigest()
        assert src_md5 == dst_md5, (
            f"{dst.name} drift: {src} != {dst}; "
            "re-run `python -m paper.make_figure_d` (which auto-syncs)."
        )


def test_figure_d_svg_has_a11y_title_desc(tmp_path: Path):
    """v0.1.5 P0-A regression: WCAG SC 1.1.1 — SVG must have <title> + <desc>."""
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    svg = out_svg.read_text(encoding="utf-8")
    # Title must appear once at top level; desc must appear once.
    assert svg.count("<title>") >= 1
    assert "<desc>" in svg
    # Descriptive text must mention both panels (FDAAA + WHO).
    assert "FDAAA" in svg
    assert "WHO 2009" in svg


def test_figure_d_svg_a11y_idempotent(tmp_path: Path):
    """v0.1.5 P0-A: re-running make() must not duplicate <title>/<desc>."""
    csv = _fake_traj_csv(tmp_path)
    out_png = tmp_path / "figure-d.png"
    out_svg = tmp_path / "figure-d.svg"
    mfd.make(csv, out_png, out_svg)
    n_title_first = out_svg.read_text(encoding="utf-8").count("<title>")
    # Manually re-run the inject step (idempotency contract).
    mfd._inject_svg_a11y(out_svg, title="Different title", desc="Different desc")
    n_title_second = out_svg.read_text(encoding="utf-8").count("<title>")
    assert n_title_first == n_title_second, "a11y inject not idempotent"
