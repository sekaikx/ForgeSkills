---
name: gamedev-art-direction
description: >
  Make mixed-source assets look like one game: one-page art bible, then a cheapest-first
  unification pass (grade, palette, materials, texel density, silhouettes), measured. Use
  when a scene has the "asset store look" or gameplay objects do not read.
license: Apache-2.0
compatibility: Engine-agnostic. Measurement via tools/refmatch and tools/texture (Python).
metadata:
  engine: any
  category: gamedev-assets
  difficulty: intermediate
---

# Art Direction and Cohesion

The "asset store look" is rarely low quality — it is **inconsistency**: one pack is
hand-painted, one photoscanned, one low-poly flat; texel density varies 4×; one set of
materials is glossy plastic and the next is chalk. Each asset is fine; together they read as
a collage. Settings and post can unify a cohesive set (`gamedev-godot-visual-polish`); they
cannot reconcile five art styles. That needs rules, then a pass.

Readability outranks beauty: the player must find the path, the enemy and the pickup before
anyone notices the palette.

## When to use

- Mixed asset packs in one scene; "it looks like a free asset demo".
- Before buying more assets — define what new assets must match.
- Interactive objects get lost against the background.
- A team or agent producing assets that drift from each other.

## When not to use

- A single cohesive asset set that just looks flat — `gamedev-godot-visual-polish` /
  `gamedev-lighting`.
- Matching one specific reference image — `gamedev-reference-reconstruction`.

## Step 1 — One-page art bible

Write the rules down before touching assets. Each rule must be checkable.

| Axis | Decide | Example rule |
|---|---|---|
| Shape language | Dominant shapes and proportions | "Chunky, rounded, 1.3× thick trims; no thin spikes on props" |
| Value structure | Where darks/lights live | "World mid-values; interactables and characters in the top or bottom 20% of value" |
| Palette roles | Colours per role, not per asset | "Ground: 3 desaturated greens/browns; accents: warm orange for interactables only" |
| Material response | Roughness/metal ranges | "No roughness below 0.35 except water/glass; metals only on trims" |
| Texel density | px per metre tiers | "Hero 1024 px/m, standard 512, background 256" |
| Detail hierarchy | Where detail concentrates | "Detail at eye height and at interaction points; plain above 3 m" |
| Edges | Hard vs soft, outlines | "Bevelled edges on all hard-surface props; no outlines" |
| Lighting & grade | Time of day, key colour, fog colour | "Late afternoon, warm key, cool sky fill, blue-grey fog" |

## Step 2 — Unification pass, cheapest first

Stop as soon as the scene passes the checks in Step 3; each step costs more than the last.

1. **Global light and grade.** One sun direction and colour, one sky, one tonemapper, one
   fog colour, one LUT. Shared light alone pulls a surprising amount together.
2. **Palette remap.** Push outlier assets toward the palette roles: hue/saturation shifts in
   the material, a shared colour-ramp texture, or a gradient map in the shader. Desaturate
   before you recolour — saturation mismatch is the commonest tell.
3. **Material normalisation.** Clamp roughness and albedo into the bible's ranges with a
   shared master material/shader that all assets inherit, so one parameter change propagates.
4. **Texel density.** Measure, then re-UV or rescale textures for the worst offenders.
   A blurry crate next to a crisp barrel breaks the illusion more than either alone.
5. **Silhouette and detail.** Replace or kitbash the assets whose *shapes* break the shape
   language. Last because it is the most expensive.
6. **Optional stylisation layer** (outline, posterise, painterly normal smoothing) applied to
   everything — only if the bible calls for it. A stylisation shader on half the assets
   makes the inconsistency worse.

## Step 3 — Measure, do not eyeball

| Check | How | Pass |
|---|---|---|
| Value read | Screenshot → greyscale | Interactables and characters separate from the background by value alone |
| Palette | `python tools/refmatch/palette_report.py --palette bible_palette.json --render shot.png` | Mean ΔE ≤ 12 (tool verdict PASS); and no large entry in the printed render clusters sits far from every bible role |
| Texel density | `python tools/texture/uv_density.py --obj asset.obj --texel 2048 --max-ratio 2` | Within 2× of the tier target; ratio check passes |
| Same-hand test | Crop 6 random assets side by side on grey | They look like one artist made them |
| Distance test | Look at near, mid and far viewpoints | Detail density falls off with distance; no noisy far field |
| Colour redundancy | View with a colour-blind simulation | Gameplay meaning also carried by shape or value, not hue alone |

Extract a palette from a reference or key frame to seed the bible:
`python tools/refmatch/palette_report.py --extract keyframe.png --k 8 --out bible_palette.json`.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Graded scene still looks like a collage | Shapes/texel density differ | Steps 4–5; grading only unifies colour |
| Everything unified, nothing readable | Interactables share world palette/value | Reserve an accent colour and value band for gameplay |
| Over-saturated "mobile game" look | Saturation used for interest instead of value | Lower saturation globally; create interest with value and light |
| Outline shader makes it worse | Applied to some assets only, or thickness in pixels varies with distance | Apply to all or none; distance-scaled width |
| New assets drift again | Rules not written or not checked | Run Step 3 checks on every asset import |

## Verification

- [ ] Art bible written: every axis has a checkable rule
- [ ] Global light, fog and grade shared by the whole scene
- [ ] Palette report PASS, and no large render cluster far from every bible role
- [ ] Texel density within 2× of tier for every visible asset
- [ ] Greyscale screenshot: interactables readable by value alone
- [ ] Same-hand test passed on 6 random assets
- [ ] Gameplay meaning not carried by hue alone

## Related

- `gamedev-godot-visual-polish` — the global light/grade step in Godot
- `gamedev-texture-authoring` — texel density, material maps
- `gamedev-modular-kit` — consistent kits by construction
- `gamedev-visual-iteration` — measure-compare-fix loop
- `gamedev-lighting` — value structure through light

## Knowledge base

T-71 (cohesion pass), T-61 (tonemap and grade), T-63 (albedo discipline).
