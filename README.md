# london-crime-data

MPS (Metropolitan Police Service) crime datasets as Parquet files, refreshed monthly.

All data is published by the MPS via the [London Datastore](https://data.london.gov.uk/) under the [Open Government Licence v2.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/). These figures cover crimes recorded by the MPS, not all crimes that occurred.

## Datasets

The geographic breakdown files (borough, ward, LSOA) are in **wide format**: one row per location/category combination, with monthly count columns (`202308`, `202309`, etc.). All other files are in long format.

| File | Rows | Description |
|------|------|-------------|
| `recorded-crime-borough.parquet` | 1,015 wide | Borough-level counts, Aug 2023–Jul 2025. Major + minor offence categories. |
| `recorded-crime-borough-historical.parquet` | 949 wide | Same, Apr 2010–Jul 2023. |
| `recorded-crime-ward.parquet` | 17,897 wide | Ward-level, Aug 2023–Jul 2025. |
| `recorded-crime-ward-historical.parquet` | 18,629 wide | Ward-level, Apr 2010–Jul 2023. |
| `recorded-crime-lsoa.parquet` | 101,048 wide | LSOA-level, Aug 2023–Jul 2025. |
| `recorded-crime-lsoa-historical.parquet` | 113,269 wide | LSOA-level, Apr 2010–Jul 2023. |
| `stop-search.parquet` | 1,351,798 | Individual stop and search records. Jun 2020–Feb 2026. Ethnicity, legislation, object of search, outcome. |
| `custody.parquet` | 32,870 | Arrests by ethnicity, disposal type, and strip search data. |
| `monthly-crime-dashboard.parquet` | 472,354 | Pan-London monthly totals by category with outcomes and rates. |
| `vawg-offences.parquet` | 411,341 | Violence against women and girls offence counts by type, borough, month. Jan 2014–present. |
| `vawg-victims.parquet` | 410,576 | VAWG victim demographics by offence type and borough. Jan 2014–present. |
| `business-crime-offences.parquet` | 290,837 | Business crime offence counts by type, borough, month. ~3.5 years. |
| `business-crime-outcomes.parquet` | 407,341 | Business crime outcomes by type, borough, month. ~3.5 years. |
| `homicide.parquet` | 4,512 | Homicide records from 2003: method, demographics, borough. |
| `stolen-animals.parquet` | 5,723 | Stolen animal reports by species, borough, month. Apr 2010–present. |
| `thorough-searches.parquet` | 44,110 | More thorough and intimate part searches (MTIPS). Jan 2019–present. |

Updated on the 6th of each month.

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

df = load.recorded_crime_borough()               # Aug 2023–Jul 2025
df = load.recorded_crime_borough(historical=True) # Apr 2010–Jul 2023
df = load.stop_search(remote=True)               # pull from GitHub without cloning
```

## Geographic data: wide format

The borough, ward, and LSOA files have one row per (location, major category, minor category) with monthly count columns. Columns: `majortext`, `minortext`, `boroughname` (or `wardname`/`lsoaname`), then `202308`, `202309`, ... `202507`.

To work with it in long format:

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

Note: the stop-search file combines snapshots with different schemas. The date is in `stopdate` (format `DD/MM/YYYY`) for records from Mar 2024 onwards, and `date` (format `YYYY-MM-DD`) for earlier records.

## Refreshing locally

```bash
git clone https://github.com/fenneh/london-crime-data
cd london-crime-data
uv sync
uv run scripts/refresh.py          # all sources
uv run scripts/refresh.py --source stop-search
uv run scripts/refresh.py --list
```

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
