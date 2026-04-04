# london-crime-data

MPS (Metropolitan Police Service) crime datasets as Parquet files, refreshed monthly.

The MPS publishes all data via the [London Datastore](https://data.london.gov.uk/) under the [Open Government Licence v2.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/). These figures are crimes the MPS recorded, not all crimes that occurred.

**[Browse the data interactively](https://fenneh.github.io/london-crime-data/)** — **[Open in Colab](https://colab.research.google.com/github/fenneh/london-crime-data/blob/main/notebooks/explore_london_crime.ipynb)**

## Datasets

The geographic breakdown files (borough, ward, LSOA) are in **wide format**: one row per location/category combination, with monthly count columns (`202308`, `202309`, etc.). All other files are in long format.

| File | Rows | Description |
|------|------|-------------|
| `recorded-crime-borough.parquet` | 1,032 wide | Borough-level counts, Mar 2024–Feb 2026. Major + minor offence categories. |
| `recorded-crime-borough-historical.parquet` | 949 wide | Same, Apr 2010–Jul 2023. |
| `recorded-crime-ward.parquet` | 18,688 wide | Ward-level, Feb 2024–Feb 2026. |
| `recorded-crime-ward-historical.parquet` | 18,629 wide | Ward-level, Apr 2010–Jul 2023. |
| `recorded-crime-lsoa.parquet` | 105,620 wide | LSOA-level, Feb 2024–Feb 2026. |
| `recorded-crime-lsoa-historical.parquet` | 113,269 wide | LSOA-level, Apr 2010–Jul 2023. |
| `stop-search.parquet` | 1,351,798 | Individual stop and search records. Jun 2020–Dec 2025. Ethnicity, legislation, object of search, outcome. |
| `custody.parquet` | 32,870 | Arrests by ethnicity, disposal type, and strip search data. Jan 2021–Feb 2026. |
| `monthly-crime-dashboard.parquet` | 59,431 | Pan-London monthly knife crime totals by area, borough, and SNT. Mar 2022–Feb 2026. |
| `vawg-offences.parquet` | 411,341 | Violence against women and girls offence counts by type, borough, month. Jan 2014–Feb 2026. |
| `vawg-victims.parquet` | 410,576 | VAWG victim demographics by offence type and borough. Jan 2014–Feb 2026. |
| `business-crime-offences.parquet` | 2,023,536 | Business crime offence counts by type, borough, month. ~3.5 years to Feb 2026. |
| `business-crime-outcomes.parquet` | 2,875,711 | Business crime outcomes by type, borough, month. ~3.5 years to Feb 2026. |
| `homicide.parquet` | 4,512 | Homicide accused records from Apr 2003. Method, demographics, borough. Proceedings date max Sep 2023 (ongoing cases excluded). |
| `stolen-animals.parquet` | 5,723 | Stolen animal reports by species, borough, month. Apr 2010–Sep 2023. |
| `thorough-searches.parquet` | 44,110 | More thorough and intimate part searches (MTIPS). Jan 2019–Feb 2026. |

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

df = load.recorded_crime_borough()               # Mar 2024–Feb 2026
df = load.recorded_crime_borough(historical=True) # Apr 2010–Jul 2023
df = load.stop_search(remote=True)               # pull from GitHub without cloning
```

## Geographic data: wide format

Each row covers one (location, major category, minor category) combination. Columns: `majortext`, `minortext`, `boroughname` (or `wardname`/`lsoaname`), then `202403`, `202404`, ... `202602`.

Convert to long format with `unpivot`:

```python
import polars as pl
from london_crime import load

df = load.recorded_crime_borough()
month_cols = [c for c in df.columns if c.isdigit()]

long = df.unpivot(
    on=month_cols,
    index=["majortext", "minortext", "boroughname"],
    variable_name="month",
    value_name="count",
)
```

### Example: knife crime by borough

```python
knife = long.filter(pl.col("minortext").str.contains("KNIFE|BLADE|WEAPON"))
by_borough = knife.group_by("boroughname").agg(pl.col("count").sum()).sort("count", descending=True)
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

The stop-search file combines snapshots from different schema versions. Records from Mar 2024 onwards use `stopdate` (DD/MM/YYYY); earlier records use `date` (YYYY-MM-DD).

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

> Contains public sector information licensed under the Open Government Licence v2.0.

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
