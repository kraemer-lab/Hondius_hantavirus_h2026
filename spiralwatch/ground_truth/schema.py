"""
Dataclasses for the ground-truth layer.

Field names are taken directly from the source files rather than invented:
  - Event            <- data/linelist/2026_hantavirus.csv (one row = one case)
  - Claim/CaseMention/ExposureMention
                      <- data/news sources/hantavirus_results.json ("result" per article)
  - Source            <- data/news sources/mc-onlinenews-mediacloud-*.csv (one row = one article)

Anything present in the source file but not worth a typed field is kept in `raw`
so ingestion never silently drops data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Event:
    """One case row from the outbreak line list."""

    gh_id: str
    pathogen: str
    case_status: str
    who_case_number: str | None
    location_country: str | None
    location_admin1: str | None
    location_admin2: str | None
    age: str | None
    gender: str | None
    nationality: str | None
    occupation: str | None
    cruise_crew: bool | None
    cruise_passenger: bool | None
    symptoms: str | None
    date_onset: date | None
    date_confirmation: date | None
    hospitalised: bool | None
    date_hospitalisation: date | None
    intensive_care: bool | None
    date_intensive_care: date | None
    isolated: bool | None
    date_isolation: date | None
    outcome: str | None
    date_death: date | None
    date_recovered: date | None
    death_cause: str | None
    contact_with_case: bool | None
    contact_gh_id: str | None
    contact_setting: str | None
    contact_comment: str | None
    ship_board_date: date | None
    ship_disembark_location: str | None
    ship_disembark_date: date | None
    travel_history: str | None
    travel_from: str | None
    travel_to: str | None
    travel_flight: str | None
    travel_comment: str | None
    confirmation_method: str | None
    confirmation_comment: str | None
    accession_id: str | None
    source_urls: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class CaseMention:
    """A case (or case cluster) as reported inside a single news article."""

    case_id: int | None
    n_cases: int | None
    age: str | None
    gender: str | None
    case_status: str | None
    case_date: str | None
    case_location: str | None
    hospitalized: bool | None
    icu: bool | None
    travel_history: str | None
    exposure_route_for_case: str | None
    outcome: str | None
    notes: str | None


@dataclass
class ExposureMention:
    """An exposure event (individual or aggregate) reported inside an article."""

    exposure_id: int | None
    exposure_category: str | None
    n_exposed: int | None
    exposure_route: str | None
    exposure_setting: str | None
    exposure_source: str | None
    exposure_location: str | None
    exposure_date: str | None
    exposure_window: str | None
    linked_to_confirmed_case: bool | None
    monitoring_status: str | None
    description: str | None


@dataclass
class Claim:
    """
    The structured extraction for one news article — what the article asserts
    about the outbreak, not what actually happened. Verification against
    `Event` records happens in narrative_graph/linker.py, not here.
    """

    id: str
    url: str
    title: str | None
    media_name: str | None
    publish_date: date | None
    language: str | None
    text: str | None

    country: str | None
    report_scope: str | None
    hantavirus_type: str | None
    syndrome: str | None
    transmission_mode_described: str | None
    reporting_window: str | None
    counting_method: str | None
    cumulative_total: int | None
    prior_cumulative_total: int | None
    prior_report_date: str | None
    is_verifiable_outbreak: bool
    outbreak_dates: list[str] = field(default_factory=list)
    outbreak_locations: list[str] = field(default_factory=list)
    total_cases_reported: int | None = None
    cases: list[CaseMention] = field(default_factory=list)
    exposures: list[ExposureMention] = field(default_factory=list)
    data_source_limitation: str | None = None
    cases_validation_note: str | None = None
    location_matches: object | None = None

    source_id: str | None = None  # joined to Source.id via url
    raw: dict = field(default_factory=dict)


@dataclass
class Source:
    """One article inventory row from the Media Cloud export."""

    id: str
    url: str
    media_name: str | None
    media_url: str | None
    title: str | None
    publish_date: date | None
    indexed_date: str | None
    language: str | None
    credibility_score: float | None = None
    raw: dict = field(default_factory=dict)
