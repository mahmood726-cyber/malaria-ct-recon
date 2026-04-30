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
