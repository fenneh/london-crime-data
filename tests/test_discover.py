"""Tests for scripts/discover.py URL extraction helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import discover  # noqa: E402


def _response(status: int, body=None, text: str = "") -> Mock:
    r = Mock()
    r.status_code = status
    if body is not None:
        r.json.return_value = body
    r.text = text
    return r


class TestTryDatapressApi:
    def test_extracts_urls_by_extension(self):
        body = {"resources": ["https://data.london.gov.uk/files/report.csv"]}
        with patch("discover.httpx.get", return_value=_response(200, body=body)):
            urls = discover._try_datapress_api("some-dataset")
        assert urls == ["https://data.london.gov.uk/files/report.csv"]

    def test_dedupes_preserving_order(self):
        body = {
            "a": "https://x.com/a.csv",
            "b": "https://x.com/b.csv",
            "c": "https://x.com/a.csv",
        }
        with patch("discover.httpx.get", return_value=_response(200, body=body)):
            urls = discover._try_datapress_api("some-dataset")
        assert urls == ["https://x.com/a.csv", "https://x.com/b.csv"]

    def test_stops_at_first_endpoint_with_urls(self):
        found = _response(200, body={"u": "https://x.com/f.csv"})
        empty = _response(200, body={})
        with patch("discover.httpx.get", side_effect=[found, empty, empty]) as get:
            urls = discover._try_datapress_api("some-dataset")
        assert urls == ["https://x.com/f.csv"]
        assert get.call_count == 1

    def test_non_200_response_yields_no_urls(self):
        with patch("discover.httpx.get", return_value=_response(404)):
            urls = discover._try_datapress_api("some-dataset")
        assert urls == []

    def test_request_exception_yields_no_urls(self):
        with patch("discover.httpx.get", side_effect=Exception("boom")):
            urls = discover._try_datapress_api("some-dataset")
        assert urls == []


class TestTryHtmlScrape:
    def test_extracts_href_links_by_extension(self):
        html = '<a href="/files/report.xlsx">Download</a>'
        with patch("discover.httpx.get", return_value=_response(200, text=html)):
            urls = discover._try_html_scrape("some-page")
        assert urls == ["https://data.london.gov.uk/files/report.xlsx"]

    def test_resolves_relative_urls_against_datastore(self):
        html = '<a href="/d/foo.csv">Download</a>'
        with patch("discover.httpx.get", return_value=_response(200, text=html)):
            urls = discover._try_html_scrape("some-page")
        assert urls[0].startswith("https://data.london.gov.uk/")

    def test_leaves_absolute_urls_untouched(self):
        html = '<a href="https://other.example.com/report.zip">Download</a>'
        with patch("discover.httpx.get", return_value=_response(200, text=html)):
            urls = discover._try_html_scrape("some-page")
        assert urls == ["https://other.example.com/report.zip"]

    def test_non_200_response_yields_no_urls(self):
        with patch("discover.httpx.get", return_value=_response(404)):
            urls = discover._try_html_scrape("some-page")
        assert urls == []

    def test_request_exception_yields_no_urls(self):
        with patch("discover.httpx.get", side_effect=Exception("boom")):
            urls = discover._try_html_scrape("some-page")
        assert urls == []
