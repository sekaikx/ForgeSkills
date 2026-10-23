"""
Side-by-side diagnostic sheet.

Metrics tell you the score. This tells you what to change. Three panels:
  1. reference,  2. render,  3. silhouette overlay (reference red, render cyan,
  agreement white).

Usage:
    python overlay.py --ref ref.png --test render.png --out diag.png
"""

import argparse

import numpy as np
from PIL import Image, ImageDraw

import compare as C


def _panel(rgb, mask, size, label, bg=(18, 18, 20)):
    h, w = size[1], size[0]
    canvas = Image.new("RGB", (w, h), bg)
    src = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    arr = np.asarray(src).copy()
    arr[~mask] = bg
    canvas.paste(Image.fromarray(arr), (0, 0))
    d = ImageDraw.Draw(canvas)
    d.text((8, 6), label, fill=(255, 255, 255))
    return canvas


def _overlay(na, nb, size, label):
    h, w = size[1], size[0]
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[na & ~nb] = (230, 60, 60)      # reference only
    img[nb & ~na] = (60, 200, 230)     # render only
    img[na & nb] = (235, 235, 235)     # agreement
    canvas = Image.fromarray(img)
    d = ImageDraw.Draw(canvas)
    d.text((8, 6), label, fill=(255, 220, 120))
    return canvas


def build(ref_path, test_path, out_path, size=(384, 512)):
    ref = C.load_rgb(ref_path, size)
    test = C.load_rgb(test_path, size)
    ma = C.mask_at_native(ref_path, size)
    mb = C.mask_at_native(test_path, size)
    na = C.normalize_mask(ma, size)
    nb = C.normalize_mask(mb, size)

    iou = C.silhouette_iou(na, nb)
    panels = [
        _panel(ref, ma, size, "REFERENCE"),
        _panel(test, mb, size, "RENDER"),
        _overlay(na, nb, size, f"OVERLAY  IoU {iou:.3f}"),
    ]
    gap = 8
    W = size[0] * 3 + gap * 2
    sheet = Image.new("RGB", (W, size[1] + 26), (10, 10, 12))
    x = 0
    for p in panels:
        sheet.paste(p, (x, 26))
        x += size[0] + gap

    d = ImageDraw.Draw(sheet)
    wa, wb = C.band_widths(na), C.band_widths(nb)
    be = C.band_errors(wa, wb)
    d.text((8, 8), f"band diffs %: " + " ".join(f"{e:+.0f}" for e in be) +
           f"    max {max(be):.1f}%    mean {np.mean(be):.1f}%", fill=(200, 200, 210))
    sheet.save(out_path)
    print(f"WROTE {out_path}  {W}x{size[1] + 26}")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--out", default="diag.png")
    a = ap.parse_args()
    build(a.ref, a.test, a.out)
