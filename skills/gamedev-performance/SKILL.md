---
name: gamedev-performance
description: >
  Hit frame budgets: draw-call reduction, LOD, decimation, occlusion, texture memory and
  detail budgeting by screen size. Use when a scene is slow, when planning budgets before
  content, or when deciding what detail is worth its cost.
license: Apache-2.0
compatibility: Engine-agnostic; Godot 4.x and Unity 6 profiler workflows.
metadata:
  engine: any
  category: gamedev-perf
  difficulty: advanced
---

# Performance — budget first, optimise second

Optimising without a budget is guessing. Set the budget, measure against it, and fix the
largest consumer. That order is the whole skill.

## When to use

- Frame time is over budget.
- Planning content and needing limits.
- Deciding whether detail is worth its cost.
- Assets are heavier than they need to be.

## When not to use

- Before anything is slow and before content exists (premature optimisation produces ugly
  work).
- When the frame rate is capped by vsync or a fixed timestep (measure first).

## Step 1 — Compute the budget from the target

```
TARGET     : 60 fps at 1080p
FRAME      : 16.67 ms total
  simulation : 4.0 ms
  rendering  : 9.0 ms
  UI/other   : 1.5 ms
  headroom   : 2.2 ms     <- always keep 10-15%
```

Never budget to 100%. Real hardware, background processes and thermal throttling will take
the rest.

Then derive content limits from measured cost:

```
draw calls   : target <= 200 for a mid-complexity scene (each ~20-60 us CPU)
triangles    : 1-3 M visible for desktop, 200-600 k for mobile
shadow casters: <= 60 active
texture memory: <= 1.5 GB desktop, <= 400 MB mobile
```

These are starting points; measure on the target hardware.

## Step 2 — Measure, and measure the right thing

```
GPU-bound  : lowering resolution improves frame time
CPU-bound  : lowering draw calls / physics improves frame time
```

That distinction decides everything. Check it first:

1. halve the render resolution — if frame time drops significantly, you are GPU-bound;
2. disable a system (shadows, particles, physics) — if frame time drops, that system is the
   cost.

Then measure with a profiler, and measure **the worst frame**, not the average. A 60 fps
average with 8 ms spikes reads as stutter.

## Step 3 — Draw calls first

Draw calls are usually the CPU bottleneck in a built environment, and the cheapest to fix.

| Technique | Effect |
|---|---|
| **Atlas + single material** | dozens of calls -> a handful |
| **Merge static meshes** by material | many objects -> one call |
| **Instancing** for repeated props | one call for N instances |
| **Texture arrays** for variants | one material, N textures |
| **Occlusion culling** | skip fully-hidden geometry |
| **Distance culling** on small props | skip sub-pixel objects |

Merge rule: merge by material, and only geometry that never moves independently. Merging the
whole level kills culling, so merge in spatial chunks (cells).

## Step 4 — LOD strategy

```
[ ] LOD by screen coverage, not only distance
[ ] 3 levels is usually enough: full, half, impostor
[ ] LOD transitions at the same screen size for all objects of a class
[ ] geometric LODs generated, then manually fixed at the silhouette
[ ] no LOD on the object the player is standing on
[ ] shadows use a lower LOD than the visible mesh
```

Automatic decimation destroys silhouettes first. Always inspect the lowest LOD's silhouette
against the highest; if the outline changes, the LOD will pop.

## Step 5 — Detail budgeting by screen size

The most useful habit: **budget detail by how many pixels an object occupies**.

```
< 32 px  : billboard or nothing
32-128   : low-poly, flat material, no shadows
128-512  : mid-poly, full material, contact shadow
> 512    : full detail, real shadow, small props welcome
```

This is why hero props get 40k triangles and background crates get 200. It is not arbitrary —
it is derived from screen coverage.

## Step 6 — Decimation with intent

When reducing an asset:

```
1. record the original bounds and silhouette
2. decimate to the target ratio
3. compare silhouette IoU against the original (>= 0.97 for LOD1, >= 0.90 for LOD2)
4. fix the outline manually where it deviates
5. re-check materials/UVs survived
```

An asset decimated to 30% with a changed outline reads as a different, worse asset. An asset
decimated to 30% with the same silhouette is free performance.

## Step 7 — Model tier testing

Test the actual tiers you intend to ship, not just the hero tier:

```
TIER A (hero)    : full detail, shadows, full material
TIER B (mid)     : 50% tris, no normal map, contact shadows
TIER C (distant) : 15% tris, flat color, no shadows, billboard at 200 m
```

Ship all three and verify at the distances and screen sizes they are actually used at.
"Optimised" assets that were only ever viewed up close are unverified.

## Step 8 — Asset library allowance

Reuse is the cheapest performance win and the cheapest production win. Define the library
explicitly:

```
LIBRARY (do not rebuild) : crates, barrels, fence, lantern, rock set, foliage cards
BESPOKE (build new)      : hero props, unique architecture, the player character
```

Every bespoke asset costs modelling, texturing, LODs, and memory. If a library asset is 80%
right, use it and adjust the material.

## Verification

```
[ ] measured on target hardware, worst frame within budget
[ ] draw calls within budget at the worst vantage point
[ ] visible triangles within budget
[ ] shadow casters within budget
[ ] texture memory within budget
[ ] no frame-time spikes > 2x average across a 60 s play session
[ ] LOD popping not visible in normal play
[ ] optimisations verified to actually improve frame time (measure before/after)
```

That last point is the one that gets skipped. Every optimisation must have a before and after
number, or it is superstition.

## Related

- `gamedev-modular-kit` — atlasing and instancing at the source
- `gamedev-texture-authoring` — texture memory and density
- `gamedev-world-from-data` — height-field LOD
- `gamedev-verification` — evidence discipline
- `gamedev-godot-visual-polish` — leave-one-out cost per graphics setting; cut quality before presence
- `gamedev-foliage` — instanced ground cover, overdraw

## Knowledge base

T-53 (height-field LOD window), T-54 (asset decimation), T-55 (model tier testing), T-56
(asset library allowance), T-57 (camera-centric detail budgeting), T-58 (parameterized kits).
