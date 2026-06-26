"""Create a short MP4 walkthrough from the Mosaic demo output."""

from argparse import ArgumentParser
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mosaic.storage import JsonMemoryStore  # noqa: E402


WIDTH = 1280
HEIGHT = 720


def main() -> int:
    parser = ArgumentParser(description="Create a Mosaic demo walkthrough MP4")
    parser.add_argument(
        "--demo-output",
        default=".mosaic/demo",
        help="Directory created by scripts/demo.py",
    )
    parser.add_argument(
        "--output",
        default=".mosaic/demo/demo.mp4",
        help="Path for the MP4 video",
    )
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print("ffmpeg is required to write MP4 video.")
        return 2

    demo_dir = Path(args.demo_output)
    _ensure_demo(demo_dir)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = output_path.parent / "video-frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    frames = _write_frames(demo_dir, frames_dir)
    _write_video(ffmpeg, frames_dir, len(frames), output_path)
    print(f"video: {output_path}")
    return 0


def _ensure_demo(demo_dir: Path) -> None:
    required = [
        demo_dir / "demo-document.png",
        demo_dir / "memory.json",
        demo_dir / "report.html",
    ]
    if all(path.exists() for path in required):
        return
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "demo.py"), "--output", str(demo_dir)],
        check=True,
    )


def _write_frames(demo_dir: Path, frames_dir: Path) -> list[Path]:
    graph = JsonMemoryStore(demo_dir / "memory.json").load()
    nodes = graph.nodes()
    summary = graph.summary()
    tile_paths = [metadata.get("tile_path") for metadata in nodes.values()]
    tile_paths = [Path(path) for path in tile_paths if path]

    frames = [
        _title_frame("Mosaic", "Pixel tiles become hypergraph memory"),
        _image_frame(demo_dir / "demo-document.png", "1. Generate a visual document"),
        _tile_grid_frame(tile_paths, "2. Ingest into saved pixel tiles"),
        _summary_frame(summary, "3. Search, link, and inspect evidence"),
        _report_frame(demo_dir / "report.html", "4. Export a static report"),
    ]

    paths = []
    for index, frame in enumerate(frames):
        path = frames_dir / f"frame_{index:03d}.png"
        frame.save(path)
        paths.append(path)
    return paths


def _write_video(ffmpeg: str, frames_dir: Path, frame_count: int, output_path: Path) -> None:
    command = [
        ffmpeg,
        "-y",
        "-framerate",
        "0.5",
        "-i",
        str(frames_dir / "frame_%03d.png"),
        "-frames:v",
        str(frame_count),
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def _base_frame(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f6f7f9")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 88), fill="#111827")
    draw.text((44, 32), title, fill="#ffffff")
    return image, draw


def _title_frame(title: str, subtitle: str) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#111827")
    draw = ImageDraw.Draw(image)
    draw.text((84, 262), title, fill="#ffffff")
    draw.text((84, 318), subtitle, fill="#d1d5db")
    draw.rectangle((84, 388, 492, 430), fill="#2563eb")
    draw.text((108, 400), "local visual memory demo", fill="#ffffff")
    return image


def _image_frame(path: Path, title: str) -> Image.Image:
    image, draw = _base_frame(title)
    source = Image.open(path).convert("RGB")
    source.thumbnail((1100, 540))
    x = (WIDTH - source.width) // 2
    image.paste(source, (x, 126))
    draw.text((44, 654), str(path), fill="#374151")
    return image


def _tile_grid_frame(tile_paths: list[Path], title: str) -> Image.Image:
    image, draw = _base_frame(title)
    x = 88
    y = 140
    for path in tile_paths[:4]:
        tile = Image.open(path).convert("RGB")
        tile.thumbnail((240, 240))
        image.paste(tile, (x, y))
        draw.rectangle((x, y, x + 240, y + 240), outline="#d6dde8", width=2)
        draw.text((x, y + 258), path.name, fill="#374151")
        x += 284
    draw.text((88, 520), "Each tile is stored as a graph node with a pixel-derived vector.", fill="#111827")
    return image


def _summary_frame(summary: dict, title: str) -> Image.Image:
    image, draw = _base_frame(title)
    stats = [
        ("Tiles", str(summary["nodes"])),
        ("Hyperedges", str(summary["edges"])),
        ("Avg degree", f"{summary['avg_degree']:.2f}"),
    ]
    for index, (label, value) in enumerate(stats):
        x = 110 + index * 360
        draw.rectangle((x, 190, x + 270, 390), fill="#ffffff", outline="#d6dde8", width=2)
        draw.text((x + 34, 232), label, fill="#586372")
        draw.text((x + 34, 292), value, fill="#111827")
    draw.text((110, 500), "The demo links two visual tiles into one persisted hyperedge.", fill="#111827")
    return image


def _report_frame(path: Path, title: str) -> Image.Image:
    image, draw = _base_frame(title)
    draw.rectangle((120, 160, 1160, 520), fill="#ffffff", outline="#d6dde8", width=2)
    draw.text((164, 212), "Mosaic Memory Report", fill="#111827")
    draw.text((164, 282), "Stored tile thumbnails", fill="#374151")
    draw.text((164, 334), "Hyperedge labels and claims", fill="#374151")
    draw.text((164, 386), "Evidence paths for review", fill="#374151")
    draw.text((120, 580), str(path), fill="#374151")
    return image


if __name__ == "__main__":
    raise SystemExit(main())
