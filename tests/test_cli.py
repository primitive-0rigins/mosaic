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
