"""Small local image embeddings for prototype visual retrieval."""

from PIL import Image


def embed_image_pixels(image: Image.Image, size: tuple[int, int] = (16, 16)) -> list[float]:
    """
    Embed an image directly from pixels.

    This is intentionally small and local. It is not a semantic vision model, but it gives
    Mosaic a real visual vector path before the Ollama VLM embedding path is hardened.
    """
    grayscale = image.convert("L").resize(size)
    pixels = [value / 255.0 for value in _pixel_values(grayscale)]
    rgb = image.convert("RGB").resize((1, 1)).getpixel((0, 0))
    color = [channel / 255.0 for channel in rgb]
    vector = pixels + color
    return _normalize(vector)


def _normalize(vector: list[float]) -> list[float]:
    magnitude = sum(value * value for value in vector) ** 0.5
    if magnitude == 0.0:
        return vector
    return [value / magnitude for value in vector]


def _pixel_values(image: Image.Image):
    if hasattr(image, "get_flattened_data"):
        return image.get_flattened_data()
    return image.getdata()
