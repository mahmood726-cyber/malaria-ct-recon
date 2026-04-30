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
