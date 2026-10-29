---
name: gamedev-foliage
description: >
  Fix foliage that looks like paper cards, a frozen world, or grass that costs too much.
  Use for canopy normals, wind, cutout leaves, and instanced ground cover.
license: Apache-2.0
compatibility: Engine-agnostic principles; ready-to-copy shaders for Godot 4.x (Forward+ or Mobile).
metadata:
  engine: any
  category: gamedev-world
  difficulty: intermediate
---

# Foliage and Vegetation

Foliage fails in three recognisable ways, each with a cheap fix:

| Looks like | Cause | Fix |
|---|---|---|
| Paper cards; noisy light/dark patches across a canopy | Each card lit by its own flat normal | Canopy (radial) normals |
| A photograph — nothing moves | No vertex motion | Wind weighted by vertex colour |
| Pasted on the floor; bare ground between props | Grass ≠ ground colour; no ground cover | Root-colour match, instanced cover, wear masks |

Cost is dominated by **overdraw**, **shadow casters**, and **instances × draw distance** —
not triangle count.

## When to use

- Trees, bushes, hedges built from alpha-cutout cards; grass, flowers, ground clutter.
- Vegetation is the most fake-looking element of a scene.

## When not to use

- Solid-mesh stylised trees (no cards) — smooth normals in the DCC.
- Biome placement over terrain — `gamedev-world-from-data`; this skill shades and scatters.

## Ready-made shaders (copy, don't retype)

| File | Use |
|---|---|
| `assets/leaf_canopy.gdshader` | Leaf cards: radial normals + wind; uniforms `canopy_center`, `canopy_radii`, `radial_blend`, `wind_noise`, `wind_strength` |
| `assets/grass_wind.gdshader` | Ground cover: root→tip colour, tip² bend, normals bent up |

Not yet run in Godot; compile and render are unverified. Copy the file into the project and assign a noise
texture; read the shader source only when changing behaviour.

## Step 1 — Canopy normals (leaf cards)

A tree is a volume: replace each card's normal with the direction from the canopy centre to
the vertex, so the canopy shades as one soft blob — lit side, shaded side. Bake it in the DCC
(Blender: Data Transfer of normals from an ellipsoid proxy) or use `leaf_canopy.gdshader`.

- `radial_blend` < 1.0 keeps a little per-card variation; 1.0 looks like a ball.
- With culling disabled Godot flips back-face normals; the shader flips them back. **Orbit
  the tree**: the lit side must stay lit from behind. If it inverts, remove the
  `FRONT_FACING` block.
- Vertex shaders have no derivatives — sample with `textureLod(..., 0.0)`.
- Canopy centre is object space: origin at trunk base, centre at canopy height (or per
  instance via `INSTANCE_CUSTOM`).

## Step 2 — Wind that reads as wind

- **Weight by vertex colour**: trunk base 0, branches ~0.3, leaf tips 1. Without weights the
  whole plant slides.
- **World-space noise** drives it, so gusts travel across the field and neighbours move
  together. A scrolling noise texture is cheaper than layered sines.
- **Two frequencies**: slow sway plus small fast flutter; centimetres, not metres.
- **`TIME`**, never per-frame increments — frame-rate independent.
- Offsets are object space; fine for scatter. For a hero tree in a storm, transform the
  offset by the inverse model matrix.

## Step 3 — Transparency: cheapest that looks right

| Mode | Use for | Cost / caveat |
|---|---|---|
| Alpha scissor (cutout) | Default for leaves and grass | Opaque pipeline, correct shadows; edges alias |
| Alpha-to-coverage (`ALPHA_ANTIALIASING_EDGE` + `ALPHA_TEXTURE_COORDINATE`) | Smooth cutout edges | Needs MSAA |
| Alpha blend | Soft fringes only | Sorting errors, no shadows, most overdraw |
| `depth_prepass_alpha` | Blended foliage that must sort | Extra depth pass |

Trim card geometry close to the leaf: transparent pixels cost as much as visible ones.

## Step 4 — Ground cover: instanced, chunked, distance-limited

1. **One `MultiMeshInstance3D` per chunk** (~25–50 m). Culling, LOD and visibility range
   apply to a whole MultiMesh — one giant one is never culled.
2. **`visibility_range_end`** per chunk (grass 30–80 m) with `visibility_range_end_margin`
   and fade mode, so it dissolves instead of popping.
3. **`cast_shadow = SHADOW_CASTING_SETTING_OFF`** on grass; contact darkness comes from SSAO
   and the root colour.
4. **Per-instance colour** (`use_colors`) for hue/height variation.
5. **Density mask**: nothing on paths, doorways, play spaces, spawn points.
6. Start low (the reference scene: 20,000 blades over a village) and raise density only while
   the ablation numbers allow (`gamedev-godot-visual-polish` Step 2).

## Step 5 — Sit vegetation in the ground

- **Root colour = ground colour**, within a few values in a screenshot.
- Ground variation: 2–3 greens on large-scale noise, plus a worn dirt mask along paths and at
  doorways.
- Contact: SSAO or a baked darker ring under trees and bushes.
- Clusters along walls, fences and path edges — not uniform scatter.

## Verification

- [ ] Orbit a tree: canopy shades as a volume from every side
- [ ] Wind: roots fixed, tips move; neighbours move together; same at 30 and 144 fps
- [ ] Grass: shadows off, chunked MultiMesh, visibility range with fade
- [ ] Paths, doorways, spawn points free of instances
- [ ] Root colour within a few values of the ground under it
- [ ] Frame time with and without ground cover recorded at every viewpoint
- [ ] Overdraw checked on the densest view (Godot: Display Advanced > Overdraw)

## Related

- `gamedev-godot-visual-polish` — where foliage sits in the full pass
- `gamedev-performance` — overdraw, LOD, instancing budgets
- `gamedev-texture-authoring` — leaf atlases, mip alpha
- `gamedev-visual-artifacts` — alpha shimmer, LOD popping

## Knowledge base

T-65 (canopy normals), T-66 (weighted wind), T-67 (instanced ground cover with clear paths).
