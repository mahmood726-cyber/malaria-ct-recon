"""Figure D — two-panel mandate-timeline (P01 FDAAA-results, P03 WHO-PCR).

Per spec §5 of 2026-05-03-methods-paper-design.md.

Reads pilots/results/year_trajectories.csv (T1 output) and writes
figures/figure-d.png + figures/figure-d.svg. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Suppress non-deterministic SVG metadata (creator timestamp etc.).
matplotlib.rcParams["svg.hashsalt"] = "malaria-ct-recon"
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["pdf.fonttype"] = 42


def _wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    from scipy.stats import norm  # local import to keep top-level light

    z = norm.ppf(1 - alpha / 2)
    phat = k / n
    denom = 1 + z**2 / n
    centre = (phat + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return max(0.0, centre - half), min(1.0, centre + half)


def _panel(ax, years, n, k, rate, mandate_year, mandate_label, ann_text, y_max, title,
           ann_xy=None):
    ci = [_wilson(int(ki), int(ni)) for ki, ni in zip(k, n)]
    lo = np.array([c[0] for c in ci])
    hi = np.array([c[1] for c in ci])
    weak = np.array([ni < 10 for ni in n])
    strong = ~weak

    ax.fill_between(years[strong], lo[strong] * 100, hi[strong] * 100,
                    alpha=0.25, color="#377eb8", linewidth=0)
    ax.plot(years[strong], rate[strong] * 100, marker="o", color="#1f4e79",
            linewidth=1.6, markersize=4, label="n ≥ 10")
    if weak.any():
        ax.fill_between(years[weak], lo[weak] * 100, hi[weak] * 100,
                        alpha=0.10, color="#377eb8", linewidth=0)
        ax.plot(years[weak], rate[weak] * 100, marker="o", color="#1f4e79",
                linewidth=0.7, markersize=4, alpha=0.5,
                markerfacecolor="white", markeredgecolor="#1f4e79",
                markeredgewidth=1.0, label="n < 10")
    ax.axvline(mandate_year, linestyle="--", color="#b25c00", linewidth=1.0)
    ax.text(mandate_year + 0.2, y_max * 0.97, mandate_label, fontsize=8,
            color="#b25c00", verticalalignment="top")
    ann_x, ann_y_frac = ann_xy if ann_xy is not None else (2004.3, 0.92)
    ax.text(ann_x, y_max * ann_y_frac, ann_text, fontsize=8,
            verticalalignment="top")
    ax.set_xlim(2003.5, 2024.5)
    ax.set_ylim(0, y_max)
    ax.set_xlabel("Primary completion year")
    ax.set_ylabel("Compliance (%)")
    ax.set_title(title, fontsize=10)


def make(csv_path: Path, out_png: Path, out_svg: Path) -> None:
    df = pd.read_csv(csv_path)
    df = df[(df["year"] >= 2004) & (df["year"] <= 2024)].sort_values("year").reset_index(drop=True)

    if df.empty:
        raise ValueError(f"No rows in year range 2004–2024 in {csv_path}")

    # Pre/post split annotations
    def split(df, col_n, col_k, cutoff):
        pre = df[df["year"] < cutoff]
        post = df[df["year"] >= cutoff]
        pre_rate = pre[col_k].sum() / max(pre[col_n].sum(), 1)
        post_rate = post[col_k].sum() / max(post[col_n].sum(), 1)
        return pre_rate, post_rate

    p01_pre, p01_post = split(df, "n_p01", "k_p01", 2017)
    p03_pre, p03_post = split(df, "n_p03", "k_p03", 2009)

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)
    _panel(
        axL,
        df["year"].to_numpy(),
        df["n_p01"].to_numpy(),
        df["k_p01"].to_numpy(),
        df["rate_p01"].to_numpy(),
        mandate_year=2017,
        mandate_label="Final Rule",
        ann_text=f"Pre-2017: {p01_pre*100:.1f}%\nPost-2017: {p01_post*100:.1f}%",
        y_max=25.0,
        title="FDAAA results-posting (P01)",
    )
    _panel(
        axR,
        df["year"].to_numpy(),
        df["n_p03"].to_numpy(),
        df["k_p03"].to_numpy(),
        df["rate_p03"].to_numpy(),
        mandate_year=2009,
        mandate_label="WHO 2009",
        ann_text=f"Pre-2009: {p03_pre*100:.1f}%\nPost-2009: {p03_post*100:.1f}%",
        y_max=10.0,
        title="WHO PCR-correction declaration (P03)",
        ann_xy=(2014.5, 0.85),
    )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200, metadata={"Software": "make_figure_d"})
    fig.savefig(out_svg, metadata={"Date": None})
    plt.close(fig)

    # v0.1.4 P1-11: inject WCAG 2.1 SC 1.1.1 text alternatives into the SVG.
    _inject_svg_a11y(
        out_svg,
        title="Compliance trajectories with two reporting requirements among "
              "registered malaria trials",
        desc=(
            "Two-panel time series 2004 to 2024. Left panel: FDAAA "
            f"results-posting (P01) rose from {p01_pre*100:.1f} percent "
            f"pre-2017 to {p01_post*100:.1f} percent post-2017, with "
            "the Final Rule year (2017) marked. Right panel: WHO "
            f"PCR-correction declaration (P03, strict regex) fell from "
            f"{p03_pre*100:.1f} percent pre-2009 to {p03_post*100:.1f} "
            "percent post-2009, with the WHO 2009 protocol year marked. "
            "Both panels use Wilson 95 percent confidence interval ribbons; "
            "years with fewer than 10 trials are shown as open circles."
        ),
    )


def _inject_svg_a11y(svg_path: Path, *, title: str, desc: str) -> None:
    """Inject <title> and <desc> immediately after the root <svg> element.

    matplotlib does not emit these by default; without them screen readers
    announce the figure as "graphic" with no semantic content. Idempotent —
    if a <title> already exists, this is a no-op.
    """
    s = svg_path.read_text(encoding="utf-8")
    if "<title>" in s.split("</svg>")[0]:
        return
    # Find end of opening <svg ...> tag
    open_tag_end = s.find(">", s.find("<svg"))
    if open_tag_end < 0:
        return
    insert = f"\n  <title>{_xml_escape(title)}</title>\n  <desc>{_xml_escape(desc)}</desc>"
    s = s[: open_tag_end + 1] + insert + s[open_tag_end + 1 :]
    svg_path.write_text(s, encoding="utf-8")


def _xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def main() -> int:
    csv = Path("pilots/results/year_trajectories.csv")
    out_png = Path("figures/figure-d.png")
    out_svg = Path("figures/figure-d.svg")
    make(csv, out_png, out_svg)
    print(f"figure-d OK: {out_png}, {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
