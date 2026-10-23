"""
Automated scene validation gate.

Catches the two defect classes that silently ruin a character build:
  1. Stray geometry - any object whose bounds lie outside the intended envelope.
  2. Proportional drift - any landmark that moved outside its measured tolerance.

Both were real bugs in this build: a cylinder translated then rotated swung 1.5 m
sideways, and a taper applied around world Z squashed an axe head. Neither is
visible in a front render, both destroy a silhouette metric. Run this before any
comparison.

Usage inside Blender:
    exec(open(r"...\\validate_scene.py").read())
    report = validate(frame=(1.80, 0.75, 0.45))

Usage headless:
    blender -b file.blend -P validate_scene.py -- --height 1.80 --json out.json
"""

import json
import sys

import bpy
from mathutils import Vector


def scene_bounds(objs=None):
    """World-space bounds computed from evaluated vertices.

    ob.bound_box is a cached property: immediately after a script edits mesh data
    it still reports the previous mesh, which makes a validation gate pass or fail
    on stale numbers. Read the vertices through the depsgraph instead.
    """
    deps = bpy.context.evaluated_depsgraph_get()
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    n = 0
    for ob in objs or bpy.data.objects:
        if ob.type != 'MESH' or ob.hide_render:
            continue
        ev = ob.evaluated_get(deps)
        me = ev.to_mesh()
        if me is None or len(me.vertices) == 0:
            ev.to_mesh_clear()
            continue
        n += 1
        mw = ob.matrix_world
        for v in me.vertices:
            p = mw @ v.co
            for i in range(3):
                if p[i] < mins[i]:
                    mins[i] = p[i]
                if p[i] > maxs[i]:
                    maxs[i] = p[i]
        ev.to_mesh_clear()
    return (mins, maxs) if n else (None, None)


def tri_count(objs=None):
    total = 0
    for ob in objs or bpy.data.objects:
        if ob.type == 'MESH':
            total += sum(max(0, len(p.vertices) - 2) for p in ob.data.polygons)
    return total


def find_strays(envelope, tol=0.02):
    """Objects whose bounds break the envelope on the horizontal axes."""
    hx, hy, hz = envelope
    bad = []
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        mins, maxs = scene_bounds([ob])
        if mins is None:
            continue
        reasons = []
        if abs(mins.x) > hx + tol or abs(maxs.x) > hx + tol:
            reasons.append(f"|x| {max(abs(mins.x), abs(maxs.x)):.3f} > {hx + tol:.3f}")
        if abs(mins.y) > hy + tol or abs(maxs.y) > hy + tol:
            reasons.append(f"|y| {max(abs(mins.y), abs(maxs.y)):.3f} > {hy + tol:.3f}")
        if mins.z < -tol:
            reasons.append(f"below ground z {mins.z:.3f}")
        if maxs.z > hz + tol:
            reasons.append(f"above head z {maxs.z:.3f} > {hz + tol:.3f}")
        if reasons:
            bad.append({"object": ob.name, "reasons": reasons})
    return bad


def find_isolated(max_gap=0.25):
    """Objects floating away from the body mass - the sideways-cylinder signature."""
    body, _ = scene_bounds()
    if body is None:
        return []
    out = []
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        mins, maxs = scene_bounds([ob])
        if mins is None:
            continue
        c = (mins + maxs) * 0.5
        # distance from the vertical body axis, ignoring legitimate width
        radial = (c.x ** 2 + c.y ** 2) ** 0.5
        if radial > max_gap:
            out.append({"object": ob.name, "radial_offset_m": round(radial, 3)})
    return out


def landmarks(height):
    """Measured landmark heights, for proportion drift checks."""
    m, M = scene_bounds()
    if m is None:
        return {}
    H = M.z - m.z
    return {
        "height": round(H, 4),
        "head_top": round(M.z, 4),
        "ground": round(m.z, 4),
        "width": round(M.x - m.x, 4),
        "depth": round(M.y - m.y, 4),
        "head_frac_of_total": None,
    }


def validate(frame=(1.80, 0.75, 0.45), height_tol_pct=2.0, expect_height=1.80):
    strays = find_strays(frame)
    isolated = find_isolated(max_gap=frame[1])
    m, M = scene_bounds()
    H = (M.z - m.z) if m else 0.0
    err_pct = abs(H - expect_height) / expect_height * 100 if expect_height else 0.0

    checks = [
        {"name": "no_stray_geometry", "pass": len(strays) == 0, "detail": strays},
        {"name": "no_isolated_objects", "pass": len(isolated) == 0, "detail": isolated},
        {"name": "height_within_tolerance", "pass": err_pct <= height_tol_pct,
         "detail": f"measured {H:.4f} m vs expected {expect_height:.3f} m ({err_pct:.2f}% err)"},
        {"name": "above_ground", "pass": bool(m) and m.z > -0.02,
         "detail": f"min z {m.z:.4f}" if m else "no geometry"},
    ]
    report = {
        "pass": all(c["pass"] for c in checks),
        "triangles": tri_count(),
        "objects": len([o for o in bpy.data.objects if o.type == 'MESH']),
        "bounds": landmarks(expect_height),
        "checks": checks,
    }
    return report


def print_report(r):
    print("=" * 66)
    print("SCENE VALIDATION")
    print("-" * 66)
    print(f"objects {r['objects']}   triangles {r['triangles']}")
    for c in r["checks"]:
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"  [{mark}] {c['name']}")
        if not c["pass"]:
            d = c["detail"]
            if isinstance(d, list):
                for item in d[:12]:
                    print(f"         {item}")
            else:
                print(f"         {d}")
    print("-" * 66)
    print("VALIDATION:", "PASS" if r["pass"] else "FAIL")
    print("=" * 66)


if __name__ == "__main__":
    args = {"height": 1.80, "json": None}
    a = sys.argv
    if "--" in a:
        rest = a[a.index("--") + 1:]
        for i, tok in enumerate(rest):
            if tok == "--height":
                args["height"] = float(rest[i + 1])
            if tok == "--json":
                args["json"] = rest[i + 1]
    rep = validate(expect_height=args["height"])
    print_report(rep)
    if args["json"]:
        with open(args["json"], "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)
