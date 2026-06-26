from PIL import Image

from mosaic.embedding.encoder import embed_query_stub
from mosaic.ingestion.tiler import Tile
from mosaic.retrieval.vector import VectorIndex, cosine_similarity


def make_tile(tile_id: str, embedding: list[float]) -> Tile:
    tile = Tile(
        tile_id=tile_id,
        source="placeholder.png",
        page=0,
        index=0,
        image=Image.new("RGB", (448, 448), "white"),
    )
    tile.embedding = embedding
    return tile


def test_cosine_similarity_handles_empty_vectors():
    assert cosine_similarity([], [1.0]) == 0.0
    assert cosine_similarity([1.0], []) == 0.0


def test_cosine_similarity_ranks_identical_vector_highest():
    query_embedding = embed_query_stub("invoice total")
    other_embedding = embed_query_stub("unrelated diagram")

    store = {
        "other": make_tile("other", other_embedding),
        "match": make_tile("match", query_embedding),
    }

    results = VectorIndex(store).search("invoice total", top_k=2)

    assert [result.tile.tile_id for result in results] == ["match", "other"]
    assert results[0].score > results[1].score


def test_vector_index_skips_unembedded_tiles():
    store = {
        "empty": make_tile("empty", []),
        "match": make_tile("match", embed_query_stub("chart")),
    }

    results = VectorIndex(store).search("chart", top_k=4)

    assert [result.tile.tile_id for result in results] == ["match"]
