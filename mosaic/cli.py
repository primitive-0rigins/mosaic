"""Command-line entry point for Mosaic."""

from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path

from mosaic.hypergraph.graph import HyperGraph
from mosaic.ingestion.tiler import tile_file
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

    memory_parser = subcommands.add_parser("memory", help="Inspect a Mosaic memory store")
    memory_parser.add_argument(
        "--store",
        default=".mosaic/memory.json",
        help="Path to the JSON memory store",
    )

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
    _add_tiles(graph, tiles)
    store.save(graph)

    summary = graph.summary()
    print(f"ingested: {path.name}")
    print(f"tiles added: {len(tiles)}")
    print(f"memory nodes: {summary['nodes']}")
    print(f"memory edges: {summary['edges']}")
    print(f"store: {store.path}")
    return 0


def _add_tiles(graph: HyperGraph, tiles) -> None:
    for tile in tiles:
        graph.add_tile(
            tile.tile_id,
            {
                "source": tile.source,
                "page": tile.page,
                "index": tile.index,
                "width": tile.image.width,
                "height": tile.image.height,
                "embedding_dim": len(tile.embedding),
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


if __name__ == "__main__":
    raise SystemExit(main())
