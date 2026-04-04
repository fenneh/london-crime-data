# london-crime-data

MPS (Metropolitan Police Service) and London crime datasets as Parquet files, refreshed monthly via GitHub Actions.

No API keys. No scraping. Direct downloads from the [London Datastore](https://data.london.gov.uk/) CKAN API, converted to Parquet.

## Datasets

All crime counts are in **wide format** — one row per (location, offence category) combination, with monthly count columns (e.g. `202308`). Use `unpivot` / `melt` to convert to long format for analysis.

| File | Description | Rows | Columns |
|------|-------------|------|---------|
| `recorded-crime-borough.parquet` | Borough-level crime counts, last 24 months. Major + minor offence categories. | ~1K | 3 + 24 months |
| `recorded-crime-borough-historical.parquet` | Same, from April 2010 | ~950 | 3 + ~160 months |
| `recorded-crime-ward.parquet` | Ward-level, last 24 months | ~18K | 5 + 24 months |
| `recorded-crime-ward-historical.parquet` | Ward-level, from April 2010 | ~19K | 5 + ~160 months |
| `recorded-crime-lsoa.parquet` | LSOA-level, last 24 months | ~100K | 5 + 24 months |
| `recorded-crime-lsoa-historical.parquet` | LSOA-level, from April 2010 | ~113K | 5 + ~160 months |
| `stop-search.parquet` | Individual stop and search records: ethnicity, legislation, object of search, outcome. Jun 2020–present. | ~1.35M | 33 |
| `custody.parquet` | Arrests by ethnicity, disposal type, strip searches | ~33K | 10 |
| `monthly-crime-dashboard.parquet` | Pan-London monthly crime totals by category with outcomes and rates | ~472K | 13 |
| `vawg-offences.parquet` | VAWG offence counts by type, borough, month. Jan 2014–present. | ~411K | 11 |
| `vawg-victims.parquet` | VAWG victim demographics by offence type and borough. Jan 2014–present. | ~411K | 9 |
| `business-crime-offences.parquet` | Business crime offence counts by type, borough, month. ~3.5 years. | ~291K | 8 |
| `business-crime-outcomes.parquet` | Business crime outcome data. ~3.5 years. | ~407K | 10 |
| `homicide.parquet` | Homicide records from 2003: method, demographics, borough | ~4.5K | 8 |
| `stolen-animals.parquet` | Stolen animal reports by species, borough, month. Apr 2010–present. | ~5.7K | 6 |
| `thorough-searches.parquet` | More thorough / intimate part search records (MTIPS). Jan 2019–present. | ~44K | 15 |

Updated on the 6th of each month.

## Usage

### Direct download (no clone needed)

```python
import polars as pl

REPO = "https://raw.githubusercontent.com/fenneh/london-crime-data/main/data"

df = pl.read_parquet(f"{REPO}/recorded-crime-borough.parquet")
```

```python
import pandas as pd

df = pd.read_parquet("https://raw.githubusercontent.com/fenneh/london-crime-data/main/data/stop-search.parquet")
```

### Via the package

```bash
pip install git+https://github.com/fenneh/london-crime-data.git
# or: uv add git+https://github.com/fenneh/london-crime-data.git
```

```python
from london_crime import load

# Recent 24 months
df = load.recorded_crime_borough()

# Full history from 2010
df = load.recorded_crime_borough(historical=True)

# Pull from GitHub without cloning
df = load.stop_search(remote=True)
```

## Data structure: recorded crime

The geographic breakdown files are in **wide format** — one row per (borough/ward/LSOA, major category, minor category), with monthly count columns:

```
shape: (1_015, 27)
┌──────────────────────────────────┬─────────────────────────────┬───────────────┬────────┬────────┐
│ majortext                        ┆ minortext                   ┆ boroughname   ┆ 202308 ┆ 202507 │
│ VIOLENCE AGAINST THE PERSON      ┆ COMMON ASSAULT              ┆ Barking       ┆ 71     ┆ 84     │
│ VIOLENCE AGAINST THE PERSON      ┆ HARASSMENT                  ┆ Barking       ┆ 45     ┆ 51     │
│ VIOLENCE AGAINST THE PERSON      ┆ GBH WITH INTENT             ┆ Barking       ┆ 8      ┆ 11     │
```

### Example: knife crime by borough

```python
import polars as pl
from london_crime import load

df = load.recorded_crime_borough()

# Melt wide → long
month_cols = [c for c in df.columns if c.isdigit()]
long = df.unpivot(on=month_cols, index=["majortext", "minortext", "boroughname"], variable_name="month", value_name="count")

# Knife crime subcategories
knife = long.filter(pl.col("minortext").str.contains("KNIFE|BLADE|WEAPON"))
by_borough = knife.group_by("boroughname").agg(pl.col("count").sum()).sort("count", descending=True)
print(by_borough.head(10))
```

### Example: stop and search by ethnicity

```python
import polars as pl
from london_crime import load

df = load.stop_search()

by_ethnicity = (
    df.group_by("ethnicappearance")
    .agg(pl.len().alias("stops"))
    .sort("stops", descending=True)
)
print(by_ethnicity)
```

## Refreshing locally

```bash
git clone https://github.com/fenneh/london-crime-data
cd london-crime-data
uv sync
uv run scripts/refresh.py          # all sources
uv run scripts/refresh.py --source stop-search  # one source
uv run scripts/refresh.py --list   # list available sources
```

## Sources

All data is published by the **Metropolitan Police Service** via the [London Datastore](https://data.london.gov.uk/) and licensed under the [UK Open Government Licence v2.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/).

> Contains public sector information licensed under the Open Government Licence v2.0.

| Dataset | London Datastore page |
|---------|----------------------|
| MPS Recorded Crime: Geographic Breakdown | [exy3m](https://data.london.gov.uk/dataset/recorded_crime_summary) |
| MPS Stop and Search Dashboard | [e6yjz](https://data.london.gov.uk/dataset/mps-stop-and-search-dashboard-data-e6yjz) |
| MPS Monthly Crime Dashboard | [e5n6w](https://data.london.gov.uk/dataset/mps-monthly-crime-dashboard-data-e5n6w) |
| MPS Custody: Arrests, Disposals, Strip Searches | [2r7po](https://data.london.gov.uk/dataset/mps-custody-arrests-disposals-strip-searches-2r7po) |
| MPS Violence Against Women and Girls Dashboard | [2yod5](https://data.london.gov.uk/dataset/mps-violence-against-women-and-girls-dashboard-data-2yod5) |
| MPS Business Crime Dashboard | [2zpjy](https://data.london.gov.uk/dataset/mps-business-crime-dashboard-data-2zpjy) |
| MPS Homicide Dashboard | [2l1w8](https://data.london.gov.uk/dataset/mps-homicide-dashboard-data-2l1w8) |
| MPS Stolen Animals Dashboard | [e756x](https://data.london.gov.uk/dataset/mps-stolen-animals-dashboard-data-e756x) |
| MPS More Thorough and Intimate Part Searches | [emxgp](https://data.london.gov.uk/dataset/mps-stop-and-search-more-thorough-searches-intimate-parts-expose-emxgp) |
