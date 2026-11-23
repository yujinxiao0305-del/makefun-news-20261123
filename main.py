#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""make.fun entry: one image summing up 23 November 2026 world news.

Standard library only. The picture itself was drawn ahead of time by
build_image.py and is carried in entry_data.py as base64 text; this
program simply decodes those bytes and writes them to the output path,
so two runs always produce exactly the same file.
"""

import base64
import os
import sys

# The grading sandbox starts this program as `python3 -P -s /bot/main.py`
# from an unrelated working directory. -P (safe_path) keeps the script's
# own folder off sys.path, so put it back explicitly before importing the
# sibling module; never rely on the current directory for anything.
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from entry_data import PNG_B64


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(out_dir, "entry.png")


def main():
    path = output_path()
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    image_bytes = base64.b64decode(PNG_B64)
    with open(path, "wb") as fh:
        fh.write(image_bytes)
    print("wrote", path, len(image_bytes), "bytes")


if __name__ == "__main__":
    main()
