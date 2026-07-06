"""
Turns narrative_graph "reports_on" edges + the ground-truth line list into a
verdict per claim: is what this article reported consistent with what the
line list actually shows as of its publish date?

This is intentionally conservative — it flags directional mismatches
(overstated/understated/unlinked), it does not accuse an article of lying.
Early reporting is expected to lag or round; the line list itself is
continuously updated, so "known_total_as_of_publish" is itself provisional.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ground_truth.schema import Claim, Event
from narrative_graph.graph_store import NarrativeGraph

CONFIRMED_LIKE_STATUSES = {"confirmed", "probable"}

# Below this edge weight we don't trust the link enough to compare counts.
MATCH_WEIGHT_THRESHOLD = 0.5


@dataclass
class ClaimVerification:
    claim_id: str
    verdict: str  # "consistent" | "overstated" | "understated" | "unlinked" | "unverifiable"
    reported_total: int | None
    known_total_as_of_publish: int | None
    matched_event_ids: list[str] = field(default_factory=list)
    best_match_weight: float = 0.0


def _known_total_as_of(events: list[Event], as_of) -> int:
    count = 0
    for event in events:
        if event.case_status not in CONFIRMED_LIKE_STATUSES:
            continue
        anchor = event.date_onset or event.date_confirmation
        if as_of is None or anchor is None or anchor <= as_of:
            count += 1
    return count


def verify_claim(claim: Claim, events: list[Event], graph: NarrativeGraph) -> ClaimVerification:
    reported_total = claim.total_cases_reported or claim.cumulative_total

    if not claim.is_verifiable_outbreak or reported_total is None:
        return ClaimVerification(
            claim_id=claim.id,
            verdict="unverifiable",
            reported_total=reported_total,
            known_total_as_of_publish=None,
        )

    matched = [
        e for e in graph.edges_from(f"claim:{claim.id}")
        if e.edge_type == "reports_on" and e.weight >= MATCH_WEIGHT_THRESHOLD
    ]
    matched.sort(key=lambda e: -e.weight)

    if not matched:
        return ClaimVerification(
            claim_id=claim.id,
            verdict="unlinked",
            reported_total=reported_total,
            known_total_as_of_publish=None,
        )

    known_total = _known_total_as_of(events, claim.publish_date)

    if known_total == 0:
        verdict = "overstated" if reported_total > 0 else "consistent"
    elif reported_total > known_total * 1.5:
        verdict = "overstated"
    elif reported_total < known_total * 0.5:
        verdict = "understated"
    else:
        verdict = "consistent"

    return ClaimVerification(
        claim_id=claim.id,
        verdict=verdict,
        reported_total=reported_total,
        known_total_as_of_publish=known_total,
        matched_event_ids=[e.target_id for e in matched],
        best_match_weight=matched[0].weight,
    )


def verify_claims(claims: list[Claim], events: list[Event], graph: NarrativeGraph) -> list[ClaimVerification]:
    return [verify_claim(c, events, graph) for c in claims]
