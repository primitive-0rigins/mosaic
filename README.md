# Mosaic

**Agentic pixel-hypergraph memory. Documents as tiles. Relationships as structure.**

> Documents become tiles. Tiles become nodes. Relationships become hyperedges.
> The agent decides what to retrieve, validates it, and builds memory as structure.

---

## Status

Mosaic is an early local-first research prototype. The working path today is:

1. Render an image or PDF into 448x448 pixel tiles
2. Store each tile as a hypergraph node
3. Persist the hypergraph to a local JSON memory store
4. Build a small pixel-derived visual vector for each tile
5. Save each tile as a PNG artifact
6. Retrieve visually similar tiles with `mosaic search-image`

The full agentic question-answering loop and VLM-grade semantic image embeddings are still
roadmap items. The prototype is intentionally small, but the implemented path is visual:
tiles are embedded from pixels, not parsed text.

---

## The Problem with Standard RAG

Standard RAG converts documents to text, chunks the text, embeds the chunks, and retrieves by similarity. It destroys everything visual in the process — tables, charts, spatial layout, color coding, cross-page relationships.

More critically: it retrieves once, blindly, and hopes the top-k results are right.

---

## How Mosaic Works

**Three layers. No text parsing.**

### Layer 1 — Pixel Tiles
Documents are rendered as images and sliced into 448×448 pixel tiles. The current prototype
stores a compact pixel-derived visual vector for each tile, plus the tile PNG itself. The
document is never parsed as text. A local VLM embedding path is planned, but not presented as
done.

### Layer 2 — Hypergraph Memory
Tiles are stored as nodes in a hypergraph. Unlike a standard knowledge graph where edges connect exactly 2 nodes, **hyperedges connect any number of nodes simultaneously**.

This matters because real evidence is n-ary:

> "The chart on page 3, the table on page 7, and the footnote on page 11 **together** establish this claim."

A binary graph cannot represent this without losing meaning. A hyperedge captures it natively.

### Layer 3 — Agentic Loop
The intended agentic loop is a local language model (qwen2.5:0.5b) driving retrieval decisions:

1. Retrieve candidate tiles
2. Evaluate: are these tiles sufficient? relevant? contradictory?
3. If not — reformulate the query and retrieve again (max 4 iterations)
4. If yes — synthesize an answer and add a hyperedge to memory

This layer is still roadmap. The current CLI proves the lower-level visual memory path first:
tile, store, persist, and retrieve visual evidence.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Agentic Loop          qwen2.5:0.5b                         │
│  retrieve → validate → re-query → answer → update memory    │
├─────────────────────────────────────────────────────────────┤
│  Hypergraph Memory                                          │
│  nodes = tiles    hyperedges = n-ary relationships          │
├─────────────────────────────────────────────────────────────┤
│  Pixel Ingestion       current: local pixel vectors          │
│  documents → 448×448 tiles → saved PNGs + vectors           │
└─────────────────────────────────────────────────────────────┘
```

---

## Sidecar Models (local, via Ollama)

| Role | Model | Size |
|------|-------|------|
| Vision | moondream2 | 1.8B |
| Language | qwen2.5:0.5b | 0.5B |

No cloud API. No model larger than 3B. Runs fully local.

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/primitive-0rigins/mosaic.git
cd mosaic

# Install dependencies
pip install -e .

# Pull sidecar models
ollama pull moondream2
ollama pull qwen2.5:0.5b

# Check sidecars are ready
python -c "from mosaic.sidecar.models import check_sidecars; print(check_sidecars())"
```

Try the current local workflow:

```bash
mosaic ingest path/to/document-or-image.png --store .mosaic/memory.json
mosaic memory --store .mosaic/memory.json
mosaic search-image path/to/query-image.png --store .mosaic/memory.json
```

`mosaic search-image` prints the stored tile path for each match, so the retrieved
evidence can be opened and inspected.

For development:

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

---

## Project Structure

```
mosaic/
├── mosaic/
│   ├── ingestion/      # render documents to pixel tiles
│   ├── embedding/      # vision sidecar tile encoding
│   ├── hypergraph/     # hypergraph memory structure
│   ├── agent/          # agentic retrieval loop
│   └── sidecar/        # sidecar model interfaces
├── docs/
│   └── architecture.md
├── tests/
└── pyproject.toml
```

---

## Architecture Decisions

| Concern | Decision |
|---------|----------|
| Document ingestion | Render to image tiles — never parse text |
| Tile size | 448×448 px — matches MoonViT/VLM input conventions |
| Memory structure | Hypergraph (n-ary edges) not standard graph (binary edges) |
| Retrieval strategy | Agentic loop — validate and re-retrieve, not single-pass |
| Vision sidecar | moondream2 (1.8B) — local, no cloud |
| Language sidecar | qwen2.5:0.5b (0.5B) — local, no cloud |
| Max iterations | 4 — balances quality vs. cost |

---

## Prior Art

| System | What it does | What's missing |
|--------|-------------|----------------|
| PixelRAG (Berkeley, 2025) | Pixel tile retrieval | No agentic loop, no hypergraph |
| HyperMem (arXiv 2604.08256) | Hypergraph agent memory | Text-only |
| VimRAG (Alibaba, arXiv 2602.12735) | Visual + graph memory | DAG not hypergraph, no agentic loop |
| Self-RAG / CRAG | Agentic retrieval | Text-only, no hypergraph |

Mosaic combines all three.

---

## Roadmap

- [x] Pixel tile ingestion
- [x] Persistent hypergraph node storage
- [x] Local pixel-derived visual vectors
- [x] Saved tile artifacts for inspection
- [x] Image-to-image tile retrieval
- [ ] Real vector store for tile retrieval (SQLite or DuckDB)
- [ ] True image embeddings via embed-capable VLM
- [ ] CLI — `mosaic query "<question>"`
- [ ] Agent evaluates retrieval and creates hyperedges from answers
- [ ] Multi-document hyperedges (cross-document evidence linking)
- [ ] Hypergraph visualization

---

## Built by

[Primitive Origin LLC](https://github.com/primitive-0rigins)
