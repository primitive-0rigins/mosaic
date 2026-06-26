"""
Tiler — converts documents into fixed-size screenshot tiles.

Documents are never parsed as text. They are rendered as images and
sliced into tiles. Each tile is the atomic unit of memory in Mosaic.
"""

from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
import hashlib


TILE_SIZE = (448, 448)


@dataclass
class Tile:
    """A single pixel tile — the atomic memory unit."""
    tile_id: str
    source: str          # path or URL of the original document
    page: int
    index: int           # tile position on the page
    image: Image.Image
    embedding: list[float] = field(default_factory=list)

    @classmethod
    def from_image(cls, image: Image.Image, source: str, page: int, index: int) -> "Tile":
        digest = hashlib.sha256(f"{source}:{page}:{index}".encode()).hexdigest()[:12]
        return cls(
            tile_id=f"tile-{digest}",
            source=source,
            page=page,
            index=index,
            image=image,
        )


def tile_image(image: Image.Image, source: str, page: int = 0) -> list[Tile]:
    """Slice a PIL image into fixed-size tiles."""
    tiles = []
    w, h = image.size
    tile_w, tile_h = TILE_SIZE
    idx = 0

    for y in range(0, h, tile_h):
        for x in range(0, w, tile_w):
            crop = image.crop((x, y, min(x + tile_w, w), min(y + tile_h, h)))
            # Pad to full tile size so all tiles are uniform
            padded = Image.new("RGB", TILE_SIZE, (255, 255, 255))
            padded.paste(crop, (0, 0))
            tiles.append(Tile.from_image(padded, source, page, idx))
            idx += 1

    return tiles


def tile_pdf(path: str) -> list[Tile]:
    """Render a PDF to tiles. Requires 'pdf2image' and poppler."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise RuntimeError("pdf2image required for PDF ingestion: pip install pdf2image")

    tiles = []
    pages = convert_from_path(path, dpi=150)
    for page_num, page_image in enumerate(pages):
        tiles.extend(tile_image(page_image, source=path, page=page_num))
    return tiles


def tile_file(path: str) -> list[Tile]:
    """Auto-detect file type and tile it."""
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        return tile_pdf(path)
    else:
        image = Image.open(path).convert("RGB")
        return tile_image(image, source=path)
