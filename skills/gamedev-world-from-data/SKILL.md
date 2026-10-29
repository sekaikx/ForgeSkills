---
name: gamedev-world-from-data
description: >
  Build terrain, roads, and rivers from real height data. Use for GIS or DEM worlds, spline
  roads, baked flow, and footprint buffers.
license: Apache-2.0
compatibility: Engine-agnostic. Python tooling for height grids; target Godot 4.x or Unity 6.
metadata:
  engine: any
  category: gamedev-world
  difficulty: advanced
---

# World from data — terrain that supports gameplay

Generated worlds fail in one of two ways: they look like noise, or they look fine and are
impossible to traverse. Both are solved by deriving the world from data with explicit rules,
then validating traversal.

## When to use

- Building a world from DEM/height data or a hand-authored heightmap.
- Connecting settlements with roads that must follow terrain sensibly.
- Rivers, lakes, floodplains.
- Multi-resolution terrain where distant landscape must stay cheap.

## When not to use

- Small handcrafted levels (0.5 km² or less) where authored layout is better.
- Pure interior spaces.

## Step 1 — Establish the elevation grid

```
GRID      : N x N samples, spacing in metres (e.g. 512 x 512 at 10 m = 5.12 km across)
VERTICAL  : height in metres, sea level = 0
RANGE     : record min/max BEFORE scaling anything
```

**Never normalize before recording the real range.** Slope, river flow and building placement
all depend on real-world gradients. A world normalized to 0..1 loses the scale that makes
those rules work.

Sanity checks that catch most bad imports:

```python
assert grid.shape == (N, N)
assert np.isfinite(grid).all()          # no NaN holes in the DEM
print("min %.1f  max %.1f  mean %.1f  std %.1f" % (grid.min(), grid.max(), grid.mean(), grid.std()))
```

A std near zero means you imported a flat plane. A max in the tens of thousands means the
units are centimetres or the projection is wrong.

## Step 2 — Slope and traversability

Derive slope from the gradient, then classify:

```python
dz_dy, dz_dx = np.gradient(grid, spacing)
slope_deg = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))
```

| Slope | Class | Gameplay |
|---|---|---|
| < 8° | buildable | structures, roads |
| 8-25° | walkable | general traversal |
| 25-40° | steep | slow, slide, blocked for vehicles |
| > 40° | cliff | impassable without special movement |

**Validate traversal before placing anything.** A road that crosses a 45° slope is a bug, not
a feature.

## Step 3 — Spline roads that respect terrain

```
1. pick endpoints (settlements, POIs)
2. use A* or a least-cost path over the slope cost field, NOT a straight line
3. fit a Catmull-Rom / Bezier spline through the path points
4. resample the spline at fixed arc length (2-5 m)
5. for each sample, set the road height to the terrain height, then SMOOTH the profile
6. carve the terrain to the road (cut and fill, within a max depth)
```

Cost function that produces believable roads:

```python
cost = 1.0 + slope_deg ** 1.6 * 0.08 + elevation_penalty
```

The exponent makes gentle slopes nearly free and steep slopes prohibitive, which is how real
roads behave. Pure distance produces roads that go straight up cliffs.

**Cut and fill limit:** cap the carve depth (e.g. 3 m). A road that creates a 20 m gash reads
as broken terrain, not engineering.

## Step 4 — Rivers by simulation, not by drawing

Hand-drawn rivers ignore hydrology and look wrong at every confluence. Simulate:

```
1. compute flow direction: steepest descent per cell (D8) or multi-flow (D-infinity)
2. accumulate flow: each cell's flow = its own + upstream contributions
3. rivers are cells where accumulation exceeds a threshold
4. widen the channel with accumulation (log scale)
5. carve the channel into the height field
6. lakes: local minima that accumulate water, filled to their spill elevation
```

```
flow_threshold_map = 0.002 * total_cells     # tune to density
channel_width = base_w + k * log(1 + accumulation)
```

This produces correct confluences, watersheds and widening downstream automatically. Drawing
rivers by hand requires reproducing all of that manually.

## Step 5 — Footprint buffers for placement

When scattering buildings, roads or props, build a **paint buffer** of occupied area so
nothing overlaps:

```python
occupied = np.zeros_like(grid, dtype=bool)

def can_place(x, y, radius_cells, slope_max=8.0):
    if slope_deg[y, x] > slope_max:
        return False
    r = radius_cells
    return not occupied[max(0,y-r):y+r+1, max(0,x-r):x+r+1].any()

def stamp(x, y, radius_cells):
    r = radius_cells
    occupied[max(0,y-r):y+r+1, max(0,x-r):x+r+1] = True
```

The buffer is what prevents the classic "three houses intersecting" artifact. Reserve space
for roads first, then buildings, then props — priority order prevents conflicts.

## Step 6 — Height-field LOD

Distant terrain must not be full resolution:

```
LOD0 (0-150 m) : full resolution, full detail
LOD1 (150-400 m) : half resolution, simplified material
LOD2 (400 m+)    : quarter resolution, flat-ish shading, no small props
```

Rules:
- **Fix LOD seams** by ensuring adjacent LOD tiles share edge vertex heights exactly (skirts
  or matching edge samples).
- **Cull detail by screen size**, not distance alone.
- **Do not LOD the ground under the player**, ever — visible popping where the player is
  standing is the worst case.

## Verification

```
[ ] elevation range recorded and plausible for the region
[ ] no NaN or hole cells
[ ] every road segment under the slope limit or explicitly marked
[ ] river network is acyclic and widens downstream
[ ] no overlapping structure footprints
[ ] a path exists from spawn to each objective (validate by pathfinding, not by eye)
[ ] LOD seam heights match at tile boundaries
[ ] frame time at the worst vantage point within budget
```

## Related

- `gamedev-modular-kit` — the structures placed on this terrain
- `gamedev-performance` — LOD and culling budgets
- `gamedev-lighting` — matching the world's atmosphere
- `gamedev-gameplay-systems` — nav validation on the generated world

## Knowledge base

T-40 (geoportal elevation grids), T-41 (spline roads), T-42 (offline river flow simulation),
T-43 (footprint paint buffer), T-53 (height-field LOD window).
