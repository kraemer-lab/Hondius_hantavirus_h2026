"""
In-memory narrative graph store.

Deliberately dependency-free (no networkx) — this is a thin adjacency
structure, not a graph algorithms library. If/when real graph algorithms
(centrality, community detection) are needed, they can operate on the
`.nodes` / `.edges` here rather than this class growing to do everything.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from .edge import NarrativeEdge
from .node import NarrativeNode


class NarrativeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, NarrativeNode] = {}
        self.edges: list[NarrativeEdge] = []
        self._outgoing: dict[str, list[int]] = defaultdict(list)
        self._incoming: dict[str, list[int]] = defaultdict(list)

    def add_node(self, node: NarrativeNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: NarrativeEdge) -> None:
        idx = len(self.edges)
        self.edges.append(edge)
        self._outgoing[edge.source_id].append(idx)
        self._incoming[edge.target_id].append(idx)

    def edges_from(self, node_id: str) -> list[NarrativeEdge]:
        return [self.edges[i] for i in self._outgoing.get(node_id, [])]

    def edges_to(self, node_id: str) -> list[NarrativeEdge]:
        return [self.edges[i] for i in self._incoming.get(node_id, [])]

    def to_json(self, path: Path) -> None:
        payload = {
            "nodes": [
                {**asdict(n), "timestamp": n.timestamp.isoformat() if n.timestamp else None}
                for n in self.nodes.values()
            ],
            "edges": [asdict(e) for e in self.edges],
        }
        path.write_text(json.dumps(payload, indent=2, default=str))
