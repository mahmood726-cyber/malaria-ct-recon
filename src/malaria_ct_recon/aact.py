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
    return con.read_csv(str(p), delimiter="|", header=True, quotechar='"', escapechar='"').df()


def list_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Return sorted list of table names (filenames without .txt)."""
    return sorted(f.stem for f in _snapshot_dir(con).glob("*.txt"))
