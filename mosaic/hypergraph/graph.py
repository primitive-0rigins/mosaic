"""
Hypergraph memory — the core of Mosaic.

Unlike a standard graph where edges connect exactly 2 nodes,
hyperedges connect ANY number of nodes simultaneously.

This matters because real evidence is n-ary:
  "Tile A, Tile C, and Tile F together establish claim X"
  cannot be represented by binary edges without losing meaning.

Structure:
  - Nodes = Tiles (pixel tiles with embeddings)
  - Hyperedges = named relationships between 2+ tiles
  - Labels = what the hyperedge means (supports, contradicts, elaborates, defines)
"""

from dataclasses import dataclass
from dataclasses import asdict
from typing import Optional
import uuid


@dataclass
class HyperEdge:
    """A relationship between two or more tiles."""
    edge_id: str
    tile_ids: list[str]        # the tiles this edge connects (n >= 2)
    label: str                 # what this relationship means
    confidence: float = 1.0    # 0.0 - 1.0
    claim: Optional[str] = None  # the claim this edge supports or represents

    @classmethod
    def create(cls, tile_ids: list[str], label: str, claim: str = None, confidence: float = 1.0) -> "HyperEdge":
        if len(tile_ids) < 2:
            raise ValueError("Hyperedges must connect at least two tiles")
        return cls(
            edge_id=str(uuid.uuid4())[:8],
            tile_ids=tile_ids,
            label=label,
            confidence=confidence,
            claim=claim,
        )


class HyperGraph:
    """
    The Mosaic memory hypergraph.
    Tiles accumulate as nodes. The agent adds hyperedges as it reasons.
    """

    def __init__(self):
        self._nodes: dict[str, dict] = {}       # tile_id -> tile metadata
        self._edges: dict[str, HyperEdge] = {}  # edge_id -> HyperEdge
        self._node_edges: dict[str, list[str]] = {}  # tile_id -> [edge_ids]

    def add_tile(self, tile_id: str, metadata: dict):
        """Register a tile as a node."""
        self._nodes[tile_id] = metadata
        if tile_id not in self._node_edges:
            self._node_edges[tile_id] = []

    def add_edge(self, edge: HyperEdge):
        """Add a hyperedge connecting multiple tiles."""
        if len(edge.tile_ids) < 2:
            raise ValueError("Hyperedges must connect at least two tiles")
        for tid in edge.tile_ids:
            if tid not in self._nodes:
                raise ValueError(f"Tile {tid} not in graph — add it first")
            self._node_edges[tid].append(edge.edge_id)
        self._edges[edge.edge_id] = edge

    def neighbors(self, tile_id: str) -> list[str]:
        """All tiles connected to this tile via any hyperedge."""
        connected = set()
        for eid in self._node_edges.get(tile_id, []):
            for tid in self._edges[eid].tile_ids:
                if tid != tile_id:
                    connected.add(tid)
        return list(connected)

    def edges_for(self, tile_id: str) -> list[HyperEdge]:
        """All hyperedges that include this tile."""
        return [self._edges[eid] for eid in self._node_edges.get(tile_id, [])]

    def cluster(self, tile_ids: list[str]) -> list[HyperEdge]:
        """Find hyperedges that span ALL of the given tiles."""
        result = []
        for edge in self._edges.values():
            if all(tid in edge.tile_ids for tid in tile_ids):
                result.append(edge)
        return result

    def nodes(self) -> dict[str, dict]:
        """Return a copy of tile node metadata."""
        return {tile_id: metadata.copy() for tile_id, metadata in self._nodes.items()}

    def edges(self) -> list[HyperEdge]:
        """Return all hyperedges."""
        return list(self._edges.values())

    def to_dict(self) -> dict:
        """Serialize the hypergraph to JSON-compatible data."""
        return {
            "nodes": self.nodes(),
            "edges": [asdict(edge) for edge in self.edges()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HyperGraph":
        """Load a hypergraph from JSON-compatible data."""
        graph = cls()
        for tile_id, metadata in data.get("nodes", {}).items():
            graph.add_tile(tile_id, metadata)
        for edge_data in data.get("edges", []):
            graph.add_edge(HyperEdge(**edge_data))
        return graph

    def summary(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "avg_degree": (
                sum(len(v) for v in self._node_edges.values()) / max(len(self._nodes), 1)
            ),
        }
