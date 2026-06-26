"""JSON persistence for Mosaic hypergraph memory."""

import json
from pathlib import Path

from mosaic.hypergraph.graph import HyperGraph


class JsonMemoryStore:
    """Persist hypergraph memory to a local JSON file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> HyperGraph:
        """Load an existing graph, or return an empty graph when no store exists."""
        if not self.path.exists():
            return HyperGraph()
        with self.path.open("r", encoding="utf-8") as handle:
            return HyperGraph.from_dict(json.load(handle))

    def save(self, graph: HyperGraph) -> None:
        """Write a graph to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(graph.to_dict(), handle, indent=2, sort_keys=True)
            handle.write("\n")
