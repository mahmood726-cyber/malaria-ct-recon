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


def _format_value(v: object) -> str:
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return repr(v) if v != int(v) else f"{v:.1f}"
    if isinstance(v, dict):
        return json.dumps(v, sort_keys=True)
    return str(v)


def write(results: Iterable[PilotResult], out_path: Path | str) -> None:
    """Write PilotResult rows to CSV (overwrites)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = [f.name for f in fields(PilotResult)]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({c: _format_value(getattr(r, c)) for c in cols})
