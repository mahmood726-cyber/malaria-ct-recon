# tests/test_methods_note_draft.py
"""Content tests for paper/methods-note-draft.md."""
import json
import re
from pathlib import Path
import pytest
import pandas as pd


DRAFT = Path("paper/methods-note-draft.md")
DECISION_RULE = Path("pilots/results/decision_rule.json")


def _md() -> str:
    return DRAFT.read_text(encoding="utf-8")


def test_draft_exists():
    assert DRAFT.exists()


def test_word_count_under_limit():
    from paper import wc
    md = _md()
    assert wc.body_word_count(md) <= 400
    assert wc.caption_word_count(md) <= 60


def test_includes_locked_body_sentence():
    """The §4 decision-rule output sentence must appear verbatim."""
    payload = json.loads(DECISION_RULE.read_text(encoding="utf-8"))
    assert payload["body_sentence"] in _md()


def test_includes_six_or_seven_references():
    md = _md()
    assert re.search(r"^##\s+References", md, re.MULTILINE)
    nums = re.findall(r"^\s*\d+\.\s+", md.split("References", 1)[1], re.MULTILINE)
    assert 6 <= len(nums) <= 7


def test_includes_repo_url_and_data_availability():
    md = _md()
    assert "github.com/mahmood726-cyber/malaria-ct-recon" in md
    assert re.search(r"AACT.*2026-04-12", md)
    assert "26a3fb0" in md  # preregistered framework HEAD
    assert "535fa2e" in md  # OTS-anchored design spec commit
    assert re.search(r"Data availability", md, re.IGNORECASE)


def test_includes_llm_disclosure():
    md = _md()
    assert re.search(r"no LLM.*extraction", md, re.IGNORECASE) \
        or re.search(r"regex-only", md, re.IGNORECASE)


def test_figure_caption_block_present():
    md = _md()
    assert "<!-- figure-caption-begin -->" in md
    assert "<!-- figure-caption-end -->" in md


def test_references_have_in_text_citations():
    """Vancouver: each numbered ref [N] must appear at least once in the body,
    and the citation set must be contiguous from 1 to the highest number."""
    md = _md()
    body, _, refs = md.partition("## References")
    nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", body)})
    assert nums, "no in-text [N] citations found"
    refs_count = len(re.findall(r"^\s*\d+\.\s+", refs, re.MULTILINE))
    assert nums == list(range(1, max(nums) + 1)), \
        f"citations {nums} are not contiguous from 1 to {max(nums)}"
    assert max(nums) <= refs_count, \
        f"highest citation [{max(nums)}] exceeds reference count {refs_count}"


def test_headline_numbers_match_production_csvs():
    """If pilot CSVs exist, the markdown headline numbers must match them.
    Skipped on fresh clones where the pilots haven't been run yet."""
    p01_path = Path("pilots/results/p01.csv")
    p03_path = Path("pilots/results/p03.csv")
    if not (p01_path.exists() and p03_path.exists()):
        pytest.skip("pilot CSVs not present (fresh clone); skipping cross-check")
    p01 = pd.read_csv(p01_path).iloc[0]
    p03 = pd.read_csv(p03_path).iloc[0]
    md = _md()
    p01_pct = round(float(p01["magnitude_value"]) * 100, 1)
    p03_pct = round(float(p03["magnitude_value"]) * 100, 1)
    p01_n = int(p01["n_trials_in_scope"])
    p03_n = int(p03["n_trials_in_scope"])
    # Accept ASCII space, NBSP (U+00A0), or no space between number and %.
    pct_variants = lambda v: (f"{v} %", f"{v} %", f"{v}%")
    assert any(s in md for s in pct_variants(p01_pct)), f"P01 headline {p01_pct}% not in draft"
    assert any(s in md for s in pct_variants(p03_pct)), f"P03 headline {p03_pct}% not in draft"
    assert f"{p01_n:,}" in md or str(p01_n) in md, f"P01 n={p01_n} not in draft"
    assert f"{p03_n:,}" in md or str(p03_n) in md, f"P03 n={p03_n} not in draft"
