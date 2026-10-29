"""
Measure texel density across the parts of a mesh.

Density is linear: texture pixels per metre of geometry, i.e. texel * sqrt(UV area /
surface area). Comparing that number between parts of a kit tells you which
parts will be blurry and which are wasting atlas space. Bounding-box area is the
wrong denominator (it flatters long thin walls), so real triangle area is used.

Reads Wavefront OBJ, which every DCC tool exports. No Blender required.

Usage:
    python uv_density.py --obj kit.obj --texel 512
    python uv_density.py --obj kit.obj --texel 2048 --max-ratio 1.6 --json

Groups are taken from `o` / `g` statements when present; otherwise the whole file is
one group.
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def parse_obj(path):
    """Return groups -> list of (v_idx, vt_idx) triangles plus vertex positions.

    OBJ indices are 1-based and may be negative (relative to the end). Faces can be
    polygons; they are fan-triangulated, which is exact for the convex quads that
    kit walls are made of and adequate for the density estimate otherwise.
    """
    verts = []
    uvs = []
    groups = defaultdict(list)
    current = "default"

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            tag = parts[0]
            if tag == "v" and len(parts) >= 4:
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif tag == "vt" and len(parts) >= 3:
                uvs.append((float(parts[1]), float(parts[2])))
            elif tag in ("o", "g"):
                current = parts[1] if len(parts) > 1 else "default"
            elif tag == "f" and len(parts) >= 4:
                corners = []
                for token in parts[1:]:
                    bits = token.split("/")
                    vi = int(bits[0])
                    ti = int(bits[1]) if len(bits) > 1 and bits[1] else 0
                    if vi < 0:
                        vi = len(verts) + vi + 1
                    if ti < 0:
                        ti = len(uvs) + ti + 1
                    corners.append((vi - 1, ti - 1))
                for i in range(1, len(corners) - 1):
                    groups[current].append((corners[0], corners[i], corners[i + 1]))

    return verts, uvs, groups


def tri_area_3d(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    cx = uy * vz - uz * vy
    cy = uz * vx - ux * vz
    cz = ux * vy - uy * vx
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


def tri_area_uv(a, b, c):
    return 0.5 * abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))


def group_stats(verts, uvs, tris):
    a3 = 0.0
    auv = 0.0
    degenerate = 0
    missing_uv = 0
    for (i0, t0), (i1, t1), (i2, t2) in tris:
        try:
            p0, p1, p2 = verts[i0], verts[i1], verts[i2]
        except IndexError:
            degenerate += 1
            continue
        area3 = tri_area_3d(p0, p1, p2)
        a3 += area3
        if min(t0, t1, t2) < 0 or max(t0, t1, t2) >= len(uvs):
            missing_uv += 1
            continue
        auv += tri_area_uv(uvs[t0], uvs[t1], uvs[t2])
    return {
        "triangles": len(tris),
        "area_3d": a3,
        "area_uv": auv,
        "degenerate": degenerate,
        "missing_uv": missing_uv,
    }


def report(path, texel=512, max_ratio=1.6, min_density=None):
    verts, uvs, groups = parse_obj(path)
    if not groups:
        raise SystemExit(f"no faces found in {path}")

    rows = []
    for name, tris in groups.items():
        st = group_stats(verts, uvs, tris)
        if st["area_3d"] <= 1e-12:
            continue
        # linear density: UV area is a fraction of the 0..1 square, so the pixel area is
        # uv*texel^2 and the pixels per metre is its square root over the 3D area
        density = texel * math.sqrt(st["area_uv"] / st["area_3d"])
        rows.append({
            "group": name,
            "triangles": st["triangles"],
            "area_3d": round(st["area_3d"], 6),
            "area_uv": round(st["area_uv"], 6),
            "texel_density": round(density, 2),
            "missing_uv_tris": st["missing_uv"],
            "degenerate_tris": st["degenerate"],
        })

    if not rows:
        raise SystemExit(f"every group in {path} has zero surface area")

    rows.sort(key=lambda r: r["texel_density"])
    lo, hi = rows[0]["texel_density"], rows[-1]["texel_density"]
    ratio = hi / lo if lo > 0 else float("inf")
    mean = sum(r["texel_density"] for r in rows) / len(rows)

    problems = []
    if ratio > max_ratio:
        problems.append(
            f"density spread {ratio:.2f}x exceeds {max_ratio}x — "
            f"'{rows[0]['group']}' gets {lo:.0f} px/m, "
            f"'{rows[-1]['group']}' gets {hi:.0f} px/m")
    if min_density is not None and lo < min_density:
        problems.append(f"lowest density {lo:.0f} px/m is under {min_density} px/m")
    for r in rows:
        if r["missing_uv_tris"]:
            problems.append(f"'{r['group']}' has {r['missing_uv_tris']} triangles without UVs")

    return {
        "obj": str(path),
        "texel": texel,
        "groups": len(rows),
        "mean_texel_density": round(mean, 2),
        "min_texel_density": lo,
        "max_texel_density": hi,
        "spread_ratio": round(ratio, 3) if ratio != float("inf") else None,
        "max_ratio_allowed": max_ratio,
        "pass": not problems,
        "problems": problems,
        "rows": rows,
    }


def print_report(r):
    print("=" * 74)
    print(f"UV DENSITY  {r['obj']}  texel {r['texel']}px  {r['groups']} groups")
    print("-" * 74)
    print(f"{'group':<28}{'tris':>7}{'m^2':>10}{'uv^2':>9}{'px/m':>10}")
    for row in r["rows"]:
        print(f"{row['group'][:27]:<28}{row['triangles']:>7}{row['area_3d']:>10.3f}"
              f"{row['area_uv']:>9.4f}{row['texel_density']:>10.0f}")
    print("-" * 74)
    print(f"mean {r['mean_texel_density']:.0f} px/m   min {r['min_texel_density']:.0f}"
          f"   max {r['max_texel_density']:.0f}   spread {r['spread_ratio']}x")
    for p in r["problems"]:
        print(f"  FAIL {p}")
    print("-" * 74)
    print("DENSITY:", "PASS" if r["pass"] else "FAIL")
    print("=" * 74)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-part texel density from an OBJ.")
    ap.add_argument("--obj", required=True)
    ap.add_argument("--texel", type=int, default=512,
                    help="atlas resolution in pixels along one axis")
    ap.add_argument("--max-ratio", type=float, default=1.6,
                    help="allowed max/min density ratio between parts")
    ap.add_argument("--min-density", type=float, default=None,
                    help="optional floor in px per metre")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    rep = report(a.obj, texel=a.texel, max_ratio=a.max_ratio, min_density=a.min_density)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print_report(rep)
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
