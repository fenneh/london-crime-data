"""london-crime-data: MPS open datasets as Parquet files.

Direct download (no clone needed)::

    import polars as pl

    REPO = "https://raw.githubusercontent.com/fenneh/london-crime-data/main/data"
    df = pl.read_parquet(f"{REPO}/recorded-crime-borough.parquet")
    df = pl.read_parquet(f"{REPO}/stop-search.parquet")

Or use the loaders::

    from london_crime import load

    df = load.recorded_crime_borough()
    df = load.recorded_crime_borough(historical=True)
    df = load.stop_search()
"""

from __future__ import annotations

from . import load

__all__ = ["load"]
