"""Test paper/wc.py — strips YAML, code, refs, figure caption; counts body."""
from pathlib import Path
from paper import wc


def test_strips_yaml_frontmatter():
    md = """---
title: foo
---
hello world hello
"""
    assert wc.body_word_count(md) == 3


def test_strips_fenced_code():
    md = "before\n```python\nignored words inside code\n```\nafter\n"
    assert wc.body_word_count(md) == 2


def test_strips_references_section():
    md = (
        "body sentence one.\n\n"
        "body sentence two.\n\n"
        "## References\n\n"
        "1. Author A. Title. Journal. 2020.\n"
        "2. Author B. Title. Journal. 2021.\n"
    )
    assert wc.body_word_count(md) == 6


def test_strips_figure_caption_block():
    md = (
        "body words here.\n\n"
        "<!-- figure-caption-begin -->\n"
        "Figure 1. caption words go here ignored\n"
        "<!-- figure-caption-end -->\n\n"
        "more body words.\n"
    )
    assert wc.body_word_count(md) == 6


def test_caption_word_count_separately():
    md = (
        "body words.\n\n"
        "<!-- figure-caption-begin -->\n"
        "Figure 1. caption words here.\n"
        "<!-- figure-caption-end -->\n"
    )
    assert wc.caption_word_count(md) == 5


def test_main_passes_under_limit(tmp_path: Path, capsys):
    md = tmp_path / "draft.md"
    md.write_text("one two three four\n", encoding="utf-8")
    rc = wc.main_check(md, body_limit=400, caption_limit=60)
    assert rc == 0


def test_main_fails_over_limit(tmp_path: Path):
    md = tmp_path / "draft.md"
    md.write_text(" ".join(["w"] * 401) + "\n", encoding="utf-8")
    rc = wc.main_check(md, body_limit=400, caption_limit=60)
    assert rc == 1
