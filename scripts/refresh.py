"""Refresh all (or specific) datasets from the London Datastore.

Usage:
    uv run scripts/refresh.py                        # refresh all sources
    uv run scripts/refresh.py --source recorded-crime-geographic
    uv run scripts/refresh.py --dry-run              # show what would run
    uv run scripts/refresh.py --list                 # list available sources
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from london_crime._fetch import refresh_source
from london_crime._sources import SOURCES

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh London crime datasets")
    parser.add_argument("--source", help="Refresh a specific source key only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched")
    parser.add_argument("--list", action="store_true", help="List available sources")
    args = parser.parse_args()

    if args.list:
        for s in SOURCES:
            print(f"  {s['key']:<40} {s['name']}")
        return

    sources = SOURCES
    if args.source:
        sources = [s for s in SOURCES if s["key"] == args.source]
        if not sources:
            logger.error("Unknown source: %r. Use --list to see available sources.", args.source)
            sys.exit(1)

    if args.dry_run:
        print("Would refresh:")
        for s in sources:
            print(f"  {s['key']} ({s['ckan_id']})")
        return

    total_files = 0
    total_rows = 0
    failed = []

    for source in sources:
        try:
            results = refresh_source(source)
            total_files += len(results)
            total_rows += sum(results.values())
        except Exception as exc:
            logger.error("FAILED %s: %s", source["key"], exc)
            failed.append(source["key"])

    print(f"\n{'='*50}")
    print(f"Refreshed {total_files} file(s), {total_rows:,} total rows")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
