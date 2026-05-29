"""Tests for london_crime._fetch pure functions."""

import polars as pl

from london_crime._fetch import _concat, _filter_resources, normalise, pick_resource


def _res(name: str, url: str = "", fmt: str = "") -> dict:
    return {"name": name, "url": url or f"https://example.com/{name}.csv", "format": fmt}


class TestPickResource:
    def test_picks_first_matching(self):
        resources = [
            _res("Borough Level Crime Jan 2024"),
            _res("Borough Level Crime Dec 2023"),
        ]
        r = pick_resource(resources, "Borough Level Crime", prefer_historical=False)
        assert r is not None
        assert "Jan 2024" in r["name"]

    def test_excludes_historical_when_not_wanted(self):
        resources = [
            _res("Borough Level Crime (Historical)"),
            _res("Borough Level Crime Jan 2024"),
        ]
        r = pick_resource(resources, "Borough Level Crime", prefer_historical=False)
        assert r is not None
        assert "(Historical)" not in r["name"]

    def test_prefers_historical(self):
        resources = [
            _res("Borough Level Crime Jan 2024"),
            _res("Borough Level Crime (Historical)"),
        ]
        r = pick_resource(resources, "Borough Level Crime", prefer_historical=True)
        assert r is not None
        assert "(Historical)" in r["name"]

    def test_returns_none_when_no_match(self):
        resources = [_res("Something Else Jan 2024")]
        r = pick_resource(resources, "Borough Level Crime", prefer_historical=False)
        assert r is None

    def test_empty_name_contains_matches_any(self):
        resources = [_res("Anything", url="https://example.com/file.csv")]
        r = pick_resource(resources, "", prefer_historical=False)
        assert r is not None

    def test_skips_non_csv_xlsx(self):
        resources = [
            {"name": "Some PDF", "url": "https://example.com/file.pdf", "format": "pdf"},
            {"name": "Some CSV", "url": "https://example.com/file.csv", "format": ""},
        ]
        r = pick_resource(resources, "", prefer_historical=False)
        assert r is not None
        assert "CSV" in r["name"]

    def test_accepts_xlsx_url(self):
        resources = [_res("Report", url="https://example.com/data.xlsx")]
        r = pick_resource(resources, "", prefer_historical=False)
        assert r is not None

    def test_accepts_format_field_fallback(self):
        resources = [{"name": "Sheet", "url": "https://example.com/noext", "format": "csv"}]
        r = pick_resource(resources, "", prefer_historical=False)
        assert r is not None


class TestFilterResources:
    def test_filters_by_name(self):
        resources = [
            _res("KnifeCrimeData Jan"),
            _res("OtherCrimeData Jan"),
        ]
        result = _filter_resources(resources, "KnifeCrimeData", prefer_historical=False)
        assert len(result) == 1
        assert "KnifeCrimeData" in result[0]["name"]

    def test_empty_filter_returns_all_valid(self):
        resources = [_res("A"), _res("B")]
        result = _filter_resources(resources, "", prefer_historical=False)
        assert len(result) == 2

    def test_excludes_historical(self):
        resources = [_res("Data (Historical)"), _res("Data Jan")]
        result = _filter_resources(resources, "Data", prefer_historical=False)
        assert all("(Historical)" not in r["name"] for r in result)

    def test_includes_only_historical(self):
        resources = [_res("Data (Historical)"), _res("Data Jan")]
        result = _filter_resources(resources, "Data", prefer_historical=True)
        assert all("(Historical)" in r["name"] for r in result)


class TestNormalise:
    def test_lowercases_columns(self):
        df = pl.DataFrame({"MajorText": ["a"], "MinorText": ["b"]})
        out = normalise(df)
        assert "majortext" in out.columns
        assert "minortext" in out.columns

    def test_replaces_spaces_and_special_chars(self):
        df = pl.DataFrame({"Some Column (Notes)": ["x"], "A-B/C.D": ["y"]})
        out = normalise(df)
        assert "some_column_notes" in out.columns
        assert "a_b_c_d" in out.columns

    def test_strips_leading_trailing_underscores(self):
        df = pl.DataFrame({"_col_": [1]})
        out = normalise(df)
        assert "col" in out.columns

    def test_collapses_double_underscores(self):
        df = pl.DataFrame({"a  b": [1]})
        out = normalise(df)
        assert "__" not in list(out.columns)[0]

    def test_casts_numeric_strings_to_int(self):
        df = pl.DataFrame({"count": ["1", "2", "3"]})
        out = normalise(df)
        assert out["count"].dtype == pl.Int64

    def test_leaves_non_numeric_strings_alone(self):
        df = pl.DataFrame({"name": ["foo", "bar"]})
        out = normalise(df)
        assert out["name"].dtype == pl.String

    def test_casts_float_strings(self):
        df = pl.DataFrame({"rate": ["1.5", "2.7"]})
        out = normalise(df)
        assert out["rate"].dtype == pl.Float64


class TestConcat:
    def test_basic_concat(self):
        a = pl.DataFrame({"x": [1], "y": ["a"]})
        b = pl.DataFrame({"x": [2], "y": ["b"]})
        out = _concat([a, b])
        assert len(out) == 2

    def test_fills_missing_columns_with_null(self):
        a = pl.DataFrame({"x": [1]})
        b = pl.DataFrame({"x": [2], "y": ["extra"]})
        out = _concat([a, b])
        assert "y" in out.columns
        assert out.filter(pl.col("x") == 1)["y"][0] is None

    def test_resolves_dtype_conflict_to_string(self):
        a = pl.DataFrame({"val": [1]})
        b = pl.DataFrame({"val": ["hello"]})
        out = _concat([a, b])
        assert out["val"].dtype == pl.String

    def test_preserves_column_order(self):
        a = pl.DataFrame({"a": [1], "b": [2], "c": [3]})
        b = pl.DataFrame({"a": [4], "b": [5], "c": [6]})
        out = _concat([a, b])
        assert out.columns == ["a", "b", "c"]
