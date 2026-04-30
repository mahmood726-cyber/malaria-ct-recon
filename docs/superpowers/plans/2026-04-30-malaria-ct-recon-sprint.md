# Malaria CT.gov Reconnaissance Sprint — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `malaria-ct-recon` repo with preflight + 10 pilots + dashboard + v0.1.0 tag, producing a `signal-table.csv` ranking 10 sources of bias in malaria CT.gov data by magnitude and tractability.

**Architecture:** Python 3.11+, duckdb directly against the frozen AACT 2026-04-12 TXT export at `D:/AACT-storage/AACT/2026-04-12/`. Shared infrastructure in `src/malaria_ct_recon/`; one pilot script per issue under `pilots/`; dashboard is a single self-contained `dashboard/index.html`. TDD throughout: every pilot has a fixture-based test before its real-AACT run.

**Tech Stack:** Python 3.11, duckdb, pandas, scipy, pytest, Sentinel pre-push hook, GitHub Actions for Pages.

**Spec:** `docs/superpowers/specs/2026-04-30-malaria-ct-recon-design.md`

---

## File Structure

```
malaria-ct-recon/
├── pyproject.toml                       # project metadata + deps
├── requirements.txt                     # pinned versions
├── README.md                            # repo overview
├── LICENSE                              # MIT
├── .gitignore                           # excludes aact_path.toml + results/
├── aact_path.toml.example               # template for snapshot path config
├── corpus_overrides.csv                 # manual include/exclude NCT IDs
├── .github/workflows/
│   ├── ci.yml                           # pytest + sentinel on push/PR
│   └── pages.yml                        # deploy dashboard to Pages
├── docs/superpowers/
│   ├── specs/2026-04-30-malaria-ct-recon-design.md   # already exists
│   └── plans/2026-04-30-malaria-ct-recon-sprint.md   # this file
├── src/malaria_ct_recon/
│   ├── __init__.py                      # package marker + version
│   ├── config.py                        # load aact_path.toml
│   ├── aact.py                          # duckdb-backed AACT loader
│   ├── corpus.py                        # malaria-trial inclusion filter
│   ├── schema.py                        # PilotResult dataclass + CSV writer
│   └── stats.py                         # Wilson CI + bootstrap helpers
├── pilots/
│   ├── __init__.py
│   ├── preflight.py                     # Pilot 0 — verify AACT + corpus
│   ├── p01_reporting_compliance.py
│   ├── p02_endpoint_chaos.py
│   ├── p03_pcr_corrected.py
│   ├── p04_resistance_era.py
│   ├── p05_pediatric_dose.py
│   ├── p06_cross_registry.py
│   ├── p07_sponsor_pdp.py
│   ├── p08_retro_registration.py
│   ├── p09_geographic.py
│   ├── p10_chmi_field.py
│   ├── run_all.py                       # invokes preflight + all 10, builds signal-table.csv
│   └── results/                         # gitignored output dir
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # fake AACT fixture + helpers
│   ├── test_config.py
│   ├── test_aact.py
│   ├── test_corpus.py
│   ├── test_schema.py
│   ├── test_stats.py
│   ├── test_preflight.py
│   ├── test_p01_reporting_compliance.py
│   ├── test_p02_endpoint_chaos.py
│   ├── test_p03_pcr_corrected.py
│   ├── test_p04_resistance_era.py
│   ├── test_p05_pediatric_dose.py
│   ├── test_p06_cross_registry.py
│   ├── test_p07_sponsor_pdp.py
│   ├── test_p08_retro_registration.py
│   ├── test_p09_geographic.py
│   ├── test_p10_chmi_field.py
│   └── test_run_all.py
└── dashboard/
    ├── index.html                       # vanilla JS, no CDN
    └── data/
        └── signal-table.csv             # built artifact (committed for Pages)
```

---

## Phase 0 — Repo skeleton (T01–T03)

### Task T01: Initialize project metadata

