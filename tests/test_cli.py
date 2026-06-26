from PIL import Image

from mosaic.cli import main


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
    Image.new("RGB", (500, 448), "white").save(image_path)

    code = main(["ingest", str(image_path), "--store", str(store_path)])

    output = capsys.readouterr().out
    assert code == 0
    assert store_path.exists()
    assert "ingested: sample.png" in output
    assert "tiles added: 2" in output
    assert "memory nodes: 2" in output


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
