import shutil
import subprocess
import sys

import pytest


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is not installed")
def test_demo_video_script_writes_mp4(tmp_path):
    demo_dir = tmp_path / "demo"
    video_path = demo_dir / "demo.mp4"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/demo_video.py",
            "--demo-output",
            str(demo_dir),
            "--output",
            str(video_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert video_path.exists()
    assert video_path.stat().st_size > 0
    assert f"video: {video_path}" in result.stdout
