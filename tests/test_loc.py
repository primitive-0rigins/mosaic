from pathlib import Path

from scripts.loc import count_lines


def test_count_lines_counts_multiple_files(tmp_path):
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("a\nb\n", encoding="utf-8")
    second.write_text("c\n", encoding="utf-8")

    assert count_lines([Path(first), Path(second)]) == 3
