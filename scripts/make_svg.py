"""Trace the artist's original JPEGs into flat-colour SVGs.

The originals are flat colour with black line art, so each pixel is first
snapped to the artwork's own palette (found from the image, not hard-coded)
and the flat image is then traced by vtracer. The result has the same square
framing as the PNG masters and a transparent background.
"""
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image
from scipy import ndimage

SCALE = 3          # upsample before tracing so curves follow the line art
PAD = 0.04         # same margin as logo.png
MERGE = 40.0       # palette colours closer than this (RGB distance) are one
BLEND = 75.0       # colour K this close to the line A-B is a blend of them


def background(rgb):
    """Near-white pixels connected to the image border (as make_logos.py)."""
    labels, _ = ndimage.label(rgb.min(axis=2) > 235)
    edge = set(np.unique(np.concatenate(
        [labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    return np.isin(labels, list(edge))


def palette(rgb):
    """The artwork's flat colours: common colours of low-gradient pixels."""
    grad = sum(np.abs(ndimage.sobel(rgb[..., c], axis=a))
               for c in range(3) for a in (0, 1))
    flat = rgb[grad < 40].astype(np.int32)
    key = (((flat[:, 0] >> 4) << 8) | ((flat[:, 1] >> 4) << 4)
           | (flat[:, 2] >> 4))
    keys, inverse, counts = np.unique(key, return_inverse=True,
                                      return_counts=True)
    sums = np.zeros((len(keys), 3))
    np.add.at(sums, inverse, flat)
    means = sums / counts[:, None]
    colours = []  # [weighted sum, weight], most common first
    for i in np.argsort(-counts):
        if counts[i] < 2e-4 * len(flat):
            break
        for c in colours:
            if np.linalg.norm(c[0] / c[1] - means[i]) < MERGE:
                c[0] += sums[i]
                c[1] += counts[i]
                break
        else:
            colours.append([sums[i].copy(), float(counts[i])])
    return np.array([c[0] / c[1] for c in colours])


def flatten(rgb, pal):
    """Label every pixel with its nearest palette colour, then clear fringes.

    An anti-aliased edge pixel sits between two colours and may be nearest to
    a third: the blend of red and black is close to the brown, of black and
    white to the light brown. So a sliver of colour K too thin to survive an
    opening is given back to A or B when both lie solidly beside it and K is
    a blend of the two. Black and white are blends of nothing, so whiskers
    and outlines are never touched.
    """
    dist = np.linalg.norm(rgb[:, :, None, :] - pal[None, None], axis=3)
    label = dist.argmin(axis=2)
    r, n = SCALE + 1, len(pal)
    core = [ndimage.binary_erosion(label == k, iterations=r) for k in range(n)]
    beside = [ndimage.binary_dilation(c, iterations=3 * r) for c in core]
    out = label.copy()
    for k in range(n):
        thin = (label == k) & ~ndimage.binary_dilation(core[k], iterations=r)
        for a in range(n):
            for b in range(a + 1, n):
                if k in (a, b):
                    continue
                ab = pal[b] - pal[a]
                t = np.dot(pal[k] - pal[a], ab) / np.dot(ab, ab)
                off = np.linalg.norm(pal[a] + t * ab - pal[k])
                if not (0.1 < t < 0.9 and off < BLEND):
                    continue
                m = thin & beside[a] & beside[b]
                out[m] = np.where(dist[m][:, a] <= dist[m][:, b], a, b)
    return out


def compact(d, fill, tx, ty, pal):
    """Rewrite a traced path: palette fill, relative whole-number commands."""
    rgb = np.array([int(fill[i:i + 2], 16) for i in (1, 3, 5)])
    near = pal[np.linalg.norm(pal - rgb, axis=1).argmin()]
    fill = "#%02x%02x%02x" % tuple(int(v) for v in near.round())
    out, cur, start = [], (0, 0), (0, 0)
    for cmd, args in re.findall(r"([MLCZ])([^MLCZ]*)", d):
        nums = [float(v) for v in args.split()]
        pts = [(round(nums[i] + tx), round(nums[i + 1] + ty))
               for i in range(0, len(nums), 2)]
        if cmd == "Z":
            out.append("z")
            cur = start
        elif cmd == "M":
            out.append("M%d %d" % pts[0])
            cur = start = pts[0]
        else:
            step = 3 if cmd == "C" else 1
            for i in range(0, len(pts), step):
                seg = pts[i:i + step]
                if all(p == cur for p in seg):
                    continue  # zero-length segment
                rel = " ".join("%d %d" % (x - cur[0], y - cur[1])
                               for x, y in seg)
                out.append(cmd.lower() + rel)
                cur = seg[-1]
    return '<path fill="%s" d="%s"/>' % (fill, "".join(out).replace(" -", "-"))


def trace(src, dst, title):
    art = Image.open(src).convert("RGB")
    pal = palette(np.asarray(art).astype(np.float32))
    big = art.resize((art.width * SCALE, art.height * SCALE), Image.LANCZOS)
    rgb = np.asarray(big).astype(np.float32)
    label = flatten(rgb, pal)
    # Background: the border-connected near-white, grown to every white-
    # labelled pixel joined to it, so no pale fringe is left round the mark.
    white = np.linalg.norm(pal - 255.0, axis=1).argmin()
    regions, _ = ndimage.label(label == white)
    bg = np.isin(regions, np.unique(regions[background(rgb)]))
    flat = np.dstack([pal[label].round(), np.where(bg, 0, 255)])
    cut = Image.fromarray(flat.astype(np.uint8), "RGBA")
    cut = cut.crop(cut.getbbox())
    size = round(max(cut.size) / (1 - 2 * PAD))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(cut, ((size - cut.width) // 2,
                                 (size - cut.height) // 2))
    with tempfile.TemporaryDirectory() as tmp:
        png, svg = Path(tmp) / "flat.png", Path(tmp) / "flat.svg"
        canvas.save(png)
        vtracer.convert_image_to_svg_py(
            str(png), str(svg), colormode="color", hierarchical="stacked",
            mode="spline", filter_speckle=4 * SCALE, color_precision=8,
            layer_difference=1, corner_threshold=60, length_threshold=4.0,
            splice_threshold=45, path_precision=0)
        traced = svg.read_text()
    paths = [compact(d, fill, float(x), float(y), pal)
             for d, fill, x, y in re.findall(
                 r'<path d="([^"]*)" fill="(#\w+)" '
                 r'transform="translate\(([-\d.]+),([-\d.]+)\)"/>', traced)]
    assert paths and len(paths) == traced.count("<path"), "tracer changed"
    dst.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Copyright (c) 2026 the artist. All rights reserved; see "
        "LICENSE.\n     Traced from original/ by "
        "scripts/make_svg.py. -->\n"
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"'
        f' width="1024" height="1024">\n<title>{title}</title>\n'
        + "\n".join(paths) + "\n</svg>\n")
    print(dst.name, f"{dst.stat().st_size // 1024} kB,", len(paths), "paths,",
          len(pal), "colours")


src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
trace(src_dir / "braveheart-logo-big.jpg", out_dir / "logo.svg",
      "Braveheart logo")
trace(src_dir / "braveheart-logo-small.jpg", out_dir / "logo-small.svg",
      "Braveheart logo (small mark)")
