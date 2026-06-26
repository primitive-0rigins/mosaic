"""
Agentic retrieval loop — the reasoning core of Mosaic.

Sidecar 2: Language model (e.g. qwen2.5:1.5b) — drives retrieval decisions.
           Decides: retrieve, validate, re-query, or answer.

The loop:
  1. Query arrives
  2. Agent retrieves candidate tiles from the hypergraph
  3. Agent evaluates: are these tiles sufficient? relevant? contradictory?
  4. If insufficient — reformulate query and re-retrieve
  5. If sufficient — synthesize answer from tiles
  6. Add new hyperedges to memory based on what was discovered

This is CRAG/Self-RAG style agentic retrieval — not a single vector lookup.
"""

from dataclasses import dataclass, field
from typing import Optional

from mosaic.hypergraph.graph import HyperGraph, HyperEdge
from mosaic.ingestion.tiler import Tile


@dataclass
class RetrievalResult:
    tiles: list[Tile]
    sufficient: bool
    confidence: float
    reason: str


@dataclass
class AgentState:
    query: str
    iterations: int = 0
    retrieved_tile_ids: list[str] = field(default_factory=list)
    answer: Optional[str] = None
    done: bool = False


MAX_ITERATIONS = 4


class MosaicAgent:
    """
    The Mosaic agentic retrieval loop.
    Uses a language sidecar to drive retrieval decisions.
    """

    def __init__(self, graph: HyperGraph, tile_store: dict[str, Tile], sidecar_model: str = "qwen2.5:0.5b"):
        self.graph = graph
        self.tile_store = tile_store  # tile_id -> Tile
        self.model = sidecar_model

    async def query(self, question: str) -> str:
        state = AgentState(query=question)

        while not state.done and state.iterations < MAX_ITERATIONS:
            state.iterations += 1

            # Step 1: retrieve candidate tiles
            candidates = self._retrieve(state.query, top_k=4)

            # Step 2: evaluate with language sidecar
            result = await self._evaluate(question, candidates, state)

            # Step 3: act on evaluation
            if result.sufficient:
                state.answer = await self._synthesize(question, result.tiles)
                state.done = True
                # Step 4: update hypergraph memory
                self._update_memory(result.tiles, question)
            else:
                # Reformulate and try again
                state.query = await self._reformulate(question, result.reason)
                state.retrieved_tile_ids.extend(t.tile_id for t in result.tiles)

        return state.answer or "Could not find sufficient evidence in memory."

    def _retrieve(self, query: str, top_k: int = 4) -> list[Tile]:
        """Retrieve tiles by cosine similarity to query embedding (stub)."""
        # Stub: return first top_k tiles. Replace with real vector search.
        tiles = list(self.tile_store.values())
        return tiles[:top_k]

    async def _evaluate(self, original_query: str, tiles: list[Tile], state: AgentState) -> RetrievalResult:
        """Ask the language sidecar: are these tiles sufficient to answer the query?"""
        import ollama
        client = ollama.AsyncClient()

        tile_descriptions = "\n".join(
            f"Tile {i+1} (id={t.tile_id}, page={t.page}, pos={t.index})"
            for i, t in enumerate(tiles)
        )

        prompt = f"""You are evaluating retrieved document tiles for a query.

Query: {original_query}

Retrieved tiles:
{tile_descriptions}

Are these tiles sufficient to answer the query? Reply with:
SUFFICIENT: <yes/no>
CONFIDENCE: <0.0-1.0>
REASON: <one sentence>"""

        response = await client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"]
        sufficient = "yes" in text.lower().split("sufficient:")[-1][:10]
        confidence = 0.8 if sufficient else 0.3
        reason = text.split("REASON:")[-1].strip() if "REASON:" in text else "unclear"

        return RetrievalResult(tiles=tiles, sufficient=sufficient, confidence=confidence, reason=reason)

    async def _synthesize(self, query: str, tiles: list[Tile]) -> str:
        """Synthesize a final answer from the retrieved tiles."""
        import ollama
        client = ollama.AsyncClient()

        response = await client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"Based on {len(tiles)} retrieved document tiles, answer: {query}"
            }]
        )
        return response["message"]["content"]

    async def _reformulate(self, original: str, reason: str) -> str:
        """Reformulate the query when retrieval was insufficient."""
        import ollama
        client = ollama.AsyncClient()

        response = await client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"The query '{original}' returned insufficient results because: {reason}\nRewrite the query to retrieve better results. Reply with only the new query."
            }]
        )
        return response["message"]["content"].strip()

    def _update_memory(self, tiles: list[Tile], claim: str):
        """Add a hyperedge connecting all tiles that jointly answered this query."""
        if len(tiles) < 2:
            return
        edge = HyperEdge.create(
            tile_ids=[t.tile_id for t in tiles],
            label="jointly_supports",
            claim=claim,
            confidence=0.9,
        )
        self.graph.add_edge(edge)
