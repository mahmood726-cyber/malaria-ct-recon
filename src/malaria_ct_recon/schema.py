"""PilotResult dataclass + CSV writer for sprint outputs."""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterable, Literal

PilotType = Literal["magnitude", "tractability_probe"]
Tractability = Literal["full", "partial", "none"]

_VALID_PILOT_TYPES = {"magnitude", "tractability_probe"}
_VALID_TRACTABILITY = {"full", "partial", "none"}


@dataclass(frozen=True)
class PilotResult:
    """Per-pilot result row.

    Fields:
        seed: Reproducibility witness. Recorded for every pilot even when the
            pilot is deterministic (P01-P04, P09, P10) — symmetric API across
            the orchestrator. Only P05 (bootstrap CI) actually consumes it.
            v0.1.4 P1-21 — kept for API symmetry; documented here as the
            single source of truth.
    """
    pilot_id: str
    pilot_title: str
    pilot_type: PilotType
    n_trials_in_scope: int
    magnitude_value: float
    magnitude_unit: str
    magnitude_ci_low: float
    magnitude_ci_high: float
    tractability_AACT_only: Tractability
    follow_up_potential: int
    n_trials_excluded_for_reason: dict[str, int]
    notes: str
    script_path: str
    script_sha256: str
    aact_snapshot: str
    seed: int
    wall_clock_seconds: float

    def __post_init__(self) -> None:
        if self.pilot_type not in _VALID_PILOT_TYPES:
            raise ValueError(f"pilot_type must be one of {_VALID_PILOT_TYPES}, got {self.pilot_type!r}")
        if self.tractability_AACT_only not in _VALID_TRACTABILITY:
            raise ValueError(f"tractability_AACT_only must be one of {_VALID_TRACTABILITY}")
        if not (1 <= self.follow_up_potential <= 5):
            raise ValueError(f"follow_up_potential must be 1..5, got {self.follow_up_potential}")


_CSV_FORMULA_LEAD = ("=", "+", "@", "\t", "\r")


def _csv_safe(s: str) -> str:
    """Prefix a leading apostrophe to cells that Excel would interpret as a formula.

    OWASP CSV-injection mitigation. If a cell value begins with =+@\\t\\r, Excel
    treats the cell as a formula on open. Prepend `'` to neutralise. v0.1.4
    P1-28; per lessons.md "CSV formula injection" rule.

    The hyphen `-` is intentionally NOT in the lead set — negative numbers are
    legitimate cell content, and Excel does not interpret leading `-` as a
    formula trigger by itself.
    """
    if s and s[0] in _CSV_FORMULA_LEAD:
        return "'" + s
    return s


def _format_value(v: object) -> str:
    """Format a PilotResult field value for CSV serialization.

    - float NaN or +/-inf -> empty string (serialised as missing)
    - other floats: repr() if fractional, f"{v:.1f}" if integer-valued
    - dict: JSON with sort_keys=True (reproducible)
    - str: formula-injection-safe (P1-28)
    - else: str(v)
    """
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return ""
        return repr(v) if v != int(v) else f"{v:.1f}"
    if isinstance(v, dict):
        return _csv_safe(json.dumps(v, sort_keys=True))
    return _csv_safe(str(v))


def write(results: Iterable[PilotResult], out_path: Path | str) -> None:
    """Write PilotResult rows to CSV (overwrites).

    CSV column order is the frozen PilotResult field order.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # CSV column order matches the frozen PilotResult field order.
    cols = [f.name for f in fields(PilotResult)]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({c: _format_value(getattr(r, c)) for c in cols})
