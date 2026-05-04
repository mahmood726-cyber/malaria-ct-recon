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
    def __init__(self, status, content_type="application/json"):
        self.status_code = status
        self.headers = {"content-type": content_type}
    def json(self):
        return {"message": {}}


# v0.1.4 P1-25: tests use DOI shapes that satisfy the registrant regex.
_VALID_DOI = "10.1234/abc"


def test_resolve_doi_passes_on_200(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(200))
    assert vr.resolve_doi(_VALID_DOI) == ("PASS", 200)


def test_resolve_doi_fails_on_404(monkeypatch):
    monkeypatch.setattr(vr.requests, "get", lambda *a, **k: _StubResp(404))
    assert vr.resolve_doi(_VALID_DOI) == ("FAIL", 404)


def test_resolve_doi_invalid_shape_fails_closed():
    """v0.1.4 P1-25: malformed DOIs are rejected before HTTP."""
    assert vr.resolve_doi("not-a-doi")[0] == "INVALID"
    assert vr.resolve_doi("../../etc/passwd")[0] == "INVALID"


def test_resolve_doi_html_200_is_not_pass(monkeypatch):
    """v0.1.4 P1-25: 200 with HTML body (Cloudflare-style) must not pass."""
    monkeypatch.setattr(vr.requests, "get",
                        lambda *a, **k: _StubResp(200, content_type="text/html"))
    assert vr.resolve_doi(_VALID_DOI) == ("BAD_CONTENT_TYPE", 200)


def test_verify_emits_csv(tmp_path: Path, monkeypatch):
    bib = tmp_path / "x.bib"
    bib.write_text(
        f'@article{{a,\n  doi = {{{_VALID_DOI}}}\n}}\n'
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
