"""Crossref REST API verifier for paper/refs.bib.

Per project rule: every BibTeX entry with a DOI must resolve at api.crossref.org
before submission. Entries without DOI (gov reports, WHO/legal documents) are
flagged NO_DOI but not failed.

Output: paper/refs_verification.csv with one row per entry: bibkey, doi, status, http_code.
"""
from __future__ import annotations

import csv
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Iterable

import requests

CROSSREF_API = "https://api.crossref.org/works/"
USER_AGENT = "malaria-ct-recon-refs-verifier/0.1 (mailto:mahmood726@gmail.com)"

# v0.1.4 P1-25: DOI shape validation (Crossref convention: 10.<registrant>/<suffix>).
# Rejects malformed input before it hits the URL builder; closes a latent SSRF
# / open-redirect surface where a `?cb=evil.com` style suffix could land in the
# hot path.
_DOI_VALIDATE_RX = re.compile(r"^10\.\d{4,9}/[\w./()<>:;\-]+$")


_ENTRY_RX = re.compile(r"^@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+)\s*,", re.MULTILINE)
_DOI_RX = re.compile(r"^\s*doi\s*=\s*\{(?P<doi>[^}]+)\}", re.IGNORECASE | re.MULTILINE)


def parse_bibtex(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    entries: list[dict] = []
    matches = list(_ENTRY_RX.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        doi_m = _DOI_RX.search(body)
        entries.append({
            "bibkey": m.group("key").strip(),
            "type": m.group("type").strip(),
            "doi": doi_m.group("doi").strip() if doi_m else None,
        })
    return entries


def resolve_doi(doi: str, *, timeout: float = 10.0) -> tuple[str, int]:
    """Resolve a DOI via Crossref. v0.1.4 P1-25 hardening.

    Validates the DOI shape, percent-encodes the suffix, and rejects 200
    responses that aren't JSON (Cloudflare-style HTML error pages return 200).
    """
    if not _DOI_VALIDATE_RX.match(doi):
        return "INVALID", 0
    encoded = urllib.parse.quote(doi, safe="/")
    r = requests.get(
        CROSSREF_API + encoded,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=timeout,
    )
    if r.status_code != 200:
        return "FAIL", int(r.status_code)
    ct = (r.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
    if ct != "application/json":
        return "BAD_CONTENT_TYPE", int(r.status_code)
    return "PASS", int(r.status_code)


def verify(bib_path: Path, out_csv: Path, *, sleep_s: float = 0.2) -> int:
    rows = parse_bibtex(bib_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["bibkey", "type", "doi", "status", "http_code"])
        w.writeheader()
        any_fail = False
        for r in rows:
            if r["doi"] is None:
                w.writerow({**r, "status": "NO_DOI", "http_code": 0})
                continue
            try:
                status, code = resolve_doi(r["doi"])
            except requests.RequestException as e:
                status, code = "ERROR", -1
                print(f"  WARN: {r['bibkey']} request error: {e}", file=sys.stderr)
            if status in ("FAIL", "INVALID", "BAD_CONTENT_TYPE"):
                any_fail = True
            w.writerow({**r, "status": status, "http_code": code})
            time.sleep(sleep_s)
    return 1 if any_fail else 0


def main() -> int:
    return verify(Path("paper/refs.bib"), Path("paper/refs_verification.csv"))


if __name__ == "__main__":
    raise SystemExit(main())