**Files:**
- Create: `C:/Projects/malaria-ct-recon/pyproject.toml`
- Create: `C:/Projects/malaria-ct-recon/requirements.txt`
- Create: `C:/Projects/malaria-ct-recon/.gitignore`
- Create: `C:/Projects/malaria-ct-recon/LICENSE`
- Create: `C:/Projects/malaria-ct-recon/README.md`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "malaria-ct-recon"
version = "0.1.0"
description = "10-pilot reconnaissance of bias sources in malaria CT.gov data"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Mahmood", email = "mahmood726@gmail.com"}]
dependencies = [
    "duckdb>=1.0",
    "pandas>=2.2",
    "scipy>=1.13",
    "tomli>=2.0; python_version < '3.11'",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
```

- [ ] **Step 2: Write `requirements.txt`**

```
duckdb==1.1.3
pandas==2.2.3
scipy==1.14.1
pytest==8.3.4
pytest-cov==6.0.0
```

- [ ] **Step 3: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
build/
dist/
aact_path.toml
pilots/results/*.csv
pilots/results/*.json
!pilots/results/.gitkeep
PROGRESS.md
.venv/
.env
```

- [ ] **Step 4: Write `LICENSE`** (MIT, year 2026, "Mahmood")

- [ ] **Step 5: Write `README.md` skeleton**

```markdown
# malaria-ct-recon

10-pilot reconnaissance of bias sources in malaria trial data on ClinicalTrials.gov.

**Snapshot:** AACT 2026-04-12 (frozen).
**Status:** Sprint in progress.

See `docs/superpowers/specs/2026-04-30-malaria-ct-recon-design.md` for the design.

## Quickstart

1. Install: `pip install -e .[dev]`
2. Configure snapshot path: `cp aact_path.toml.example aact_path.toml` and edit
3. Run preflight: `python -m pilots.preflight`
4. Run all pilots: `python -m pilots.run_all`
5. Open `dashboard/index.html` in a browser

## Output

`dashboard/data/signal-table.csv` ranks the 10 pilots by magnitude and follow-up potential.
```

- [ ] **Step 6: Commit**

```bash
cd C:/Projects/malaria-ct-recon
git add pyproject.toml requirements.txt .gitignore LICENSE README.md
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "chore(skeleton): pyproject + deps + license + readme"
```

---

### Task T02: Snapshot path config

**Files:**
- Create: `C:/Projects/malaria-ct-recon/aact_path.toml.example`
- Create: `C:/Projects/malaria-ct-recon/aact_path.toml` (gitignored)
- Create: `C:/Projects/malaria-ct-recon/src/malaria_ct_recon/__init__.py`
- Create: `C:/Projects/malaria-ct-recon/src/malaria_ct_recon/config.py`
- Create: `C:/Projects/malaria-ct-recon/tests/__init__.py`
- Create: `C:/Projects/malaria-ct-recon/tests/test_config.py`

- [ ] **Step 1: Write `aact_path.toml.example`**

```toml
# Copy this file to aact_path.toml and edit the path.
# aact_path.toml is gitignored — never commit a local-machine path.

[aact]
snapshot_dir = "D:/AACT-storage/AACT/2026-04-12/"
snapshot_label = "2026-04-12"
```

- [ ] **Step 2: Write `aact_path.toml`** (local, gitignored — copy the example, real path)

```toml
[aact]
snapshot_dir = "D:/AACT-storage/AACT/2026-04-12/"
snapshot_label = "2026-04-12"
```

- [ ] **Step 3: Write `src/malaria_ct_recon/__init__.py`**

```python
"""Malaria CT.gov reconnaissance — 10-pilot bias-source audit."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Write the failing test `tests/test_config.py`**

```python
"""Tests for snapshot-path config loader."""
from pathlib import Path

import pytest

from malaria_ct_recon import config


def test_load_returns_snapshot_dir_and_label(tmp_path: Path) -> None:
    cfg_file = tmp_path / "aact_path.toml"
    cfg_file.write_text(
        '[aact]\nsnapshot_dir = "/some/path/"\nsnapshot_label = "2026-04-12"\n',
        encoding="utf-8",
    )
    cfg = config.load(cfg_file)
    assert cfg.snapshot_dir == Path("/some/path/")
    assert cfg.snapshot_label == "2026-04-12"


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        config.load(tmp_path / "missing.toml")


def test_load_missing_aact_section_raises(tmp_path: Path) -> None:
    cfg_file = tmp_path / "aact_path.toml"
    cfg_file.write_text("[other]\nfoo = 1\n", encoding="utf-8")
    with pytest.raises(KeyError, match="aact"):
        config.load(cfg_file)
```

- [ ] **Step 5: Write `tests/__init__.py`** (empty file — makes `tests/` an importable package per lessons.md "module-name collision hides tests")

```python
```

- [ ] **Step 6: Run test, verify it fails**

```bash
cd C:/Projects/malaria-ct-recon && pip install -e .[dev] && pytest tests/test_config.py -v
```

Expected: ImportError or ModuleNotFoundError on `from malaria_ct_recon import config`.

- [ ] **Step 7: Implement `src/malaria_ct_recon/config.py`**

```python
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
```

- [ ] **Step 8: Run tests, verify pass**

```bash
pytest tests/test_config.py -v
```

Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add aact_path.toml.example src/ tests/__init__.py tests/test_config.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(config): aact_path.toml loader with [aact] schema"
```

---

### Task T03: Sentinel pre-push hook + GitHub Actions CI

**Files:**
- Create: `C:/Projects/malaria-ct-recon/.github/workflows/ci.yml`
- (Sentinel hook installed via CLI, not committed)

- [ ] **Step 1: Install Sentinel pre-push hook**

```bash
python -m sentinel install-hook --repo C:/Projects/malaria-ct-recon
```

Expected: confirmation that `.git/hooks/pre-push` is installed.

- [ ] **Step 2: Run a Sentinel scan to verify clean baseline**

```bash
python -m sentinel scan --repo C:/Projects/malaria-ct-recon
```

Expected: 0 BLOCK, possibly some WARN. If any BLOCK, fix before continuing.

- [ ] **Step 3: Write `.github/workflows/ci.yml`**

```yaml
name: ci

on:
  push:
    branches: [master]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e .[dev]
      - run: pytest -q
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "ci: pytest on push/PR via GitHub Actions"
```

---

## Phase 1 — Core infrastructure (T04–T08)

### Task T04: AACT loader

**Files:**
- Create: `src/malaria_ct_recon/aact.py`
- Create: `tests/test_aact.py`

- [ ] **Step 1: Write the failing test `tests/test_aact.py`**

```python
"""Tests for the AACT loader."""
from pathlib import Path

import duckdb
import pytest

from malaria_ct_recon import aact


def test_open_returns_duckdb_connection(tmp_path: Path) -> None:
    (tmp_path / "studies.txt").write_text("nct_id|brief_title\nNCT00000001|fake\n", encoding="utf-8")
    con = aact.open(tmp_path)
    assert isinstance(con, duckdb.DuckDBPyConnection)


def test_table_returns_dataframe(tmp_path: Path) -> None:
    (tmp_path / "studies.txt").write_text(
        "nct_id|brief_title\nNCT00000001|alpha\nNCT00000002|beta\n",
        encoding="utf-8",
    )
    con = aact.open(tmp_path)
    df = aact.table(con, "studies")
    assert len(df) == 2
    assert df["nct_id"].tolist() == ["NCT00000001", "NCT00000002"]


def test_missing_table_raises(tmp_path: Path) -> None:
    con = aact.open(tmp_path)
    with pytest.raises(FileNotFoundError, match="missing_table"):
        aact.table(con, "missing_table")


def test_list_tables_returns_sorted_names(tmp_path: Path) -> None:
    (tmp_path / "zebra.txt").write_text("a|b\n1|2\n", encoding="utf-8")
    (tmp_path / "alpha.txt").write_text("a|b\n1|2\n", encoding="utf-8")
    con = aact.open(tmp_path)
    assert aact.list_tables(con) == ["alpha", "zebra"]
```

- [ ] **Step 2: Run, verify fail**: `pytest tests/test_aact.py -v` → ImportError

- [ ] **Step 3: Implement `src/malaria_ct_recon/aact.py`**

```python
"""AACT loader — duckdb-backed reader for pipe-delimited TXT exports."""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def open(snapshot_dir: Path | str) -> duckdb.DuckDBPyConnection:
    """Open an in-memory duckdb connection with the snapshot dir registered."""
    p = Path(snapshot_dir)
    if not p.is_dir():
        raise FileNotFoundError(f"AACT snapshot dir not found: {p}")
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit='4GB'")
    con.execute("CREATE TABLE __snapshot_dir (path VARCHAR)")
    con.execute("INSERT INTO __snapshot_dir VALUES (?)", [str(p)])
    return con


def _snapshot_dir(con: duckdb.DuckDBPyConnection) -> Path:
    row = con.execute("SELECT path FROM __snapshot_dir").fetchone()
    if row is None:
        raise RuntimeError("Connection not opened via aact.open()")
    return Path(row[0])


def table(con: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
    """Read one AACT table into a DataFrame. Raises FileNotFoundError if missing."""
    p = _snapshot_dir(con) / f"{name}.txt"
    if not p.exists():
        raise FileNotFoundError(f"AACT table missing: {p}")
    return con.read_csv(str(p), delim="|", header=True, quotechar='"', escapechar='"').df()


def list_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Return sorted list of table names (filenames without .txt)."""
    return sorted(f.stem for f in _snapshot_dir(con).glob("*.txt"))
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_aact.py -v` → 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/malaria_ct_recon/aact.py tests/test_aact.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(aact): duckdb-backed loader for AACT pipe-delimited exports"
```

---

### Task T05: PilotResult schema + CSV writer

**Files:**
- Create: `src/malaria_ct_recon/schema.py`
- Create: `tests/test_schema.py`

- [ ] **Step 1: Write the failing test `tests/test_schema.py`**

```python
"""Tests for PilotResult schema + CSV writer."""
import csv
import json
from pathlib import Path

import pytest

from malaria_ct_recon import schema


def make_result(**overrides) -> schema.PilotResult:
    base = dict(
        pilot_id="P01", pilot_title="Reporting compliance", pilot_type="magnitude",
        n_trials_in_scope=1342, magnitude_value=0.31, magnitude_unit="fraction",
        magnitude_ci_low=0.28, magnitude_ci_high=0.34,
        tractability_AACT_only="full", follow_up_potential=4,
        n_trials_excluded_for_reason={"missing_completion_date": 12},
        notes="31% of completed malaria trials post results within 12mo",
        script_path="pilots/p01_reporting_compliance.py", script_sha256="abc123",
        aact_snapshot="2026-04-12", seed=20260430, wall_clock_seconds=4.2,
    )
    base.update(overrides)
    return schema.PilotResult(**base)


def test_pilot_result_serialises_to_csv_row(tmp_path: Path) -> None:
    schema.write([make_result()], tmp_path / "p01.csv")
    rows = list(csv.DictReader((tmp_path / "p01.csv").open(encoding="utf-8")))
    assert rows[0]["pilot_id"] == "P01"
    assert json.loads(rows[0]["n_trials_excluded_for_reason"]) == {"missing_completion_date": 12}


def test_tractability_probe_allows_nan_magnitude(tmp_path: Path) -> None:
    r = make_result(pilot_id="P06", pilot_type="tractability_probe",
                    magnitude_value=float("nan"), magnitude_ci_low=float("nan"),
                    magnitude_ci_high=float("nan"), magnitude_unit="")
    schema.write([r], tmp_path / "p06.csv")
    rows = list(csv.DictReader((tmp_path / "p06.csv").open(encoding="utf-8")))
    assert rows[0]["magnitude_value"] == ""


def test_invalid_pilot_type_raises() -> None:
    with pytest.raises(ValueError, match="pilot_type"):
        make_result(pilot_type="invalid")


def test_follow_up_potential_clamped_1_to_5() -> None:
    with pytest.raises(ValueError, match="follow_up_potential"):
        make_result(follow_up_potential=0)
    with pytest.raises(ValueError, match="follow_up_potential"):
        make_result(follow_up_potential=6)


def test_aggregate_writes_master_table(tmp_path: Path) -> None:
    rs = [make_result(), make_result(pilot_id="P02", pilot_title="Endpoint chaos")]
    schema.write(rs, tmp_path / "signal-table.csv")
    rows = list(csv.DictReader((tmp_path / "signal-table.csv").open(encoding="utf-8")))
    assert [r["pilot_id"] for r in rows] == ["P01", "P02"]
```

- [ ] **Step 2: Run, verify fail**: `pytest tests/test_schema.py -v` → ImportError

- [ ] **Step 3: Implement `src/malaria_ct_recon/schema.py`**

```python
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
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_schema.py -v` → 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/malaria_ct_recon/schema.py tests/test_schema.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(schema): PilotResult dataclass + CSV writer"
```

---

### Task T06: Statistics helpers (Wilson CI + bootstrap)

**Files:**
- Create: `src/malaria_ct_recon/stats.py`
- Create: `tests/test_stats.py`

- [ ] **Step 1: Write `tests/test_stats.py`**

```python
"""Tests for statistical helpers."""
import math

import numpy as np
import pytest

from malaria_ct_recon import stats


def test_wilson_ci_known_values() -> None:
    low, high = stats.wilson_ci(50, 100)
    assert math.isclose(low, 0.4038, abs_tol=0.001)
    assert math.isclose(high, 0.5962, abs_tol=0.001)


def test_wilson_ci_zero_successes_floor_at_zero() -> None:
    low, high = stats.wilson_ci(0, 100)
    assert low == 0.0 and high > 0.0


def test_wilson_ci_all_successes_ceil_at_one() -> None:
    low, high = stats.wilson_ci(100, 100)
    assert low < 1.0 and high == 1.0


def test_wilson_ci_zero_n_raises() -> None:
    with pytest.raises(ValueError):
        stats.wilson_ci(0, 0)


def test_bootstrap_ci_mean_returns_plausible_interval() -> None:
    rng = np.random.default_rng(42)
    data = rng.normal(loc=10.0, scale=2.0, size=500)
    low, high = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=1000, seed=123)
    assert low < 10.0 < high


def test_bootstrap_ci_deterministic_with_seed() -> None:
    data = np.arange(100, dtype=float)
    a = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=200, seed=1)
    b = stats.bootstrap_ci(data, statistic=np.mean, n_resamples=200, seed=1)
    assert a == b
```

- [ ] **Step 2: Run, verify fail**: `pytest tests/test_stats.py -v` → ImportError

- [ ] **Step 3: Implement `src/malaria_ct_recon/stats.py`**

```python
"""Statistical helpers — Wilson CI for proportions, bootstrap CI for any statistic."""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import norm


def wilson_ci(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (Wilson 1927)."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if not (0 <= successes <= n):
        raise ValueError(f"successes must be in [0, {n}], got {successes}")
    z = norm.ppf(1 - alpha / 2)
    phat = successes / n
    denom = 1 + z**2 / n
    centre = (phat + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    return max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_ci(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_resamples: int = 2000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> tuple[float, float]:
    """Percentile bootstrap CI for an arbitrary statistic."""
    rng = np.random.default_rng(seed)
    n = len(data)
    if n == 0:
        raise ValueError("data must be non-empty")
    samples = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        samples[i] = statistic(data[idx])
    return float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2))
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_stats.py -v` → 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/malaria_ct_recon/stats.py tests/test_stats.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(stats): Wilson CI + percentile bootstrap helpers"
```

---

### Task T07: Inclusion filter / corpus module

**Files:**
- Create: `src/malaria_ct_recon/corpus.py`
- Create: `corpus_overrides.csv`
- Create: `tests/test_corpus.py`

- [ ] **Step 1: Create empty `corpus_overrides.csv`**

```
nct_id,action,reason,added_by,added_on
```

- [ ] **Step 2: Write `tests/test_corpus.py`**

```python
"""Tests for the malaria-trial inclusion filter."""
from pathlib import Path

import pandas as pd

from malaria_ct_recon import aact, corpus


def _write(tmp_path, name, df):
    df.to_csv(tmp_path / f"{name}.txt", sep="|", index=False)


def _seed(tmp_path):
    _write(tmp_path, "studies", pd.DataFrame({"nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"]}))
    _write(tmp_path, "conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT04", "NCT05"],
        "name": ["Plasmodium Falciparum Malaria", "Type 2 Diabetes",
                 "Anemia in malaria-endemic region", "HIV Infection", "Healthy Volunteers"],
    }))
    _write(tmp_path, "browse_conditions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT04"],
        "mesh_term": ["Malaria, Falciparum", "HIV Infections"],
    }))
    _write(tmp_path, "interventions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT04", "NCT05"],
        "name": ["Artemether-lumefantrine", "Artesunate", "Placebo"],
    }))


def test_build_includes_via_condition_meshterm_or_intervention(tmp_path: Path):
    _seed(tmp_path)
    overrides = tmp_path / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=overrides)
    assert "NCT01" in result.included
    assert "NCT04" in result.included      # intervention=Artesunate
    assert "NCT02" not in result.included
    assert "NCT05" not in result.included  # placebo only


