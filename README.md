# london-crime-data

[![CI](https://github.com/fenneh/london-crime-data/actions/workflows/ci.yml/badge.svg)](https://github.com/fenneh/london-crime-data/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

MPS (Metropolitan Police Service) crime datasets as Parquet files, refreshed monthly.

The MPS publishes all data via the [London Datastore](https://data.london.gov.uk/) under the [Open Government Licence v2.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/). These figures are crimes the MPS recorded, not all crimes that occurred.

**[Browse the data interactively](https://fenneh.github.io/london-crime-data/)** — **[Open in Colab](https://colab.research.google.com/github/fenneh/london-crime-data/blob/main/notebooks/explore_london_crime.ipynb)**

## Datasets

The geographic breakdown files (borough, ward, LSOA) are in **wide format**: one row per location/category combination, with monthly count columns (`202308`, `202309`, etc.). All other files are in long format.

| File | Rows | Description |
|------|------|-------------|
| `recorded-crime-borough.parquet` | 989 wide | Borough-level counts, Sep 2024–Aug 2026. Major + minor offence categories. |
| `recorded-crime-borough-historical.parquet` | 1,124 wide | Same layout, Sep 2020–Aug 2024. Older 48-month window. |
| `recorded-crime-ward.parquet` | 18,804 wide | Ward-level, Sep 2024–Aug 2026. |
| `recorded-crime-ward-historical.parquet` | 20,951 wide | Ward-level, Sep 2020–Aug 2024. Older 48-month window. |
| `recorded-crime-lsoa.parquet` | 106,275 wide | LSOA-level, Sep 2024–Aug 2026. |
| `recorded-crime-lsoa-historical.parquet` | 121,222 wide | LSOA-level, Aug 2020–Jul 2024. Older 48-month window. |
| `stop-search.parquet` | 1,275,512 | Individual stop and search records. May 2020–Sep 2026. Ethnicity, legislation, object of search, outcome. |
| `custody.parquet` | 17,941 | Arrests by ethnicity, disposal type, and strip search data. Jan 2022–Aug 2026. |
| `monthly-crime-dashboard.parquet` | 60,732 | Pan-London monthly knife crime totals by area, borough, and SNT. Sep 2022–Aug 2026. |
| `vawg-offences.parquet` | 413,821 | Violence against women and girls offence counts by type, borough, month. Jan 2014–Apr 2026. |
| `vawg-victims.parquet` | 416,894 | VAWG victim demographics by offence type and borough. Jan 2014–Apr 2026. |
| `business-crime-offences.parquet` | 2,649,498 | Business crime offence counts by type, borough, month. Jun 2022–Aug 2026. |
| `business-crime-outcomes.parquet` | 3,438,451 | Business crime outcomes by type, borough, month. Jun 2022–Aug 2026. |
| `homicide.parquet` | 3,131 | Homicide records, Apr 2003–Sep 2025. Method, demographics, borough. |
| `stolen-animals.parquet` | 5,723 | Stolen animal reports by species, borough, month. Apr 2010–Sep 2023. |
| `thorough-searches.parquet` | 56,411 | More thorough and intimate part searches (MTIPS). Jan 2019–Sep 2026. |

Updated on the 6th of each month.

## Terminology

The datasets use MPS and Home Office standard terminology. Key definitions:

**Crime categories** — `majortext` and `minortext` follow the [National Crime Recording Standard (NCRS)](https://www.gov.uk/government/publications/counting-rules-for-recorded-crime). The Home Office publishes [counting rules](https://www.gov.uk/government/publications/counting-rules-for-recorded-crime) that define exactly what qualifies as each offence type.

**Stop and search legislation** — the `legislation` column in `stop-search.parquet` refers to the power used:

| Code | Power |
|------|-------|
| s1 PACE 1984 | Police and Criminal Evidence Act — general suspicion-based search |
| s23 MDA 1971 | Misuse of Drugs Act — suspicion of drug possession |
| s60 CJPOA 1994 | Criminal Justice and Public Order Act — no suspicion required, authorised in advance for a specific area/time |
| s47A Terrorism Act 2000 | Suspicion-free search in a designated area |

**Ethnicity coding** — stop-search records use two systems. Officer-defined appearance (`ethnicappearance`) uses a 6-category code: W (White), B (Black), A (Asian), M (Mixed), C (Chinese or other), O (Other/Not stated). Self-defined ethnicity uses the [ONS 16+1 categories](https://www.ethnicity-facts-figures.service.gov.uk/style-guide/ethnic-groups). Records from before Mar 2024 use `ethnic_appearance` (older column name).

**LSOA** — Lower Super Output Area. ONS-defined statistical geography of approximately 400–1,200 households, used across UK government statistics. [Full definitions and boundaries](https://www.ons.gov.uk/methodology/geography/ukgeographies/censusgeographies/census2021geographies).

**VAWG** — Violence Against Women and Girls. The MPS definition covers domestic abuse, rape, sexual offences, stalking, harassment, forced marriage, and honour-based abuse. [MPS VAWG strategy](https://www.met.police.uk/advice/advice-and-information/vawg/violence-against-women-and-girls/).

**MTIPS** — More Thorough and Intimate Part Searches. Searches conducted under s54 or s55 PACE 1984 that go beyond a standard pat-down. Governed by [PACE Code A](https://www.gov.uk/government/publications/pace-code-a-2023).

## Usage

### Direct download

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
```

```python
from london_crime import load

df = load.recorded_crime_borough()               # current 24-month window
df = load.recorded_crime_borough(historical=True) # older 48-month window
df = load.stop_search(remote=True)               # pull from GitHub without cloning
```

## Geographic data: wide format

Each row covers one (location, major category, minor category) combination. Columns vary by file: `group` and `subgroup` for the offence category, plus `bocu` (borough), `wardname` and `wardcode` (ward), or `lsoa_code`, `lsoa_name` and `borough` (LSOA), then monthly count columns `202409`, `202410`, ... `202608`.

Convert to long format with `unpivot`:

```python
import polars as pl
from london_crime import load

df = load.recorded_crime_borough()
month_cols = [c for c in df.columns if c.isdigit()]

long = df.unpivot(
    on=month_cols,
    index=["group", "subgroup", "bocu"],
    variable_name="month",
    value_name="count",
)
```

### Example: knife crime by borough

```python
knife = long.filter(pl.col("subgroup").str.contains("KNIFE|BLADE|WEAPON"))
by_borough = knife.group_by("bocu").agg(pl.col("count").sum()).sort("count", descending=True)
print(by_borough.head(10))
```

### Example: stop and search by officer-defined ethnicity

```python
import polars as pl
from london_crime import load

df = load.stop_search()

# Newer records use 'ethnicappearance', older records use 'ethnic_appearance'
by_ethnicity = (
    df.group_by("ethnicappearance")
    .agg(pl.len().alias("stops"))
    .sort("stops", descending=True)
)
print(by_ethnicity)
```

The stop-search file combines snapshots from different schema versions. Newer records use `stopdate`, mid-period records use `date`, and the oldest snapshots use `year_month`. All three are ISO-style strings.

## Refreshing locally

```bash
git clone https://github.com/fenneh/london-crime-data
cd london-crime-data
uv sync
uv run scripts/refresh.py          # all sources
uv run scripts/refresh.py --source stop-search
uv run scripts/refresh.py --list
```

## Related

[**uk-police-api**](https://github.com/fenneh/uk-police-api) — Python client for the [data.police.uk](https://data.police.uk/docs/) REST API. Covers all 44 forces (not just the MPS), with street-level crime, stop and search, neighbourhoods, and outcomes queryable by coordinate, postcode, or polygon. Useful when you need live or recent data, specific addresses, or forces outside London.

## Sources

> Contains public sector information licensed under the Open Government Licence v2.0. Code in this repo is [MIT licensed](LICENSE); the datasets themselves remain under OGL v2.0.

| Dataset | London Datastore |
|---------|-----------------|
| MPS Recorded Crime: Geographic Breakdown | [exy3m](https://data.london.gov.uk/dataset/recorded_crime_summary) |
| MPS Stop and Search Dashboard | [e6yjz](https://data.london.gov.uk/dataset/mps-stop-and-search-dashboard-data-e6yjz) |
| MPS Monthly Crime Dashboard | [e5n6w](https://data.london.gov.uk/dataset/mps-monthly-crime-dashboard-data-e5n6w) |
| MPS Custody: Arrests, Disposals, Strip Searches | [2r7po](https://data.london.gov.uk/dataset/mps-custody-arrests-disposals-strip-searches-2r7po) |
| MPS Violence Against Women and Girls Dashboard | [2yod5](https://data.london.gov.uk/dataset/mps-violence-against-women-and-girls-dashboard-data-2yod5) |
| MPS Business Crime Dashboard | [2zpjy](https://data.london.gov.uk/dataset/mps-business-crime-dashboard-data-2zpjy) |
| MPS Homicide Dashboard | [2l1w8](https://data.london.gov.uk/dataset/mps-homicide-dashboard-data-2l1w8) |
| MPS Stolen Animals Dashboard | [e756x](https://data.london.gov.uk/dataset/mps-stolen-animals-dashboard-data-e756x) |
| MPS More Thorough and Intimate Part Searches | [emxgp](https://data.london.gov.uk/dataset/mps-stop-and-search-more-thorough-searches-intimate-parts-expose-emxgp) |
