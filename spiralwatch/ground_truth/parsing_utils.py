"""Small, shared parsing helpers for the CSV/JSON ingestion scripts."""

from __future__ import annotations

from datetime import date, datetime

_NA_TOKENS = {"", "na", "n/a", "unknown", "none", "null"}


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = value.strip()
    if value.lower() in _NA_TOKENS:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_yn_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    value = value.strip().lower()
    if value in _NA_TOKENS:
        return None
    if value in {"y", "yes", "true"}:
        return True
    if value in {"n", "no", "false"}:
        return False
    return None


def clean_str(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value.lower() not in _NA_TOKENS else None
