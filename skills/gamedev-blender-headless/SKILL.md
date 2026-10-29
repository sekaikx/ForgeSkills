---
name: gamedev-blender-headless
description: >
  Script Blender for builds, batches, renders, and exports. Use for programmatic modelling,
  many assets, or choosing headless vs MCP vs clicking. Blender 4.x and 5.x.
license: Apache-2.0
compatibility: Blender 4.2+ / 5.x. Optional live control through the Blender MCP server.
metadata:
  engine: blender
  category: gamedev-pipeline
  difficulty: intermediate
---

# Blender headless — script everything

The value of scripting Blender is not saving clicks. It is that a wrong roof becomes a
one-line change and a re-run instead of a rebuilding session. Treat the scene as build
output, not as hand-crafted state.

## When to use

- Building geometry procedurally or from measured numbers.
- Batch work: many variants, many renders, many exports.
- Any task that will need more than two iterations.
- Controlling a live Blender session programmatically.

## When not to use

- One-off sculpting or hand-modelling that will never be repeated.
- Final hero detail work where interactive feedback is genuinely faster (do the blockout
  and the export by script anyway).

## Two execution modes

**Headless** — deterministic, CI-able, no UI state involved:

```
blender.exe -b -P tools/blender/character_blockout.py -- --height 1.80 --out out/explorer_blockout.blend
```

`-b` runs without UI. Everything after `--` is yours; parse it from `sys.argv`.
Save the file at the end if the output must persist:

```python
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
```

**Live session** — for iterating against the user's open file. Use the MCP tool
`execute_blender_code` to `exec` a script inside the running instance, and `look` to see the
result. Same scripts work in both modes if you keep them `exec`-safe:

```python
ns = {"__name__": "not_main"}          # stops the __main__ block from firing
exec(compile(open(script, "r", encoding="utf-8").read(), script, "exec"), ns)
ns["build"](1.80)
```

Do not import your build module in a live session without reloading it — Blender caches
modules, and you will debug a fix that is already on disk:

```python
import importlib
importlib.reload(my_build_module)
```

## Script structure that survives iteration

```python
"""One paragraph: what this builds, units, orientation, entry point."""

import bpy, bmesh, math
from mathutils import Vector, Matrix

# 1. PARAMETERS — all tunables at the top, in metres
PROPORTIONS = {...}       # fractions of height, from the reference
PALETTE = {...}           # sampled hex/linear values, named by role

# 2. PURE HELPERS — geometry builders with no scene state
def capsule(...): ...
def loft(...): ...

# 3. BUILD — idempotent: clears its own collection, rebuilds
def build(height=1.80): ...

# 4. REPORT — prints measured facts, so the caller can assert on them
def report(): ...

if __name__ == "__main__":
    build(); report()
```

**Idempotence is mandatory.** `build()` must be safe to run repeatedly. Clear the collection
it owns at the start:

```python
col = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
for ob in list(col.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
```

Otherwise iteration duplicates geometry and every measurement drifts.

## Units and orientation

| Convention | Value |
|---|---|
| Unit system | metric, scale 1.0, **1 BU = 1 m** |
| Up axis | +Z |
| Character forward | **-Y** (front camera sits at -Y looking +Y) |
| Origin | at ground between the feet, or at the base of the prop |

Assert it at the top of the script; a scale slip ruins every downstream number:

```python
assert abs(bpy.context.scene.unit_settings.scale_length - 1.0) < 1e-6
```

## API pitfalls that cost hours

### `bound_box` is cached

Right after editing mesh data, `object.bound_box` still reports the **previous** mesh. A
validator built on it will pass or fail on stale numbers. Read evaluated vertices:

```python
deps = bpy.context.evaluated_depsgraph_get()
ev = ob.evaluated_get(deps)
me = ev.to_mesh()
for v in me.vertices:
    p = ob.matrix_world @ v.co
ev.to_mesh_clear()
```

### Translate-then-rotate rotates about the origin

```python
# WRONG: verts moved to `center`, object origin still at world zero -> swings away
for v in bm.verts: v.co += Vector(center)
ob.rotation_euler = (0, math.radians(90), 0)

# RIGHT: build local, orient the mesh, then place the object
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                 matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
ob.location = Vector(center)
```

This bug is invisible in a single view and catastrophic in a silhouette metric — an object
can sit a metre and a half off to the side.

### Loft rings with mismatched vertex counts

A quad band needs equal counts on both rings. Declare ring resolution once and resample all
rings to it:

```python
sides = max(int(r[3]) for r in rings)   # do not trust per-ring values
```

### Editing coordinates in the wrong space

`v.co` is **local**. If a mesh was built around a centre, tapering with a world-space
absolute (`v.co.z *= 0.62`) collapses it toward the world origin. Always taper about the
feature's own centre:

```python
v.co.z = centre_z + (v.co.z - centre_z) * factor
```

### Enum identifiers change between versions

Never hardcode render engines or file formats. Read the current value and assign inside a
`try/except TypeError`, whose message lists valid options:

```python
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
```

Look shader nodes up by `type`, never by localized name:

```python
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
```

### Materials: colors go on shader inputs

`material.diffuse_color` affects only the viewport. Set `Base Color` on the Principled BSDF.
Input socket names drift between versions — guard optional ones:

```python
for key in ("Specular IOR Level", "Specular"):
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = 0.4
        break
```

## Rendering for comparison

Render with **transparent film** and RGBA. It gives an exact silhouette mask; colour-keying a
lit gradient backdrop is guesswork that produces unexplainable metrics.

```python
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
```

Scale light energies with **height squared** so the same rig reads identically at any asset
scale. Keep the camera in a function so every pass is framed identically:

```python
def setup_camera(lens_mm=85.0, margin=1.12, res=(1024, 1024)): ...
```

Use 85 mm for characters and props (minimal perspective distortion), 24-35 mm for
environments.

## Export checklist

```
[ ] apply modifiers or enable export-time application
[ ] forward axis matches the engine (+Y or -Z depending on target; verify by re-import)
[ ] scale is 1.0, no unapplied object scales
[ ] materials export with textures packed or copied alongside
[ ] re-import the file and measure it — an exporter's exit code proves nothing
```

## Which driver

Headless and MCP both write Python. Headless is the default for a pipeline: parallel
processes, no shared screen, and a script you can re-run with no agent. MCP is for one
prop you want to watch; its viewport check is faster than a full render. Clicking the UI
lost a timed test on cost and on the model. Numbers, the edit-round upset, and the
five-agent queue: `references/mcp-vs-headless.md` (T-73).

## Reporting

Print measured facts so a caller can assert without parsing the scene:

```
MEASURED height : 1.7820 m  (target 1.800)  err +1.0%
MEASURED width  : 0.5200 m
TRIANGLES       : 10032
OBJECTS         : 18
```

## Related

- `gamedev-procedural-modeling` — geometry techniques and topology
- `gamedev-reference-reconstruction` — the measured build loop
- `gamedev-texture-authoring` — baking and map derivation
- `gamedev-animation` — rigs and clips by script

## Knowledge base

T-09 (headless scripts as the iteration unit), T-73 (when MCP or computer-use loses),
T-11 (grid scale), T-14 (measure the drawing), T-20 (batch CLI with orientation QA),
T-58 (kit as reuse unit).
