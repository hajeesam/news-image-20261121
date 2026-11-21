#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- Saturday 21 November 2026.

Entry point for the make.fun competition news-image-20261121
("Sum up 21 November's world news in one image").

The finished one-page newspaper is bundled with this repository as
entry.png (1024x1024, palette-256 PNG). This script hands that file to
the grader: it copies entry.png into the output directory as
entry.png, then reads the copy back and verifies it is byte-identical
to the bundled image by comparing its SHA-256 fingerprint against the
expected digest recorded below.

Python 3, standard library only. No network access, no image
generation at run time -- the image is shipped with the repo.
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE_NAME = "entry.png"
IMAGE_PATH = HERE / IMAGE_NAME

# SHA-256 of the approved r2 draft image, as bundled in this repo.
EXPECTED_SHA256 = (
    "6f171d4ae07ba55d3b9d50439ab9ebab947ad3abeda9fdf8573a5a473ad994e8"
)
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(blob: bytes) -> tuple[int, int]:
    """Return (width, height) read from a PNG's IHDR chunk.

    Raises ValueError if the bytes are not a PNG, or if the IHDR
    chunk is missing or truncated.
    """
    if blob[:8] != PNG_SIGNATURE:
        raise ValueError(f"{IMAGE_NAME} does not start with the PNG signature")
    if len(blob) < 24:
        raise ValueError(f"{IMAGE_NAME} is too short to hold an IHDR chunk")
    if blob[12:16] != b"IHDR":
        raise ValueError(f"{IMAGE_NAME} has no IHDR chunk where one belongs")
    width = int.from_bytes(blob[16:20], byteorder="big")
    height = int.from_bytes(blob[20:24], byteorder="big")
    return width, height


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "./output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    blob = IMAGE_PATH.read_bytes()

    width, height = png_size(blob)
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        print(
            f"error: {IMAGE_NAME} is {width}x{height}, "
            f"but the entry must be {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}",
            file=sys.stderr,
        )
        return 1

    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA256:
        print(
            f"error: {IMAGE_NAME} sha256 {digest} does not match "
            f"the expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1

    dest = out_dir / "entry.png"
    dest.write_bytes(blob)

    # Read the copy back off disk and prove it is the same image:
    # same dimensions, same bytes, same SHA-256 fingerprint.
    written = dest.read_bytes()
    out_width, out_height = png_size(written)
    if out_width != EXPECTED_WIDTH or out_height != EXPECTED_HEIGHT:
        print(
            f"error: written file is {out_width}x{out_height}, "
            f"but the entry must be {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}",
            file=sys.stderr,
        )
        return 1
    if written != blob:
        print(
            "error: written file differs from the bundled entry image",
            file=sys.stderr,
        )
        return 1
    written_digest = hashlib.sha256(written).hexdigest()
    if written_digest != EXPECTED_SHA256:
        print(
            f"error: written file sha256 {written_digest} does not match "
            f"the expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1

    print(f"wrote {dest} ({len(written)} bytes, {out_width}x{out_height})")
    print(f"sha256: {written_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
