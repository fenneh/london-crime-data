"""Convenience loaders for the Parquet files in data/.

Works whether you've cloned the repo or want to pull directly from GitHub::

    from london_crime import load

    df = load.recorded_crime_borough()        # local clone
    df = load.recorded_crime_borough(remote=True)  # pull from GitHub, no clone needed

Or with polars/pandas directly::

    import polars as pl
    REPO = "https://raw.githubusercontent.com/fenneh/london-crime-data/main/data"
    df = pl.read_parquet(f"{REPO}/recorded-crime-borough.parquet")
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

_DATA = Path(__file__).parent.parent / "data"
_REMOTE = "https://raw.githubusercontent.com/fenneh/london-crime-data/main/data"


def _load(filename: str, remote: bool) -> pl.DataFrame:
    if remote:
        return pl.read_parquet(f"{_REMOTE}/{filename}")
    path = _DATA / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Not found: {path}\n"
            "Run `uv run scripts/refresh.py` to download, or pass remote=True."
        )
    return pl.read_parquet(path)


def recorded_crime_borough(*, historical: bool = False, remote: bool = False) -> pl.DataFrame:
    """Monthly crime counts by London borough with major + minor offence categories.

    Columns: majortext, minortext, boroughname, then monthly count columns (e.g. 202308).

    This is the richest sub-category dataset — violent crime breaks down into
    Common Assault, GBH, Harassment, Stalking, etc.

    Args:
        historical: If True, returns the full dataset from January 2008.
                    If False (default), returns the most recent 24 months.
    """
    filename = "recorded-crime-borough-historical.parquet" if historical else "recorded-crime-borough.parquet"
    return _load(filename, remote)


def recorded_crime_ward(*, historical: bool = False, remote: bool = False) -> pl.DataFrame:
    """Monthly crime counts at ward level with major + minor offence categories.

    Args:
        historical: If True, returns the full dataset from January 2008.
    """
    filename = "recorded-crime-ward-historical.parquet" if historical else "recorded-crime-ward.parquet"
    return _load(filename, remote)


def recorded_crime_lsoa(*, historical: bool = False, remote: bool = False) -> pl.DataFrame:
    """Monthly crime counts at Lower Super Output Area (LSOA) level.

    Args:
        historical: If True, returns the full dataset from January 2008.
    """
    filename = "recorded-crime-lsoa-historical.parquet" if historical else "recorded-crime-lsoa.parquet"
    return _load(filename, remote)


def stop_search(*, remote: bool = False) -> pl.DataFrame:
    """Stop and search records: borough, legislation, ethnicity, age, gender, outcome."""
    return _load("stop-search.parquet", remote)


def custody(*, remote: bool = False) -> pl.DataFrame:
    """Custody records: arrests by ethnicity, disposal type, strip searches."""
    return _load("custody.parquet", remote)


def monthly_crime_dashboard(*, remote: bool = False) -> pl.DataFrame:
    """Pan-London monthly crime totals by category with outcomes and rates."""
    return _load("monthly-crime-dashboard.parquet", remote)


def vawg_offences(*, remote: bool = False) -> pl.DataFrame:
    """Violence Against Women and Girls offence counts by type, borough, and month. Jan 2014–present."""
    return _load("vawg-offences.parquet", remote)


def vawg_victims(*, remote: bool = False) -> pl.DataFrame:
    """VAWG victim demographics (age, ethnicity) by offence type and borough. Jan 2014–present."""
    return _load("vawg-victims.parquet", remote)


def business_crime_offences(*, remote: bool = False) -> pl.DataFrame:
    """Business crime offence counts by type, borough, and month. ~3.5 years of data."""
    return _load("business-crime-offences.parquet", remote)


def business_crime_outcomes(*, remote: bool = False) -> pl.DataFrame:
    """Business crime outcome data by type, borough, and month. ~3.5 years of data."""
    return _load("business-crime-outcomes.parquet", remote)


def homicide(*, remote: bool = False) -> pl.DataFrame:
    """Homicide records from 2003: method, demographics, borough."""
    return _load("homicide.parquet", remote)


def stolen_animals(*, remote: bool = False) -> pl.DataFrame:
    """Stolen animal reports by species, borough, and month. Apr 2010–present."""
    return _load("stolen-animals.parquet", remote)


def thorough_searches(*, remote: bool = False) -> pl.DataFrame:
    """More thorough / intimate part search records (MTIPS). Ethnicity, age, outcome. Jan 2019–present."""
    return _load("thorough-searches.parquet", remote)
