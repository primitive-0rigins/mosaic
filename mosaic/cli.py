"""Command-line entry point for Mosaic."""

from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path

from mosaic.ingestion.tiler import tile_file
from mosaic.sidecar.models import check_sidecars


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="mosaic", description="Agentic pixel-hypergraph memory tools")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("sidecars", help="Check required local Ollama sidecar models")

    tile_parser = subcommands.add_parser("tile", help="Render a file into Mosaic pixel tiles")
    tile_parser.add_argument("path", help="Image or PDF file to tile")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "sidecars":
        return _sidecars()
    if args.command == "tile":
        return _tile(args)
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


if __name__ == "__main__":
    raise SystemExit(main())
