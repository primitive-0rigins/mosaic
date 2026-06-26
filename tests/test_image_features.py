from PIL import Image

from mosaic.embedding.image_features import embed_image_pixels
from mosaic.retrieval.vector import cosine_similarity


def test_embed_image_pixels_returns_normalized_vector():
    embedding = embed_image_pixels(Image.new("RGB", (448, 448), "white"))

    magnitude = sum(value * value for value in embedding) ** 0.5
    assert round(magnitude, 6) == 1.0


def test_embed_image_pixels_separates_different_images():
    white = embed_image_pixels(Image.new("RGB", (448, 448), "white"))
    black = embed_image_pixels(Image.new("RGB", (448, 448), "black"))

    assert cosine_similarity(white, black) < 0.5
