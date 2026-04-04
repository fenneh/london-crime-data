"""Discover download URLs for London Datastore datasets.

The London Datastore blocks automated HTML access, but dataset pages show
direct download links. This script tries several methods to find them.

Usage:
    uv run scripts/discover.py                  # try all sources
    uv run scripts/discover.py --source custody

If automated discovery fails for a dataset, visit the URL manually in a
browser and find the CSV/Excel download link, then add it to london_crime/_sources.py
in the `direct_urls` list for that source.

Dataset pages (open these in a browser if automated discovery fails):
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from london_crime._sources import SOURCES

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# London Datastore dataset page URLs for manual discovery
DATASET_PAGES = {
    "recorded-crime-borough":   "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m",
    "recorded-crime-ward":      "https://data.london.gov.uk/dataset/mps-recorded-crime-geographic-breakdown-exy3m",
    "knife-crime":              "https://data.london.gov.uk/dataset/mps-knife-enabled-crime-dashboard-data",
    "stop-search":              "https://data.london.gov.uk/dataset/mps-stop-and-search-dashboard-data-e6yjz",
    "custody":                  "https://data.london.gov.uk/dataset/mps-custody-arrests-disposals-strip-searches-2r7po",
    "homicide":                 "https://data.london.gov.uk/dataset/mps-homicide-dashboard-data",
    "monthly-crime-dashboard":  "https://data.london.gov.uk/dataset/mps-monthly-crime-dashboard-data-e5n6w",
}


def _try_datapress_api(dataset_id: str) -> list[str]:
    """Try London Datastore's WordPress/DataPress REST API."""
    urls = []
    # DataPress exposes dataset metadata via WP REST API
    for endpoint in [
        f"https://data.london.gov.uk/wp-json/wp/v2/dataset?slug={dataset_id}",
        f"https://data.london.gov.uk/wp-json/datapress/v1/dataset/{dataset_id}",
        f"https://data.london.gov.uk/wp-json/datapress/v1/datasets?slug={dataset_id}",
    ]:
        try:
            r = httpx.get(endpoint, timeout=15, follow_redirects=True, headers=_HEADERS)
            if r.status_code == 200:
                body = r.json()
                logger.info("  DataPress API success: %s", endpoint)
                # Extract download URLs from response
                text = json.dumps(body)
                for ext in (".csv", ".xlsx", ".xls", ".zip"):
                    import re
                    found = re.findall(r'https?://[^\s"\'<>]+' + re.escape(ext), text)
                    urls.extend(found)
                if urls:
                    break
        except Exception:
            pass
    return list(dict.fromkeys(urls))  # deduplicate, preserve order


def _try_html_scrape(dataset_id: str) -> list[str]:
    """Try to fetch HTML page and extract download links."""
    import re

    url = f"https://data.london.gov.uk/dataset/{dataset_id}"
    try:
        r = httpx.get(url, timeout=20, follow_redirects=True, headers=_HEADERS)
        if r.status_code != 200:
            logger.warning("  HTML page returned %d: %s", r.status_code, url)
            return []
        text = r.text
        urls = []
        for ext in (".csv", ".xlsx", ".xls", ".zip"):
            found = re.findall(r'href=["\']([^"\']+' + re.escape(ext) + r')["\']', text)
            urls.extend(found)
        # Make relative URLs absolute
        from urllib.parse import urljoin
        return [urljoin("https://data.london.gov.uk", u) for u in urls]
    except Exception as exc:
        logger.warning("  HTML scrape failed: %s", exc)
        return []


def discover(source_key: str | None = None) -> None:
    sources = SOURCES if source_key is None else [s for s in SOURCES if s["key"] == source_key]

    print("\nDataset page URLs (open these in a browser if automated discovery fails):\n")
    for key, page_url in DATASET_PAGES.items():
        print(f"  {key:<40} {page_url}")

    print("\n--- Automated discovery ---\n")

    for source in sources:
        key = source["key"]
        ckan_id = source.get("ckan_id", key)
        print(f"\n{source['name']} ({key})")

        found: list[str] = []

        # Try DataPress API
        found.extend(_try_datapress_api(ckan_id))

        # Try HTML scrape
        if not found and key in DATASET_PAGES:
            page_id = DATASET_PAGES[key].split("/")[-1]
            found.extend(_try_html_scrape(page_id))

        if found:
            print("  Found URLs:")
            for u in found:
                print(f"    {u}")
            print(f"\n  Add these to direct_urls for '{key}' in london_crime/_sources.py")
        else:
            page_url = DATASET_PAGES.get(key, "")
            print(f"  Automated discovery failed.")
            if page_url:
                print(f"  → Open manually: {page_url}")
                print(f"    Right-click CSV/Excel link → Copy link address")
                print(f"    Add to direct_urls for '{key}' in london_crime/_sources.py")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Discover URLs for a specific source key")
    args = parser.parse_args()
    discover(args.source)
