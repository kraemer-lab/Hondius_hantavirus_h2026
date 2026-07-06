"""
Builds a NarrativeGraph out of the ground-truth layer: one node per Event
and per Claim, with "reports_on" edges where a claim's stated location/date
overlaps a real case's. This is a heuristic — not a resolver of exactly which
event a claim describes — the match strength (edge weight) is what downstream
consumers (e.g. analytics/claim_verification.py) reason about, not a boolean.
"""

from __future__ import annotations

from datetime import date, timedelta

from ground_truth.schema import Claim, Event

from .edge import NarrativeEdge
from .graph_store import NarrativeGraph
from .node import NarrativeNode

# How far a claim's publish date may sit from a case's onset date and still
# plausibly be "about" that case. Wide, because reports lag confirmation by
# weeks (see Case 2: onset 2026-04-22, confirmed 2026-05-04).
DATE_WINDOW = timedelta(days=45)


def event_node(event: Event) -> NarrativeNode:
    timestamp = event.date_onset or event.date_confirmation
    location = ", ".join(
        filter(None, [event.location_admin2, event.location_admin1, event.location_country])
    ) or None
    return NarrativeNode(
        id=f"event:{event.gh_id}",
        kind="event",
        text=f"Case {event.gh_id} ({event.case_status}, {event.outcome or 'ongoing'})",
        timestamp=timestamp,
        location=location,
        metadata={"case_status": event.case_status, "outcome": event.outcome},
    )


def claim_node(claim: Claim) -> NarrativeNode:
    return NarrativeNode(
        id=f"claim:{claim.id}",
        kind="claim",
        text=claim.title,
        timestamp=claim.publish_date,
        location=claim.country,
        metadata={
            "media_name": claim.media_name,
            "is_verifiable_outbreak": claim.is_verifiable_outbreak,
            "total_cases_reported": claim.total_cases_reported,
        },
    )


def _event_location_tokens(event: Event) -> set[str]:
    fields = [
        event.location_country,
        event.location_admin1,
        event.location_admin2,
        event.ship_disembark_location,
        event.travel_from,
        event.travel_to,
    ]
    return {f.lower() for f in fields if f and f.lower() not in {"other*", "na"}}


def _claim_location_tokens(claim: Claim) -> set[str]:
    tokens = set(claim.outbreak_locations)
    if claim.country and claim.country.upper() != "MULTI-COUNTRY":
        tokens.add(claim.country)
    return {t.lower() for t in tokens}


def _location_overlap(event: Event, claim: Claim) -> float:
    event_tokens = _event_location_tokens(event)
    claim_tokens = _claim_location_tokens(claim)
    if not event_tokens or not claim_tokens:
        return 0.0
    hits = sum(
        1
        for e in event_tokens
        for c in claim_tokens
        if e in c or c in e
    )
    return min(1.0, hits / len(event_tokens))


def _date_overlap(event: Event, claim: Claim) -> float:
    anchor = event.date_onset or event.date_confirmation
    if not anchor or not claim.publish_date:
        return 0.0
    delta = abs((claim.publish_date - anchor).days)
    if delta > DATE_WINDOW.days:
        return 0.0
    return 1.0 - (delta / DATE_WINDOW.days)


def match_strength(event: Event, claim: Claim) -> float:
    """0..1 heuristic score for "this claim is plausibly reporting on this event"."""
    location_score = _location_overlap(event, claim)
    date_score = _date_overlap(event, claim)
    if location_score == 0.0 and date_score == 0.0:
        return 0.0
    # Location match is the stronger signal; date proximity alone (no location
    # match at all) is treated as weak corroborating evidence, not a match.
    return 0.7 * location_score + 0.3 * date_score


def build_graph(events: list[Event], claims: list[Claim], min_match: float = 0.2) -> NarrativeGraph:
    graph = NarrativeGraph()

    for event in events:
        graph.add_node(event_node(event))
    for claim in claims:
        graph.add_node(claim_node(claim))

    for claim in claims:
        for event in events:
            strength = match_strength(event, claim)
            if strength >= min_match:
                graph.add_edge(
                    NarrativeEdge(
                        source_id=f"claim:{claim.id}",
                        target_id=f"event:{event.gh_id}",
                        edge_type="reports_on",
                        weight=strength,
                    )
                )

    return graph
