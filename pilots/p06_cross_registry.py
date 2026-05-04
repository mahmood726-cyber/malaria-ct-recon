"""Pilot P06 — Cross-registry coverage (tractability probe).

Question: Of malaria trials with non-NCT registry IDs (PACTR, ISRCTN, RBR, ANZCTR, EUCTR, etc.),
what fraction also have a CT.gov registration? This is a tractability probe to assess the feasibility
of linking trials across registry ecosystems. AACT alone cannot see PACTR-only or ISRCTN-only trials,
hence the probe is "partial" — the true coverage requires a full ICTRP/PACTR scraper.
"""
from __future__ import annotations

import hashlib
import re
import time
from collections import Counter
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P06"
PILOT_TITLE = "Cross-registry coverage"
SCRIPT_PATH = "pilots/p06_cross_registry.py"

_REGISTRY_PATTERNS = [
    ("ISRCTN", re.compile(r"^ISRCTN\d{6,}$", re.IGNORECASE)),
    ("PACTR", re.compile(r"^PACTR\d{10,}$", re.IGNORECASE)),
    ("RBR", re.compile(r"^RBR-[A-Za-z0-9]+", re.IGNORECASE)),
    ("ANZCTR", re.compile(r"^ACTRN\d{10,}$", re.IGNORECASE)),
    ("EUCTR", re.compile(r"^EUDRA[T]?-?\d{4}-\d+", re.IGNORECASE)),
    ("WHO_UTN", re.compile(r"^U\d{4}-\d{4}-\d{4}", re.IGNORECASE)),
    ("DRKS", re.compile(r"^DRKS\d{6,}$", re.IGNORECASE)),
    ("CTRI", re.compile(r"^CTRI/\d", re.IGNORECASE)),
    ("ChiCTR", re.compile(r"^ChiCTR", re.IGNORECASE)),
    ("JPRN", re.compile(r"^JPRN-", re.IGNORECASE)),
]


def _registry_kind(value: str) -> str | None:
    """Identify registry type from an ID string.

    Returns the registry name (e.g. 'ISRCTN', 'PACTR', 'RBR') if matched,
    None if the value is an NCT ID or unrecognized.

    Args:
        value: Registry ID string (e.g. 'ISRCTN12345678', 'NCT01234567')

    Returns:
        Registry name or None
    """
    v = (value or "").strip()
    if v.upper().startswith("NCT"):
        return None
    for name, rx in _REGISTRY_PATTERNS:
        if rx.match(v):
            return name
    return None


def _sha256_self() -> str:
    """Return the SHA256 hash of this file's contents."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    """Run P06 cross-registry coverage probe.

    Identifies trials in the corpus that have non-NCT registry IDs in the AACT id_information table.
    Counts how many non-NCT registry IDs are found per registry type.

    Since AACT only indexes CT.gov registrations, this probe measures the "ceiling" of cross-registry
    coverage visible in CT.gov alone. A full atlas would need ICTRP/PACTR/ISRCTN direct scrapers
    to identify the inverse (trials registered ONLY in non-NCT registries).

    Args:
        con: DuckDB connection to AACT snapshot
        corpus: Corpus of included trials (by NCT ID)
        aact_snapshot: Label for the AACT snapshot (for metadata)
        seed: Random seed (unused for tractability probes, kept for API consistency)

    Returns:
        PilotResult with pilot_type="tractability_probe" and magnitude_value=NaN
    """
    t0 = time.perf_counter()

    try:
        ids_table = aact.table(con, "id_information")
    except FileNotFoundError:
        # id_information table missing; still valid to report 0 cross-registry
        ids_table = pd.DataFrame({
            "nct_id": [],
            "id_value": [],
            "id_type": [],
        })

    # Filter to trials in corpus
    in_corpus = ids_table[ids_table["nct_id"].astype(str).isin(corpus.included)].copy()

    # Map each id_value to a registry kind
    in_corpus["registry_kind"] = in_corpus["id_value"].astype(str).map(_registry_kind)

    # Keep only rows where registry_kind is not None (non-NCT registries)
    cross = in_corpus.dropna(subset=["registry_kind"])

    # Count unique trials with at least one non-NCT registry ID
    cross_count = cross["nct_id"].nunique() if len(cross) > 0 else 0

    # Count trials per registry kind
    kind_counts = Counter()
    if len(cross) > 0:
        for kind in cross["registry_kind"].unique():
            count = cross[cross["registry_kind"] == kind]["nct_id"].nunique()
            kind_counts[kind] = int(count)

    n_in_scope = len(corpus.included)

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="tractability_probe",
        n_trials_in_scope=int(n_in_scope),
        magnitude_value=float("nan"),
        magnitude_unit="",
        magnitude_ci_low=float("nan"),
        magnitude_ci_high=float("nan"),
        tractability_AACT_only="partial",
        # follow_up_potential=2: AACT alone cannot resolve the inverse
        # (PACTR-only trials); a full atlas needs ICTRP/PACTR scrapers.
        follow_up_potential=2,
        n_trials_excluded_for_reason={
            "no_registry_id_record": int(n_in_scope - in_corpus["nct_id"].nunique())
        },
        notes=f"cross_registered_count={cross_count}/{n_in_scope}; "
              f"by_kind={dict(kind_counts)}; "
              f"AACT cannot see PACTR/ISRCTN-only trials — needs ICTRP/PACTR scraper",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    """Run P06 against the configured AACT snapshot."""
    from malaria_ct_recon import config, corpus as corpus_mod

    cfg = config.load()
    with aact.connect(cfg.snapshot_dir) as con:
        c = corpus_mod.build(con)
        result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
        schema.write([result], Path("pilots/results/p06.csv"))
        print(f"P06 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
