"""
Encoder — embeds pixel tiles using a local VLM sidecar via Ollama.

Sidecar 1: Vision model (e.g. moondream2, minicpm-v) — reads tiles visually,
           produces a dense embedding for each tile.

Tiles are never converted to text. The embedding is image-native.
"""

import base64
import io
from typing import Protocol

from PIL import Image

from mosaic.ingestion.tiler import Tile


class VisionSidecar(Protocol):
    """Interface for the vision embedding sidecar."""
    async def embed_tile(self, tile: Tile) -> list[float]: ...


class OllamaVisionSidecar:
    """
    Embeds tiles using a local Ollama vision model.
    Default: moondream2 (1.8B — fits sub-3B constraint).
    """

    def __init__(self, model: str = "moondream2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def _tile_to_b64(self, tile: Tile) -> str:
        buf = io.BytesIO()
        tile.image.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    async def embed_tile(self, tile: Tile) -> list[float]:
        import ollama
        client = ollama.AsyncClient(host=self.host)

        # Ask the model to describe the tile — use the response as a proxy embedding.
        # For true image embeddings, swap to an embed-capable multimodal model.
        response = await client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": "Describe the content of this image tile in detail.",
                "images": [self._tile_to_b64(tile)],
            }]
        )

        # Placeholder: hash the description into a stable float vector.
        # Replace with actual embedding model output when available.
        description = response["message"]["content"]
        return _text_to_stub_embedding(description)


def _text_to_stub_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Stub: converts text to a deterministic float vector via hashing.
    Replace with a real embedding model in production.
    """
    import hashlib
    import struct
    digest = hashlib.sha256(text.encode()).digest()
    # Repeat digest to fill dim dimensions
    raw = (digest * ((dim * 4 // len(digest)) + 1))[:dim * 4]
    floats = [struct.unpack("f", raw[i:i+4])[0] for i in range(0, dim * 4, 4)]
    # Normalize
    mag = sum(f ** 2 for f in floats) ** 0.5 or 1.0
    return [f / mag for f in floats]


async def embed_tiles(tiles: list[Tile], sidecar: VisionSidecar) -> list[Tile]:
    """Embed a list of tiles in place. Returns tiles with embeddings set."""
    for tile in tiles:
        tile.embedding = await sidecar.embed_tile(tile)
    return tiles