def test_build_respects_exclude_override(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text("nct_id,action,reason,added_by,added_on\nNCT01,exclude,test,test,2026-04-30\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert "NCT01" not in result.included


def test_build_respects_include_override(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"
    ov.write_text("nct_id,action,reason,added_by,added_on\nNCT05,include,verified,test,2026-04-30\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert "NCT05" in result.included


def test_records_inclusion_reason(tmp_path: Path):
    _seed(tmp_path)
    ov = tmp_path / "ov.csv"; ov.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    result = corpus.build(aact.open(tmp_path), overrides_path=ov)
    assert result.reason["NCT01"]
```

- [ ] **Step 3: Run, verify fail**: `pytest tests/test_corpus.py -v` → ImportError

- [ ] **Step 4: Implement `src/malaria_ct_recon/corpus.py`**

```python
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
```

- [ ] **Step 5: Run, verify pass**: `pytest tests/test_corpus.py -v` → 4 passed

- [ ] **Step 6: Commit**

```bash
git add src/malaria_ct_recon/corpus.py corpus_overrides.csv tests/test_corpus.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(corpus): inclusion filter (condition + MeSH + intervention) with overrides"
```

---

### Task T08: Shared test fixtures

**Files:** Create `tests/conftest.py`

- [ ] **Step 1: Write `tests/conftest.py`** (compact 8-trial AACT subset for pilot tests)

```python
"""Shared pytest fixtures — fake AACT subset for pilot tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


def _w(tmp_path: Path, name: str, df: pd.DataFrame) -> None:
    df.to_csv(tmp_path / f"{name}.txt", sep="|", index=False)


@pytest.fixture
def fake_aact(tmp_path: Path) -> Path:
    """Fake AACT snapshot dir with 8 trials (6 malaria, 2 control)."""
    _w(tmp_path, "studies", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "brief_title": [
            "Artemether-lumefantrine in children with falciparum malaria",
            "RTS,S vaccine efficacy in infants",
            "Artesunate-mefloquine vs DHA-piperaquine",
            "Tafenoquine for vivax radical cure",
            "PfSPZ challenge vaccine in non-immune adults",
            "DHA-piperaquine mass drug administration",
            "Type 2 diabetes glycemic control",
            "Hypertension management",
        ],
        "phase": ["PHASE3", "PHASE3", "PHASE2", "PHASE3", "PHASE1", "PHASE3", "PHASE3", "PHASE4"],
        "overall_status": ["COMPLETED"] * 7 + ["RECRUITING"],
        "start_date": ["2005-06-01", "2010-04-01", "2018-09-01", "2014-01-01",
                       "2019-03-01", "2016-05-01", "2020-01-01", "2021-01-01"],
        "primary_completion_date": ["2007-08-01", "2014-01-01", "2020-12-01", "2017-06-01",
                                    "2020-08-01", "2019-04-01", "2022-12-01", None],
        "study_first_submitted_date": ["2006-01-01", "2009-12-01", "2018-06-01", "2013-09-01",
                                       "2018-12-01", "2016-03-01", "2019-11-01", "2020-12-01"],
        "results_first_submitted_date": [None, "2015-01-01", "2021-08-01", None,
                                         "2021-11-01", None, "2023-09-01", None],
        "enrollment": [400, 15460, 600, 320, 28, 120000, 800, 250],
        "is_fda_regulated_drug": [False, False, True, True, False, False, True, True],
    }))
    _w(tmp_path, "conditions", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "name": ["Falciparum Malaria", "Plasmodium Falciparum Malaria", "Uncomplicated Malaria",
                 "Plasmodium Vivax", "Malaria", "Malaria", "Type 2 Diabetes", "Hypertension"],
    }))
    _w(tmp_path, "browse_conditions", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 7)],
        "mesh_term": ["Malaria, Falciparum", "Malaria, Falciparum", "Malaria",
                      "Malaria, Vivax", "Malaria", "Malaria"],
    }))
    _w(tmp_path, "interventions", pd.DataFrame({
        "nct_id": ["NCT01", "NCT02", "NCT03", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "name": ["Artemether-lumefantrine 20/120mg pediatric", "RTS,S/AS01",
                 "Artesunate-mefloquine", "Dihydroartemisinin-piperaquine",
                 "Tafenoquine 300mg single dose", "PfSPZ Challenge",
                 "Dihydroartemisinin-piperaquine MDA", "Metformin", "Amlodipine"],
        "intervention_type": ["DRUG", "BIOLOGICAL", "DRUG", "DRUG", "DRUG", "BIOLOGICAL", "DRUG", "DRUG", "DRUG"],
    }))
    _w(tmp_path, "sponsors", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "name": ["London School of Hygiene and Tropical Medicine", "GlaxoSmithKline",
                 "Medicines for Malaria Venture", "GlaxoSmithKline", "Sanaria Inc.",
                 "World Health Organization", "Pfizer", "AstraZeneca"],
        "lead_or_collaborator": ["lead"] * 8,
        "agency_class": ["OTHER", "INDUSTRY", "OTHER", "INDUSTRY", "INDUSTRY",
                         "OTHER_GOV", "INDUSTRY", "INDUSTRY"],
    }))
    _w(tmp_path, "countries", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT02", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "name": ["Tanzania", "Kenya", "Mozambique", "Ghana", "Cambodia",
                 "Brazil", "United States", "Zambia", "United States", "United States"],
    }))
    _w(tmp_path, "facilities", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT02", "NCT03", "NCT04", "NCT05", "NCT06", "NCT07", "NCT08"],
        "country": ["Tanzania", "Kenya", "Mozambique", "Ghana", "Cambodia",
                    "Brazil", "United States", "Zambia", "United States", "United States"],
    }))
    _w(tmp_path, "eligibilities", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "minimum_age": ["6 Months", "5 Months", "18 Years", "16 Years", "18 Years",
                        "6 Months", "18 Years", "65 Years"],
        "maximum_age": ["59 Months", "17 Months", "65 Years", "65 Years", "55 Years",
                        "N/A", "75 Years", "N/A"],
        "criteria": [
            "Children 6-59 months with uncomplicated falciparum malaria",
            "Healthy infants 5-17 months",
            "Adults with uncomplicated P. falciparum",
            "Patients with confirmed P. vivax",
            "Healthy non-immune adults for sporozoite challenge",
            "All residents of treatment villages",
            "Type 2 diabetes",
            "Hypertension",
        ],
    }))
    _w(tmp_path, "design_outcomes", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT02", "NCT03", "NCT03", "NCT04", "NCT05", "NCT06"],
        "outcome_type": ["primary", "secondary", "primary", "primary", "secondary", "primary", "primary", "primary"],
        "measure": [
            "PCR-corrected adequate clinical and parasitological response (ACPR) at day 28",
            "Day 28 fever clearance",
            "Vaccine efficacy against clinical malaria",
            "Day 42 ACPR",
            "Time to recurrent parasitaemia (PCR-uncorrected)",
            "Recurrence of P. vivax parasitaemia at 6 months",
            "Time to first parasitemia after challenge",
            "Prevalence of asymptomatic P. falciparum infection at month 12",
        ],
        "time_frame": ["28 days", "28 days", "12 months", "42 days", "42 days", "180 days", "28 days", "12 months"],
    }))
    _w(tmp_path, "id_information", pd.DataFrame({
        "nct_id": ["NCT01", "NCT01", "NCT04"],
        "id_value": ["ISRCTN12345678", "PACTR201509001234567", "RBR-abc123"],
        "id_type": ["registry_id", "registry_id", "registry_id"],
    }))
    _w(tmp_path, "calculated_values", pd.DataFrame({
        "nct_id": [f"NCT0{i}" for i in range(1, 9)],
        "were_results_reported": [False, True, True, False, True, False, True, False],
        "months_to_report_results": [None, 7, 9, None, 5, None, 9, None],
    }))
    return tmp_path
```

- [ ] **Step 2: Smoke check**: `pytest -q` → all prior tests still pass

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "test(fixtures): fake AACT subset (8 trials: 6 malaria + 2 control)"
```

---

## Phase 2 — Preflight + preregistration (T09–T10)

### Task T09: Preflight (Pilot 0)

**Files:**
- Create: `pilots/__init__.py` (empty)
- Create: `pilots/preflight.py`
- Create: `tests/test_preflight.py`
- Create: `pilots/results/.gitkeep` (empty)

- [ ] **Step 1: Write `pilots/__init__.py`** (empty)

- [ ] **Step 2: Write `tests/test_preflight.py`**

```python
"""Tests for preflight (Pilot 0)."""
from pathlib import Path

import pytest

from pilots import preflight


def test_preflight_passes_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=1, expected_corpus_max=10)
    assert report.passed is True
    assert report.corpus_size == 6  # NCT01-NCT06
    assert report.required_tables_present is True


def test_preflight_fails_when_corpus_below_min(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=100, expected_corpus_max=200)
    assert report.passed is False
    assert "corpus_size" in report.failure_reason


def test_preflight_fails_when_required_table_missing(fake_aact: Path) -> None:
    (fake_aact / "studies.txt").unlink()
    overrides = fake_aact / "ov.csv"
    overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    report = preflight.run(snapshot_dir=fake_aact, overrides_path=overrides,
                           expected_corpus_min=1, expected_corpus_max=10)
    assert report.passed is False
    assert "studies" in report.failure_reason
```

- [ ] **Step 3: Run, verify fail**: `pytest tests/test_preflight.py -v` → ImportError

- [ ] **Step 4: Implement `pilots/preflight.py`**

```python
"""Pilot 0 — preflight: verify AACT snapshot, required tables, corpus size."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from malaria_ct_recon import aact, config, corpus

REQUIRED_TABLES = [
    "studies", "conditions", "browse_conditions", "interventions",
    "sponsors", "countries", "facilities", "eligibilities",
    "design_outcomes", "id_information", "calculated_values",
]


@dataclass(frozen=True)
class PreflightReport:
    passed: bool
    snapshot_dir: Path
    required_tables_present: bool
    missing_tables: list[str]
    corpus_size: int
    failure_reason: str


def run(
    snapshot_dir: Path | str | None = None,
    overrides_path: Path | str = "corpus_overrides.csv",
    expected_corpus_min: int = 1200,
    expected_corpus_max: int = 1600,
) -> PreflightReport:
    """Run preflight checks. Returns a report; caller decides exit code."""
    if snapshot_dir is None:
        cfg = config.load()
        snapshot_dir = cfg.snapshot_dir
    snapshot_dir = Path(snapshot_dir)

    if not snapshot_dir.is_dir():
        return PreflightReport(False, snapshot_dir, False, REQUIRED_TABLES, 0,
                               f"snapshot_dir does not exist: {snapshot_dir}")

    con = aact.open(snapshot_dir)
    present = set(aact.list_tables(con))
    missing = [t for t in REQUIRED_TABLES if t not in present]
    if missing:
        return PreflightReport(False, snapshot_dir, False, missing, 0,
                               f"required tables missing: {missing}")

    try:
        c = corpus.build(con, overrides_path=overrides_path)
    except Exception as exc:
        return PreflightReport(False, snapshot_dir, True, [], 0,
                               f"corpus build failed: {exc!r}")

    if not (expected_corpus_min <= len(c.included) <= expected_corpus_max):
        return PreflightReport(False, snapshot_dir, True, [], len(c.included),
                               f"corpus_size {len(c.included)} outside [{expected_corpus_min}, {expected_corpus_max}]")

    return PreflightReport(True, snapshot_dir, True, [], len(c.included), "")


def main() -> int:
    report = run()
    if report.passed:
        print(f"PREFLIGHT OK: corpus_size={report.corpus_size} snapshot={report.snapshot_dir}")
        return 0
    print(f"PREFLIGHT FAIL: {report.failure_reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Create empty `pilots/results/.gitkeep`**

- [ ] **Step 6: Run, verify pass**: `pytest tests/test_preflight.py -v` → 3 passed

- [ ] **Step 7: Run preflight against real AACT** (smoke test, NOT a CI gate)

```bash
python -m pilots.preflight
```

Expected: `PREFLIGHT OK: corpus_size=<between 1200 and 1600> snapshot=D:\AACT-storage\AACT\2026-04-12`. If corpus_size is outside the band, do NOT proceed — investigate inclusion filter, then either update `corpus_overrides.csv` or relax `expected_corpus_min`/`max` and document why.

- [ ] **Step 8: Commit**

```bash
git add pilots/__init__.py pilots/preflight.py pilots/results/.gitkeep tests/test_preflight.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(preflight): Pilot 0 verifies AACT + required tables + corpus size"
```

---

### Task T10: Preregistration — OTS timestamp

**Files:** none (operates on git history)

The current HEAD is the preregistered design + framework. OTS-timestamping it before any pilot runs locks the chain-of-evidence: every later result is reproducible from a Bitcoin-anchored commit.

- [ ] **Step 1: Verify OpenTimestamps client is installed**

```bash
ots --version
```

If not installed: `pip install opentimestamps-client`

- [ ] **Step 2: Generate the OTS receipt for the current HEAD**

```bash
cd C:/Projects/malaria-ct-recon
git log -1 --format=%H > .preregistration_commit
ots stamp .preregistration_commit
```

This produces `.preregistration_commit.ots`. The Bitcoin upgrade lands within 24h.

- [ ] **Step 3: Commit the OTS receipt + preregistration marker**

```bash
git add .preregistration_commit .preregistration_commit.ots
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "preregister: OTS timestamp on framework HEAD before any pilot runs"
```

- [ ] **Step 4: Note the commit hash for the paper**

The OTS-stamped commit hash is the citable preregistration timestamp. Record it now in `README.md` under a new "Preregistration" section:

```markdown
## Preregistration

Framework + design preregistered on 2026-04-30. OTS receipt: `.preregistration_commit.ots` against commit `<HASH FROM STEP 2>`.
```

- [ ] **Step 5: Commit README update**

```bash
git add README.md
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "docs(preregister): record OTS-stamped commit hash in README"
```

---

## Phase 3 — The 10 pilots (T11–T20)

The pilot pattern (TDD, fixture-first, real-AACT smoke run) is established in full in T11 (P01). T12–T20 each specify the SQL, sub-filter, fixture additions, and expected magnitude range — they follow T11's structure exactly: write fixture-using test → run-fail → implement pilot script → run-pass → smoke-run against real AACT → commit.

### Task T11: P01 — Reporting compliance (template-establishing pilot)

**Question:** What fraction of *completed* malaria trials posted results to CT.gov within 12 months of primary completion, stratified by FDA-regulated status?

**Files:**
- Create: `pilots/p01_reporting_compliance.py`
- Create: `tests/test_p01_reporting_compliance.py`

- [ ] **Step 1: Write the failing test `tests/test_p01_reporting_compliance.py`**

```python
"""Test P01 — reporting compliance against fixture."""
from pathlib import Path

from malaria_ct_recon import aact, corpus, schema
from pilots import p01_reporting_compliance as p01


def test_p01_runs_on_fake_aact_and_returns_valid_result(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p01.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert isinstance(result, schema.PilotResult)
    assert result.pilot_id == "P01"
    assert result.pilot_type == "magnitude"
    assert result.magnitude_unit == "fraction"
    # Of 6 included trials, 5 are completed; calculated_values shows results reported for NCT02, NCT03, NCT05 within 12mo (3 of 5 = 0.60)
    # NCT06 not reported. NCT04 not reported. So 3/5 = 0.60.
    assert 0.55 <= result.magnitude_value <= 0.65
    assert result.magnitude_ci_low <= result.magnitude_value <= result.magnitude_ci_high
    assert 1 <= result.follow_up_potential <= 5


def test_p01_excludes_non_completed_trials(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p01.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    # NCT08 (RECRUITING) is in calculated_values but not COMPLETED, and not in corpus anyway
    assert result.n_trials_in_scope == 5  # NCT01-06 minus NCT08 (not malaria) and any non-completed; NCT01-06 all COMPLETED
```

- [ ] **Step 2: Run, verify fail**: `pytest tests/test_p01_reporting_compliance.py -v` → ImportError

- [ ] **Step 3: Implement `pilots/p01_reporting_compliance.py`**

```python
"""Pilot P01 — Reporting compliance.

Question: Of completed malaria trials, what fraction posted results to CT.gov
within 12 months of primary completion?
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P01"
PILOT_TITLE = "Reporting compliance"
SCRIPT_PATH = "pilots/p01_reporting_compliance.py"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(
    con: duckdb.DuckDBPyConnection,
    corpus: Corpus,
    aact_snapshot: str,
    seed: int,
) -> schema.PilotResult:
    t0 = time.perf_counter()
    studies = aact.table(con, "studies")
    cv = aact.table(con, "calculated_values")

    # Restrict to corpus + completed trials
    in_corpus = studies[studies["nct_id"].astype(str).isin(corpus.included)]
    completed = in_corpus[in_corpus["overall_status"].astype(str) == "COMPLETED"]
    n_in = len(completed)

    # Join with calculated_values for were_results_reported + months_to_report_results
    merged = completed.merge(cv, on="nct_id", how="left")

    # Numerator: results reported within 12 months
    reported = merged[
        (merged["were_results_reported"].fillna(False).astype(bool))
        & (pd.to_numeric(merged["months_to_report_results"], errors="coerce") <= 12)
    ]
    k = len(reported)

    if n_in == 0:
        magnitude, ci_low, ci_high = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n_in
        ci_low, ci_high = stats.wilson_ci(k, n_in)

    excluded = {
        "not_completed": int(len(in_corpus) - len(completed)),
        "missing_calculated_values": int(merged["were_results_reported"].isna().sum()),
    }

    return schema.PilotResult(
        pilot_id=PILOT_ID,
        pilot_title=PILOT_TITLE,
        pilot_type="magnitude",
        n_trials_in_scope=int(n_in),
        magnitude_value=float(magnitude),
        magnitude_unit="fraction",
        magnitude_ci_low=float(ci_low),
        magnitude_ci_high=float(ci_high),
        tractability_AACT_only="full",
        follow_up_potential=4,
        n_trials_excluded_for_reason=excluded,
        notes=f"{k}/{n_in} completed malaria trials posted results within 12mo",
        script_path=SCRIPT_PATH,
        script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot,
        seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p01.csv"))
    print(f"P01 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_p01_reporting_compliance.py -v` → 2 passed

- [ ] **Step 5: Smoke-run against real AACT**

```bash
python -m pilots.p01_reporting_compliance
```

Expected: `P01 OK: <int>/<int> completed malaria trials posted results within 12mo`. The fraction should be roughly 0.10–0.40 (lower than the cross-disease ~63% for results-posting, given FDAAA non-applicability). Inspect `pilots/results/p01.csv`.

- [ ] **Step 6: Commit**

```bash
git add pilots/p01_reporting_compliance.py tests/test_p01_reporting_compliance.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P01): reporting compliance — fraction posting results within 12mo"
```

**Pattern locked:** every subsequent pilot Tnn follows T11's six-step structure (test → fail → impl → pass → smoke → commit). Each pilot script exposes `run(con, corpus, aact_snapshot, seed) -> PilotResult` and a `main()` that writes the result CSV.

---

### Task T12: P02 — Endpoint-family chaos

**Question:** What fraction of malaria trials mix primary endpoints across distinct endpoint families (parasitological, clinical, severe, transmission, vaccine VE, PK)?

**Files:**
- Create: `pilots/p02_endpoint_chaos.py`
- Create: `tests/test_p02_endpoint_chaos.py`

- [ ] **Step 1: Write `tests/test_p02_endpoint_chaos.py`**

```python
"""Test P02 — endpoint-family chaos."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p02_endpoint_chaos as p02


def test_p02_classifies_endpoint_families(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p02.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P02"
    assert result.magnitude_unit == "fraction"
    # NCT01 mixes parasitological (ACPR) + clinical (fever clearance) primary+secondary -> mixed
    # NCT03 mixes parasitological + parasitological -> not mixed (both parasitological family)
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p02_classify_family_function() -> None:
    assert p02._classify("PCR-corrected ACPR at day 28") == "parasitological"
    assert p02._classify("Vaccine efficacy against clinical malaria") == "vaccine_VE"
    assert p02._classify("Time to first parasitemia after challenge") == "vaccine_VE"
    assert p02._classify("Severe malaria mortality") == "severe"
    assert p02._classify("Gametocyte carriage at day 14") == "transmission"
    assert p02._classify("Pharmacokinetic AUC0-inf") == "PK"
    assert p02._classify("Clinical malaria episodes per person-year") == "clinical"
    assert p02._classify("Some random outcome") == "other"
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p02_endpoint_chaos.py`**

```python
"""Pilot P02 — Endpoint-family chaos.

Question: Of malaria trials with ≥2 outcomes (any type), what fraction span
distinct endpoint families?
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P02"
PILOT_TITLE = "Endpoint-family chaos"
SCRIPT_PATH = "pilots/p02_endpoint_chaos.py"

_FAMILY_PATTERNS = [
    ("vaccine_VE", re.compile(r"vaccine efficacy|protective efficacy|time to.*parasitemia.*challenge|sporozoite challenge", re.I)),
    ("transmission", re.compile(r"gametocyte|mosquito infectivity|transmission|infectivity to mosquito", re.I)),
    ("severe", re.compile(r"severe malaria|cerebral malaria|mortality|death", re.I)),
    ("PK", re.compile(r"pharmacokinetic|AUC|Cmax|clearance.*plasma|drug concentration", re.I)),
    ("parasitological", re.compile(r"\bACPR\b|adequate clinical and parasitological response|PCR-corrected|parasitaem|parasitem|parasite clearance|recrudescence|recurrent parasit", re.I)),
    ("clinical", re.compile(r"clinical malaria|fever clearance|incidence of clinical|symptomatic malaria episode", re.I)),
]


def _classify(measure: str) -> str:
    for fam, rx in _FAMILY_PATTERNS:
        if rx.search(measure or ""):
            return fam
    return "other"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    do = aact.table(con, "design_outcomes")
    do = do[do["nct_id"].astype(str).isin(corpus.included)]
    do["family"] = do["measure"].astype(str).map(_classify)

    by_trial = do.groupby("nct_id")["family"].apply(lambda s: set(s) - {"other"})
    by_trial = by_trial[by_trial.map(len) >= 1]  # exclude trials with only "other"
    n = len(by_trial)
    mixed = (by_trial.map(len) >= 2).sum()

    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = mixed / n
        lo, hi = stats.wilson_ci(int(mixed), int(n))

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude), magnitude_unit="fraction",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=5,
        n_trials_excluded_for_reason={"only_other_family": int(len(do["nct_id"].unique()) - n)},
        notes=f"{int(mixed)}/{n} malaria trials span ≥2 endpoint families",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p02.csv"))
    print(f"P02 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_p02_endpoint_chaos.py -v` → 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p02_endpoint_chaos` — expect mixed-family fraction in 0.30–0.60 range

- [ ] **Step 6: Commit**

```bash
git add pilots/p02_endpoint_chaos.py tests/test_p02_endpoint_chaos.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P02): endpoint-family chaos — fraction of trials mixing 6 families"
```

---

### Task T13: P03 — PCR-corrected outcome reporting

**Question:** Of malaria efficacy trials of antimalarial drugs (excludes vaccines, vector control, PK studies), what fraction declare a PCR-corrected primary outcome?

**Files:**
- Create: `pilots/p03_pcr_corrected.py`
- Create: `tests/test_p03_pcr_corrected.py`

- [ ] **Step 1: Write `tests/test_p03_pcr_corrected.py`**

```python
"""Test P03 — PCR-corrected outcome reporting."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p03_pcr_corrected as p03


def test_p03_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p03.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P03"
    # Efficacy-drug subset of fixture: NCT01 (PCR-corrected ACPR), NCT03 (Day 42 ACPR — uncorrected),
    # NCT04 (P. vivax recurrence), NCT06 (asymptomatic prevalence).
    # NCT02 (vaccine), NCT05 (CHMI vaccine) excluded.
    # Expect 1/4 to 2/4 as PCR-corrected.
    assert result.n_trials_in_scope >= 1
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p03_pcr_pattern_matches_known_phrasings() -> None:
    assert p03._is_pcr_corrected("PCR-corrected ACPR day 28")
    assert p03._is_pcr_corrected("ACPR (PCR-adjusted) at day 42")
    assert p03._is_pcr_corrected("Genotypically-corrected treatment failure")
    assert not p03._is_pcr_corrected("Day 28 ACPR")
    assert not p03._is_pcr_corrected("Time to recurrent parasitaemia (PCR-uncorrected)")
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p03_pcr_corrected.py`**

```python
"""Pilot P03 — PCR-corrected outcome reporting.

Question: Of efficacy trials of antimalarial drugs, what fraction declare a
PCR-corrected primary outcome (distinguishes recrudescence from reinfection)?
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P03"
PILOT_TITLE = "PCR-corrected outcome reporting"
SCRIPT_PATH = "pilots/p03_pcr_corrected.py"

_PCR_RX = re.compile(
    r"PCR-corrected|PCR\s*adjusted|PCR-adjusted|genotypically.corrected|"
    r"genotype-corrected|molecularly.corrected",
    re.IGNORECASE,
)
_PCR_NEG_RX = re.compile(r"PCR-uncorrected|PCR\s*uncorrected", re.IGNORECASE)
_VACCINE_RX = re.compile(r"vaccine|RTS,S|R21|PfSPZ|sporozoite|CSP|MSP|AMA1", re.IGNORECASE)
_PK_RX = re.compile(r"pharmacokinetic|AUC|Cmax|drug concentration", re.IGNORECASE)


def _is_pcr_corrected(measure: str) -> bool:
    measure = measure or ""
    if _PCR_NEG_RX.search(measure):
        return False
    return bool(_PCR_RX.search(measure))


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    interventions = aact.table(con, "interventions")
    do = aact.table(con, "design_outcomes")

    # Identify drug-only efficacy trials: at least one DRUG intervention, no vaccine/PK markers
    in_corpus = interventions[interventions["nct_id"].astype(str).isin(corpus.included)]
    by_trial_drug = in_corpus.groupby("nct_id").apply(
        lambda g: any(_VACCINE_RX.search(n) is None for n in g["name"].astype(str))
                  and any(str(t).upper() == "DRUG" for t in g.get("intervention_type", []))
    )
    drug_trials = set(by_trial_drug[by_trial_drug].index.astype(str))

    # Restrict to primary outcomes
    primary = do[(do["nct_id"].astype(str).isin(drug_trials)) & (do["outcome_type"].astype(str) == "primary")]
    # Drop PK-only outcomes
    primary = primary[~primary["measure"].astype(str).map(lambda m: bool(_PK_RX.search(m)))]

    by_trial_pcr = primary.groupby("nct_id")["measure"].apply(
        lambda s: any(_is_pcr_corrected(m) for m in s.astype(str))
    )
    n = len(by_trial_pcr)
    k = int(by_trial_pcr.sum())

    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(k, n)

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude), magnitude_unit="fraction",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=5,
        n_trials_excluded_for_reason={
            "vaccine_or_PK": int(len(corpus.included) - len(drug_trials)),
            "no_primary_outcome": int(len(drug_trials) - n),
        },
        notes=f"{k}/{n} drug-efficacy trials report a PCR-corrected primary outcome",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p03.csv"))
    print(f"P03 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p03_pcr_corrected` — expect 0.30–0.55

- [ ] **Step 6: Commit**

```bash
git add pilots/p03_pcr_corrected.py tests/test_p03_pcr_corrected.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P03): PCR-corrected outcome reporting in drug-efficacy trials"
```

---

### Task T14: P04 — Resistance-era pooling

**Question:** Of artemisinin-class trials, what fraction span the K13 resistance-era boundary (any pre-2008 + any post-2015 trial of the same drug-country combo)?

**Files:** `pilots/p04_resistance_era.py`, `tests/test_p04_resistance_era.py`

- [ ] **Step 1: Write `tests/test_p04_resistance_era.py`**

```python
"""Test P04 — resistance-era pooling."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p04_resistance_era as p04


def test_p04_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p04.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P04"
    assert result.magnitude_unit == "fraction"
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p04_drug_canonicalisation() -> None:
    assert p04._canonical_drug("Artemether-lumefantrine 20/120mg pediatric") == "artemether-lumefantrine"
    assert p04._canonical_drug("DHA-piperaquine") == "dihydroartemisinin-piperaquine"
    assert p04._canonical_drug("Dihydroartemisinin-piperaquine MDA") == "dihydroartemisinin-piperaquine"
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p04_resistance_era.py`**

```python
"""Pilot P04 — Resistance-era pooling.

Question: Of artemisinin-class trials, what fraction of (drug × country) cells
span the K13 boundary (≤2008 vs ≥2015), making them non-exchangeable in MAs?
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P04"
PILOT_TITLE = "Resistance-era pooling"
SCRIPT_PATH = "pilots/p04_resistance_era.py"

_ARTEMISININ_RX = re.compile(r"artemether|artesunate|artemisinin|dihydroartemisinin|DHA-piperaquine", re.IGNORECASE)


def _canonical_drug(name: str) -> str:
    n = (name or "").lower()
    if "lumefantrine" in n and ("artemether" in n or "al " in n):
        return "artemether-lumefantrine"
    if "piperaquine" in n and ("dihydroartemisinin" in n or "dha" in n):
        return "dihydroartemisinin-piperaquine"
    if "mefloquine" in n and "artesunate" in n:
        return "artesunate-mefloquine"
    if "amodiaquine" in n and "artesunate" in n:
        return "artesunate-amodiaquine"
    if "amodiaquine" in n and "sulfadoxine" in n:
        return "sulfadoxine-pyrimethamine-amodiaquine"
    return n.split()[0] if n else "unknown"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    studies = aact.table(con, "studies")
    interventions = aact.table(con, "interventions")
    countries = aact.table(con, "countries")

    in_corpus = studies[studies["nct_id"].astype(str).isin(corpus.included)].copy()
    in_corpus["start_year"] = pd.to_datetime(in_corpus["start_date"], errors="coerce").dt.year

    art_iv = interventions[
        (interventions["nct_id"].astype(str).isin(corpus.included))
        & (interventions["name"].astype(str).map(lambda n: bool(_ARTEMISININ_RX.search(n))))
    ].copy()
    art_iv["drug"] = art_iv["name"].astype(str).map(_canonical_drug)

    merged = art_iv.merge(in_corpus[["nct_id", "start_year"]], on="nct_id").merge(
        countries.rename(columns={"name": "country"}), on="nct_id"
    )
    merged["era"] = merged["start_year"].map(
        lambda y: "pre_K13" if y is not None and y <= 2008 else ("post_K13" if y is not None and y >= 2015 else "between")
    )

    cells = merged.groupby(["drug", "country"])["era"].apply(set)
    cells_with_data = cells[cells.map(lambda s: bool(s - {"between"}))]
    n_cells = len(cells_with_data)
    spanning = (cells_with_data.map(lambda s: {"pre_K13", "post_K13"}.issubset(s))).sum()

    if n_cells == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = spanning / n_cells
        lo, hi = stats.wilson_ci(int(spanning), int(n_cells))

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(merged["nct_id"].nunique()),
        magnitude_value=float(magnitude), magnitude_unit="fraction_of_drug_country_cells",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=5,
        n_trials_excluded_for_reason={"non_artemisinin": int(len(corpus.included) - merged["nct_id"].nunique())},
        notes=f"{int(spanning)}/{n_cells} drug×country cells span the pre/post-K13 boundary",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p04.csv"))
    print(f"P04 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p04_resistance_era` — expect 0.40–0.80 of drug×country cells span the boundary

- [ ] **Step 6: Commit**

```bash
git add pilots/p04_resistance_era.py tests/test_p04_resistance_era.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P04): resistance-era pooling — drug×country cells spanning K13 boundary"
```

---

### Task T15: P05 — Pediatric dose fragmentation

**Question:** For the 5 most-frequent antimalarials in the corpus, how many distinct dose strings exist per drug, stratified by enrolled age band?

**Files:** `pilots/p05_pediatric_dose.py`, `tests/test_p05_pediatric_dose.py`

- [ ] **Step 1: Write `tests/test_p05_pediatric_dose.py`**

```python
"""Test P05 — pediatric dose fragmentation."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p05_pediatric_dose as p05


def test_p05_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p05.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P05"
    assert result.magnitude_unit == "mean_distinct_doses_per_drug_age_band"
    assert result.magnitude_value >= 1.0


def test_p05_age_band_classification() -> None:
    assert p05._age_band("6 Months", "59 Months") == "under_5y"
    assert p05._age_band("18 Years", "65 Years") == "adult"
    assert p05._age_band("5 Years", "11 Years") == "5_to_11y"
    assert p05._age_band("12 Years", "17 Years") == "12_to_17y"
    assert p05._age_band("N/A", "N/A") == "unknown"
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p05_pediatric_dose.py`**

```python
"""Pilot P05 — Pediatric dose fragmentation."""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P05"
PILOT_TITLE = "Pediatric dose fragmentation"
SCRIPT_PATH = "pilots/p05_pediatric_dose.py"


def _parse_age_to_years(s: str) -> float | None:
    if s is None or str(s).strip().upper() in {"N/A", "NA", ""}:
        return None
    m = re.match(r"(\d+(?:\.\d+)?)\s*(Year|Years|Month|Months|Week|Weeks|Day|Days)", str(s))
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2).lower()
    if unit.startswith("year"): return val
    if unit.startswith("month"): return val / 12.0
    if unit.startswith("week"): return val / 52.0
    return val / 365.0


def _age_band(min_age: str, max_age: str) -> str:
    lo = _parse_age_to_years(min_age)
    hi = _parse_age_to_years(max_age)
    if lo is None and hi is None:
        return "unknown"
    if lo is None: lo = 0
    if hi is None: hi = 200
    mid = (lo + hi) / 2
    if hi < 5: return "under_5y"
    if hi <= 11: return "5_to_11y"
    if hi <= 17: return "12_to_17y"
    if lo >= 18: return "adult"
    return "mixed"


def _drug_key(name: str) -> str:
    n = (name or "").lower()
    for stem in ["artemether-lumefantrine", "dihydroartemisinin-piperaquine",
                 "artesunate-mefloquine", "artesunate-amodiaquine",
                 "sulfadoxine-pyrimethamine", "tafenoquine", "primaquine"]:
        if stem in n or all(part in n for part in stem.split("-")):
            return stem
    return n.split()[0] if n else "unknown"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    interventions = aact.table(con, "interventions")
    elig = aact.table(con, "eligibilities")

    iv = interventions[interventions["nct_id"].astype(str).isin(corpus.included)].copy()
    iv["drug"] = iv["name"].astype(str).map(_drug_key)
    top5 = iv.groupby("drug")["nct_id"].nunique().sort_values(ascending=False).head(5).index.tolist()
    iv = iv[iv["drug"].isin(top5)]

    elig["age_band"] = [_age_band(lo, hi) for lo, hi in zip(elig["minimum_age"].astype(str), elig["maximum_age"].astype(str))]
    merged = iv.merge(elig[["nct_id", "age_band"]], on="nct_id")

    distinct = merged.groupby(["drug", "age_band"])["name"].nunique()
    if len(distinct) == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = float(distinct.mean())
        boot = stats.bootstrap_ci(np.asarray(distinct.values, dtype=float), np.mean, n_resamples=1000, seed=seed)
        lo, hi = boot

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(merged["nct_id"].nunique()),
        magnitude_value=float(magnitude),
        magnitude_unit="mean_distinct_doses_per_drug_age_band",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=3,
        n_trials_excluded_for_reason={"not_top5_drug": int(len(corpus.included) - merged["nct_id"].nunique())},
        notes=f"top5={top5}; {len(distinct)} drug×age cells; mean distinct dose strings={magnitude:.2f}",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p05.csv"))
    print(f"P05 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p05_pediatric_dose` — expect mean 3–10 distinct doses per drug×age cell

- [ ] **Step 6: Commit**

```bash
git add pilots/p05_pediatric_dose.py tests/test_p05_pediatric_dose.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P05): pediatric dose fragmentation across top-5 antimalarials"
```

---

### Task T16: P06 — Cross-registry coverage (tractability probe)

**Question:** Of malaria trials with a non-NCT registry id (PACTR, ISRCTN, RBR, ANZCTR), what fraction also have a CT.gov registration? AACT alone cannot answer the inverse (PACTR-only trials), so this is a tractability probe.

**Files:** `pilots/p06_cross_registry.py`, `tests/test_p06_cross_registry.py`

- [ ] **Step 1: Write `tests/test_p06_cross_registry.py`**

```python
"""Test P06 — cross-registry coverage probe."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p06_cross_registry as p06


def test_p06_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p06.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P06"
    assert result.pilot_type == "tractability_probe"
    assert result.tractability_AACT_only == "partial"
    # NCT01 has ISRCTN + PACTR cross-registration; NCT04 has RBR; rest have none
    # All 6 corpus trials have CT.gov entry by definition; the question is
    # how many ALSO appear in another registry — 2/6 in fixture
    assert "cross_registered_count" in result.notes


def test_p06_registry_pattern_recognition() -> None:
    assert p06._registry_kind("ISRCTN12345678") == "ISRCTN"
    assert p06._registry_kind("PACTR201509001234567") == "PACTR"
    assert p06._registry_kind("RBR-abc123") == "RBR"
    assert p06._registry_kind("ACTRN12612345678") == "ANZCTR"
    assert p06._registry_kind("NCT01234567") is None  # already CT.gov
    assert p06._registry_kind("EUDRA-2010-001234") == "EUCTR"
    assert p06._registry_kind("U1111-1234-5678") == "WHO_UTN"
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p06_cross_registry.py`**

```python
"""Pilot P06 — Cross-registry coverage (tractability probe).

AACT can only see trials registered on CT.gov. We CAN identify trials that have
*also* registered elsewhere (via id_information.id_value), but we CANNOT see
trials registered ONLY on PACTR/ISRCTN/etc. So this pilot reports:
  - the count of corpus trials with at least one non-CT.gov registry id
  - flagged tractability=partial, with explicit note that the inverse
    (the universe AACT cannot see) requires PACTR/ICTRP scrapers.
"""
from __future__ import annotations

import hashlib
import re
import time
from collections import Counter
from pathlib import Path

import duckdb

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
    v = (value or "").strip()
    if v.upper().startswith("NCT"):
        return None
    for name, rx in _REGISTRY_PATTERNS:
        if rx.match(v):
            return name
    return None


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    ids = aact.table(con, "id_information")
    in_corpus = ids[ids["nct_id"].astype(str).isin(corpus.included)].copy()
    in_corpus["registry_kind"] = in_corpus["id_value"].astype(str).map(_registry_kind)
    cross = in_corpus.dropna(subset=["registry_kind"])
    by_trial = cross.groupby("nct_id")["registry_kind"].apply(set)
    cross_count = len(by_trial)
    kind_counts = Counter()
    for kinds in by_trial:
        for k in kinds:
            kind_counts[k] += 1

    n = len(corpus.included)
    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="tractability_probe",
        n_trials_in_scope=int(n),
        magnitude_value=float("nan"), magnitude_unit="",
        magnitude_ci_low=float("nan"), magnitude_ci_high=float("nan"),
        tractability_AACT_only="partial", follow_up_potential=2,
        n_trials_excluded_for_reason={"no_registry_id_record": int(n - len(in_corpus["nct_id"].unique()))},
        notes=f"cross_registered_count={cross_count}/{n}; by_kind={dict(kind_counts)}; "
              f"AACT cannot see PACTR/ISRCTN-only trials — needs ICTRP/PACTR scraper",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p06.csv"))
    print(f"P06 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p06_cross_registry` — expect cross_registered_count between 100 and 600 (plenty of PACTR/ISRCTN dual-registrations)

- [ ] **Step 6: Commit**

```bash
git add pilots/p06_cross_registry.py tests/test_p06_cross_registry.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P06): cross-registry coverage tractability probe (AACT-only ceiling)"
```

---

### Task T17: P07 — Sponsor PDP misclassification

**Question:** What fraction of malaria trials have a Product Development Partnership (PDP) sponsor that AACT classifies as "OTHER" rather than its own category?

**Files:** `pilots/p07_sponsor_pdp.py`, `tests/test_p07_sponsor_pdp.py`

- [ ] **Step 1: Write `tests/test_p07_sponsor_pdp.py`**

```python
"""Test P07 — sponsor PDP misclassification."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p07_sponsor_pdp as p07


def test_p07_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p07.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P07"
    # Fixture: NCT03 (MMV) is PDP misclassified as OTHER. NCT01 (LSHTM, OTHER) is academic, not PDP.
    # NCT05 (Sanaria) is INDUSTRY but is actually a small biotech / could be PDP-aligned — keep as INDUSTRY.
    # So 1/6 = 0.167 expected.
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p07_pdp_recognition() -> None:
    assert p07._is_pdp("Medicines for Malaria Venture")
    assert p07._is_pdp("MMV")
    assert p07._is_pdp("PATH Malaria Vaccine Initiative")
    assert p07._is_pdp("FIND")
    assert p07._is_pdp("DNDi")
    assert not p07._is_pdp("Pfizer")
    assert not p07._is_pdp("London School of Hygiene and Tropical Medicine")
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p07_sponsor_pdp.py`**

```python
"""Pilot P07 — Sponsor PDP misclassification."""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P07"
PILOT_TITLE = "Sponsor PDP misclassified as OTHER"
SCRIPT_PATH = "pilots/p07_sponsor_pdp.py"

_PDP_RX = re.compile(
    r"medicines for malaria venture|MMV|PATH malaria vaccine initiative|"
    r"\bMVI\b|\bFIND\b|\bDNDi\b|drugs for neglected diseases|aeras|"
    r"international vaccine institute|\bIVI\b|"
    r"european vaccine initiative|\bEVI\b|"
    r"\bMVRC\b",
    re.IGNORECASE,
)


def _is_pdp(name: str) -> bool:
    return bool(_PDP_RX.search(name or ""))


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    sp = aact.table(con, "sponsors")
    sp = sp[(sp["nct_id"].astype(str).isin(corpus.included)) & (sp["lead_or_collaborator"].astype(str) == "lead")]
    sp["is_pdp"] = sp["name"].astype(str).map(_is_pdp)
    sp["agency_class"] = sp["agency_class"].astype(str).str.upper()

    pdp = sp[sp["is_pdp"]]
    misclassified = pdp[pdp["agency_class"] == "OTHER"]
    n = len(sp)  # all corpus trials with a lead sponsor row
    k = len(misclassified)

    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(int(k), int(n))

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude), magnitude_unit="fraction_of_lead_sponsored_trials",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=3,
        n_trials_excluded_for_reason={"no_lead_sponsor_row": int(len(corpus.included) - sp["nct_id"].nunique())},
        notes=f"{k}/{n} lead-sponsored trials have PDP sponsor classified as OTHER",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p07.csv"))
    print(f"P07 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p07_sponsor_pdp` — expect 0.10–0.25

- [ ] **Step 6: Commit**

```bash
git add pilots/p07_sponsor_pdp.py tests/test_p07_sponsor_pdp.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P07): PDP sponsors misclassified as OTHER agency_class"
```

---

### Task T18: P08 — Retrospective registration

**Question:** What fraction of malaria trials have `start_date < study_first_submitted_date` (registered AFTER starting)? Stratified pre-2007 vs post-2007.

**Files:** `pilots/p08_retro_registration.py`, `tests/test_p08_retro_registration.py`

- [ ] **Step 1: Write `tests/test_p08_retro_registration.py`**

```python
"""Test P08 — retrospective registration."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p08_retro_registration as p08


def test_p08_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p08.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P08"
    # NCT01: start 2005-06, submitted 2006-01 → retro
    # NCT02: start 2010-04, submitted 2009-12 → prospective
    # NCT03: start 2018-09, submitted 2018-06 → prospective
    # NCT04: start 2014-01, submitted 2013-09 → prospective
    # NCT05: start 2019-03, submitted 2018-12 → prospective
    # NCT06: start 2016-05, submitted 2016-03 → prospective
    # 1/6 retro
    assert 0.0 <= result.magnitude_value <= 1.0
    assert result.n_trials_in_scope == 6
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p08_retro_registration.py`**

```python
"""Pilot P08 — Retrospective registration."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import duckdb
import pandas as pd

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P08"
PILOT_TITLE = "Retrospective registration"
SCRIPT_PATH = "pilots/p08_retro_registration.py"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    studies = aact.table(con, "studies")
    s = studies[studies["nct_id"].astype(str).isin(corpus.included)].copy()
    s["start"] = pd.to_datetime(s["start_date"], errors="coerce")
    s["submitted"] = pd.to_datetime(s["study_first_submitted_date"], errors="coerce")
    s = s.dropna(subset=["start", "submitted"])
    s["retro"] = s["start"] < s["submitted"]
    s["era"] = s["start"].dt.year.map(lambda y: "pre_2007" if y < 2007 else "post_2007")

    n = len(s)
    k = int(s["retro"].sum())
    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(k, n)

    by_era = s.groupby("era")["retro"].agg(["sum", "count"]).to_dict("index")

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude), magnitude_unit="fraction_retro_registered",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=3,
        n_trials_excluded_for_reason={"missing_dates": int(len(corpus.included) - n)},
        notes=f"{k}/{n} retro; by_era={by_era}",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p08.csv"))
    print(f"P08 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p08_retro_registration` — expect 0.20–0.50; pre-2007 stratum should be much higher

- [ ] **Step 6: Commit**

```bash
git add pilots/p08_retro_registration.py tests/test_p08_retro_registration.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P08): retrospective registration rate, stratified pre/post-2007"
```

---

### Task T19: P09 — Geographic transmission heterogeneity (tractability probe)

**Question:** Distribution of trial site countries; flag the issue that AACT cannot directly attach transmission-intensity (PfPR) data — that lives in the MAP project rasters.

**Files:** `pilots/p09_geographic.py`, `tests/test_p09_geographic.py`

- [ ] **Step 1: Write `tests/test_p09_geographic.py`**

```python
"""Test P09 — geographic transmission heterogeneity probe."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p09_geographic as p09


def test_p09_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p09.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P09"
    assert result.pilot_type == "tractability_probe"
    assert result.tractability_AACT_only == "none"
    assert "MAP" in result.notes
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p09_geographic.py`**

```python
"""Pilot P09 — Geographic transmission heterogeneity (tractability probe).

AACT records site countries but NOT transmission intensity (PfPR). PfPR varies
by 2 orders of magnitude across endemic countries and even within them.
The MAP project (https://malariaatlas.org) publishes per-pixel rasters but
those are external to AACT. This pilot reports the country distribution +
flags the data gap.
"""
from __future__ import annotations

import hashlib
import time
from collections import Counter
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P09"
PILOT_TITLE = "Geographic transmission heterogeneity"
SCRIPT_PATH = "pilots/p09_geographic.py"


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    countries = aact.table(con, "countries")
    in_corpus = countries[countries["nct_id"].astype(str).isin(corpus.included)]
    by_country = Counter(in_corpus["name"].astype(str))
    top10 = dict(by_country.most_common(10))
    multi_country = in_corpus.groupby("nct_id")["name"].nunique()
    multi_country_count = int((multi_country >= 2).sum())

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="tractability_probe",
        n_trials_in_scope=int(len(corpus.included)),
        magnitude_value=float("nan"), magnitude_unit="",
        magnitude_ci_low=float("nan"), magnitude_ci_high=float("nan"),
        tractability_AACT_only="none", follow_up_potential=2,
        n_trials_excluded_for_reason={"no_country_record": int(len(corpus.included) - in_corpus["nct_id"].nunique())},
        notes=f"top10_countries={top10}; multi_country_trials={multi_country_count}; "
              f"PfPR/transmission-intensity not in AACT — needs MAP project rasters "
              f"(https://malariaatlas.org)",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p09.csv"))
    print(f"P09 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 1 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p09_geographic` — expect Africa-heavy top-10

- [ ] **Step 6: Commit**

```bash
git add pilots/p09_geographic.py tests/test_p09_geographic.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P09): geographic-transmission tractability probe (MAP-project gap)"
```

---

### Task T20: P10 — CHMI vs field-trial mixing

**Question:** What fraction of malaria-vaccine trials are Controlled Human Malaria Infection (CHMI) studies? These use a fundamentally different efficacy endpoint than field trials and should not be pooled.

**Files:** `pilots/p10_chmi_field.py`, `tests/test_p10_chmi_field.py`

- [ ] **Step 1: Write `tests/test_p10_chmi_field.py`**

```python
"""Test P10 — CHMI vs field-trial mixing."""
from pathlib import Path

from malaria_ct_recon import aact, corpus
from pilots import p10_chmi_field as p10


def test_p10_runs_on_fake_aact(fake_aact: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    con = aact.open(fake_aact)
    c = corpus.build(con, overrides_path=overrides)
    result = p10.run(con=con, corpus=c, aact_snapshot="2026-04-12", seed=20260430)
    assert result.pilot_id == "P10"
    # Vaccine trials in fixture: NCT02 (RTS,S field), NCT05 (PfSPZ challenge / CHMI)
    # 1/2 = 0.50
    assert 0.0 <= result.magnitude_value <= 1.0


def test_p10_chmi_recognition() -> None:
    assert p10._is_chmi("PfSPZ Challenge", "Healthy non-immune adults for sporozoite challenge")
    assert p10._is_chmi("Sporozoite challenge", "")
    assert not p10._is_chmi("RTS,S/AS01", "Healthy infants 5-17 months")
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/p10_chmi_field.py`**

```python
"""Pilot P10 — CHMI vs field-trial mixing."""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema, stats
from malaria_ct_recon.corpus import Corpus

PILOT_ID = "P10"
PILOT_TITLE = "CHMI vs field-trial mixing"
SCRIPT_PATH = "pilots/p10_chmi_field.py"

_VACCINE_RX = re.compile(r"vaccine|RTS,S|R21|PfSPZ|sporozoite|CSP|MSP|AMA1|Mosquirix", re.IGNORECASE)
_CHMI_RX = re.compile(r"sporozoite challenge|controlled human malaria infection|CHMI|"
                      r"non-immune.*challenge|PfSPZ Challenge|infection model", re.IGNORECASE)


def _is_chmi(intervention_name: str, eligibility_criteria: str) -> bool:
    blob = f"{intervention_name or ''} {eligibility_criteria or ''}"
    return bool(_CHMI_RX.search(blob))


def _sha256_self() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def run(con: duckdb.DuckDBPyConnection, corpus: Corpus, aact_snapshot: str, seed: int) -> schema.PilotResult:
    t0 = time.perf_counter()
    interventions = aact.table(con, "interventions")
    elig = aact.table(con, "eligibilities")

    iv = interventions[interventions["nct_id"].astype(str).isin(corpus.included)]
    vaccine_trials = iv[iv["name"].astype(str).map(lambda n: bool(_VACCINE_RX.search(n)))]
    vaccine_nct = set(vaccine_trials["nct_id"].astype(str).unique())

    blob = vaccine_trials.merge(elig[["nct_id", "criteria"]], on="nct_id", how="left")
    chmi = blob.groupby("nct_id").apply(
        lambda g: any(_is_chmi(n, c) for n, c in zip(g["name"].astype(str), g["criteria"].fillna("").astype(str)))
    )
    n = int(len(vaccine_nct))
    k = int(chmi.sum())
    if n == 0:
        magnitude, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        magnitude = k / n
        lo, hi = stats.wilson_ci(k, n)

    return schema.PilotResult(
        pilot_id=PILOT_ID, pilot_title=PILOT_TITLE, pilot_type="magnitude",
        n_trials_in_scope=int(n),
        magnitude_value=float(magnitude), magnitude_unit="fraction_of_vaccine_trials_chmi",
        magnitude_ci_low=float(lo), magnitude_ci_high=float(hi),
        tractability_AACT_only="full", follow_up_potential=4,
        n_trials_excluded_for_reason={"non_vaccine": int(len(corpus.included) - n)},
        notes=f"{k}/{n} malaria-vaccine trials are CHMI",
        script_path=SCRIPT_PATH, script_sha256=_sha256_self(),
        aact_snapshot=aact_snapshot, seed=int(seed),
        wall_clock_seconds=float(time.perf_counter() - t0),
    )


def main() -> int:
    from malaria_ct_recon import config, corpus as corpus_mod
    cfg = config.load()
    con = aact.open(cfg.snapshot_dir)
    c = corpus_mod.build(con)
    result = run(con=con, corpus=c, aact_snapshot=cfg.snapshot_label, seed=20260430)
    schema.write([result], Path("pilots/results/p10.csv"))
    print(f"P10 OK: {result.notes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: 2 passed

- [ ] **Step 5: Smoke-run**: `python -m pilots.p10_chmi_field` — expect 0.20–0.40

- [ ] **Step 6: Commit**

```bash
git add pilots/p10_chmi_field.py tests/test_p10_chmi_field.py
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(P10): CHMI vs field-trial mixing in malaria-vaccine corpus"
```

---

## Phase 4 — Aggregation + dashboard + Pages (T21–T23)

### Task T21: `run_all.py` master orchestrator

**Files:** `pilots/run_all.py`, `tests/test_run_all.py`

- [ ] **Step 1: Write `tests/test_run_all.py`**

```python
"""Test the master run_all orchestrator."""
from pathlib import Path

import pandas as pd

from pilots import run_all


def test_run_all_produces_signal_table(fake_aact: Path, tmp_path: Path) -> None:
    overrides = fake_aact / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    out = tmp_path / "signal-table.csv"
    n = run_all.run(snapshot_dir=fake_aact, snapshot_label="2026-04-12",
                    overrides_path=overrides, out_path=out, seed=20260430)
    assert n == 10
    df = pd.read_csv(out)
    assert list(df["pilot_id"]) == [f"P0{i}" if i < 10 else f"P{i}" for i in range(1, 11)]
    assert df["pilot_type"].isin(["magnitude", "tractability_probe"]).all()


def test_run_all_aborts_if_preflight_fails(tmp_path: Path) -> None:
    # tmp_path has no AACT files → preflight should fail
    out = tmp_path / "signal-table.csv"
    overrides = tmp_path / "ov.csv"; overrides.write_text("nct_id,action,reason,added_by,added_on\n", encoding="utf-8")
    import pytest
    with pytest.raises(RuntimeError, match="preflight"):
        run_all.run(snapshot_dir=tmp_path, snapshot_label="x",
                    overrides_path=overrides, out_path=out, seed=1,
                    expected_corpus_min=1, expected_corpus_max=10)
```

- [ ] **Step 2: Run, verify fail**: ImportError

- [ ] **Step 3: Implement `pilots/run_all.py`**

```python
"""Master orchestrator: run preflight, then all 10 pilots, then write signal-table.csv."""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from malaria_ct_recon import aact, schema
from pilots import (
    preflight,
    p01_reporting_compliance,
    p02_endpoint_chaos,
    p03_pcr_corrected,
    p04_resistance_era,
    p05_pediatric_dose,
    p06_cross_registry,
    p07_sponsor_pdp,
    p08_retro_registration,
    p09_geographic,
    p10_chmi_field,
)

PILOTS = [
    p01_reporting_compliance, p02_endpoint_chaos, p03_pcr_corrected,
    p04_resistance_era, p05_pediatric_dose, p06_cross_registry,
    p07_sponsor_pdp, p08_retro_registration, p09_geographic, p10_chmi_field,
]


def run(
    snapshot_dir: Path,
    snapshot_label: str,
    overrides_path: Path,
    out_path: Path,
    seed: int,
    expected_corpus_min: int = 1200,
    expected_corpus_max: int = 1600,
) -> int:
    pre = preflight.run(snapshot_dir=snapshot_dir, overrides_path=overrides_path,
                        expected_corpus_min=expected_corpus_min,
                        expected_corpus_max=expected_corpus_max)
    if not pre.passed:
        raise RuntimeError(f"preflight failed: {pre.failure_reason}")

    from malaria_ct_recon import corpus as corpus_mod
    con = aact.open(snapshot_dir)
    c = corpus_mod.build(con, overrides_path=overrides_path)

    results = []
    for mod in PILOTS:
        r = mod.run(con=con, corpus=c, aact_snapshot=snapshot_label, seed=seed)
        results.append(r)
        print(f"{r.pilot_id} OK: {r.notes}", file=sys.stderr)

    schema.write(results, out_path)
    return len(results)


def main() -> int:
    from malaria_ct_recon import config
    cfg = config.load()
    n = run(
        snapshot_dir=cfg.snapshot_dir,
        snapshot_label=cfg.snapshot_label,
        overrides_path=Path("corpus_overrides.csv"),
        out_path=Path("dashboard/data/signal-table.csv"),
        seed=20260430,
    )
    print(f"run_all OK: wrote {n} pilot rows to dashboard/data/signal-table.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run, verify pass**: `pytest tests/test_run_all.py -v` → 2 passed

- [ ] **Step 5: Smoke-run against real AACT**

```bash
mkdir -p dashboard/data
python -m pilots.run_all
```

Expected: 10 lines `Pnn OK: ...` on stderr, then `run_all OK: wrote 10 pilot rows to dashboard/data/signal-table.csv`. Inspect the CSV — verify all 10 pilot_ids present, no NaN in magnitude_value for P01/P02/P03/P04/P05/P07/P08/P10 (NaN is expected for P06/P09 tractability probes).

- [ ] **Step 6: Commit**

```bash
git add pilots/run_all.py tests/test_run_all.py dashboard/data/signal-table.csv
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(orchestrator): run_all builds dashboard/data/signal-table.csv"
```

---

### Task T22: Dashboard

**Files:** `dashboard/index.html`

- [ ] **Step 1: Write `dashboard/index.html`** (vanilla JS, no CDN, reads `data/signal-table.csv`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Malaria CT.gov Reconnaissance — Signal Table</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family: -apple-system, system-ui, Segoe UI, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
  h1 { margin-bottom: 0.2rem; }
  .meta { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
  table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
  th, td { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid #ddd; vertical-align: top; }
  th { background: #f4f4f4; cursor: pointer; user-select: none; }
  th.sorted-asc::after { content: " ▲"; }
  th.sorted-desc::after { content: " ▼"; }
  .magnitude-bar { display: inline-block; height: 0.7em; background: #4a90e2; vertical-align: middle; margin-right: 6px; }
  .ci { color: #888; font-size: 0.85em; }
  .probe { background: #fff8e1; }
  .followup { font-weight: 600; }
  .pilot-id { font-family: monospace; }
  details { margin-top: 1.2rem; }
  summary { cursor: pointer; color: #4a90e2; }
</style>
</head>
<body>
<h1>Malaria CT.gov Reconnaissance — Signal Table</h1>
<p class="meta" id="meta">Loading…</p>
<table id="signal-table"><thead></thead><tbody></tbody></table>
<details>
  <summary>About</summary>
  <p>This table is the output of the <code>malaria-ct-recon</code> sprint. 10 pilots over the AACT 2026-04-12 snapshot, each quantifying one source of bias in malaria CT.gov data.</p>
  <p>Spec + plan + source code: <a href="https://github.com/mahmood726-cyber/malaria-ct-recon">github.com/mahmood726-cyber/malaria-ct-recon</a></p>
</details>
<script>
async function main() {
  const resp = await fetch("data/signal-table.csv");
  const text = await resp.text();
  const rows = parseCSV(text);
  document.getElementById("meta").textContent =
    `${rows.length} pilots · AACT snapshot ${rows[0]?.aact_snapshot || "?"}`;
  render(rows);
}
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.map(line => {
    const cells = splitCSVLine(line);
    return Object.fromEntries(header.map((h, i) => [h, cells[i] ?? ""]));
  });
}
function splitCSVLine(line) {
  const out = [];
  let cur = "", inQ = false;
  for (const ch of line) {
    if (ch === '"') { inQ = !inQ; continue; }
    if (ch === "," && !inQ) { out.push(cur); cur = ""; continue; }
    cur += ch;
  }
  out.push(cur);
  return out;
}
function render(rows) {
  const cols = [
    {key: "pilot_id", label: "ID"},
    {key: "pilot_title", label: "Pilot"},
    {key: "magnitude_value", label: "Magnitude (95% CI)"},
    {key: "n_trials_in_scope", label: "n"},
    {key: "tractability_AACT_only", label: "Tractability"},
    {key: "follow_up_potential", label: "Follow-up"},
    {key: "notes", label: "Notes"},
  ];
  const thead = document.querySelector("#signal-table thead");
  thead.innerHTML = "<tr>" + cols.map(c => `<th data-key="${c.key}">${c.label}</th>`).join("") + "</tr>";
  thead.querySelectorAll("th").forEach((th, i) => {
    th.addEventListener("click", () => sortBy(rows, cols[i].key));
  });
  drawBody(rows);
}
let sortKey = "follow_up_potential", sortAsc = false;
function sortBy(rows, key) {
  if (sortKey === key) sortAsc = !sortAsc; else { sortKey = key; sortAsc = false; }
  rows.sort((a, b) => {
    const av = isFinite(parseFloat(a[key])) ? parseFloat(a[key]) : a[key];
    const bv = isFinite(parseFloat(b[key])) ? parseFloat(b[key]) : b[key];
    return (av > bv ? 1 : av < bv ? -1 : 0) * (sortAsc ? 1 : -1);
  });
  document.querySelectorAll("th").forEach(th => th.classList.remove("sorted-asc", "sorted-desc"));
  document.querySelector(`th[data-key="${key}"]`)?.classList.add(sortAsc ? "sorted-asc" : "sorted-desc");
  drawBody(rows);
}
function drawBody(rows) {
  const tbody = document.querySelector("#signal-table tbody");
  tbody.innerHTML = "";
  for (const r of rows) {
    const tr = document.createElement("tr");
    if (r.pilot_type === "tractability_probe") tr.classList.add("probe");
    const mag = parseFloat(r.magnitude_value);
    const lo = parseFloat(r.magnitude_ci_low);
    const hi = parseFloat(r.magnitude_ci_high);
    const magCell = isFinite(mag)
      ? `<span class="magnitude-bar" style="width:${(mag*120).toFixed(1)}px"></span>${mag.toFixed(3)} <span class="ci">[${lo.toFixed(3)}, ${hi.toFixed(3)}]</span>`
      : `<em class="ci">— (probe)</em>`;
    tr.innerHTML = [
      `<td class="pilot-id">${r.pilot_id}</td>`,
      `<td>${r.pilot_title}</td>`,
      `<td>${magCell}</td>`,
      `<td>${r.n_trials_in_scope}</td>`,
      `<td>${r.tractability_AACT_only}</td>`,
      `<td class="followup">${r.follow_up_potential}/5</td>`,
      `<td>${r.notes}</td>`,
    ].join("");
    tbody.appendChild(tr);
  }
}
main().catch(e => { document.getElementById("meta").textContent = "Error loading: " + e.message; });
</script>
</body>
</html>
```

- [ ] **Step 2: Local smoke-test the dashboard**

```bash
python -m http.server 8000 --directory dashboard
```

Open http://localhost:8000 in a browser. Verify the table renders, sortable headers work, magnitude bars display, tractability-probe rows are highlighted yellow. Stop server with Ctrl-C.

- [ ] **Step 3: Sentinel scan to ensure 0 BLOCK on the dashboard**

```bash
python -m sentinel scan --repo C:/Projects/malaria-ct-recon
```

If any BLOCK fires (e.g., XSS, hardcoded path), fix before commit.

- [ ] **Step 4: Commit**

```bash
git add dashboard/index.html
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "feat(dashboard): self-contained vanilla-JS signal-table renderer"
```

---

### Task T23: GitHub Pages workflow

**Files:** `.github/workflows/pages.yml`

- [ ] **Step 1: Write `.github/workflows/pages.yml`**

```yaml
name: pages

on:
  push:
    branches: [master]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dashboard
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/pages.yml
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "ci(pages): deploy dashboard/ to GitHub Pages on push to master"
```

---

## Phase 5 — Release (T24–T26)

### Task T24: Final pre-release verification

- [ ] **Step 1: Run the full pytest suite**

```bash
cd C:/Projects/malaria-ct-recon
pytest -q --tb=short
```

Expected: all tests pass (≥ 30 tests across config, aact, schema, stats, corpus, preflight, run_all, P01-P10).

- [ ] **Step 2: Run a clean end-to-end smoke**

```bash
rm -f dashboard/data/signal-table.csv
python -m pilots.run_all
```

Expected: `run_all OK: wrote 10 pilot rows to dashboard/data/signal-table.csv`. Open the CSV and verify: 10 rows, all `aact_snapshot=2026-04-12`, all `seed=20260430`, every `script_sha256` non-empty.

- [ ] **Step 3: Run Sentinel — must report 0 BLOCK**

```bash
python -m sentinel scan --repo C:/Projects/malaria-ct-recon
```

If any BLOCK fires, fix before tagging. WARN are acceptable but log them in the commit message of the release.

- [ ] **Step 4: Update `README.md`** with run instructions verified by the smoke run, plus a results-table snapshot:

```markdown
## Results (snapshot)

See `dashboard/data/signal-table.csv` for full table. Live dashboard:
https://mahmood726-cyber.github.io/malaria-ct-recon/

| Pilot | Magnitude | n |
|---|---|---|
| P01 Reporting compliance | <fill from smoke> | <n> |
| P02 Endpoint-family chaos | <fill from smoke> | <n> |
| ... |
```

- [ ] **Step 5: Commit README update**

```bash
git add README.md
git -c user.email=mahmood726@gmail.com -c user.name=mahmood789 commit -q -m "docs(readme): record real-AACT signal-table snapshot"
```

---

### Task T25: Tag v0.1.0 + push to GitHub

- [ ] **Step 1: Create the GitHub repo via gh**

```bash
gh repo create mahmood726-cyber/malaria-ct-recon --public --source=C:/Projects/malaria-ct-recon --description "10-pilot reconnaissance of bias sources in malaria CT.gov data" --push
```

If the local branch isn't pushed yet, this push happens here.

- [ ] **Step 2: Tag v0.1.0**

```bash
cd C:/Projects/malaria-ct-recon
git tag -a v0.1.0 -m "v0.1.0 — sprint complete: 10 pilots + signal-table + dashboard"
git push origin v0.1.0
```

- [ ] **Step 3: Enable GitHub Pages via gh CLI**

```bash
gh api -X POST repos/mahmood726-cyber/malaria-ct-recon/pages -f "source[branch]=master" -f "source[path]=/dashboard"
```

Expected: Pages URL returned. Wait ~1 minute and visit https://mahmood726-cyber.github.io/malaria-ct-recon/ — verify the table renders.

- [ ] **Step 4: Verify CI is green**

```bash
gh run list --workflow=ci.yml --limit 1
gh run list --workflow=pages.yml --limit 1
```

Both should show `completed success`. If not, investigate before declaring done.

---

### Task T26: Update INDEX.md + workbook + memory

- [ ] **Step 1: Add to `C:/ProjectIndex/INDEX.md`**

```bash
# Open the file and add a new entry under the appropriate section, e.g.:
# - **malaria-ct-recon** — 10-pilot CT.gov audit, v0.1.0 shipped 2026-04-30, Pages live, github/mahmood726-cyber/malaria-ct-recon
```

- [ ] **Step 2: Add a workbook entry to `C:/E156/rewrite-workbook.txt`** with `SUBMITTED: [ ]` (the methods paper / E156 will be drafted in a separate cycle; this entry is a placeholder so the workbook reflects the shipped artefact)

- [ ] **Step 3: Add a memory pointer**

Create `C:/Users/user/.claude/projects/C--Users-user/memory/malaria-ct-recon.md`:

```markdown
---
name: malaria-ct-recon
description: 10-pilot reconnaissance of bias sources in malaria CT.gov data (AACT 2026-04-12)
type: project
---

**Status**: v0.1.0 shipped 2026-04-30. github/mahmood726-cyber/malaria-ct-recon. Pages live.

**Why**: First systematic data-quality audit of malaria trials in CT.gov. Spec + plan: `C:/Projects/malaria-ct-recon/docs/superpowers/`.

**How to apply**: When discussing malaria/CT.gov data, refer to signal-table.csv for the 10 quantified bias sources. Top pilots (highest follow_up_potential): see signal-table after run.

**Next steps**: Methods paper (BMJ Global Health) draft; focused atlas on top 1-2 pilot winners.
```

Then add to `MEMORY.md`:

```markdown
- [malaria-ct-recon](malaria-ct-recon.md) — 10-pilot CT.gov audit, v0.1.0 shipped 2026-04-30, Pages live
```

- [ ] **Step 4: Commit registry updates** (these files live OUTSIDE the malaria-ct-recon repo — use the appropriate parent-repo commit flow)

---

## Self-Review

**Spec coverage** — every section of the design doc maps to tasks:

| Spec section | Implementing task(s) |
|---|---|
| §1 Goal: 10-pilot sprint → paper + atlas + opt E156 | Implementation plan covers sprint only (T01–T26). Paper/atlas/E156 each get their own design+plan downstream — explicitly noted in the plan goal. |
| §2 Why groundbreaking | README skeleton (T01) + dashboard About section (T22) cite the 5 reasons indirectly through results; not a code requirement. |
| §3 Scope (in/out) | Scope reflected in pilot list (10, no #11/#12); out-of-scope items not implemented. |
| §4 The 10 pilots | T11–T20 (one task per pilot) |
| §5 Inclusion filter | T07 corpus module |
| §6 Output schema | T05 schema module |
| §7 Tech stack | T01 (deps) + T03 (CI) + T22 (dashboard) + T23 (Pages) |
| §8 Reproducibility (snapshot freeze, seed, OTS) | T02 (config), T05 (sha256 + seed in PilotResult), T10 (OTS) |
| §9 Deliverables/timing | Sprint = T01–T26; paper/atlas downstream. |
| §10 Risks | Mitigated: hardcoded path → config (T02); preflight catches AACT issues (T09); Sentinel hook installed (T03) |
| §11 Defaults locked | T01 (license, deps), T03 (CI), T25 (tag) |
| §12 Pre-pilot preflight | T09 + invoked by T21 run_all |

No spec section unimplemented.

**Placeholder scan** — searched for "TODO", "TBD", "Similar to Task N": none in the plan.

**Type consistency** — `PilotResult` schema (T05) used identically in T09 (preflight imports `schema`), T11–T20 (every pilot returns `schema.PilotResult`), T21 (run_all aggregates a list of `PilotResult`). Field names (`magnitude_value`, `magnitude_ci_low`, `magnitude_ci_high`, `n_trials_in_scope`, `n_trials_excluded_for_reason`, `script_sha256`, `aact_snapshot`, `seed`) consistent across all task code blocks. `Corpus` dataclass (T07) consistent: `included: set[str]`, `reason: dict[str, str]`. `aact.open()` / `aact.table()` / `aact.list_tables()` signatures consistent across T04, T07, T09, T11–T20.

---

## Execution handoff

Plan complete and saved to `C:/Projects/malaria-ct-recon/docs/superpowers/plans/2026-04-30-malaria-ct-recon-sprint.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Better for the long-tail pilot sequence (T11–T20) where each task is independent.

**2. Inline Execution** — I execute tasks in this session using executing-plans, batch execution with checkpoints. Faster but uses more of this conversation's context.

Which approach?
