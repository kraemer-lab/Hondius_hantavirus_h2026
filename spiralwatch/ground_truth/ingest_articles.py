"""
Merges hantavirus_articles.json (raw article text/metadata) with
hantavirus_results.json (structured per-article extraction) into Claim objects,
joined on url. Optionally cross-referenced against Source records so each
Claim carries a source_id.
"""

from __future__ import annotations

import json
from pathlib import Path

from .parsing_utils import parse_date
from .schema import CaseMention, Claim, ExposureMention, Source

DEFAULT_ARTICLES_PATH = Path("data/news sources/hantavirus_articles.json")
DEFAULT_RESULTS_PATH = Path("data/news sources/hantavirus_results.json")


def _case_mention_from_dict(d: dict) -> CaseMention:
    return CaseMention(
        case_id=d.get("case_id"),
        n_cases=d.get("n_cases"),
        age=d.get("age"),
        gender=d.get("gender"),
        case_status=d.get("case_status"),
        case_date=d.get("case_date"),
        case_location=d.get("case_location"),
        hospitalized=d.get("hospitalized"),
        icu=d.get("icu"),
        travel_history=d.get("travel_history"),
        exposure_route_for_case=d.get("exposure_route_for_case"),
        outcome=d.get("outcome"),
        notes=d.get("notes"),
    )


def _exposure_mention_from_dict(d: dict) -> ExposureMention:
    return ExposureMention(
        exposure_id=d.get("exposure_id"),
        exposure_category=d.get("exposure_category"),
        n_exposed=d.get("n_exposed"),
        exposure_route=d.get("exposure_route"),
        exposure_setting=d.get("exposure_setting"),
        exposure_source=d.get("exposure_source"),
        exposure_location=d.get("exposure_location"),
        exposure_date=d.get("exposure_date"),
        exposure_window=d.get("exposure_window"),
        linked_to_confirmed_case=d.get("linked_to_confirmed_case"),
        monitoring_status=d.get("monitoring_status"),
        description=d.get("description"),
    )


def load_claims(
    articles_path: Path = DEFAULT_ARTICLES_PATH,
    results_path: Path = DEFAULT_RESULTS_PATH,
    sources: dict[str, Source] | None = None,
) -> list[Claim]:
    with open(articles_path, encoding="utf-8") as f:
        articles = json.load(f)
    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    articles_by_url = {a["url"]: a for a in articles}
    sources = sources or {}

    claims: list[Claim] = []
    for entry in results:
        url = entry["url"]
        if entry.get("status") != "success" or not entry.get("result"):
            continue
        result = entry["result"]
        article = articles_by_url.get(url, {})
        source = sources.get(url)

        claims.append(
            Claim(
                id=article.get("id", url),
                url=url,
                title=article.get("title"),
                media_name=article.get("media_name"),
                publish_date=parse_date(article.get("publish_date")),
                language=article.get("language"),
                text=article.get("text"),
                country=result.get("country"),
                report_scope=result.get("report_scope"),
                hantavirus_type=result.get("hantavirus_type"),
                syndrome=result.get("syndrome"),
                transmission_mode_described=result.get("transmission_mode_described"),
                reporting_window=result.get("reporting_window"),
                counting_method=result.get("counting_method"),
                cumulative_total=result.get("cumulative_total"),
                prior_cumulative_total=result.get("prior_cumulative_total"),
                prior_report_date=result.get("prior_report_date"),
                is_verifiable_outbreak=bool(result.get("is_verifiable_outbreak")),
                outbreak_dates=result.get("outbreak_dates") or [],
                outbreak_locations=result.get("outbreak_locations") or [],
                total_cases_reported=result.get("total_cases_reported"),
                cases=[_case_mention_from_dict(c) for c in result.get("cases") or []],
                exposures=[_exposure_mention_from_dict(e) for e in result.get("exposures") or []],
                data_source_limitation=result.get("data_source_limitation"),
                cases_validation_note=result.get("cases_validation_note"),
                location_matches=result.get("location_matches"),
                source_id=source.id if source else None,
                raw=entry,
            )
        )
    return claims
