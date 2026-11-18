#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261118 bounty.

The entry is a single image: an editorial front page, "The World in One
Day", summing up the world news of Wednesday 18 November 2026 in six
illustrated stories. The image ships in this repository as entry.png,
beside this file.

The grader runs this program twice in a sandbox with no network and a
read-only repository. All the program does is copy entry.png, byte for
byte, into the output directory, so both runs write identical bytes.
Paths are resolved from this file's own location, never from the
working directory, and nothing in the output directory is ever deleted
or cleaned.
"""

import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
CHUNK = 64 * 1024


def copy_image(source: Path, target: Path) -> int:
    """Copy source to target in chunks; return the number of bytes written."""
    written = 0
    with source.open("rb") as fin, target.open("wb") as fout:
        while True:
            block = fin.read(CHUNK)
            if not block:
                break
            fout.write(block)
            written += len(block)
    return written


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"entry image not found beside main.py: {SOURCE}")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    written = copy_image(SOURCE, out_dir / "entry.png")
    print(f"wrote {written} bytes to {out_dir / 'entry.png'}")


if __name__ == "__main__":
    main()
