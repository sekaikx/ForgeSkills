"""
Detect visible seams in a tiling texture.

The test is not "does it look OK when tiled". It is whether the wrap boundary is
continuous with the texture's own interior. Two measurements, both at native
resolution so resampling cannot manufacture an artefact:

1. Step ratio — the difference between opposite edges, divided by the mean
   adjacent-pixel difference inside the image. A seamless tile sits near 1.
2. Percentile rank — where the seam step falls in the distribution of all interior
   adjacent steps. A real seam is an outlier; a smooth wrap is not.

An earlier version tiled the image and downscaled it to look for periodic spikes.
That reports seams that do not exist, because downscaling near-Nyquist detail beats
against the tile stride. Measuring the boundary directly has no such failure mode.

Usage:
    python tile_seam_check.py --image wall.png --json
    python tile_seam_check.py --image wall.png --tile 3 --out seam_report.png

Requires: Pillow, numpy.
"""

import argparse
import json
import sys

import numpy as np
from PIL import Image


FLAT_EPS = 1e-4  # luminance step (0-1) treated as no step at all


def load_gray(path):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im, dtype=np.float32) / 255.0
    return 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]


def boundary_metrics(lum):
    """Compare the wrap edge against every interior adjacent pair.

    `percentile` answers "is this edge unusual for this image?" without assuming a
    particular noise level. `ratio` answers "how many times the typical step is it?"
    They fail together on a bad tile and agree on a good one, which is why both are
    reported rather than a single score.
    """
    # interior adjacent differences along each axis
    inner_v = np.abs(np.diff(lum, axis=1)).ravel()
    inner_h = np.abs(np.diff(lum, axis=0)).ravel()

    # wrap edges: last column against first, last row against first
    seam_v = np.abs(lum[:, -1] - lum[:, 0])
    seam_h = np.abs(lum[-1, :] - lum[0, :])

    def stats(seam, inner):
        s = float(seam.mean())
        med = float(np.median(inner))
        mean = float(inner.mean())
        pct = float((inner < seam.mean()).mean() * 100.0)
        return {
            "seam_step": round(s, 5),
            "interior_median": round(med, 5),
            "interior_mean": round(mean, 5),
            "ratio_to_median": round(s / med, 3) if med > 1e-9 else None,
            "percentile": round(pct, 2),
        }

    return {"vertical": stats(seam_v, inner_v), "horizontal": stats(seam_h, inner_h)}


def assess(path, step_ratio_threshold=1.6, percentile_threshold=99.0):
    lum = load_gray(path)
    m = boundary_metrics(lum)

    checks = {}
    for axis in ("vertical", "horizontal"):
        s = m[axis]
        ratio = s["ratio_to_median"]
        checks[f"{axis}_step_ratio"] = {
            "value": ratio,
            "threshold": step_ratio_threshold,
            # a flat interior has no typical step to compare against: the seam passes
            # only if it is flat too
            "pass": bool(s["seam_step"] <= FLAT_EPS if ratio is None
                         else ratio <= step_ratio_threshold),
        }
        checks[f"{axis}_percentile"] = {
            "value": s["percentile"],
            "threshold": percentile_threshold,
            "pass": bool(s["percentile"] <= percentile_threshold),
        }

    return {
        "image": str(path),
        "size": [int(lum.shape[1]), int(lum.shape[0])],
        "boundaries": m,
        "checks": checks,
        "seamless": all(c["pass"] for c in checks.values()),
    }


def write_tile_sheet(path, out, tile=3, size=384):
    """Tiled preview, so the seam can be looked at and not only measured."""
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    sheet = Image.new("RGB", (size * tile, size * tile))
    for y in range(tile):
        for x in range(tile):
            sheet.paste(im, (x * size, y * size))
    sheet.save(out)
    return out


def print_report(r):
    print("=" * 64)
    print(f"TILING CHECK  {r['image']}  {r['size'][0]}x{r['size'][1]}")
    print("-" * 64)
    for axis in ("vertical", "horizontal"):
        s = r["boundaries"][axis]
        print(f"{axis:10s} seam {s['seam_step']:.5f}  interior med "
              f"{s['interior_median']:.5f}  ratio {s['ratio_to_median']}  "
              f"pct {s['percentile']:.1f}")
    print("-" * 64)
    for k, c in r["checks"].items():
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"  [{mark}] {k:24s} {c['value']:>8}  (need <= {c['threshold']})")
    print("-" * 64)
    print("SEAMLESS:", "yes" if r["seamless"] else "no")
    print("=" * 64)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Measure seams in a tiling texture.")
    ap.add_argument("--image", required=True)
    ap.add_argument("--tile", type=int, default=3, help="tiles per axis for the preview")
    ap.add_argument("--out", help="optional tiled preview PNG")
    ap.add_argument("--step-ratio", type=float, default=1.6)
    ap.add_argument("--percentile", type=float, default=99.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    rep = assess(a.image, step_ratio_threshold=a.step_ratio,
                 percentile_threshold=a.percentile)

    if a.out:
        rep["preview"] = write_tile_sheet(a.image, a.out, tile=max(2, min(4, a.tile)))
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print_report(rep)
        if a.out:
            print(f"preview written: {a.out}")
    return 0 if rep["seamless"] else 1


if __name__ == "__main__":
    sys.exit(main())
