"""
Explorer character — pass 2: garments, equipment, hair.

Builds on the blockout. Each call is idempotent: it clears prior pass-2 objects
from the collection, so the script can be re-run after any number change.

    exec(open(r"...\\explorer_build.py").read())
    build_explorer(1.80)
"""

import bpy
import bmesh
import math
from mathutils import Vector

try:
    from explorer_common import PALETTE, Dim, mat, assign, loft, rounded_box, cylinder
except ImportError:
    import importlib.util, os
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "explorer_common.py")
    _spec = importlib.util.spec_from_file_location("explorer_common", _p)
    _m = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    PALETTE, Dim, mat, assign, loft, rounded_box, cylinder = (
        _m.PALETTE, _m.Dim, _m.mat, _m.assign, _m.loft, _m.rounded_box, _m.cylinder)


PASS2 = "Explorer_Kit"


def _fresh_col():
    col = bpy.data.collections.get(PASS2)
    if col is None:
        col = bpy.data.collections.new(PASS2)
        bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return col


def _mats():
    return {
        "skin":    mat("M_Skin", PALETTE["skin"], rough=0.58, spec=0.4),
        "hair":    mat("M_Hair", PALETTE["hair"], rough=0.62, spec=0.3),
        "shirt":   mat("M_Shirt", PALETTE["shirt"], rough=0.86, sheen=0.25),
        "vest":    mat("M_VestLeather", PALETTE["vest"], rough=0.52, spec=0.5),
        "hood":    mat("M_Hood", PALETTE["hood"], rough=0.88, sheen=0.3),
        "pants":   mat("M_Pants", PALETTE["pants"], rough=0.90, sheen=0.15),
        "boot":    mat("M_BootLeather", PALETTE["boot"], rough=0.48, spec=0.55),
        "leather": mat("M_Leather", PALETTE["leather"], rough=0.44, spec=0.55),
        "canvas":  mat("M_Canvas", PALETTE["canvas"], rough=0.92, sheen=0.2),
        "steel":   mat("M_Steel", PALETTE["steel"], rough=0.32, metal=0.95),
        "wood":    mat("M_Wood", PALETTE["wood"], rough=0.68),
        "wrap":    mat("M_Wrap", PALETTE["wrap"], rough=0.92, sheen=0.2),
        "buckle":  mat("M_Buckle", PALETTE["buckle"], rough=0.36, metal=0.9),
    }


