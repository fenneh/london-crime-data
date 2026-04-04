"""Generate summary JSON files for the static site from Parquet data."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = Path(__file__).parent.parent / "docs" / "data"


def build_monthly_totals() -> dict:
    df = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = sorted(c for c in df.columns if c.isdigit())
    labels = [f"{m[:4]}-{m[4:]}" for m in month_cols]
    values = [int(df[m].sum()) for m in month_cols]
    return {"labels": labels, "values": values}


def build_knife_crime() -> dict:
    df = pl.read_parquet(DATA_DIR / "monthly-crime-dashboard.parquet")
    result = (
        df.filter(
            (pl.col("area_type") == "Borough")
            & (pl.col("measure") == "Offences")
            & (pl.col("crime_type") == "Knife Crime")
        )
        .group_by("month_year")
        .agg(pl.col("count").sum())
        .sort("month_year")
        .tail(36)
    )
    labels = [str(d)[:7] for d in result["month_year"].to_list()]
    values = [int(v) for v in result["count"].to_list()]
    return {"labels": labels, "values": values}


def build_by_category() -> dict:
    df = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = [c for c in df.columns if c.isdigit()]
    result = (
        df.with_columns(pl.sum_horizontal(month_cols).alias("total"))
        .group_by("majortext")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
        .head(10)
    )
    labels = [s.title() for s in result["majortext"].to_list()]
    values = [int(v) for v in result["total"].to_list()]
    return {"labels": labels, "values": values}


def build_by_borough() -> dict:
    df = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = [c for c in df.columns if c.isdigit()]
    result = (
        df.with_columns(pl.sum_horizontal(month_cols).alias("total"))
        .group_by("boroughname")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )
    return {
        "labels": result["boroughname"].to_list(),
        "values": [int(v) for v in result["total"].to_list()],
    }


def build_stop_search_ethnicity() -> dict:
    df = pl.read_parquet(DATA_DIR / "stop-search.parquet")
    result = (
        df.filter(
            pl.col("ethnicappearance").is_not_null()
            & (pl.col("ethnicappearance") != "Unknown")
        )
        .group_by("ethnicappearance")
        .agg(pl.len().alias("stops"))
        .sort("stops", descending=True)
    )
    return {
        "labels": result["ethnicappearance"].to_list(),
        "values": [int(v) for v in result["stops"].to_list()],
        "note": "Officer-defined ethnicity. Covers records where this field is populated (~260K of 1.35M total).",
    }


def build_sample_rows() -> dict:
    df = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = sorted(c for c in df.columns if c.isdigit())
    recent = month_cols[-3:]
    sample = (
        df.select(["majortext", "minortext", "boroughname"] + recent)
        .filter(
            pl.col("majortext").str.contains("VIOLENCE")
            & pl.col("boroughname").str.contains("Westminster|Southwark|Hackney|Tower Hamlets|Lambeth")
        )
        .head(8)
    )
    return {
        "columns": sample.columns,
        "rows": sample.rows(),
    }


def build_meta() -> dict:
    sizes = {}
    for name, filename in [
        ("stop_search", "stop-search.parquet"),
        ("vawg_offences", "vawg-offences.parquet"),
        ("homicide", "homicide.parquet"),
        ("thorough_searches", "thorough-searches.parquet"),
    ]:
        path = DATA_DIR / filename
        if path.exists():
            sizes[name] = pl.scan_parquet(path).select(pl.len()).collect().item()

    borough = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = sorted(c for c in borough.columns if c.isdigit())
    latest = month_cols[-1] if month_cols else ""
    updated = f"{latest[:4]}-{latest[4:]}" if latest else ""

    return {"updated": updated, "rows": sizes}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "monthly_totals.json": build_monthly_totals,
        "knife_crime.json": build_knife_crime,
        "by_category.json": build_by_category,
        "by_borough.json": build_by_borough,
        "stop_search_ethnicity.json": build_stop_search_ethnicity,
        "sample_rows.json": build_sample_rows,
        "meta.json": build_meta,
    }

    for filename, builder in datasets.items():
        data = builder()
        path = OUT_DIR / filename
        path.write_text(json.dumps(data, separators=(",", ":")))
        print(f"  Written: {path.relative_to(Path(__file__).parent.parent)}")


if __name__ == "__main__":
    main()
