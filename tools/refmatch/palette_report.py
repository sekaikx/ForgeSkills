"""
Palette extraction and delta-E comparison.

Two jobs:
  1. Read a named palette file (JSON or a simple key=hex list) and report hex + linear values.
  2. Compare that palette against the dominant colors of a render, and report delta-E per role.

Why a separate tool: during reconstruction, the palette is the part most often *invented*
rather than sampled. Having the sampled values in a file makes the invention visible, and
makes "the vest should be #30241C" a data edit instead of a re-litigation.

Usage:
    python palette_report.py --extract ref.png --k 8
    python palette_report.py --extract ref.png --out palette.json
    python palette_report.py --palette palette.json --render out/front.png
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# reuse the segmentation and lab conversion so both tools agree on what "the subject" is
sys.path.insert(0, str(Path(__file__).parent))
try:
    import compare as C
except ImportError:  # pragma: no cover
    C = None


def hex_of(rgb):
    return "#%02X%02X%02X" % tuple(int(round(float(v) * 255)) for v in np.clip(rgb, 0, 1))


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def subject_pixels(path, k=8):
    """Subject pixels of an image, segmented at native resolution."""
    rgb = C.load_rgb(path, None) if C else np.asarray(
        Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    mask = C.mask_at_native(path, (rgb.shape[1], rgb.shape[0])) if C else np.ones(
        rgb.shape[:2], dtype=bool)
    px = rgb[mask]
    if len(px) < k:
        raise SystemExit(f"only {len(px)} subject pixels in {path}; nothing to cluster")
    return px


def kmeans(px, k=8, iters=20, seed=3):
    rng = np.random.default_rng(seed)
    centers = px[rng.choice(len(px), k, replace=False)].copy()
    for _ in range(iters):
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
    return centers[order], counts[order] / counts.sum()


def extract(path, k=8):
    px = subject_pixels(path, k)
    centers, shares = kmeans(px, k)
    lab = C._srgb_to_lab(centers) if C else None
    out = []
    for i, (c, s) in enumerate(zip(centers, shares)):
        out.append({
            "hex": hex_of(c),
            "rgb": [round(float(v), 4) for v in c],
            "share": round(float(s), 4),
        })
    return out


def delta_e(a_rgb, b_rgb):
    """CIE76 delta-E. Above ~12 is a clearly different color to most viewers."""
    if C is None:
        return float("nan")
    la = C._srgb_to_lab(np.array(a_rgb, dtype=np.float32))
    lb = C._srgb_to_lab(np.array(b_rgb, dtype=np.float32))
    return float(np.linalg.norm(la - lb))


def load_palette(path):
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"palette file not found: {path}")
    text = p.read_text(encoding="utf-8")
    if text.lstrip().startswith(("{", "[")):
        data = json.loads(text)
        if isinstance(data, dict):
            return {k: v for k, v in data.items()}
        return {d.get("role", f"c{i}"): d["hex"] for i, d in enumerate(data)}
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
        elif ":" in line:
            k, v = line.split(":", 1)
        else:
            continue
        out[k.strip()] = v.strip()
    return out


def compare_to_render(palette, render_path, k=8):
    """For each named palette role, find the nearest render cluster and report delta-E."""
    rendered = extract(render_path, k)
    rows = []
    for role, hx in palette.items():
        want = hex_to_rgb(hx)
        best, best_de = None, 1e9
        for cluster in rendered:
            de = delta_e(want, cluster["rgb"])
            if de < best_de:
                best, best_de = cluster, de
        rows.append({
            "role": role,
            "target": hx,
            "nearest_render": best["hex"] if best else None,
            "delta_e": round(best_de, 2),
            "share": best["share"] if best else None,
        })
    rows.sort(key=lambda r: -r["delta_e"])
    return rendered, rows


def print_rows(rows, rendered=None):
    if rendered:
        print("RENDER CLUSTERS")
        for c in rendered:
            print(f"  {c['hex']}  share {c['share'] * 100:5.1f}%")
        print()
    print(f"{'ROLE':<14}{'TARGET':<10}{'NEAREST':<10}{'dE':>7}   verdict")
    print("-" * 56)
    for r in rows:
        verdict = "match" if r["delta_e"] <= 6 else ("close" if r["delta_e"] <= 12 else "OFF")
        print(f"{r['role']:<14}{r['target']:<10}{str(r['nearest_render']):<10}"
              f"{r['delta_e']:>7.2f}   {verdict}")
    worst = max(r["delta_e"] for r in rows)
    mean = float(np.mean([r["delta_e"] for r in rows]))
    print("-" * 56)
    print(f"mean dE {mean:.2f}   worst {worst:.2f}   "
          f"({'PASS' if mean <= 12 else 'FAIL'} at threshold 12)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", help="image to extract a palette from")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--out", help="write extracted palette as JSON")
    ap.add_argument("--palette", help="palette file (JSON or key=hex lines)")
    ap.add_argument("--render", help="render to compare the palette against")
    a = ap.parse_args()

    if a.extract:
        pal = extract(a.extract, a.k)
        print(f"{'HEX':<10}{'SHARE':>8}   RGB")
        for c in pal:
            print(f"{c['hex']:<10}{c['share'] * 100:>7.1f}%   "
                  f"[{', '.join(f'{v:.3f}' for v in c['rgb'])}]")
        if a.out:
            Path(a.out).write_text(json.dumps(pal, indent=2), encoding="utf-8")
            print(f"\nwrote {a.out}")
        return 0

    if a.palette and a.render:
        pal = load_palette(a.palette)
        rendered, rows = compare_to_render(pal, a.render, a.k)
        print_rows(rows, rendered)
        if a.out:
            Path(a.out).write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"wrote {a.out}")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
