"""
Parametric human blockout from measured sheet fractions.

Every dimension is a fraction of total height H, taken from the reference sheet.
Nothing is eyeballed. Change a fraction, re-run, compare.

Usage (headless):
    blender -b -P character_blockout.py -- --height 1.80 --out out/explorer_blockout.blend

Usage (inside a live session):
    exec(open(r"...\\character_blockout.py").read())

Convention: 1 BU = 1 m, +Z up, character faces -Y, origin at ground between feet.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# --- sheet fractions (measured off the turnaround panel) -----------------------
PROPORTIONS = {
    "eye":        0.930,
    "chin":       0.870,
    "neck_base":  0.815,
    "shoulder":   0.820,
    "nipple":     0.720,
    "waist":      0.610,
    "hip":        0.520,
    "crotch":     0.480,
    "wrist":      0.480,
    "elbow":      0.630,
    "knee":       0.280,
    "calf":       0.180,
    "ankle":      0.060,
}

SPANS = {           # widths as fraction of H
    "head_w":      0.098,
    "head_d":      0.115,
    "neck_w":      0.048,
    "shoulder_w":  0.228,
    "chest_w":     0.180,
    "chest_d":     0.115,
    "waist_w":     0.140,
    "waist_d":     0.095,
    "hip_w":       0.165,
    "hip_d":       0.110,
    "thigh_d":     0.078,
    "knee_d":      0.058,
    "calf_d":      0.055,
    "ankle_d":     0.035,
    "upperarm_d":  0.040,
    "forearm_d":   0.034,
    "wrist_d":     0.024,
    "foot_len":    0.150,
    "foot_w":      0.048,
    "hand_len":    0.105,
}

# -----------------------------------------------------------------------------


def purge_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves,
                  bpy.data.lights, bpy.data.cameras):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def get_collection(name="Explorer"):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    return ob


def capsule(name, p0, p1, r0, r1, segs=16, sides=16, col=None):
    """Tapered capsule from p0 to p1 with radii r0/r1. Deterministic geometry."""
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0)
    length = axis.length
    if length < 1e-6:
        length = 1e-6
    axis = axis.normalized()
    up = Vector((0, 0, 1)) if abs(axis.dot(Vector((0, 0, 1)))) < 0.99 else Vector((0, 1, 0))
    x = axis.cross(up).normalized()
    y = axis.cross(x).normalized()

    verts, faces = [], []
    rings = []
    for i in range(segs + 1):
        t = i / segs
        z = -r0 + t * (length + r0 + r1)
        if z < 0:
            r = r0 * math.sqrt(max(0.0, 1 - (z / r0) ** 2)) if r0 > 0 else 0.0
        elif z > length:
            r = r1 * math.sqrt(max(0.0, 1 - ((z - length) / r1) ** 2)) if r1 > 0 else 0.0
        else:
            r = r0 + (r1 - r0) * (z / length)
        ring = []
        for j in range(sides):
            a = 2 * math.pi * j / sides
            p = p0 + axis * z + x * (math.cos(a) * r) + y * (math.sin(a) * r)
            ring.append(len(verts))
            verts.append(p)
        rings.append(ring)

    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            faces.append([a[j], a[k], b[k], b[j]])

    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    (col or get_collection()).objects.link(ob)
    return ob


def box(name, center, size, col=None, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
        v.co += Vector(center)
    if bevel > 0:
        bmesh.ops.bevel(
            bm,
            geom=list(bm.edges) + list(bm.verts),
            offset=bevel,
            segments=3,
            profile=0.6,
            affect='EDGES',
        )
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (col or get_collection()).objects.link(ob)
    return ob


def sphere(name, center, radii, segments=32, rings=20, col=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    for v in bm.verts:
        v.co.x *= radii[0]
        v.co.y *= radii[1]
        v.co.z *= radii[2]
        v.co += Vector(center)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (col or get_collection()).objects.link(ob)
    return ob


def shade_smooth(ob, angle_deg=42.0):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    mod = ob.modifiers.get("SmoothByAngle") or ob.modifiers.new("SmoothByAngle", 'SMOOTH_BY_ANGLE') \
        if hasattr(bpy.types, "SmoothByAngleModifier") else None
    return ob


def build(height=1.80):
    H = height
    P, S = PROPORTIONS, SPANS
    col = get_collection("Explorer_Body")

    def z(k):
        return P[k] * H

    def w(k):
        return S[k] * H

    # --- head ---------------------------------------------------------------
    head_c = (0, 0, z("chin") + w("head_w") * 0.62)
    head = sphere("Head", head_c, (w("head_w") * 0.5, w("head_d") * 0.5, w("head_w") * 0.62),
                  col=col)
    # jaw taper
    for v in head.data.vertices:
        if v.co.z < head_c[2] - w("head_w") * 0.05:
            v.co.x *= 0.82
            v.co.y *= 0.90

    # --- neck ---------------------------------------------------------------
    capsule("Neck", (0, 0, z("neck_base")), (0, 0, z("chin") + 0.02),
            w("neck_w") * 0.5, w("neck_w") * 0.46, col=col)

    # --- torso: chest + waist + pelvis as a lofted stack --------------------
    capsule("Torso_chest", (0, 0, z("waist")), (0, 0, z("shoulder")),
            w("chest_w") * 0.5, w("chest_w") * 0.47, col=col)
    for v in bpy.data.objects["Torso_chest"].data.vertices:
        # flatten front-to-back into a chest profile
        v.co.y *= (w("chest_d") / w("chest_w"))
    capsule("Torso_pelvis", (0, 0, z("crotch")), (0, 0, z("waist") + 0.02),
            w("hip_w") * 0.5, w("waist_w") * 0.52, col=col)
    for v in bpy.data.objects["Torso_pelvis"].data.vertices:
        v.co.y *= (w("hip_d") / w("hip_w"))

    # --- arms ---------------------------------------------------------------
    for side, sx in (("L", 1), ("R", -1)):
        shoulder = Vector((sx * w("shoulder_w") * 0.5, 0, z("shoulder") - 0.02))
        elbow = Vector((sx * (w("shoulder_w") * 0.5 + 0.012), 0.004, z("elbow")))
        wrist = Vector((sx * (w("shoulder_w") * 0.5 + 0.028), 0.010, z("wrist")))
        sphere(f"Deltoid_{side}", shoulder, (w("shoulder_w") * 0.115,) * 2 +
               (w("shoulder_w") * 0.10,), col=col)
        capsule(f"UpperArm_{side}", shoulder, elbow,
                w("upperarm_d") * 0.55, w("upperarm_d") * 0.45, col=col)
        capsule(f"Forearm_{side}", elbow, wrist,
                w("forearm_d") * 0.52, w("wrist_d") * 0.52, col=col)
        # hand: flattened box, fingers suggested by chamfer
        hand_c = (wrist.x, wrist.y, wrist.z - w("hand_len") * 0.5)
        box(f"Hand_{side}", hand_c,
            (w("foot_w") * 0.62, w("upperarm_d") * 0.52, w("hand_len") * 0.95),
            col=col, bevel=0.006)

    # --- legs ---------------------------------------------------------------
    for side, sx in (("L", 1), ("R", -1)):
        hip = Vector((sx * w("hip_w") * 0.24, 0, z("crotch") + 0.02))
        knee = Vector((sx * w("hip_w") * 0.26, 0.004, z("knee")))
        ankle = Vector((sx * w("hip_w") * 0.25, 0.010, z("ankle")))
        capsule(f"Thigh_{side}", hip, knee,
                w("thigh_d") * 0.55, w("knee_d") * 0.52, col=col)
        capsule(f"Calf_{side}", knee, ankle,
                w("calf_d") * 0.52, w("ankle_d") * 0.55, col=col)
        # foot points -Y
        box(f"Foot_{side}", (ankle.x, -w("foot_len") * 0.28, z("ankle") * 0.55),
            (w("foot_w"), w("foot_len"), z("ankle") * 1.05), col=col, bevel=0.008)

    return col


def report(H):
    """Print measured bounds so the comparison step has numbers, not vibes."""
    import bpy
    mins = Vector((1e9,) * 3)
    maxs = Vector((-1e9,) * 3)
    tris = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        tris += sum(len(p.vertices) - 2 for p in ob.data.polygons)
        for c in ob.bound_box:
            pt = ob.matrix_world @ Vector(c)
            mins = Vector((min(mins[i], pt[i]) for i in range(3)))
            maxs = Vector((max(maxs[i], pt[i]) for i in range(3)))
    dims = maxs - mins
    print("=" * 60)
    print(f"MEASURED height   : {dims.z:.4f} m  (target {H:.3f})  err {abs(dims.z-H)/H*100:+.1f}%")
    print(f"MEASURED width    : {dims.x:.4f} m")
    print(f"MEASURED depth    : {dims.y:.4f} m")
    print(f"TRIANGLES         : {tris}")
    print(f"OBJECTS           : {len([o for o in bpy.data.objects if o.type=='MESH'])}")
    print("=" * 60)


if __name__ == "__main__":
    H = 1.80
    import sys
    argv = sys.argv
    if "--" in argv:
        for i, a in enumerate(argv):
            if a == "--height":
                H = float(argv[i + 1])
    purge_scene()
    build(H)
    report(H)
