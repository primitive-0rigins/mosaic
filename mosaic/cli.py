"""Command-line entry point for Mosaic."""

from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path

from mosaic.embedding.image_features import embed_image_pixels
from mosaic.hypergraph.graph import HyperGraph
from mosaic.ingestion.tiler import tile_file
from mosaic.retrieval.vector import cosine_similarity
from mosaic.sidecar.models import check_sidecars
from mosaic.storage import JsonMemoryStore


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="mosaic", description="Agentic pixel-hypergraph memory tools")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("sidecars", help="Check required local Ollama sidecar models")

    tile_parser = subcommands.add_parser("tile", help="Render a file into Mosaic pixel tiles")
    tile_parser.add_argument("path", help="Image or PDF file to tile")

    ingest_parser = subcommands.add_parser("ingest", help="Tile a file and save it into memory")
    ingest_parser.add_argument("path", help="Image or PDF file to ingest")
    ingest_parser.add_argument(
        "--store",
        default=".mosaic/memory.json",
        help="Path to the JSON memory store",
    )
    ingest_parser.add_argument(
        "--tiles-dir",
        help="Directory for saved tile PNG artifacts. Defaults to <store parent>/tiles",
    )

    memory_parser = subcommands.add_parser("memory", help="Inspect a Mosaic memory store")
    memory_parser.add_argument(
        "--store",
        default=".mosaic/memory.json",
        help="Path to the JSON memory store",
    )

    image_query_parser = subcommands.add_parser(
        "search-image",
        help="Retrieve visually similar tiles from memory",
    )
    image_query_parser.add_argument("path", help="Image file to search with")
    image_query_parser.add_argument(
        "--store",
        default=".mosaic/memory.json",
        help="Path to the JSON memory store",
    )
    image_query_parser.add_argument("--top-k", type=int, default=4, help="Number of tiles to return")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "sidecars":
        return _sidecars()
    if args.command == "tile":
        return _tile(args)
    if args.command == "ingest":
        return _ingest(args)
    if args.command == "memory":
        return _memory(args)
    if args.command == "search-image":
        return _search_image(args)
    raise ValueError(f"Unsupported command: {args.command}")


def _sidecars() -> int:
    statuses = check_sidecars()
    for model, available in statuses.items():
        state = "ok" if available else "missing"
        print(f"{model}: {state}")
    return 0 if all(statuses.values()) else 1


def _tile(args: Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    tiles = tile_file(str(path))
    pages = Counter(tile.page for tile in tiles)

    print(f"source: {path.name}")
    print(f"tiles: {len(tiles)}")
    for page, count in sorted(pages.items()):
        print(f"page {page}: {count}")
    return 0


def _ingest(args: Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    store = JsonMemoryStore(args.store)
    graph = store.load()
    tiles = tile_file(str(path))
    tiles_dir = Path(args.tiles_dir) if args.tiles_dir else store.path.parent / "tiles"
    _add_tiles(graph, tiles, tiles_dir)
    store.save(graph)

    summary = graph.summary()
    print(f"ingested: {path.name}")
    print(f"tiles added: {len(tiles)}")
    print(f"memory nodes: {summary['nodes']}")
    print(f"memory edges: {summary['edges']}")
    print(f"store: {store.path}")
    print(f"tiles dir: {tiles_dir}")
    return 0


def _add_tiles(graph: HyperGraph, tiles, tiles_dir: Path) -> None:
    tiles_dir.mkdir(parents=True, exist_ok=True)
    for tile in tiles:
        tile_path = tiles_dir / f"{tile.tile_id}.png"
        tile.image.save(tile_path)
        graph.add_tile(
            tile.tile_id,
            {
                "source": tile.source,
                "page": tile.page,
                "index": tile.index,
                "tile_path": str(tile_path),
                "width": tile.image.width,
                "height": tile.image.height,
                "embedding_dim": len(tile.embedding),
                "visual_embedding": embed_image_pixels(tile.image),
            },
        )


def _memory(args: Namespace) -> int:
    store = JsonMemoryStore(args.store)
    graph = store.load()
    summary = graph.summary()

    print(f"store: {store.path}")
    print(f"nodes: {summary['nodes']}")
    print(f"edges: {summary['edges']}")
    print(f"avg degree: {summary['avg_degree']:.2f}")
    return 0


def _search_image(args: Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    from PIL import Image

    query_embedding = embed_image_pixels(Image.open(path).convert("RGB"))
    graph = JsonMemoryStore(args.store).load()
    results = _search_visual_nodes(graph.nodes(), query_embedding, top_k=args.top_k)
    if not results:
        print("No visual tiles found in memory.")
        return 1

    for rank, (tile_id, score, metadata) in enumerate(results, start=1):
        tile_path = metadata.get("tile_path", "")
        tile_path_part = f" tile_path={tile_path}" if tile_path else ""
        print(
            f"{rank}. {tile_id} score={score:.3f} "
            f"source={Path(metadata['source']).name} page={metadata['page']} index={metadata['index']}"
            f"{tile_path_part}"
        )
    return 0


def _search_visual_nodes(
    nodes: dict[str, dict],
    query_embedding: list[float],
    top_k: int,
) -> list[tuple[str, float, dict]]:
    if top_k <= 0:
        return []

    scored = []
    for tile_id, metadata in nodes.items():
        embedding = metadata.get("visual_embedding", [])
        if embedding:
            scored.append((tile_id, cosine_similarity(query_embedding, embedding), metadata))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    raise SystemExit(main())
