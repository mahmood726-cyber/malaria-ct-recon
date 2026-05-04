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


def test_table_on_bare_duckdb_connection_raises_runtime_error() -> None:
    bare_con = duckdb.connect(":memory:")
    with pytest.raises(RuntimeError, match="Connection not opened via aact.open"):
        aact.list_tables(bare_con)


# v0.1.6 P1-11: tests for v0.1.4 hardening that were missing.

def test_connect_contextmanager_closes_on_exception(tmp_path: Path) -> None:
    """v0.1.4 P1-19: aact.connect() must close the connection even on raise."""
    (tmp_path / "studies.txt").write_text("nct_id|x\nNCT0001|a\n", encoding="utf-8")
    held = {}
    with pytest.raises(RuntimeError, match="boom"):
        with aact.connect(tmp_path) as con:
            held["con"] = con
            raise RuntimeError("boom")
    # Connection should be closed: any subsequent op raises.
    with pytest.raises((duckdb.ConnectionException, RuntimeError, Exception)):
        held["con"].execute("SELECT 1")


def test_connect_contextmanager_closes_on_normal_exit(tmp_path: Path) -> None:
    (tmp_path / "studies.txt").write_text("nct_id|x\nNCT0001|a\n", encoding="utf-8")
    with aact.connect(tmp_path) as con:
        df = aact.table(con, "studies")
        assert len(df) == 1
    with pytest.raises((duckdb.ConnectionException, RuntimeError, Exception)):
        con.execute("SELECT 1")


@pytest.mark.parametrize("bad_name", [
    "../../etc/passwd",
    "studies; DROP TABLE",
    "Studies",            # uppercase rejected by regex
    "1bad",               # leading digit rejected
    "with space",
    "",
])
def test_table_rejects_invalid_names(tmp_path: Path, bad_name: str) -> None:
    """v0.1.4 P1-26: aact.table() validates table-name regex (path-traversal hardening)."""
    con = aact.open(tmp_path)
    with pytest.raises(ValueError, match="invalid AACT table name"):
        aact.table(con, bad_name)


def test_table_columns_returns_header(tmp_path: Path) -> None:
    """v0.1.4 P1-22: aact.table_columns() used by preflight schema-drift check."""
    (tmp_path / "studies.txt").write_text(
        "nct_id|overall_status|primary_completion_date\nNCT001|COMPLETED|2020-01-01\n",
        encoding="utf-8",
    )
    con = aact.open(tmp_path)
    cols = aact.table_columns(con, "studies")
    assert set(cols) == {"nct_id", "overall_status", "primary_completion_date"}
