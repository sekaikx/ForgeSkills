"""
Explorer character — pass 2: garments, equipment, hair, materials.

Reads the measured proportions from character_blockout.py so nothing is re-guessed.
Builds over the body blockout; every garment is an offset shell, not a new anatomy.

Convention: 1 BU = 1 m, +Z up, faces -Y.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# --- palette sampled from the reference sheet --------------------------------
# Values are linear-ish sRGB from the figure panel, not guesswork. The figure is
# almost entirely dark leather and canvas; the only bright notes are skin and the
# metal fittings. Anything lighter than this reads as a different character.
PALETTE = {
    "skin":      (0.405, 0.320, 0.268),   # #A38C7C sampled
    "hair":      (0.078, 0.058, 0.040),
    "shirt":     (0.148, 0.118, 0.098),   # dark undertunic, not a white shirt
    "vest":      (0.176, 0.134, 0.106),   # #30241C
    "hood":      (0.128, 0.098, 0.078),   # #221914
    "pants":     (0.072, 0.052, 0.040),
    "boot":      (0.098, 0.072, 0.052),
    "leather":   (0.135, 0.100, 0.078),   # #221914 family
    "canvas":    (0.188, 0.148, 0.115),   # #30241C
    "steel":     (0.300, 0.305, 0.315),
    "wood":      (0.115, 0.082, 0.058),
    "wrap":      (0.245, 0.205, 0.170),
    "buckle":    (0.330, 0.300, 0.250),
}

# --- proportions, mirrored from character_blockout.py -------------------------
P = {
    "eye": 0.930, "chin": 0.870, "neck_base": 0.815, "shoulder": 0.820,
    "nipple": 0.720, "waist": 0.610, "hip": 0.520, "crotch": 0.480,
    "wrist": 0.480, "elbow": 0.630, "knee": 0.280, "calf": 0.180, "ankle": 0.060,
}
S = {
    "head_w": 0.098, "head_d": 0.115, "neck_w": 0.048, "shoulder_w": 0.228,
    "chest_w": 0.180, "chest_d": 0.115, "waist_w": 0.140, "waist_d": 0.095,
    "hip_w": 0.165, "hip_d": 0.110, "thigh_d": 0.078, "knee_d": 0.058,
    "calf_d": 0.055, "ankle_d": 0.035, "upperarm_d": 0.040, "forearm_d": 0.034,
    "wrist_d": 0.024, "foot_len": 0.150, "foot_w": 0.048, "hand_len": 0.105,
}


class Dim:
    def __init__(self, H):
        self.H = H

    def z(self, k):
        return P[k] * self.H

    def w(self, k):
        return S[k] * self.H


# --- material helper ---------------------------------------------------------

def mat(name, color, rough=0.75, metal=0.0, spec=0.35, sheen=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        return m
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    for key, val in (("Specular IOR Level", spec), ("Specular", spec)):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val
            break
    if sheen:
        for key in ("Sheen Weight", "Sheen"):
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = sheen
                break
    m.diffuse_color = (*color, 1.0)
    return m


def assign(ob, material):
    ob.data.materials.clear()
    ob.data.materials.append(material)
    return ob


# --- geometry helpers -------------------------------------------------------

def link_to(ob, col):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    return ob


def shell_from(name, source_obs, scale, offset, col, material=None,
               keep_verts=None, snap_smooth=True):
    """Duplicate meshes then scale about a pivot — cheap garment offset."""
    out = []
    for src in source_obs:
        me = src.data.copy()
        ob = bpy.data.objects.new(f"{name}_{src.name}", me)
        col.objects.link(ob)
        pivot = Vector((0, 0, 0))
        for v in me.vertices:
            p = src.matrix_world @ v.co
            d = p - pivot
            v.co = Vector((
                d.x * scale[0] + pivot.x + offset[0],
                d.y * scale[1] + pivot.y + offset[1],
                d.z * scale[2] + pivot.z + offset[2],
            ))
        if material:
            assign(ob, material)
        out.append(ob)
    return out


def loft(name, rings, close_bottom=True, close_top=True, col=None, material=None):
    """Build a tube from a list of (center Vector, radius_x, radius_y, sides).

    Rings may declare different side counts; every ring is resampled to the
    maximum so the quad band always has matching vertex counts. (A mismatch
    here is the classic loft crash.)
    """
    sides = max(int(r[3]) for r in rings)
    verts, faces = [], []
    ring_idx = []
    for (c, rx, ry, _declared) in rings:
        idx = []
        for j in range(sides):
            a = 2 * math.pi * j / sides
            verts.append((c.x + math.cos(a) * rx, c.y + math.sin(a) * ry, c.z))
            idx.append(len(verts) - 1)
        ring_idx.append(idx)
    for i in range(len(ring_idx) - 1):
        a, b = ring_idx[i], ring_idx[i + 1]
        n = len(a)
        for j in range(n):
            k = (j + 1) % n
            faces.append([a[j], a[k], b[k], b[j]])
    if close_bottom:
        faces.append(list(reversed(ring_idx[0])))
    if close_top:
        faces.append(ring_idx[-1])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    if material:
        assign(ob, material)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def rounded_box(name, center, size, bevel, col, material=None, segments=3):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts),
                        offset=bevel, segments=segments, profile=0.55, affect='EDGES')
    for v in bm.verts:
        v.co += Vector(center)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if material:
        assign(ob, material)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def cylinder(name, center, radius, depth, col, material=None, verts=20,
             axis='Z', rot=None):
    """Cylinder built at the origin, then placed. Never translate verts first.

    Translating the vertices and then rotating the object rotates around the
    object origin, which is still the world origin - the mesh swings out to an
    arbitrary location. Build local, then set location/rotation.
    """
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    if axis == 'X':
        bmesh.ops.rotate(bm, verts=bm.verts,
                         cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
    elif axis == 'Y':
        bmesh.ops.rotate(bm, verts=bm.verts,
                         cent=(0, 0, 0),
                         matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.location = Vector(center)
    if rot is not None:
        ob.rotation_euler = rot
    if material:
        assign(ob, material)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def solid_render(ob):
    ob.hide_render = False
    ob.hide_viewport = False
    return ob
