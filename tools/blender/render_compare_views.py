"""
Fixed-camera turnaround renders for reference comparison.

Sets one camera + a neutral studio light rig, renders front/side/back/three-quarter
at a matched aspect ratio, so every iteration is judged from the same viewpoint.

Usage inside a live Blender session:
    exec(open(r"...\\render_compare_views.py").read())
    render_turnaround("out/", height=1.80)

Usage headless:
    blender -b file.blend -P render_compare_views.py -- --out out/ --height 1.80
"""

import bpy
import math
import os
from mathutils import Vector


def _ensure_world(bg=(0.045, 0.048, 0.055, 1.0)):
    world = bpy.data.worlds.get("RefWorld") or bpy.data.worlds.new("RefWorld")
    world.use_nodes = True
    nt = world.node_tree
    bg_node = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
    if bg_node is None:
        bg_node = nt.nodes.new('ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = bg
    bg_node.inputs['Strength'].default_value = 1.0
    bpy.context.scene.world = world
    return world


def _area(name, loc, rot, size, energy, color=(1, 1, 1)):
    ld = bpy.data.lights.get(name)
    if ld is None:
        ld = bpy.data.lights.new(name, 'AREA')
    ld.type = 'AREA'
    ld.size = size
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(ob)
    ob.data = ld
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def _scene_bounds():
    """World bounds from evaluated vertices: bound_box is stale after mesh edits."""
    deps = bpy.context.evaluated_depsgraph_get()
    mins = Vector((1e9,) * 3)
    maxs = Vector((-1e9,) * 3)
    found = False
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.hide_render:
            continue
        ev = ob.evaluated_get(deps)
        me = ev.to_mesh()
        if me is None or len(me.vertices) == 0:
            ev.to_mesh_clear()
            continue
        found = True
        mw = ob.matrix_world
        for v in me.vertices:
            p = mw @ v.co
            for i in range(3):
                mins[i] = min(mins[i], p[i])
                maxs[i] = max(maxs[i], p[i])
        ev.to_mesh_clear()
    if not found:
        return Vector((-0.5, -0.5, 0)), Vector((0.5, 0.5, 1.8))
    return mins, maxs


def setup_camera(lens_mm=85.0, margin=1.12):
    mins, maxs = _scene_bounds()
    center = (mins + maxs) * 0.5
    height = maxs.z - mins.z
    # frame vertically at a distance that fits `height` with margin
    sensor = 36.0
    res_x, res_y = 1024, 1024
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.render.resolution_percentage = 100
    vfov = 2 * math.atan(sensor * (res_y / res_x) / (2 * lens_mm))
    dist = (height * margin * 0.5) / math.tan(vfov * 0.5)

    cam = bpy.data.objects.get("RefCam")
    if cam is None:
        cd = bpy.data.cameras.new("RefCam")
        cam = bpy.data.objects.new("RefCam", cd)
        bpy.context.scene.collection.objects.link(cam)
    cam.data.lens = lens_mm
    cam.data.sensor_width = sensor
    bpy.context.scene.camera = cam
    cam.location = (center.x, center.y - dist, center.z)
    cam.rotation_euler = (math.radians(90), 0, 0)
    return cam, center, dist, height


def setup_lighting(center, height, key_scale=1.0, fill_scale=1.0, rim_scale=1.0):
    """Three-point rig scaled to subject height.

    Energies scale with height squared so the same rig reads identically at any
    asset scale. The reference sheet is a dark, moody concept panel, so the
    default key here is deliberately low: a bright studio setup makes every
    material read two stops lighter than the sheet and fails the value histogram
    for reasons that have nothing to do with the model.
    """
    _ensure_world((0.020, 0.021, 0.024, 1.0))
    key = _area("Key", (center.x - height * 0.9, center.y - height * 1.3, center.z + height * 0.75),
                (math.radians(62), 0, math.radians(-32)),
                size=height * 0.9, energy=height * height * 12.0 * key_scale,
                color=(1.0, 0.96, 0.90))
    fill = _area("Fill", (center.x + height * 1.1, center.y - height * 1.0, center.z + height * 0.30),
                 (math.radians(78), 0, math.radians(48)),
                 size=height * 1.2, energy=height * height * 3.5 * fill_scale,
                 color=(0.72, 0.80, 1.0))
    rim = _area("Rim", (center.x + height * 0.2, center.y + height * 1.4, center.z + height * 1.0),
                (math.radians(115), 0, math.radians(178)),
                size=height * 0.8, energy=height * height * 8.0 * rim_scale,
                color=(0.82, 0.90, 1.0))
    return key, fill, rim


def setup_render(engine="BLENDER_EEVEE", samples=48, transparent=False):
    sc = bpy.context.scene
    try:
        sc.render.engine = engine
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    eevee = getattr(sc, "eevee", None)
    if eevee is not None:
        for attr in ("taa_render_samples", "taa_samples"):
            if hasattr(eevee, attr):
                setattr(eevee, attr, samples)
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'AgX' if 'AgX' in [
        v.name for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items
    ] else 'Filmic'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    return sc


VIEWS = {
    "front": 0.0,
    "side": 90.0,
    "back": 180.0,
    "three_quarter": 35.0,
}


def render_turnaround(out_dir, height=1.80, views=None, lens_mm=85.0):
    os.makedirs(out_dir, exist_ok=True)
    cam, center, dist, h = setup_camera(lens_mm=lens_mm)
    setup_lighting(center, h)
    setup_render()
    sc = bpy.context.scene
    paths = {}
    for name in (views or VIEWS):
        ang = math.radians(VIEWS[name])
        cam.location = (
            center.x + math.sin(ang) * dist,
            center.y - math.cos(ang) * dist,
            center.z,
        )
        cam.rotation_euler = (math.radians(90), 0, ang)
        p = os.path.join(out_dir, f"view_{name}.png")
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths[name] = p
        print("RENDERED", p)
    print("CAMERA lens=%smm dist=%.3fm height=%.3fm" % (lens_mm, dist, h))
    return paths


if __name__ == "__main__":
    import sys
    out = "out"
    h = 1.80
    a = sys.argv
    if "--" in a:
        i = a.index("--")
        rest = a[i + 1:]
        for j, tok in enumerate(rest):
            if tok == "--out":
                out = rest[j + 1]
            if tok == "--height":
                h = float(rest[j + 1])
    render_turnaround(out, height=h)
