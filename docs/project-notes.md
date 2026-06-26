# Mosaic Project Notes

## Portfolio Role

Mosaic demonstrates visual AI memory architecture: documents are treated as pixels first,
stored as inspectable tile artifacts, retrieved by visual similarity, and linked through
hypergraph relationships.

## What Works

- Image/PDF tiling into 448x448 visual tiles
- Pixel-derived local visual vectors
- JSON hypergraph memory store
- Image-to-image tile search
- Manual multi-tile hyperedge creation
- Tile inspection CLI
- Static HTML memory report
- Runnable demo and generated MP4 walkthrough

## Key Design Choices

- **Visual-first ingestion:** the prototype does not parse documents into text chunks.
- **Hypergraph memory:** evidence can be represented as n-ary relationships, not only pairs.
- **Inspectable artifacts:** every retrieved tile can point back to a saved PNG.
- **Small MVP:** the project proves the visual memory path before adding semantic VLM embeddings.

## Roadmap Boundary

Mosaic does not yet provide full natural-language question answering, agent-created
hyperedges, a production vector database, or VLM-grade semantic image embeddings. Those are
intentionally documented as roadmap items.

## Proof Path

```bash
python scripts/demo.py --output .mosaic/demo
python scripts/demo_video.py --demo-output .mosaic/demo --output .mosaic/demo/demo.mp4
```
