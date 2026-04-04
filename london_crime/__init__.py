"""london-crime-data: MPS open datasets as Parquet files.

Load data directly from GitHub (no clone needed)::

    import polars as pl

    REPO = "https://raw.githubusercontent.com/fenneh/london-crime-data/main/data"

    df = pl.read_parquet(f"{REPO}/recorded-crime-geographic/borough.parquet")
    df = pl.read_parquet(f"{REPO}/recorded-crime-geographic/ward.parquet")
    df = pl.read_parquet(f"{REPO}/recorded-crime-geographic/lsoa.parquet")
    df = pl.read_parquet(f"{REPO}/stop-search.parquet")
    df = pl.read_parquet(f"{REPO}/knife-crime.parquet")
    df = pl.read_parquet(f"{REPO}/custody.parquet")
    df = pl.read_parquet(f"{REPO}/homicide.parquet")

Or if you've cloned the repo, use the loader::

    from london_crime import load

    df = load.recorded_crime("borough")   # polars DataFrame
    df = load.stop_search()
    df = load.knife_crime()
"""

from __future__ import annotations

from . import load

__all__ = ["load"]
