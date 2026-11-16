"""Make the README banner shared by every Braveheart-Chess repository.

The big mark on the left, the BRAVEHEART wordmark and a tagline on the right,
over a three-colour rule in the artwork's own gold, red and woad blue. The
background is transparent, so there are two variants: dark lettering for
GitHub's light theme and light lettering for its dark theme. READMEs pick one
with a <picture> element (see README.md).

Usage: python scripts/make_banner.py logo.png <out_dir>
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logo_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

W, H = 1280, 360
LOGO = 320
GAP = 24
# Colours from the artwork's palette (see logo.svg).
GOLD, RED, WOAD = (207, 144, 49), (192, 40, 27), (57, 129, 239)
VARIANTS = {
    "banner-light.png": {"word": (15, 1, 1), "tag": (90, 80, 76)},
    "banner-dark.png": {"word": (240, 236, 230), "tag": (170, 162, 156)},
}
FONTS = "/System/Library/Fonts/Supplemental/"
word_font = ImageFont.truetype(FONTS + "Arial Black.ttf", 104)
tag_font = ImageFont.truetype(FONTS + "Arial Bold.ttf", 34)

logo = Image.open(logo_path).convert("RGBA").resize((LOGO, LOGO), Image.LANCZOS)

for name, ink in VARIANTS.items():
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    # Centre the mark and the wordmark together.
    word_w = draw.textlength("BRAVEHEART", font=word_font)
    left = (W - (LOGO + GAP + word_w)) // 2
    card.alpha_composite(logo, (int(left), (H - LOGO) // 2))
    x = left + LOGO + GAP
    draw.text((x, 92), "BRAVEHEART", font=word_font, fill=ink["word"])
    right = x + word_w
    # The rule spans the wordmark: gold, red, woad blue, in equal thirds.
    third = (right - x) / 3
    for i, colour in enumerate((GOLD, RED, WOAD)):
        draw.rectangle(
            (x + i * third, 220, x + (i + 1) * third - 6, 228), fill=colour
        )
    draw.text(
        (x + 2, 248), "A UCI chess engine in Rust", font=tag_font, fill=ink["tag"]
    )
    card.save(out_dir / name, optimize=True)
    print(name, card.size)
