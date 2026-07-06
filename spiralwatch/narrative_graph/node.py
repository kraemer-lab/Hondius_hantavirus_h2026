"""A node in the narrative graph — anything that can be linked: an event,
a claim, a source, or (later) a social post/account/topic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class NarrativeNode:
    id: str
    kind: str  # "event" | "claim" | "source" | "post" | "account" | "topic"
    text: str | None
    timestamp: date | None
    location: str | None
    metadata: dict = field(default_factory=dict)
