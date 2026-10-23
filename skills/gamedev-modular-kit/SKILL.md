---
name: gamedev-modular-kit
description: >
  Design and build reusable modular asset kits — walls, buildings, props — that snap
  together on a grid, share a texture atlas, and support parameterized variants. Use when
  building a village, interior, dungeon or any environment from repeated parts instead of
  one-off meshes.
license: Apache-2.0
compatibility: Blender 4.2+/5.x. Grid and pivot rules apply in any engine.
metadata:
  engine: blender
  category: gamedev-assets
  difficulty: advanced
---

# Modular kits — build once, place many

A kit is not "a few props". It is a **closed set of parts with fixed rules** about size,
pivot, texture space and joinery, such that any legal combination assembles without gaps or
misalignment.

## When to use

- Environment built from repeated structure: villages, interiors, dungeons, stations.
- The user wants variety without proportional cost growth.
- Content will be extended later by someone else (rules must be explicit).

## When not to use

- A single hero building with unique architecture.
- Organic terrain (see `gamedev-world-from-data`).

## Step 1 — Fix the grid before making anything

Choose one module size and never break it. Everything derives from it.

```
MODULE      : 2.0 m  (wall segment length, floor tile edge)
WALL_H      : 3.0 m  (storey height, floor to floor)
WALL_T      : 0.2 m  (thickness)
DOOR        : 1.0 x 2.1 m, centred in a module
WINDOW      : 0.9 x 1.2 m, sill at 1.0 m
PIVOT       : at the module's own origin, on the floor, at the corner facing -Y
```

Sizes must be **integer multiples or clean fractions** of the module. A 2.4 m wall in a 2.0 m
grid guarantees visible seams, and no amount of careful placement hides them.

**Pivot rule:** identical pivots across all parts of a family. If one wall pivots at its
left edge and another at its centre, assembly becomes guesswork.

## Step 2 — Define the kit's part list

Write it down before modelling. Every part earns its place by unlocking combinations.

| Family | Parts | Unlocks |
|---|---|---|
| Wall | straight, straight-window, straight-door, corner, end-cap | all room layouts |
| Floor | tile, tile-stairs, tile-hole | interiors, multi-storey |
| Roof | slope-30, slope-45, ridge, eave | silhouettes |
| Trim | beam, post, bracket, rail | visual rhythm |
| Prop | crate, barrel, bench, lantern | habitation |

A kit with 5 wall variants and 2 roof variants supports far more buildings than 20 unique
walls with one roof.

## Step 3 — Build one part properly, then parameterize

Model the straight wall first, with:

- **Manifold, quad-dominant topology**; no interior faces (they cost fill rate and show
  through at grazing angles).
- **Bevel on every hard edge** 4-8 mm, so it catches light.
- **UVs on a shared atlas** (see below), not per-part textures.
- **Pivot at the documented point**, scale applied, rotation zero.

Then parameterize the family from that one definition:

```python
def wall(length=2.0, height=3.0, thickness=0.2,
         openings=(), trim=True):
    """openings: list of (kind, u_center, width, sill, top) in metres."""
```

Every variant is the same function with different arguments. That is what makes a kit
maintainable: a change to wall thickness propagates to all variants.

## Step 4 — Share one atlas

One material and one atlas for the whole kit kills draw calls, and draw calls are usually
the binding cost in a built environment.

```
ATLAS 2048x2048
  [0.00-0.25] wall plaster         [0.25-0.50] wall stone
  [0.50-0.75] roof tile            [0.75-1.00] trim wood
   + a strip for small props: crate, barrel, metal fittings
```

Rules:

- **Consistent texel density** across all parts (e.g. 512 px per metre). Inconsistent
  density is the single most visible "asset pack" tell.
- **Gutters**: 4-8 px padding between islands to stop bleeding at mip levels.
- **Orient islands to the same axes** so wood grain and stone courses run consistently.
- Pack with a real packer, then check the occupied ratio. Below 70% means the atlas is too
  big or the islands are badly arranged.

## Step 5 — Assemble a test building

Never ship a kit without assembling a scene from it. The assembly is the test.

```
[ ] every joint closes with no gap at any rotation
[ ] no z-fighting where parts overlap
[ ] corner pieces align with straight pieces at both ends
[ ] roof meets wall at the chosen slope with no hole
[ ] the whole structure sits on the floor plane, pivots honoured
[ ] assembled scene draw calls within budget
```

Screenshot the assembly from three angles. A kit that looks fine part-by-part and broken
assembled is the normal failure.

## Step 6 — Variants without new geometry

Cheap variety comes from parameters and materials, not new meshes:

| Variation | Mechanism | Cost |
|---|---|---|
| Dimensions | swap module count | free |
| Damage | swap a subset of parts for cracked variants | small |
| Material | second atlas region / material instance | free |
| Decoration | procedural prop scatter | small |
| Silhouette | roof slope, extra storey | moderate |

## Anti-patterns

| Anti-pattern | Result | Fix |
|---|---|---|
| Sizes not on the grid | gaps and overlaps everywhere | re-derive all sizes from MODULE |
| Per-part textures | hundreds of draw calls | one atlas |
| Interior faces left in | fill-rate waste, visible at angles | delete non-visible faces |
| Pivot inconsistency | parts placed by hand, never reusable | standardize pivots |
| No assembly test | kit looks fine, scene is broken | always assemble before shipping |
| 40 unique walls | cost with no combinatorial gain | 5 variants x parameters |

## Related

- `gamedev-procedural-modeling` — the builders each part is made from
- `gamedev-texture-authoring` — atlas authoring and texel density
- `gamedev-performance` — draw-call budgeting for assembled scenes
- `gamedev-world-from-data` — placing kits on real terrain

## Knowledge base

T-58 (kit as the reuse unit), T-11 (grid scale), T-18 (atlas allocation), T-56 (asset
library allowance), T-57 (parameterized reuse).
