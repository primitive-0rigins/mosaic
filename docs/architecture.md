# Mosaic Architecture

## Core Idea

Standard RAG converts documents to text, chunks the text, embeds the chunks as vectors, and retrieves by similarity. It destroys visual structure — tables, charts, spatial layout, color coding — in the process.

Mosaic never converts documents to text. Documents become **pixel tiles**. Tiles become
**nodes in a hypergraph**. The current prototype can ingest, persist, and visually retrieve
tiles. The intended agentic loop will decide what to retrieve, validate it, and build memory
as structure.

---

## Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — Agentic Loop                                     │
│  Sidecar 2: qwen2.5:0.5b                                    │
│  Roadmap: retrieve → validate → re-query → answer           │
│  Roadmap: update memory after each successful query          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2 — Hypergraph Memory                                │
│  Nodes = tiles. Hyperedges = n-ary relationships.           │
│  "Tiles A, C, F together support claim X"                   │
│  Unlike standard graphs, edges span any number of nodes.    │
├─────────────────────────────────────────────────────────────┤
│  Layer 1 — Pixel Tile Ingestion + Visual Vectors            │
│  Current: compact pixel-derived vectors + saved tile PNGs   │
│  Documents rendered as images → sliced into 448x448 tiles   │
│  Each tile is represented visually — never parsed as text   │
└─────────────────────────────────────────────────────────────┘
```

---

## Why Hypergraph (not a standard graph)?

A standard knowledge graph uses binary edges — each edge connects exactly 2 nodes.

Real evidence is n-ary. Example:

> A chart on page 3, a footnote on page 11, and a table on page 7 **together** establish a financial claim.

A binary graph forces you to decompose this into pairwise edges and lose the joint meaning. A hyperedge connects all three at once, preserving the n-ary relationship.

This is the key structural difference between Mosaic and VimRAG (Alibaba, 2026), which uses a DAG (binary edges, no cycles).

---

## Intended Agentic Loop (CRAG/Self-RAG Pattern)

```
Query arrives
    │
    ▼
Retrieve candidate tiles (vector similarity)
    │
    ▼
Sidecar 2 evaluates: sufficient? relevant? contradictory?
    │
    ├── Yes ──► Synthesize answer
    │                │
    │           Update hypergraph memory
    │           (new hyperedge connecting the tiles that answered)
    │
    └── No ───► Reformulate query
                    │
                    └──► Retrieve again (max 4 iterations)
```

---

This loop is not the current CLI path yet. The working path today is image/PDF tiling, JSON
hypergraph persistence, saved tile artifacts, and image-to-image tile retrieval.

---

## Sidecar Models

| Role | Model | Size | Purpose |
|------|-------|------|---------|
| Vision | moondream2 | 1.8B | Roadmap VLM path for tile understanding |
| Language | qwen2.5:0.5b | 0.5B | Roadmap agentic loop decisions |

Both run locally via Ollama. No cloud API. No model larger than 3B.

---

## What Survives That Text Parsers Destroy

- Tables with merged cells
- Charts with axis labels and color coding
- Form layouts and spatial relationships
- Mathematical notation rendered as images
- Visual hierarchy (headers, callouts, sidebars)
- Cross-page evidence that only makes sense seen together

---

## Prior Art (what Mosaic builds on)

| System | Contribution | Gap |
|--------|-------------|-----|
| PixelRAG (Berkeley, 2025) | Pixel tile retrieval | No agentic loop, no hypergraph |
| HyperMem (arXiv 2604.08256) | Hypergraph agent memory | Text-only |
| VimRAG (Alibaba, arXiv 2602.12735) | Visual + graph memory | DAG not hypergraph, no agentic loop |
| Self-RAG / CRAG | Agentic retrieval patterns | Text-only, no hypergraph |

Mosaic is the first system to combine all three.
