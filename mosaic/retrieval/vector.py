"""In-memory vector retrieval over embedded Mosaic tiles."""

from dataclasses import dataclass

from mosaic.embedding.encoder import embed_query_stub
from mosaic.ingestion.tiler import Tile


@dataclass(frozen=True)
class SearchResult:
    """A tile returned from vector search with its similarity score."""

    tile: Tile
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for two vectors."""
    if not left or not right:
        return 0.0

    size = min(len(left), len(right))
    dot = sum(left[i] * right[i] for i in range(size))
    left_mag = sum(value * value for value in left[:size]) ** 0.5
    right_mag = sum(value * value for value in right[:size]) ** 0.5
    if left_mag == 0.0 or right_mag == 0.0:
        return 0.0

    return dot / (left_mag * right_mag)


class VectorIndex:
    """
    Query-time vector index for tiles already held in memory.

    The index does not own tile data. It reads from the provided tile store so the
    hypergraph and tile store remain the memory source of truth.
    """

    def __init__(self, tile_store: dict[str, Tile]):
        self.tile_store = tile_store

    def search(self, query: str, top_k: int = 4) -> list[SearchResult]:
        """Rank embedded tiles by similarity to a deterministic query embedding."""
        if top_k <= 0:
            return []

        query_embedding = embed_query_stub(query)
        results = [
            SearchResult(tile=tile, score=cosine_similarity(query_embedding, tile.embedding))
            for tile in self.tile_store.values()
            if tile.embedding
        ]
        results.sort(key=lambda result: result.score, reverse=True)
        return results[:top_k]
