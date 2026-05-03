"""Test python-docx exporter — Synthēsis house format."""
from pathlib import Path
import pytest

docx = pytest.importorskip("docx")
from paper import build_docx as bd


def test_export_creates_valid_docx(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text(
        "---\ntitle: Foo\n---\n# Foo\n\nbody.\n\n"
        "<!-- figure-caption-begin -->\nFig 1.\n<!-- figure-caption-end -->\n\n"
        "## References\n1. Ref one.\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    assert out.exists() and out.stat().st_size > 1000
    d = docx.Document(out)
    assert any("Foo" in p.text for p in d.paragraphs)


def test_uses_calibri_11pt(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text("# H\n\nbody.\n", encoding="utf-8")
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    d = docx.Document(out)
    style = d.styles["Normal"]
    assert style.font.name == "Calibri"
    assert int(style.font.size.pt) == 11


def test_a4_page_size(tmp_path: Path):
    """A4 = 210 × 297 mm = 8.27 × 11.69 in."""
    md = tmp_path / "in.md"
    md.write_text("# H\n\nbody.\n", encoding="utf-8")
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=None)
    d = docx.Document(out)
    section = d.sections[0]
    width_mm = section.page_width / 36000
    height_mm = section.page_height / 36000
    assert abs(width_mm - 210) < 1
    assert abs(height_mm - 297) < 1


def test_inserts_figure_when_provided(tmp_path: Path):
    md = tmp_path / "in.md"
    md.write_text(
        "# H\n\nbody.\n\n"
        "<!-- figure-caption-begin -->\nFig 1.\n<!-- figure-caption-end -->\n",
        encoding="utf-8",
    )
    fig = tmp_path / "fig.png"
    import base64
    fig.write_bytes(base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkAAIAAAoAAv/lxKUAAAAASUVORK5CYII="
    ))
    out = tmp_path / "out.docx"
    bd.export(md, out, figure_path=fig)
    d = docx.Document(out)
    assert len(d.inline_shapes) >= 1
