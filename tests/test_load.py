"""Tests for london_crime.load filename routing and error handling."""

from __future__ import annotations

from unittest.mock import patch

import polars as pl
import pytest

from london_crime import load

_DUMMY = pl.DataFrame({"x": [1]})


def _mock():
    return patch("london_crime.load._load", return_value=_DUMMY)


class TestFilenameRouting:
    def test_borough_default(self):
        with _mock() as m:
            load.recorded_crime_borough()
            m.assert_called_once_with("recorded-crime-borough.parquet", False)

    def test_borough_historical(self):
        with _mock() as m:
            load.recorded_crime_borough(historical=True)
            m.assert_called_once_with("recorded-crime-borough-historical.parquet", False)

    def test_ward_default(self):
        with _mock() as m:
            load.recorded_crime_ward()
            m.assert_called_once_with("recorded-crime-ward.parquet", False)

    def test_ward_historical(self):
        with _mock() as m:
            load.recorded_crime_ward(historical=True)
            m.assert_called_once_with("recorded-crime-ward-historical.parquet", False)

    def test_lsoa_default(self):
        with _mock() as m:
            load.recorded_crime_lsoa()
            m.assert_called_once_with("recorded-crime-lsoa.parquet", False)

    def test_lsoa_historical(self):
        with _mock() as m:
            load.recorded_crime_lsoa(historical=True)
            m.assert_called_once_with("recorded-crime-lsoa-historical.parquet", False)

    def test_stop_search(self):
        with _mock() as m:
            load.stop_search()
            m.assert_called_once_with("stop-search.parquet", False)

    def test_remote_flag_forwarded(self):
        with _mock() as m:
            load.stop_search(remote=True)
            m.assert_called_once_with("stop-search.parquet", True)

    def test_homicide(self):
        with _mock() as m:
            load.homicide()
            m.assert_called_once_with("homicide.parquet", False)

    def test_stolen_animals(self):
        with _mock() as m:
            load.stolen_animals()
            m.assert_called_once_with("stolen-animals.parquet", False)


class TestLoadErrors:
    def test_missing_local_file_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(load, "_DATA", tmp_path)
        with pytest.raises(FileNotFoundError, match="refresh.py"):
            load.recorded_crime_borough()

    def test_error_message_hints_remote(self, tmp_path, monkeypatch):
        monkeypatch.setattr(load, "_DATA", tmp_path)
        with pytest.raises(FileNotFoundError, match="remote=True"):
            load.recorded_crime_borough()

    def test_remote_builds_https_url(self):
        with patch("london_crime.load.pl.read_parquet", return_value=_DUMMY) as m:
            load.recorded_crime_borough(remote=True)
            url = m.call_args[0][0]
            assert url.startswith("https://")
            assert "recorded-crime-borough.parquet" in url
