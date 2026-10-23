"""
Derive PBR maps from a single albedo image.

Game textures usually arrive as one colour image. Roughness, normal and ambient
occlusion can be derived from luminance structure, which is what this script does.
It is deliberately simple and inspectable: every map is a documented operation on
the albedo, so a result that looks wrong can be traced to one step.

Usage:
    python tex_to_maps.py --albedo wall.png --out out/wall --strength 0.6
    python tex_to_maps.py --albedo leaf.png --out out/leaf --ao --json

Outputs (into --out):
    <name>_roughness.png   grayscale
    <name>_normal.png      RGB, tangent-space
    <name>_ao.png          grayscale, only with --ao

Requires: Pillow, numpy.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def load_gray(path):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im, dtype=np.float32) / 255.0
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    return arr, lum


def blur(img, radius):
    """Box blur via integral image. O(1) per pixel regardless of radius.

    A gaussian would be smoother, but a box blur is enough for map derivation and
    avoids a scipy dependency. Radius is in pixels and is clamped to the image.
    """
    r = max(1, int(radius))
    pad = np.pad(img, r, mode="edge")
    ii = pad.cumsum(0).cumsum(1)
    ii = np.pad(ii, ((1, 0), (1, 0)), mode="constant")
    h, w = img.shape
    k = 2 * r + 1
    # window sums from the integral image
    s = (ii[k:k + h, k:k + w]
         - ii[0:h, k:k + w]
         - ii[k:k + h, 0:w]
         + ii[0:h, 0:w])
    return s / (k * k)


def high_pass(lum, radius):
    """Luminance minus its local mean: the detail that a normal map encodes."""
    return lum - blur(lum, radius)


def derive_roughness(lum, contrast=1.0, base=0.5):
    """Dark, matte surfaces read rougher; highlights read smoother.

    The mapping is inverted luminance around a mid base. `contrast` widens the
    spread; 0 would give a flat constant roughness, which is a valid choice for
    stylised work.
    """
    r = base + (0.5 - lum) * contrast
    return np.clip(r, 0.04, 1.0)


def derive_normal(hp, strength=1.0):
    """Sobel the high-pass band and encode as a tangent-space normal.

    Scaling by `strength` is the only artistic control that matters. Over 2.0 the
    result reads as plastic micro-contrast on concrete; under 0.3 the surface looks
    painted on. Concrete sits near 0.4, brick near 1.0.
    """
    gy, gx = np.gradient(hp)
    n = np.stack([-gx * strength, -gy * strength, np.ones_like(hp)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return (n * 0.5 + 0.5).clip(0, 1)


def derive_ao(lum, radius, strength=1.0):
    """Cavity estimate: pixels darker than their neighbourhood are occluded.

    This is not real ambient occlusion — it has no geometry. It is a cheap cavity
    mask for adding grime in crevices, and it must not be used as a lighting
    solution.
    """
    local = blur(lum, radius)
    cavity = np.clip((local - lum) * 4.0 * strength, 0.0, 1.0)
    return 1.0 - cavity


def save_gray(arr, path):
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(path)


def save_rgb(arr, path):
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB").save(path)


def process(albedo, out_prefix, strength=1.0, contrast=1.0, radius=3, ao=False,
            ao_radius=12):
    _, lum = load_gray(albedo)
    hp = high_pass(lum, radius)

    out_prefix = Path(out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    rough = derive_roughness(lum, contrast=contrast)
    normal = derive_normal(hp, strength=strength)

    written = {}
    rp = out_prefix.with_name(out_prefix.name + "_roughness.png")
    save_gray(rough, rp)
    written["roughness"] = str(rp)

    np_ = out_prefix.with_name(out_prefix.name + "_normal.png")
    save_rgb(normal, np_)
    written["normal"] = str(np_)

    if ao:
        a = derive_ao(lum, ao_radius)
        ap = out_prefix.with_name(out_prefix.name + "_ao.png")
        save_gray(a, ap)
        written["ao"] = str(ap)

    return {
        "albedo": str(albedo),
        "size": list(lum.shape[::-1]),
        "strength": strength,
        "radius": radius,
        "roughness_mean": round(float(rough.mean()), 4),
        "roughness_std": round(float(rough.std()), 4),
        "written": written,
        "warning": ("roughness_std < 0.02 — the map is nearly flat; the surface will "
                    "read as a single material" if float(rough.std()) < 0.02 else None),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive PBR maps from one albedo.")
    ap.add_argument("--albedo", required=True)
    ap.add_argument("--out", required=True, help="output prefix, e.g. out/wall")
    ap.add_argument("--strength", type=float, default=1.0,
                    help="normal strength; concrete ~0.4, brick ~1.0")
    ap.add_argument("--contrast", type=float, default=1.0,
                    help="roughness spread; 0 = constant roughness")
    ap.add_argument("--radius", type=int, default=3,
                    help="high-pass radius in px; larger = coarser detail")
    ap.add_argument("--ao", action="store_true", help="also write a cavity/AO map")
    ap.add_argument("--ao-radius", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    rep = process(a.albedo, a.out, strength=a.strength, contrast=a.contrast,
                  radius=a.radius, ao=a.ao, ao_radius=a.ao_radius)

    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"albedo  {rep['albedo']}  {rep['size'][0]}x{rep['size'][1]}")
        print(f"roughness mean {rep['roughness_mean']:.3f}  std {rep['roughness_std']:.3f}")
        for k, v in rep["written"].items():
            print(f"wrote   {k:9s} {v}")
        if rep["warning"]:
            print(f"WARN    {rep['warning']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
