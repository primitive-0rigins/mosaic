from PIL import Image

from mosaic.agent.loop import MosaicAgent
from mosaic.embedding.encoder import embed_query_stub
from mosaic.hypergraph.graph import HyperGraph
from mosaic.ingestion.tiler import Tile


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


def test_agent_retrieve_uses_vector_similarity():
    store = {
        "first": make_tile("first", embed_query_stub("network mesh")),
        "target": make_tile("target", embed_query_stub("pixel memory")),
    }
    agent = MosaicAgent(HyperGraph(), store)

    results = agent._retrieve("pixel memory", top_k=1)

    assert [tile.tile_id for tile in results] == ["target"]
