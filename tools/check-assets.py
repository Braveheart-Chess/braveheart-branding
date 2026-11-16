"""Check that every published image is where it should be, at its size.

Other repositories link to these files by path (the engine's README shows
logo.png from this repository's main branch), so a renamed, resized or
flattened image breaks them. This checks each one against the list below,
which matches the table in README.md, and fails on an image it does not list.

Standard library only: python3 tools/check-assets.py
"""

import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", ".venv"}
IMAGE_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg"}

# path: (width, height, transparent background)
PNGS = {
    "logo.png": (1024, 1024, True),
    "logo-small.png": (512, 512, True),
    "avatar.png": (1024, 1024, False),
    "social-preview.png": (1280, 640, False),
    "favicon-32.png": (32, 32, True),
    "favicon-64.png": (64, 64, True),
    "favicon-180.png": (180, 180, True),
    "banner-light.png": (1280, 360, True),
    "banner-dark.png": (1280, 360, True),
}
SVGS = {"logo.svg": (1024, 1024), "logo-small.svg": (1024, 1024)}
JPEGS = {"original/braveheart-logo-big.jpg", "original/braveheart-logo-small.jpg"}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# PNG colour types with an alpha channel: greyscale+alpha and RGBA.
ALPHA_COLOUR_TYPES = {4, 6}


def check_png(path, width, height, transparent):
    data = path.read_bytes()[:33]
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        return ["not a PNG"]
    w, h, _depth, colour_type = struct.unpack(">IIBB", data[16:26])
    errors = []
    if (w, h) != (width, height):
        errors.append(f"is {w}x{h}, expected {width}x{height}")
    if transparent and colour_type not in ALPHA_COLOUR_TYPES:
        errors.append("has no alpha channel; it must have a transparent background")
    return errors


def check_svg(path, width, height):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as err:
        return [f"is not valid XML ({err})"]
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        return [f"root element is {root.tag}, expected an SVG <svg>"]
    size = (root.get("width"), root.get("height"))
    if size != (str(width), str(height)):
        return [f"declares {size[0]}x{size[1]}, expected {width}x{height}"]
    return []


def check_jpeg(path):
    return [] if path.read_bytes()[:3] == b"\xff\xd8\xff" else ["not a JPEG"]


def main():
    errors = []
    expected = set(PNGS) | set(SVGS) | JPEGS
    for name in sorted(expected):
        path = ROOT / name
        if not path.is_file():
            errors.append(f"{name}: missing")
            continue
        if name in PNGS:
            problems = check_png(path, *PNGS[name])
        elif name in SVGS:
            problems = check_svg(path, *SVGS[name])
        else:
            problems = check_jpeg(path)
        errors += [f"{name}: {p}" for p in problems]

    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if (
            SKIP_DIRS.intersection(rel.parts)
            or path.suffix.lower() not in IMAGE_SUFFIXES
        ):
            continue
        if rel.as_posix() not in expected:
            errors.append(
                f"{rel.as_posix()}: not listed; add it to tools/check-assets.py and README.md"
            )

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"ok: {len(expected)} images present at their published sizes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
