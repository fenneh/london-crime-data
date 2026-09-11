"""Tests for scripts/refresh.py CLI argument handling."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import refresh  # noqa: E402

SOURCES = [
    {"key": "source-a", "name": "Source A", "short_id": "aaaaa", "output": "a.parquet"},
    {"key": "source-b", "name": "Source B", "short_id": "bbbbb", "output": "b.parquet"},
]


def _run(args):
    with patch.object(sys, "argv", ["refresh.py", *args]):
        refresh.main()


class TestList:
    def test_lists_all_source_keys(self, capsys):
        with patch.object(refresh, "SOURCES", SOURCES):
            _run(["--list"])
        out = capsys.readouterr().out
        assert "source-a" in out
        assert "source-b" in out


class TestDryRun:
    def test_shows_all_sources_by_default(self, capsys):
        with patch.object(refresh, "SOURCES", SOURCES):
            _run(["--dry-run"])
        out = capsys.readouterr().out
        assert "source-a (aaaaa)" in out
        assert "source-b (bbbbb)" in out

    def test_filters_to_requested_source(self, capsys):
        with patch.object(refresh, "SOURCES", SOURCES):
            _run(["--dry-run", "--source", "source-a"])
        out = capsys.readouterr().out
        assert "source-a" in out
        assert "source-b" not in out


class TestUnknownSource:
    def test_exits_with_error(self):
        with patch.object(refresh, "SOURCES", SOURCES):
            with pytest.raises(SystemExit) as exc_info:
                _run(["--source", "does-not-exist"])
        assert exc_info.value.code == 1


class TestMain:
    def test_reports_total_files_and_rows(self, capsys):
        with (
            patch.object(refresh, "SOURCES", SOURCES),
            patch.object(refresh, "refresh_source", return_value={"a.parquet": 10}),
        ):
            _run([])
        out = capsys.readouterr().out
        assert "Refreshed 2 file(s), 20 total rows" in out

    def test_continues_after_failure_and_exits_nonzero(self, capsys):
        def fake_refresh(source):
            if source["key"] == "source-a":
                raise RuntimeError("boom")
            return {"b.parquet": 5}

        with (
            patch.object(refresh, "SOURCES", SOURCES),
            patch.object(refresh, "refresh_source", side_effect=fake_refresh),
        ):
            with pytest.raises(SystemExit) as exc_info:
                _run([])
        assert exc_info.value.code == 1
        out = capsys.readouterr().out
        assert "Failed: source-a" in out
        assert "Refreshed 1 file(s), 5 total rows" in out
