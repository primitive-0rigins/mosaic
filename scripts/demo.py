"""Run a self-contained Mosaic demo."""

from argparse import ArgumentParser
from pathlib import Path
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mosaic.cli import main as mosaic_main  # noqa: E402
from mosaic.storage import JsonMemoryStore  # noqa: E402


def main() -> int:
    parser = ArgumentParser(description="Run a self-contained Mosaic demo")
    parser.add_argument(
        "--output",
        default=".mosaic/demo",
        help="Directory for generated demo files",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "demo-document.png"
    store_path = output_dir / "memory.json"
    tiles_dir = output_dir / "tiles"
    report_path = output_dir / "report.html"

    if store_path.exists():
        store_path.unlink()

    _write_demo_image(image_path)

    print("== ingest ==")
    _run(
        [
            "ingest",
            str(image_path),
            "--store",
            str(store_path),
            "--tiles-dir",
            str(tiles_dir),
        ]
    )

    print("\n== visual search ==")
    _run(["search-image", str(image_path), "--store", str(store_path), "--top-k", "2"])

    tile_ids = list(JsonMemoryStore(store_path).load().nodes())[:2]
    if len(tile_ids) < 2:
        print("Demo needs at least two generated tiles.")
        return 1

    print("\n== link evidence ==")
    _run(
        [
            "link",
            *tile_ids,
            "--store",
            str(store_path),
            "--label",
            "supports",
            "--claim",
            "The generated chart and table are part of the same visual document.",
        ]
    )

    print("\n== inspect tile ==")
    _run(["show", tile_ids[0], "--store", str(store_path)])

    print("\n== write report ==")
    _run(["report", "--store", str(store_path), "--output", str(report_path)])

    print("\nDemo complete.")
    print(f"image: {image_path}")
    print(f"memory: {store_path}")
    print(f"report: {report_path}")
    return 0


def _run(argv: list[str]) -> None:
    code = mosaic_main(argv)
    if code != 0:
        raise SystemExit(code)


def _write_demo_image(path: Path) -> None:
    image = Image.new("RGB", (896, 448), "#f8fafc")
    draw = ImageDraw.Draw(image)

    draw.rectangle((28, 26, 420, 86), fill="#111827")
    draw.text((48, 46), "Mosaic Visual Memory Demo", fill="#ffffff")

    draw.rectangle((48, 126, 380, 362), outline="#2563eb", width=4)
    for i, height in enumerate([82, 138, 190, 116]):
        x0 = 82 + i * 70
        draw.rectangle((x0, 330 - height, x0 + 38, 330), fill="#2563eb")
    draw.text((82, 374), "pixel chart tile", fill="#111827")

    draw.rectangle((476, 42, 848, 384), outline="#059669", width=4)
    for row in range(5):
        y = 104 + row * 48
        draw.line((506, y, 818, y), fill="#059669", width=2)
    for col in range(4):
        x = 506 + col * 78
        draw.line((x, 80, x, 344), fill="#059669", width=2)
    draw.text((526, 56), "evidence table tile", fill="#111827")
    draw.rectangle((524, 124, 800, 156), fill="#d1fae5")
    draw.rectangle((524, 220, 800, 252), fill="#d1fae5")

    image.save(path)


if __name__ == "__main__":
    raise SystemExit(main())
