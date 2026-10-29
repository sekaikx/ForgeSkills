---
name: gamedev-texture-authoring
description: >
  Author game textures: derive roughness/normal/AO from albedo, make seamless tiles, set
  texel density, pack atlases, bake procedural detail. Use when surfacing models, fixing
  tiling seams, or when materials look flat and plastic. Not for scene lighting (lighting)
  or engine settings.
license: Apache-2.0
compatibility: Blender 4.2+/5.x for baking. Python tooling in tools/texture/ (Pillow + numpy).
metadata:
  engine: blender
  category: gamedev-assets
  difficulty: advanced
---

# Texture authoring — make surfaces read as material

The single most common failure in AI-generated assets is not geometry. It is that everything
reads as uniformly smooth plastic because base color is the only channel that carries
information.

## When to use

- A model has materials but looks flat, plasticky or "default".
- Textures visible tiling seams.
- You need PBR maps but only have an albedo image.
- An atlas must be packed and texel density unified.

## When not to use

- Flat stylized work where a single color is the intended look.
- UI, which is not a PBR problem.

## The channel budget

You do not need four hand-painted maps. You can derive most of them:

| Map | Derive from albedo? | How |
|---|---|---|
| Roughness | yes, roughly | luminance inverted, then curve; darker = glossier for leather/metal, lighter = rougher for cloth |
| Normal | yes, partially | high-pass / Sobel of luminance, scaled small — surfaces detail, not form |
| AO | yes, poorly | luminance in crevices; real AO needs geometry, use a bake |
| Height | yes, for stylized | luminance as displacement reference |
| Metallic | no | must be authored (mask of metal regions) |

**Caveat that matters:** derived maps are a shortcut for detail, not a substitute for
material understanding. Leather is rough with soft specular; metal is metallic with a sharp
highlight; cloth is rough with sheen. If you derive roughness by inverting luminance globally,
a dark leather and a dark cloth become identical. Segment by material first, then derive per
region.

## Roughness is the most important channel

Most "flat plastic" problems are roughness problems. Rules that hold almost universally:

- **Vary roughness across the surface.** A perfectly constant roughness is the tell.
- **Roughness range 0.25-0.95** for most real materials. 0.0 is mirror; 1.0 is chalk.
- **Break it up at the scale of the object**, not at pixel scale: patches, wear, handling.
- **Cloth: 0.85-0.95.** Leather: 0.45-0.65. Worn metal: 0.30-0.45. Polished metal:
  0.05-0.20. Skin: 0.45-0.60.

## Texture scale must match physical size

The most common scale error: a 2 m wall and a 0.2 m crate sharing a texture whose features
are the same pixel size. The wall's grain looks like boulders; the crate looks like a
mountain.

**Texel density** is pixels per metre. Pick it and hold it:

```
TEXEL_DENSITY = 512 px/m         (typical for a mid-detail game asset)
a 2 m wall with a 2048 map       -> 1024 px/m  (too high; waste)
a 0.2 m crate with a 512 map     -> 2560 px/m  (absurd)
a 2 m wall with a 1024 map       -> 512 px/m   (correct)
```

In shader terms, drive tiling from physical size, not a hand-picked number:

```python
uv_scale = object_size_m * TEXEL_DENSITY / texture_resolution_px
```

If two objects of different sizes share a material, either accept the mismatch (small,
distant props) or give them separate UV sets at matching density.

## Seamless tiling

A tiling texture must wrap without a visible join. The test is not "does it look OK" but
"is the gradient across the seam continuous".

```python
# wrap-around difference across the vertical seam
col0, colN = arr[:, 0], arr[:, -1]
seam_step = np.abs(col0.astype(float) - colN.astype(float)).mean()
interior_step = np.abs(arr[:, 1:-1].astype(float) - arr[:, :-2].astype(float)).mean()
ratio = seam_step / max(1e-6, interior_step)
# ratio near 1.0 = seamless; > 1.6 = visible seam
```

Fixes, in order of preference:

1. **Author it tileable** (offset the image by half, fix the seam, offset back).
2. **Mirror-blend the edges** (cheap, but creates a symmetry tell).
3. **Use a larger non-tiling texture** with a triplanar or world-space projection.

## Atlas packing

```
[ ] consistent texel density across islands
[ ] 4-8 px gutters between islands
[ ] islands oriented consistently (grain direction, course direction)
[ ] occupied ratio > 70%
[ ] small islands grouped in a strip, not scattered
```

Draw calls scale with materials, not with meshes. One atlas for a whole kit is usually the
difference between 12 and 90 draw calls.

## Baking procedural detail

Procedural noise is fine for a hero shot and wrong for a shipping asset (cost per pixel,
no control, no LOD). Bake it:

```
1. build the procedural material on the high-poly / reference mesh
2. UV the low-poly
3. bake diffuse, roughness, normal to the low-poly's UVs
4. assign the baked set to the low-poly
5. keep the procedural source in the file, muted, for future edits
```

Bake at the target texel density, not higher "to be safe" — you will pay for it in memory.

## Material checklist

```
[ ] base color: measured/sampled, not invented
[ ] roughness: varied, in the right band for the material family
[ ] metallic: 0 except actual metal
[ ] normal: present, subtle, scale-matched
[ ] texel density matches physical size
[ ] tiling checked numerically across the seam
[ ] no pure black (0,0,0) or pure white (255,255,255) in albedo
[ ] viewed under the target lighting, not a neutral studio
```

## Tools

| Script | Purpose |
|---|---|
| `tools/texture/tex_to_maps.py` | Derive roughness, normal and cavity maps from one albedo |
| `tools/texture/tile_seam_check.py` | Measure wrap-boundary continuity; writes a tiled preview |
| `tools/texture/uv_density.py` | Per-part texel density from an OBJ, flags density spread |

## Related

- `gamedev-modular-kit` — atlas strategy for kits
- `gamedev-lighting` — how materials read under the actual light rig
- `gamedev-performance` — texture memory budgets
- `gamedev-blender-headless` — scripting bakes

## Knowledge base

T-15 (roughness and normal from albedo), T-16 (projected dirt), T-17 (roughness vs texture
scale), T-18 (atlas allocation), T-19 (baked leaf cards).
