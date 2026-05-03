"""Word-count enforcer for paper/methods-note-draft.md.

Synthēsis Methods Notes are capped at 400 words in the body. Figure caption
counted separately. This script strips YAML frontmatter, fenced code blocks,
the References section, and the figure caption block (delimited by HTML
comments) before counting whitespace-separated tokens.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_FRONTMATTER_RX = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_CODE_FENCE_RX = re.compile(r"```.*?```", re.DOTALL)
_CAPTION_RX = re.compile(
    r"<!--\s*figure-caption-begin\s*-->.*?<!--\s*figure-caption-end\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_REFERENCES_RX = re.compile(r"^##\s+References\s*$.*", re.DOTALL | re.IGNORECASE | re.MULTILINE)
_HTML_COMMENT_RX = re.compile(r"<!--.*?-->", re.DOTALL)
_TABLE_PIPE_RX = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)


def _strip(md: str) -> str:
    md = _FRONTMATTER_RX.sub("", md, count=1)
    md = _CAPTION_RX.sub("", md)
    md = _REFERENCES_RX.sub("", md)
    md = _CODE_FENCE_RX.sub("", md)
    md = _HTML_COMMENT_RX.sub("", md)
    return md


def body_word_count(md: str) -> int:
    return len(_strip(md).split())


def caption_word_count(md: str) -> int:
    m = _CAPTION_RX.search(md)
    if not m:
        return 0
    text = m.group(0)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return len(text.split())


def main_check(md_path: Path, *, body_limit: int = 400, caption_limit: int = 60) -> int:
    md = md_path.read_text(encoding="utf-8")
    body = body_word_count(md)
    caption = caption_word_count(md)
    print(f"body={body}/{body_limit}  caption={caption}/{caption_limit}")
    over_body = body > body_limit
    over_caption = caption > caption_limit
    if over_body:
        print(f"FAIL: body word count {body} > {body_limit}", file=sys.stderr)
    if over_caption:
        print(f"FAIL: caption word count {caption} > {caption_limit}", file=sys.stderr)
    return 1 if (over_body or over_caption) else 0


def main() -> int:
    return main_check(Path("paper/methods-note-draft.md"))


if __name__ == "__main__":
    raise SystemExit(main())
