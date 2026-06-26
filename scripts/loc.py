"""Count Mosaic Python lines of code."""

from pathlib import Path


ROOTS = (Path("mosaic"), Path("tests"))


def python_files() -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def count_lines(paths: list[Path]) -> int:
    return sum(len(path.read_text(encoding="utf-8").splitlines()) for path in paths)


def main() -> int:
    files = python_files()
    total = count_lines(files)
    print(f"python files: {len(files)}")
    print(f"python lines: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
