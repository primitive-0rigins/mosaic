from mosaic.hypergraph.graph import HyperEdge, HyperGraph
from mosaic.storage import JsonMemoryStore


def test_json_memory_store_round_trips_graph(tmp_path):
    graph = HyperGraph()
    graph.add_tile("tile-a", {"source": "placeholder.png", "page": 0})
    graph.add_tile("tile-b", {"source": "placeholder.png", "page": 0})
    graph.add_edge(HyperEdge.create(["tile-a", "tile-b"], "supports", claim="demo"))

    store = JsonMemoryStore(tmp_path / "memory.json")
    store.save(graph)

    loaded = store.load()

    assert loaded.summary()["nodes"] == 2
    assert loaded.summary()["edges"] == 1
    assert loaded.neighbors("tile-a") == ["tile-b"]


def test_json_memory_store_loads_empty_graph_when_missing(tmp_path):
    graph = JsonMemoryStore(tmp_path / "missing.json").load()

    assert graph.summary()["nodes"] == 0
    assert graph.summary()["edges"] == 0
