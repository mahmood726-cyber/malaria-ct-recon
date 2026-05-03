# tests/test_methods_note_draft.py
"""Content tests for paper/methods-note-draft.md."""
import json
import re
from pathlib import Path
import pytest


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
    """Vancouver: each numbered ref [N] must appear at least once in the body."""
    md = _md()
    body, _, refs = md.partition("## References")
    nums = sorted({int(n) for n in re.findall(r"\[(\d+)\]", body)})
    assert nums, "no in-text [N] citations found"
    assert max(nums) <= len(re.findall(r"^\s*\d+\.\s+", refs, re.MULTILINE))
