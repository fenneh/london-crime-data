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
    totals = {m: int(df[m].sum()) for m in month_cols}
    labels = [f"{m[:4]}-{m[4:]}" for m in month_cols]
    return {"labels": labels, "values": list(totals.values())}


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


def build_meta() -> dict:
    files = {
        "stop_search": "stop-search.parquet",
        "recorded_crime_borough": "recorded-crime-borough.parquet",
        "vawg_offences": "vawg-offences.parquet",
        "homicide": "homicide.parquet",
    }
    rows = {}
    for key, filename in files.items():
        path = DATA_DIR / filename
        if path.exists():
            df = pl.scan_parquet(path)
            rows[key] = df.select(pl.len()).collect().item()

    borough = pl.read_parquet(DATA_DIR / "recorded-crime-borough.parquet")
    month_cols = sorted(c for c in borough.columns if c.isdigit())
    latest_month = month_cols[-1] if month_cols else ""
    updated = f"{latest_month[:4]}-{latest_month[4:]}" if latest_month else ""

    return {"updated": updated, "rows": rows}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "monthly_totals.json": build_monthly_totals,
        "by_category.json": build_by_category,
        "by_borough.json": build_by_borough,
        "meta.json": build_meta,
    }

    for filename, builder in datasets.items():
        data = builder()
        path = OUT_DIR / filename
        path.write_text(json.dumps(data, separators=(",", ":")))
        print(f"  Written: {path.relative_to(Path(__file__).parent.parent)}")


if __name__ == "__main__":
    main()
