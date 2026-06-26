import subprocess
import sys


def test_demo_script_runs_end_to_end(tmp_path):
    output_dir = tmp_path / "demo"

    result = subprocess.run(
        [sys.executable, "scripts/demo.py", "--output", str(output_dir)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (output_dir / "demo-document.png").exists()
    assert (output_dir / "memory.json").exists()
    assert (output_dir / "report.html").exists()
    assert "Demo complete." in result.stdout
    assert "Mosaic Memory Report" in (output_dir / "report.html").read_text(encoding="utf-8")
