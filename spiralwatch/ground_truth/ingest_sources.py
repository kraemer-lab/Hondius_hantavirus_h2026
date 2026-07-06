"""Reads the Media Cloud article inventory CSV into Source objects."""

from __future__ import annotations

import csv
from pathlib import Path

from .parsing_utils import clean_str, parse_date
from .schema import Source

DEFAULT_SOURCES_PATH = Path("data/news sources/mc-onlinenews-mediacloud-20260507155422-content.csv")


def _row_to_source(row: dict[str, str]) -> Source:
    return Source(
        id=row["id"],
        url=row["url"],
        media_name=clean_str(row.get("media_name")),
        media_url=clean_str(row.get("media_url")),
        title=clean_str(row.get("title")),
        publish_date=parse_date(row.get("publish_date")),
        indexed_date=clean_str(row.get("indexed_date")),
        language=clean_str(row.get("language")),
        raw=dict(row),
    )


def load_sources(path: Path = DEFAULT_SOURCES_PATH) -> dict[str, Source]:
    """Returns Sources keyed by url, since that's what Claims join on."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sources = [_row_to_source(row) for row in reader]
    return {s.url: s for s in sources}
