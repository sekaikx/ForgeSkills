---
name: gamedev-procedural-modeling
description: >
  Build 3D geometry from parameters and code: lofts, capsules, sweeps, scattered props,
  fracture-ready shapes. Use when an asset must be regenerable, parameterized, or produced
  in variants, and when deciding which parts should be procedural versus hand-authored.
license: Apache-2.0
compatibility: Blender 4.2+/5.x (bpy, bmesh). Techniques transfer to any DCC with a scripting API.
metadata:
  engine: blender
  category: gamedev-assets
  difficulty: advanced
---

# Procedural modelling — parameters over sculpting

Procedural geometry is worth it exactly when a number should control a shape. It is a trap
when the shape's identity comes from a one-off silhouette.

## When to use

- Repeated or parametric forms: straps, pipes, fences, rails, foliage, rock clusters.
- Anything that needs variants (5 crates, 3 building tiers, 12 enemy sizes).
- Blockouts at measured proportions.
- Anything that must be regenerated after a spec change.

## When not to use

- A distinctive hero silhouette (a specific face, a unique weapon head, a signature hat).
- Organic forms needing sculpted asymmetry.
- Anything where "adjust one number" is not actually desirable.

**Decision rule:** if the shape can be described as *dimensions + profile*, script it. If it
can only be described as *a drawing*, model it (or import a base mesh and script the
adjustments).

## The primitives that cover most needs

| Builder | Use | Key parameters |
|---|---|---|
| **Capsule / tapered tube** | limbs, pipes, branches, handles | p0, p1, r0, r1, segments, sides |
| **Loft** | garments, torsos, vases, terrain columns | ordered rings of (center, rx, ry) |
| **Sweep along curve** | cables, rails, ropes, straps | path points + profile radius |
| **Rounded box** | crates, packs, blocks, machine parts | size, bevel radius, bevel segments |
| **Scatter** | rocks, debris, foliage, bolts | surface, count, size range, seed |
| **Extrude + inset** | panels, plating, armour | profile loop, inset distance, depth |

Every builder should take **metres** and return an object with a stable name. Nothing should
read scene state; nothing should depend on selection or the active object.

## Loft: the workhorse

A loft is an ordered list of rings, each with a centre and elliptical radii. It covers
torsos, garments, vases, tapered columns and table legs.

```python
def loft(name, rings, close_bottom=True, close_top=True, col=None, material=None):
    sides = max(int(r[3]) for r in rings)     # resample ALL rings to this count
    verts, faces, ring_idx = [], [], []
    for (c, rx, ry, _) in rings:
        idx = []
        for j in range(sides):
            a = 2 * math.pi * j / sides
            verts.append((c.x + math.cos(a) * rx, c.y + math.sin(a) * ry, c.z))
            idx.append(len(verts) - 1)
        ring_idx.append(idx)
    for i in range(len(ring_idx) - 1):
        a, b = ring_idx[i], ring_idx[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            faces.append([a[j], a[k], b[k], b[j]])
    ...
```

Design notes that matter:

- **Ring resolution must be uniform** or the quad band crashes / degenerates.
- Put rings at *feature heights*, not evenly spaced. A coat needs a ring at the hem, the
  knee, the hip, the waist and the chest, because those are where its radius changes.
- Offset the ring centre to lean or curve a form (a leaning tower, a curved horn).
- Elliptical radii (`rx != ry`) are how a body becomes a body rather than a barrel.

## Capsule: limbs and pipes

```python
def capsule(name, p0, p1, r0, r1, segs=16, sides=16):
    axis = (Vector(p1) - Vector(p0))
    length = axis.length
    axis.normalize()
    # build orthonormal frame, then a tapered tube with hemispherical caps
```

Build it along an arbitrary axis, not just Z — a limb from shoulder to elbow is a diagonal.
The frame must be computed from the axis, never from a fixed up-vector (which degenerates
when the axis is vertical):

```python
up = Vector((0, 0, 1)) if abs(axis.z) < 0.99 else Vector((0, 1, 0))
x = axis.cross(up).normalized()
y = axis.cross(x).normalized()
```

## Garments: offset shells, not new anatomy

Clothing should be the body plus clearance, then reshaped. Never re-derive anatomy for a
garment.

```
1. take the body volume's rings
2. add clearance (0.006-0.020 m depending on fabric)
3. change the radius PROFILE at the garment's own feature heights
4. open the front where the garment opens (pull forward verts apart)
```

A coat is not a bigger torso. Its profile differs: it pinches at the waist, flares at the
hem, and its hem is often the widest point of the whole figure. Measure those three
widths and the silhouette follows.

## Before/after: what a profile change does

Two coat profiles against a reference, same everything else:

| Profile | Chest width | Hem width | Band error |
|---|---|---|---|
| fitted vest, no flare | 0.32 m | 0.28 m | 30-47% at bands 7-9 |
| measured long coat | 0.46 m | 0.44 m | 1-3% at bands 3-6 |

The band profile names the defect for you: bands 7-9 too narrow means *the lower garment is
missing or too tight*, not "the model looks off".

## Topology rules

- **Quads on curved surfaces**, triangles only at caps and hard corners.
- **Match ring counts** when joining two lofts, or accept a visible seam and hide it under a
  belt/strap (that is what real garments do).
- **Smooth shading with an angle limit** (30-45°) so hard edges stay hard:
  mark `use_smooth` per polygon and let auto-smooth handle the rest.
- **No zero-area faces.** Taper to a small radius, never to exactly 0.
- Keep the object origin meaningful — at the pivot you would animate or place.

## Bevels

Bevel is what separates "programmer geometry" from "asset". A 4-10 mm bevel on a hard edge
catches light and reads as a manufactured object.

```python
bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts),
                offset=bevel, segments=3, profile=0.55, affect='EDGES')
```

Use `segments=1` for chunky stylized forms, `3` for believable hard-surface, `5+` only where
the camera gets close.

## Scatter with a seed

```python
rng = random.Random(seed)            # seeded: same output every run
for i in range(count):
    x, y = sample_in_area(rng)
    scale = rng.uniform(smin, smax)
    rot = rng.uniform(0, math.tau)
```

Always seed. An unseeded scatter cannot be iterated on, because every render is a different
asset.

## Naming and grouping

```
Body_Torso, Body_Head, Coat, Hood, Pack_Body, Pack_Strap_L, Axe_Head
```

Group into collections by role: `Body`, `Kit`, `Props`. This is what lets a validator find
stray geometry and lets a renderer isolate parts.

## Related

- `gamedev-blender-headless` — how to run these scripts, and the API pitfalls
- `gamedev-modular-kit` — building kits whose parts combine
- `gamedev-reference-reconstruction` — when the parameters come from a reference
- `gamedev-texture-authoring` — surfacing the result

## Knowledge base

T-11 (grid scale), T-58 (parameterized kit reuse), T-09 (script as iteration unit), T-19
(leaf cards / baked detail).