def build_explorer(H=1.80):
    D = Dim(H)
    col = _fresh_col()
    M = _mats()
    z, w = D.z, D.w

    # ---- shirt torso: lofted, follows the chest volume with clearance -------
    shirt_rings = [
        (Vector((0, 0, z("crotch") + 0.01)), w("hip_w") * 0.53, w("hip_d") * 0.55, 24),
        (Vector((0, 0, z("waist"))),        w("waist_w") * 0.54, w("waist_d") * 0.56, 24),
        (Vector((0, 0, z("nipple"))),       w("chest_w") * 0.54, w("chest_d") * 0.56, 24),
        (Vector((0, 0, z("shoulder") - 0.02)), w("shoulder_w") * 0.44, w("chest_d") * 0.52, 24),
        (Vector((0, 0, z("neck_base") + 0.012)), w("neck_w") * 0.72, w("neck_w") * 0.78, 20),
    ]
    loft("Shirt", shirt_rings, col=col, material=M["shirt"])

    # ---- pants: two legs + seat, offset from body --------------------------
    for side, sx in (("L", 1), ("R", -1)):
        rings = [
            (Vector((sx * w("hip_w") * 0.24, 0, z("crotch") + 0.03)),
             w("thigh_d") * 0.60, w("thigh_d") * 0.58, 18),
            (Vector((sx * w("hip_w") * 0.26, 0.004, z("knee"))),
             w("knee_d") * 0.58, w("knee_d") * 0.56, 18),
            (Vector((sx * w("hip_w") * 0.25, 0.010, z("ankle") + 0.045)),
             w("calf_d") * 0.52, w("calf_d") * 0.50, 18),
        ]
        loft(f"Pants_{side}", rings, col=col, material=M["pants"])

    # ---- boots: shaft + foot, sole slightly proud --------------------------
    for side, sx in (("L", 1), ("R", -1)):
        shaft = [
            (Vector((sx * w("hip_w") * 0.25, 0.008, z("ankle") + 0.10)),
             w("calf_d") * 0.58, w("calf_d") * 0.56, 16),
            (Vector((sx * w("hip_w") * 0.25, 0.004, z("ankle") - 0.005)),
             w("ankle_d") * 0.72, w("ankle_d") * 0.70, 16),
        ]
        loft(f"BootShaft_{side}", shaft, col=col, material=M["boot"])
        rounded_box(f"BootFoot_{side}",
                    (sx * w("hip_w") * 0.25, -w("foot_len") * 0.26, z("ankle") * 0.46),
                    (w("foot_w") * 1.02, w("foot_len") * 1.06, z("ankle") * 0.94),
                    bevel=0.012, col=col, material=M["boot"])

    # ---- long coat: the silhouette-defining garment ------------------------
    # Measured off the reference in metres (figure height 1.80 m): the coat is
    # widest at chest level ~0.46 m, pinches to ~0.33 m near the knee, and the hem
    # reaches mid-calf at ~0.44 m. Those three numbers drive the whole profile.
    coat_rings = [
        (Vector((0, 0, z("knee") - 0.075)), w("hip_w") * 1.08, w("hip_d") * 0.92, 28),
        (Vector((0, 0, z("knee") + 0.055)), w("hip_w") * 0.92, w("hip_d") * 0.84, 28),
        (Vector((0, 0, z("crotch") - 0.01)), w("hip_w") * 0.78, w("hip_d") * 0.76, 28),
        (Vector((0, 0, z("hip"))),           w("hip_w") * 0.70, w("hip_d") * 0.70, 28),
        (Vector((0, 0, z("waist"))),         w("waist_w") * 0.64, w("waist_d") * 0.68, 28),
        (Vector((0, 0, z("nipple"))),        w("chest_w") * 0.62, w("chest_d") * 0.64, 28),
        (Vector((0, 0, z("shoulder") - 0.03)), w("shoulder_w") * 0.50, w("chest_d") * 0.56, 28),
    ]
    coat = loft("Coat", coat_rings, close_bottom=False, close_top=False,
                col=col, material=M["vest"])

    # open the front: pull the forward-facing rows apart along -Y
    for v in coat.data.vertices:
        if v.co.y < -w("chest_d") * 0.10:
            lateral = abs(v.co.x) / max(1e-6, w("shoulder_w") * 0.30)
            v.co.y += w("chest_d") * 0.055 * min(1.0, lateral)

    # ---- hood worn UP ------------------------------------------------------
    # The hood is the widest part of the head silhouette: 0.33 m across, which is
    # nearly twice the skull width. Without it the top band reads far too narrow.
    loft("HoodShell", [
        (Vector((0, 0.022, z("chin") + 0.070)), w("head_w") * 0.80, w("head_d") * 0.55, 26),
        (Vector((0, 0.030, z("neck_base") + 0.030)), w("head_w") * 0.94, w("head_d") * 0.64, 26),
        (Vector((0, 0.032, z("neck_base") - 0.030)), w("shoulder_w") * 0.40, w("chest_d") * 0.46, 26),
        (Vector((0, 0.026, z("shoulder") - 0.010)), w("shoulder_w") * 0.44, w("chest_d") * 0.42, 26),
    ], col=col, material=M["hood"])

    # hood peak, offset back so the face opening stays clear
    cowl = rounded_box("HoodPeak", (0, w("head_d") * 0.36, z("chin") + 0.085),
                       (w("head_w") * 0.82, w("head_d") * 0.36, w("head_w") * 0.50),
                       bevel=0.034, col=col, material=M["hood"])
    for v in cowl.data.vertices:
        if v.co.z < z("chin") + 0.050:
            v.co.z -= abs(v.co.x) * 0.08

    # ---- belt + pouches ---------------------------------------------------
    belt_z = z("hip") + 0.012
    loft("Belt", [
        (Vector((0, 0, belt_z - 0.026)), w("waist_w") * 0.575, w("waist_d") * 0.60, 26),
        (Vector((0, 0, belt_z + 0.026)), w("waist_w") * 0.575, w("waist_d") * 0.60, 26),
    ], col=col, material=M["leather"])

    rounded_box("Buckle", (0, -w("waist_d") * 0.60, belt_z),
                (0.052, 0.014, 0.046), bevel=0.004, col=col, material=M["buckle"])

    for i, (sx, dz, dw) in enumerate(((1, -0.035, 0.075), (-1, -0.030, 0.070),
                                     (1, -0.115, 0.052), (-1, -0.110, 0.050))):
        rounded_box(f"Pouch_{i}", (sx * w("hip_w") * 0.42, -w("waist_d") * 0.50,
                                   belt_z + dz),
                    (dw, 0.055, 0.085), bevel=0.008, col=col, material=M["leather"])

    # ---- backpack + bedroll ----------------------------------------------
    pack_z = z("nipple") + 0.03
    rounded_box("PackBody", (0, w("chest_d") * 0.62, pack_z),
                (w("chest_w") * 0.78, w("chest_d") * 0.62, 0.34),
                bevel=0.020, col=col, material=M["canvas"])
    rounded_box("PackLid", (0, w("chest_d") * 0.62, pack_z + 0.185),
                (w("chest_w") * 0.76, w("chest_d") * 0.60, 0.055),
                bevel=0.012, col=col, material=M["leather"])
    # bedroll across the top — axis along X, so no post-hoc object rotation
    cylinder("Bedroll", (0, w("chest_d") * 0.62, pack_z + 0.235),
             radius=0.052, depth=w("shoulder_w") * 0.78, col=col,
             material=M["canvas"], verts=18, axis='X')
    # straps over the shoulders
    for sx in (1, -1):
        rounded_box(f"PackStrap_{'L' if sx > 0 else 'R'}",
                    (sx * w("chest_w") * 0.30, -w("chest_d") * 0.16,
                     (z("shoulder") + z("nipple")) * 0.5),
                    (0.032, w("chest_d") * 1.05, (z("shoulder") - z("nipple")) * 1.25),
                    bevel=0.006, col=col, material=M["leather"])

    # ---- axe on the right hip --------------------------------------------
    axe_x = -w("hip_w") * 0.52
    axe_z = belt_z + 0.145
    cylinder("AxeHandle", (axe_x, -0.02, belt_z - 0.10),
             radius=0.0135, depth=0.46, col=col, material=M["wood"], verts=12,
             rot=(math.radians(6), 0, math.radians(-8)))
    head = rounded_box("AxeHead", (axe_x - 0.006, -0.03, axe_z),
                       (0.016, 0.086, 0.072), bevel=0.004, col=col, material=M["steel"])
    # taper the bit about the head's OWN centre, never about world z
    for v in head.data.vertices:
        if v.co.y < -0.055:
            v.co.z = axe_z + (v.co.z - axe_z) * 0.62

    # ---- arm wraps --------------------------------------------------------
    for side, sx in (("L", 1), ("R", -1)):
        loft(f"WristWrap_{side}", [
            (Vector((sx * (w("shoulder_w") * 0.5 + 0.026), 0.010, z("wrist") + 0.035)),
             w("wrist_d") * 0.60, w("wrist_d") * 0.58, 14),
            (Vector((sx * (w("shoulder_w") * 0.5 + 0.028), 0.010, z("wrist") - 0.045)),
             w("wrist_d") * 0.56, w("wrist_d") * 0.54, 14),
        ], col=col, material=M["wrap"])

    # ---- hair mass: the biggest silhouette contributor after the body -----
    head_c = (0, 0, z("chin") + w("head_w") * 0.62)
    hair = bpy.data.meshes.new("Hair")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=18, radius=1.0)
    hx, hy, hz = w("head_w") * 0.56, w("head_d") * 0.56, w("head_w") * 0.68
    for v in bm.verts:
        # only keep the shell above the hairline, and flare it at the sides
        v.co.x *= hx
        v.co.y *= hy
        v.co.z *= hz
        if v.co.z < -0.012:
            v.co.z *= 0.55
        v.co += Vector(head_c)
    bm.to_mesh(hair)
    bm.free()
    hair_ob = bpy.data.objects.new("Hair", hair)
    col.objects.link(hair_ob)
    assign(hair_ob, M["hair"])
    for p in hair_ob.data.polygons:
        p.use_smooth = True

    # ---- face plane: eyes as dark insets so the head reads at distance -----
    for sx in (1, -1):
        eye = rounded_box(f"Eye_{'L' if sx > 0 else 'R'}",
                          (sx * w("head_w") * 0.20, -w("head_d") * 0.44,
                           head_c[2] + w("head_w") * 0.06),
                          (0.017, 0.010, 0.011), bevel=0.003, col=col,
                          material=mat("M_Eye", (0.055, 0.045, 0.040), rough=0.25))

    print("PASS2 objects:", len([o for o in col.objects]))
    return col
