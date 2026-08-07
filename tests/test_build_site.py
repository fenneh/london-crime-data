"""Tests for scripts/build_site.py summary builders."""

from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import build_site  # noqa: E402


def _use_data_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(build_site, "DATA_DIR", tmp_path)
    return tmp_path


class TestBuildMonthlyTotals:
    def test_sums_month_columns_and_formats_labels(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame({"group": ["A", "B"], "202401": [1, 2], "202402": [3, 4]})
        df.write_parquet(data_dir / "recorded-crime-borough.parquet")

        result = build_site.build_monthly_totals()

        assert result == {"labels": ["2024-01", "2024-02"], "values": [3, 7]}


class TestBuildKnifeCrime:
    def test_filters_and_aggregates_borough_offences(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame(
            {
                "area_type": ["Borough", "Borough", "MPS", "Borough"],
                "measure": ["Offences", "Offences", "Offences", "Rate"],
                "crime_type": ["Knife Crime", "Knife Crime", "Knife Crime", "Knife Crime"],
                "month_year": ["2024-01-01", "2024-01-01", "2024-01-01", "2024-01-01"],
                "count": [5, 3, 100, 99],
            }
        )
        df.write_parquet(data_dir / "monthly-crime-dashboard.parquet")

        result = build_site.build_knife_crime()

        assert result["labels"] == ["2024-01"]
        assert result["values"] == [8]


class TestBuildByCategory:
    def test_sums_totals_by_group_descending(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame(
            {
                "group": ["theft", "violence"],
                "202401": [1, 10],
                "202402": [1, 10],
            }
        )
        df.write_parquet(data_dir / "recorded-crime-borough.parquet")

        result = build_site.build_by_category()

        assert result["labels"] == ["Violence", "Theft"]
        assert result["values"] == [20, 2]


class TestBuildByBorough:
    def test_sums_totals_by_bocu(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame(
            {
                "bocu": ["Camden", "Camden", "Enfield"],
                "202401": [2, 3, 1],
            }
        )
        df.write_parquet(data_dir / "recorded-crime-borough.parquet")

        result = build_site.build_by_borough()

        assert result["labels"] == ["Camden", "Enfield"]
        assert result["values"] == [5, 1]


class TestBuildStopSearchEthnicity:
    def test_excludes_null_and_unknown(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame(
            {
                "ethnicappearance": ["Asian", "Asian", "White", "Unknown", None],
            }
        )
        df.write_parquet(data_dir / "stop-search.parquet")

        result = build_site.build_stop_search_ethnicity()

        assert result["labels"] == ["Asian", "White"]
        assert result["values"] == [2, 1]


class TestBuildSampleRows:
    def test_filters_violence_in_target_boroughs(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        df = pl.DataFrame(
            {
                "group": ["VIOLENCE AGAINST THE PERSON", "THEFT", "VIOLENCE AGAINST THE PERSON"],
                "subgroup": ["Assault", "Burglary", "Assault"],
                "bocu": ["Westminster", "Westminster", "Barnet"],
                "202401": [1, 2, 3],
                "202402": [1, 2, 3],
                "202403": [1, 2, 3],
            }
        )
        df.write_parquet(data_dir / "recorded-crime-borough.parquet")

        result = build_site.build_sample_rows()

        assert result["columns"] == ["group", "subgroup", "bocu", "202401", "202402", "202403"]
        assert len(result["rows"]) == 1
        assert result["rows"][0][2] == "Westminster"


class TestBuildMeta:
    def test_reports_latest_month_and_optional_sizes(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        borough = pl.DataFrame({"202401": [1], "202403": [2], "202402": [3]})
        borough.write_parquet(data_dir / "recorded-crime-borough.parquet")
        pl.DataFrame({"x": [1, 2, 3]}).write_parquet(data_dir / "homicide.parquet")

        result = build_site.build_meta()

        assert result["updated"] == "2024-03"
        assert result["rows"] == {"homicide": 3}

    def test_missing_optional_files_are_skipped(self, monkeypatch, tmp_path):
        data_dir = _use_data_dir(monkeypatch, tmp_path)
        pl.DataFrame({"202401": [1]}).write_parquet(data_dir / "recorded-crime-borough.parquet")

        result = build_site.build_meta()

        assert result["rows"] == {}
