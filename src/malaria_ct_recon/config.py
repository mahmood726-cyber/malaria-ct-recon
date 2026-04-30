"""Load the AACT snapshot path config (aact_path.toml)."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True)
class AactConfig:
    snapshot_dir: Path
    snapshot_label: str


def load(path: Path | str = "aact_path.toml") -> AactConfig:
    """Read aact_path.toml and return AactConfig.

    Raises FileNotFoundError if path does not exist.
    Raises KeyError if [aact] section or required keys are missing.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"AACT config not found: {p}")
    with p.open("rb") as fh:
        data = tomllib.load(fh)
    if "aact" not in data:
        raise KeyError("aact_path.toml missing required [aact] section")
    aact = data["aact"]
    return AactConfig(
        snapshot_dir=Path(aact["snapshot_dir"]),
        snapshot_label=str(aact["snapshot_label"]),
    )
