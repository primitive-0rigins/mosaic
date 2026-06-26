from PIL import Image

from mosaic.cli import main
from mosaic.storage import JsonMemoryStore


def test_tile_command_reports_tiles(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (500, 448), "white").save(image_path)

    code = main(["tile", str(image_path)])

    output = capsys.readouterr().out
    assert code == 0
    assert "source: sample.png" in output
    assert "tiles: 2" in output
    assert "page 0: 2" in output


def test_tile_command_returns_error_for_missing_file(capsys):
    code = main(["tile", "missing.png"])

    output = capsys.readouterr().out
    assert code == 2
    assert "File not found: missing.png" in output


def test_ingest_command_saves_memory(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    store_path = tmp_path / "memory.json"
    tiles_dir = tmp_path / "tiles"
    Image.new("RGB", (500, 448), "white").save(image_path)

    code = main(
        [
            "ingest",
            str(image_path),
            "--store",
            str(store_path),
            "--tiles-dir",
            str(tiles_dir),
        ]
    )

    output = capsys.readouterr().out
    assert code == 0
    assert store_path.exists()
    assert len(list(tiles_dir.glob("tile-*.png"))) == 2
    assert "ingested: sample.png" in output
    assert "tiles added: 2" in output
    assert "memory nodes: 2" in output
    assert f"tiles dir: {tiles_dir}" in output


def test_memory_command_reports_summary(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    store_path = tmp_path / "memory.json"
    Image.new("RGB", (500, 448), "white").save(image_path)
    assert main(["ingest", str(image_path), "--store", str(store_path)]) == 0
    capsys.readouterr()

    code = main(["memory", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert code == 0
    assert f"store: {store_path}" in output
    assert "nodes: 2" in output
    assert "edges: 0" in output


def test_link_command_creates_hyperedge(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    store_path = tmp_path / "memory.json"
    Image.new("RGB", (500, 448), "white").save(image_path)
    assert main(["ingest", str(image_path), "--store", str(store_path)]) == 0
    capsys.readouterr()

    tile_ids = list(JsonMemoryStore(store_path).load().nodes())
    code = main(
        [
            "link",
            *tile_ids,
            "--store",
            str(store_path),
            "--label",
            "supports",
            "--claim",
            "same source image",
        ]
    )

    output = capsys.readouterr().out
    graph = JsonMemoryStore(store_path).load()
    assert code == 0
    assert graph.summary()["edges"] == 1
    assert "linked:" in output
    assert "label: supports" in output
    assert "claim: same source image" in output


def test_link_command_requires_multiple_tiles(tmp_path, capsys):
    store_path = tmp_path / "memory.json"

    code = main(["link", "tile-a", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert code == 2
    assert "Hyperedges must connect at least two tiles" in output


def test_show_command_reports_tile_and_edges(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    store_path = tmp_path / "memory.json"
    Image.new("RGB", (500, 448), "white").save(image_path)
    assert main(["ingest", str(image_path), "--store", str(store_path)]) == 0
    capsys.readouterr()

    tile_ids = list(JsonMemoryStore(store_path).load().nodes())
    assert main(
        [
            "link",
            *tile_ids,
            "--store",
            str(store_path),
            "--label",
            "supports",
            "--claim",
            "same source image",
        ]
    ) == 0
    capsys.readouterr()

    code = main(["show", tile_ids[0], "--store", str(store_path)])

    output = capsys.readouterr().out
    assert code == 0
    assert f"tile: {tile_ids[0]}" in output
    assert "source:" in output
    assert "tile path:" in output
    assert "edges: 1" in output
    assert "label=supports" in output
    assert "claim: same source image" in output


def test_show_command_reports_missing_tile(tmp_path, capsys):
    store_path = tmp_path / "memory.json"

    code = main(["show", "tile-missing", "--store", str(store_path)])

    output = capsys.readouterr().out
    assert code == 2
    assert "Tile not found: tile-missing" in output


def test_search_image_command_reports_visual_match(tmp_path, capsys):
    image_path = tmp_path / "sample.png"
    store_path = tmp_path / "memory.json"
    Image.new("RGB", (500, 448), "white").save(image_path)
    assert main(["ingest", str(image_path), "--store", str(store_path)]) == 0
    capsys.readouterr()

    code = main(["search-image", str(image_path), "--store", str(store_path), "--top-k", "1"])

    output = capsys.readouterr().out
    assert code == 0
    assert "1. tile-" in output
    assert "source=sample.png" in output
    assert "tile_path=" in output


def test_sidecars_command_reports_model_status(monkeypatch, capsys):
    monkeypatch.setattr(
        "mosaic.cli.check_sidecars",
        lambda: {"moondream2": True, "qwen2.5:0.5b": False},
    )

    code = main(["sidecars"])

    output = capsys.readouterr().out
    assert code == 1
    assert "moondream2: ok" in output
    assert "qwen2.5:0.5b: missing" in output
