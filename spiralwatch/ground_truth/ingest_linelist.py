"""Reads data/linelist/2026_hantavirus.csv into Event objects."""

from __future__ import annotations

import csv
from pathlib import Path

from .parsing_utils import clean_str, parse_date, parse_yn_bool
from .schema import Event

DEFAULT_LINELIST_PATH = Path("data/linelist/2026_hantavirus.csv")

_SOURCE_COLUMNS = [
    "Source_I",
    "Source_II",
    "Source_III",
    "Source_IV",
    "Source_V",
    "Source_VI",
    "Source_VII",
]


def _row_to_event(row: dict[str, str]) -> Event:
    return Event(
        gh_id=row["Gh_ID"],
        pathogen=row["Pathogen_name"],
        case_status=row["Case_status"],
        who_case_number=clean_str(row.get("WHO_case number")),
        location_country=clean_str(row.get("Location_Admin 0")),
        location_admin1=clean_str(row.get("Location_Admin 1")),
        location_admin2=clean_str(row.get("Location_Admin 2")),
        age=clean_str(row.get("Age")),
        gender=clean_str(row.get("Gender")),
        nationality=clean_str(row.get("Nationality")),
        occupation=clean_str(row.get("Occupation")),
        cruise_crew=parse_yn_bool(row.get("Cruise_crew")),
        cruise_passenger=parse_yn_bool(row.get("Cruise_passenger guest")),
        symptoms=clean_str(row.get("Symptoms")),
        date_onset=parse_date(row.get("Date_onset")),
        date_confirmation=parse_date(row.get("Date_confirmation")),
        hospitalised=parse_yn_bool(row.get("Hospitalised")),
        date_hospitalisation=parse_date(row.get("Date_hospitalisation")),
        intensive_care=parse_yn_bool(row.get("Intensive_care")),
        date_intensive_care=parse_date(row.get("Date_intensive care")),
        isolated=parse_yn_bool(row.get("Isolated")),
        date_isolation=parse_date(row.get("Date_isolation")),
        outcome=clean_str(row.get("Outcome")),
        date_death=parse_date(row.get("Date_death")),
        date_recovered=parse_date(row.get("Date_recovered")),
        death_cause=clean_str(row.get("Death_cause")),
        contact_with_case=parse_yn_bool(row.get("Contact_with_case")),
        contact_gh_id=clean_str(row.get("Contact_GhID")),
        contact_setting=clean_str(row.get("Contact_setting")),
        contact_comment=clean_str(row.get("Contact_comment")),
        ship_board_date=parse_date(row.get("Ship_board date")),
        ship_disembark_location=clean_str(row.get("Ship_disembark location")),
        ship_disembark_date=parse_date(row.get("Ship_disembark date")),
        travel_history=clean_str(row.get("Travel_history")),
        travel_from=clean_str(row.get("Travel_from")),
        travel_to=clean_str(row.get("Travel_to")),
        travel_flight=clean_str(row.get("Travel_flight")),
        travel_comment=clean_str(row.get("Travel_comment")),
        confirmation_method=clean_str(row.get("Confirmation_method")),
        confirmation_comment=clean_str(row.get("Confirmation_comment")),
        accession_id=clean_str(row.get("accession_id")),
        source_urls=[
            url.strip()
            for col in _SOURCE_COLUMNS
            if (url := clean_str(row.get(col)))
        ],
        raw=dict(row),
    )


def load_events(path: Path = DEFAULT_LINELIST_PATH) -> list[Event]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [_row_to_event(row) for row in reader]
