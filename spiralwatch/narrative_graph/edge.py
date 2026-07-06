"""An edge in the narrative graph."""

from __future__ import annotations

from dataclasses import dataclass

# "reports_on"    claim -> event, this claim is (heuristically) about this event
# "cites"         claim -> source
# "amplifies"     post -> claim/event (added once scrapers/analytics exist)
# "contradicts"   claim -> claim, conflicting reports about the same event
# "derives_from"  claim -> claim, near-duplicate/syndicated content
EdgeType = str


@dataclass
class NarrativeEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float
    evidence: str | None = None
