"""AACT loader — duckdb-backed reader for pipe-delimited TXT exports."""
from __future__ import annotations

import contextlib
import re
from pathlib import Path

import duckdb
import pandas as pd

# v0.1.4 P1-26: latent path-traversal hardening. Table names f-stringed into
# filesystem paths (`{name}.txt`); restrict to AACT-style identifiers.
_TABLE_NAME_RX = re.compile(r"^[a-z_][a-z0-9_]{0,63}$")


def open(snapshot_dir: Path | str) -> duckdb.DuckDBPyConnection:
    """Open an in-memory duckdb connection with the snapshot dir registered.

    Note: callers should prefer ``connect(...)`` (contextmanager) for proper
    cleanup. This function is kept for backwards compatibility; the caller
    is responsible for calling ``con.close()``.
    """
    p = Path(snapshot_dir)
    if not p.is_dir():
        raise FileNotFoundError(f"AACT snapshot dir not found: {p}")
    con = duckdb.connect(":memory:")
    con.execute("SET memory_limit='4GB'")
    con.execute("CREATE TABLE __snapshot_dir (path VARCHAR)")
    con.execute("INSERT INTO __snapshot_dir VALUES (?)", [str(p)])
    return con


@contextlib.contextmanager
def connect(snapshot_dir: Path | str):
    """Contextmanager wrapper around ``open()`` that always closes the connection.

    Use this in new code to ensure DuckDB connections are released even when
    a pilot raises mid-run. v0.1.4 P1-19.
    """
    con = open(snapshot_dir)
    try:
        yield con
    finally:
        con.close()


def _snapshot_dir(con: duckdb.DuckDBPyConnection) -> Path:
    """Return the snapshot dir registered on this connection.

    Raises RuntimeError if the connection was not created via aact.open().
    """
    try:
        row = con.execute("SELECT path FROM __snapshot_dir").fetchone()
    except duckdb.CatalogException as exc:
        raise RuntimeError("Connection not opened via aact.open()") from exc
    if row is None:
        raise RuntimeError("Connection not opened via aact.open()")
    return Path(row[0])


def table(con: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
    """Read one AACT table into a DataFrame. Raises FileNotFoundError if missing."""
    if not _TABLE_NAME_RX.match(name):
        raise ValueError(f"invalid AACT table name: {name!r}")
    p = _snapshot_dir(con) / f"{name}.txt"
    if not p.exists():
        raise FileNotFoundError(f"AACT table missing: {p}")
    return con.read_csv(str(p), delimiter="|", header=True, quotechar='"', escapechar='"').df()


def list_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Return sorted list of table names (filenames without .txt)."""
    return sorted(f.stem for f in _snapshot_dir(con).glob("*.txt"))


def table_columns(con: duckdb.DuckDBPyConnection, name: str) -> list[str]:
    """Return the column names of an AACT table without materialising it.

    v0.1.4 P1-22: used by preflight to detect AACT schema drift between
    snapshots before pilots run.
    """
    if not _TABLE_NAME_RX.match(name):
        raise ValueError(f"invalid AACT table name: {name!r}")
    p = _snapshot_dir(con) / f"{name}.txt"
    if not p.exists():
        raise FileNotFoundError(f"AACT table missing: {p}")
    rel = con.read_csv(str(p), delimiter="|", header=True, quotechar='"',
                       escapechar='"', sample_size=1)
    return [c[0] for c in rel.description]
