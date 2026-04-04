"""Registry of London Datastore MPS datasets.

Discovery: the London Datastore runs a CKAN-compatible API accessible via
the 5-character short ID at the end of each dataset slug, e.g.:
  mps-recorded-crime-geographic-breakdown-exy3m  →  short_id = "exy3m"
  https://data.london.gov.uk/api/action/package_show?id=exy3m
"""

from __future__ import annotations

CKAN_BASE = "https://data.london.gov.uk/api/action"

SOURCES: list[dict] = [
    # ── Recorded crime: borough, ward, LSOA ──────────────────────────────────
    # This is the richest dataset — includes major_category AND minor_category,
    # so "Violence Against the Person" splits into GBH, assault, harassment, etc.
    {
        "key": "recorded-crime-borough",
        "name": "MPS Recorded Crime: Borough Level",
        "short_id": "exy3m",
        "resource_name_contains": "Borough Level Crime",
        "prefer_historical": False,
        "output": "recorded-crime-borough.parquet",
        "description": (
            "Monthly crime counts by borough. Includes major + minor offence categories "
            "(e.g. Violence Against the Person → Common Assault, GBH, Harassment, etc). "
            "24 most recent months, updated monthly."
        ),
    },
    {
        "key": "recorded-crime-borough-historical",
        "name": "MPS Recorded Crime: Borough Level (Historical)",
        "short_id": "exy3m",
        "resource_name_contains": "Borough Level Crime (Historical)",
        "prefer_historical": True,
        "output": "recorded-crime-borough-historical.parquet",
        "description": "Full historical borough-level crime data from January 2008.",
    },
    {
        "key": "recorded-crime-ward",
        "name": "MPS Recorded Crime: Ward Level",
        "short_id": "exy3m",
        "resource_name_contains": "Ward Level Crime",
        "prefer_historical": False,
        "output": "recorded-crime-ward.parquet",
        "description": "Monthly crime counts at ward level with major/minor category breakdown.",
    },
    {
        "key": "recorded-crime-ward-historical",
        "name": "MPS Recorded Crime: Ward Level (Historical)",
        "short_id": "exy3m",
        "resource_name_contains": "Ward Level Crime (Historical)",
        "prefer_historical": True,
        "output": "recorded-crime-ward-historical.parquet",
        "description": "Full historical ward-level crime data from January 2008.",
    },
    {
        "key": "recorded-crime-lsoa",
        "name": "MPS Recorded Crime: LSOA Level",
        "short_id": "exy3m",
        "resource_name_contains": "LSOA Level Crime",
        "prefer_historical": False,
        "output": "recorded-crime-lsoa.parquet",
        "description": "Monthly crime counts at Lower Super Output Area level.",
    },
    {
        "key": "recorded-crime-lsoa-historical",
        "name": "MPS Recorded Crime: LSOA Level (Historical)",
        "short_id": "exy3m",
        "resource_name_contains": "LSOA Level Crime (Historical)",
        "prefer_historical": True,
        "output": "recorded-crime-lsoa-historical.parquet",
        "description": "Full historical LSOA-level crime data from January 2008.",
    },

    # ── Stop and search ───────────────────────────────────────────────────────
    # Dataset has ~45 monthly rolling-window snapshots. We use stride=22 to
    # download every 22nd resource (≈3 downloads) covering ~5 years of individual
    # stop records. Older resources use a different schema; _concat fills gaps with nulls.
    {
        "key": "stop-search",
        "name": "MPS Stop and Search Dashboard",
        "short_id": "e6yjz",
        "resource_name_contains": "LDS_Extract",
        "prefer_historical": False,
        "combine_resources": True,
        "combine_stride": 22,
        "output": "stop-search.parquet",
        "description": (
            "Individual stop and search records. Borough, legislation, ethnicity "
            "(officer-defined and self-defined), age, gender, outcome. "
            "Combined from multiple rolling-window snapshots (~5 years of data)."
        ),
    },

    # ── Monthly crime dashboard ───────────────────────────────────────────────
    # The dataset publishes 3 separate rolling files: KnifeCrimeData, OtherCrimeData,
    # TNOCrimeData (different schema, no crime_type column). We target KnifeCrimeData
    # here as it's the only one with a consistent crime_type column across all rows.
    {
        "key": "monthly-crime-dashboard",
        "name": "MPS Monthly Crime Dashboard",
        "short_id": "e5n6w",
        "resource_name_contains": "KnifeCrimeData",
        "prefer_historical": False,
        "output": "monthly-crime-dashboard.parquet",
        "description": "Pan-London monthly knife crime totals by area type and borough with outcomes and rates.",
    },

    # ── Custody ───────────────────────────────────────────────────────────────
    {
        "key": "custody",
        "name": "MPS Custody: Arrests, Disposals, Strip Searches",
        "short_id": "2r7po",
        "resource_name_contains": "",
        "prefer_historical": False,
        "output": "custody.parquet",
        "description": (
            "Custody suite records. Arrests by ethnicity, disposal type, strip searches."
        ),
    },

    # ── Violence Against Women and Girls (VAWG) ───────────────────────────────
    {
        "key": "vawg-offences",
        "name": "MPS VAWG: Offence Data",
        "short_id": "2yod5",
        "resource_name_contains": "Offence",
        "prefer_historical": False,
        "output": "vawg-offences.parquet",
        "description": "VAWG offence counts by type, borough, and month.",
    },
    {
        "key": "vawg-victims",
        "name": "MPS VAWG: Victim Data",
        "short_id": "2yod5",
        "resource_name_contains": "Victim",
        "prefer_historical": False,
        "output": "vawg-victims.parquet",
        "description": "VAWG victim demographics by offence type and borough.",
    },

    # ── Business crime ────────────────────────────────────────────────────────
    # stride=4 keeps memory usage manageable (6 downloads vs 24) while still
    # spanning the full ~3.5 year history.
    {
        "key": "business-crime-offences",
        "name": "MPS Business Crime: Offences",
        "short_id": "2zpjy",
        "resource_name_contains": "OffencesData",
        "prefer_historical": False,
        "combine_resources": True,
        "combine_stride": 4,
        "output": "business-crime-offences.parquet",
        "description": "Business crime offence counts by type, borough, and month. Combined from sampled snapshots (~3.5 years).",
    },
    {
        "key": "business-crime-outcomes",
        "name": "MPS Business Crime: Outcomes",
        "short_id": "2zpjy",
        "resource_name_contains": "OutcomesData",
        "prefer_historical": False,
        "combine_resources": True,
        "combine_stride": 4,
        "output": "business-crime-outcomes.parquet",
        "description": "Business crime outcome data by type, borough, and month. Combined from sampled snapshots (~3.5 years).",
    },

    # ── Homicide ──────────────────────────────────────────────────────────────
    {
        "key": "homicide",
        "name": "MPS Homicide Dashboard",
        "short_id": "2l1w8",
        "resource_name_contains": "",
        "prefer_historical": False,
        "output": "homicide.parquet",
        "description": "Homicide records from 2003: method, demographics, borough.",
    },

    # ── Stolen animals ────────────────────────────────────────────────────────
    {
        "key": "stolen-animals",
        "name": "MPS Stolen Animals Dashboard",
        "short_id": "e756x",
        "resource_name_contains": "",
        "prefer_historical": False,
        "output": "stolen-animals.parquet",
        "description": "Stolen animal reports by species, borough, and month.",
    },

    # ── More thorough / intimate part searches ────────────────────────────────
    # 40 resources with consistent schema going back to Jan 2019 — combine all.
    {
        "key": "thorough-searches",
        "name": "MPS More Thorough and Intimate Part Searches",
        "short_id": "emxgp",
        "resource_name_contains": "",
        "prefer_historical": False,
        "combine_resources": True,
        "combine_stride": 1,
        "output": "thorough-searches.parquet",
        "description": (
            "Strip search / more thorough search records (MTIPS). "
            "Ethnicity, age, gender, outcome. Combined from all snapshots (Jan 2019–present)."
        ),
    },
]

# Dataset page URLs for reference
DATASET_PAGES = {s["key"]: f"https://data.london.gov.uk/dataset/{s['short_id']}" for s in SOURCES}
