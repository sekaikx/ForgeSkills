"""
Extract clean single-view reference panels from a concept sheet.

The sheet is a grid of panels on a dark background. Any metric computed against a
panel that still contains titles, borders or neighbouring panels is garbage, so this
isolates one figure on a flat backdrop and writes it as the comparison target.

Usage:
    python measure_sheet.py --sheet ref.png --list
    python measure_sheet.py --sheet ref.png --crop 258,20,352,392 --out front.png
    python measure_sheet.py --sheet ref.png --auto-front --out front.png --preview
"""

import argparse
import json
import sys

import numpy as np
from PIL import Image


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def subject_mask(rgb, tol=0.06):
    h, w, _ = rgb.shape
    bw = max(1, int(min(h, w) * 0.02))
    border = np.concatenate([
        rgb[:bw].reshape(-1, 3), rgb[-bw:].reshape(-1, 3),
        rgb[:, :bw].reshape(-1, 3), rgb[:, -bw:].reshape(-1, 3),
    ])
    bg = np.median(border, axis=0)
    return np.linalg.norm(rgb - bg, axis=2) > tol


def tight(mask, min_pixels=40):
    ys, xs = np.where(mask)
    if len(ys) < min_pixels:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def save_crop(img, box, out, pad_frac=0.04, square=False, bg=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    px, py = int(w * pad_frac), int(h * pad_frac)
    X0, Y0 = max(0, x0 - px), max(0, y0 - py)
    X1, Y1 = min(img.width, x1 + px), min(img.height, y1 + py)
    c = img.crop((X0, Y0, X1, Y1))
    if square:
        side = max(c.size)
        canvas = Image.new("RGB", (side, side), bg or c.getpixel((0, 0)))
        canvas.paste(c, ((side - c.width) // 2, (side - c.height) // 2))
        c = canvas
    if out:
        c.save(out)
        print(f"WROTE {out}  {c.size[0]}x{c.size[1]}  from box {box}")
    return c


def auto_front(sheet_rgb, region=None):
    """Find the tallest narrow subject column inside a region — the front view."""
    if region:
        x0, y0, x1, y1 = region
        sub = sheet_rgb[y0:y1, x0:x1]
        off = (x0, y0)
    else:
        sub = sheet_rgb
        off = (0, 0)
    m = subject_mask(sub)
    col = m.sum(axis=0)
    if col.max() == 0:
        return None
    thresh = col.max() * 0.35
    xs = np.where(col > thresh)[0]
    # split into runs and take the tallest
    runs, start = [], xs[0]
    for i in range(1, len(xs)):
        if xs[i] != xs[i - 1] + 1:
            runs.append((start, xs[i - 1]))
            start = xs[i]
    runs.append((start, xs[-1]))
    best, best_h = None, 0
    for a, b in runs:
        band = m[:, a:b + 1]
        rows = np.where(band.any(axis=1))[0]
        if len(rows) and (rows.max() - rows.min()) > best_h:
            best_h = rows.max() - rows.min()
            best = (a + off[0], rows.min() + off[1], b + 1 + off[0], rows.max() + 1 + off[1])
    return best


def palette(rgb, mask, k=8, seed=3):
    px = rgb[mask]
    if len(px) < k:
        return []
    rng = np.random.default_rng(seed)
    centers = px[rng.choice(len(px), k, replace=False)].copy()
    for _ in range(18):
        d = ((px[:, None, :] - centers[None]) ** 2).sum(2)
        lab = d.argmin(1)
        for j in range(k):
            sel = px[lab == j]
            if len(sel):
                centers[j] = sel.mean(0)
    d = ((px[:, None, :] - centers[None]) ** 2).sum(2)
    lab = d.argmin(1)
    counts = np.bincount(lab, minlength=k)
    order = np.argsort(-counts)
    out = []
    for i in order:
        c = centers[i]
        out.append({"hex": "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in np.clip(c, 0, 1)),
                    "rgb": [round(float(v), 3) for v in c],
                    "share": round(float(counts[i] / counts.sum()), 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--crop", help="x0,y0,x1,y1")
    ap.add_argument("--region", help="search region x0,y0,x1,y1 for --auto-front")
    ap.add_argument("--auto-front", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--palette", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--square", action="store_true")
    a = ap.parse_args()

    img = Image.open(a.sheet).convert("RGB")
    rgb = load(a.sheet)
    print(f"SHEET {a.sheet}  {img.size[0]}x{img.size[1]}")

    if a.list:
        m = subject_mask(rgb)
        b = tight(m)
        print("global subject box:", b)
        print("mean rgb:", [round(float(v), 3) for v in rgb[m].mean(0)] if b else None)
        return

    box = None
    if a.crop:
        box = tuple(int(v) for v in a.crop.split(","))
    elif a.auto_front:
        region = tuple(int(v) for v in a.region.split(",")) if a.region else None
        box = auto_front(rgb, region)
        print("auto-front box:", box)
    if box is None:
        print("no crop box", file=sys.stderr)
        return 1

    x0, y0, x1, y1 = box
    sub = rgb[y0:y1, x0:x1]
    m = subject_mask(sub)
    inner = tight(m)
    if inner:
        box = (x0 + inner[0], y0 + inner[1], x0 + inner[2], y0 + inner[3])
        print("tight subject box:", box)

    save_crop(img, box, a.out, square=a.square)

    if a.palette:
        sub = rgb[box[1]:box[3], box[0]:box[2]]
        mm = subject_mask(sub)
        pal = palette(sub, mm)
        print(json.dumps(pal, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
