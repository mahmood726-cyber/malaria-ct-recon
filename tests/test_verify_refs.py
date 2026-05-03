"""Test paper/verify_refs.py — Crossref REST API verifier."""
from pathlib import Path
import pandas as pd
import pytest
from paper import verify_refs as vr


def test_parse_bibtex_extracts_doi(tmp_path: Path):
    bib = tmp_path / "x.bib"
    bib.write_text(
        '@article{a,\n  doi = {10.1371/journal.pone.0033677}\n}\n'
        '@article{b,\n  doi = {10.1016/S0140-6736(19)33220-9}\n}\n'
        '@techreport{c,\n  year = {2008}\n}\n',
        encoding="utf-8",
    )
    rows = vr.parse_bibtex(bib)
    assert {r["bibkey"] for r in rows} == {"a", "b", "c"}
    a = next(r for r in rows if r["bibkey"] == "a")
    c = next(r for r in rows if r["bibkey"] == "c")
    assert a["doi"] == "10.1371/journal.pone.0033677"
    assert c["doi"] is None


class _StubResp:
    def __init__(self, status):
        self.status_code = status
    def json(self):
        return {"message": {}}


def test_resolve_doi_passes_on_200(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(200))
    assert vr.resolve_doi("10.X/Y") == ("PASS", 200)


def test_resolve_doi_fails_on_404(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(404))
    assert vr.resolve_doi("10.X/Y") == ("FAIL", 404)


def test_verify_emits_csv(tmp_path: Path, monkeypatch):
    bib = tmp_path / "x.bib"
    bib.write_text(
        '@article{a,\n  doi = {10.1/A}\n}\n'
        '@techreport{b,\n  year = {2008}\n}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(200))
    out = tmp_path / "verify.csv"
    rc = vr.verify(bib, out)
    assert rc == 0
    df = pd.read_csv(out)
    assert set(df["bibkey"]) == {"a", "b"}
    a = df[df["bibkey"] == "a"].iloc[0]
    b = df[df["bibkey"] == "b"].iloc[0]
    assert a["status"] == "PASS"
    assert b["status"] == "NO_DOI"  # techreport without DOI is allowed but flagged
