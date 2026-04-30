"""Build the malaria-trial corpus from AACT via the inclusion filter."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact

_CONDITION_RX = re.compile(r"\b(malaria|plasmodium|falciparum|vivax|ovale|malariae|knowlesi)\b", re.IGNORECASE)

_MESH_INCLUDE = {
    "malaria", "malaria, falciparum", "malaria, vivax", "malaria, cerebral",
    "plasmodium falciparum", "plasmodium vivax",
}

_ANTIMALARIAL_RX = re.compile(
    r"(artemether|artesunate|artemisinin|lumefantrine|amodiaquine|piperaquine|"
    r"mefloquine|chloroquine|primaquine|tafenoquine|quinine|sulfadoxine|"
    r"pyrimethamine|atovaquone|proguanil|dihydroartemisinin|artefenomel|"
    r"ferroquine|RTS,S|R21|PfSPZ|Mosquirix|MSP|AMA1|CSP)",
    re.IGNORECASE,
)
# The antimalarial-intervention clause intentionally catches trials of dual-use drugs
# (e.g., quinine for leg cramps, atovaquone for pneumocystis prophylaxis); false
# positives are handled in corpus_overrides.csv when material to a specific pilot.


@dataclass(frozen=True)
class Corpus:
    included: set[str]
    reason: dict[str, str]
    excluded_by_override: set[str] = field(default_factory=set)
    included_by_override: set[str] = field(default_factory=set)


def _load_overrides(path: Path) -> tuple[set[str], set[str]]:
    if not path.exists():
        return set(), set()
    inc, exc = set(), set()
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            nct = row["nct_id"].strip()
            action = row["action"].strip().lower()
            if action == "exclude":
                exc.add(nct)
            elif action == "include":
                inc.add(nct)
            else:
                raise ValueError(
                    f"Unknown action {row['action']!r} for {nct} in overrides — "
                    f"must be 'include' or 'exclude'"
                )
    return inc, exc


def build(con: duckdb.DuckDBPyConnection, overrides_path: Path | str = "corpus_overrides.csv") -> Corpus:
    forced_in, forced_out = _load_overrides(Path(overrides_path))
    studies = aact.table(con, "studies")
    all_nct = set(studies["nct_id"].astype(str))
    conditions = aact.table(con, "conditions")
    interventions = aact.table(con, "interventions")
    try:
        browse = aact.table(con, "browse_conditions")
    except FileNotFoundError:
        browse = pd.DataFrame(columns=["nct_id", "mesh_term"])

    cond_hits = {nct: name for nct, name in zip(conditions["nct_id"].astype(str), conditions["name"].astype(str))
                 if _CONDITION_RX.search(name)}
    mesh_hits = {nct: term for nct, term in zip(browse["nct_id"].astype(str), browse["mesh_term"].astype(str))
                 if term.strip().lower() in _MESH_INCLUDE}
    interv_hits = {nct: name for nct, name in zip(interventions["nct_id"].astype(str), interventions["name"].astype(str))
                   if _ANTIMALARIAL_RX.search(name)}

    included, reason = set(), {}
    for nct in all_nct:
        if nct in forced_out:
            continue
        if nct in forced_in:
            included.add(nct); reason[nct] = "manual_include"; continue
        rs = []
        if nct in cond_hits: rs.append(f"condition='{cond_hits[nct][:60]}'")
        if nct in mesh_hits: rs.append(f"mesh='{mesh_hits[nct]}'")
        if nct in interv_hits: rs.append(f"intervention='{interv_hits[nct][:60]}'")
        if rs:
            included.add(nct); reason[nct] = "; ".join(rs)

    return Corpus(included=included, reason=reason,
                  excluded_by_override=forced_out, included_by_override=forced_in & all_nct)
