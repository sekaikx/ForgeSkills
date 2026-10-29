---
name: gamedev-godot-visual-polish
description: >
  Make a Godot 4 3D scene read finished using engine settings only (fog, tonemap, SSAO,
  glow), then measure each setting's frame cost. Use when a Godot scene looks default or
  graphics eat the budget. Not for light placement (lighting) or material detail (texture-
  authoring).
license: Apache-2.0
compatibility: Godot 4.3+ (AgX needs 4.4+). Forward+ for SDFGI/SSIL/SSAO/TAA; notes for Mobile and Compatibility.
metadata:
  engine: godot
  category: gamedev-world
  difficulty: intermediate
---

# Godot Visual Polish (settings, not assets)

Most "Godot looks bad" scenes are default settings, not bad assets: overhead white sun, grey
ambient, linear tonemap, no contact shading, no atmosphere. One ordered pass changes the look;
the second half of this skill finds out what each setting costs.

Two rules carry the skill:

1. **Add an effect only when you can name the problem it solves.** "Looks flat" is not a
   problem; "both visible faces of every building are equally bright" is.
2. **Separate presence from quality.** The sun's direction and colour are free; its shadow
   resolution and filtering are expensive. Reduce quality knobs first, remove presence last.

## When to use

- A Godot 3D scene that reads flat, grey, plastic or "asset flip".
- Before deciding the assets are the problem.
- Frame rate dropped after "making it pretty" and nobody knows which setting did it.
- Building Low/Medium/High presets.

## When not to use

- 2D games. Clashing art styles: `gamedev-art-direction` first. Specific bugs (shimmer, acne,
  leaks, stutter): `gamedev-visual-artifacts`.

## Step 0 — Baseline

1. **3 fixed viewpoints** as `Marker3D`: close, mid, far. Every comparison uses all three.
2. **Milliseconds with vsync off**, never capped FPS — "75 fps both ways" hides every saving.
3. **Renderer check** — unsupported settings are silently ignored:

| Feature | Forward+ | Mobile | Compatibility |
|---|---|---|---|
| SDFGI, VoxelGI, SSIL, SSAO, SSR, TAA, volumetric fog | yes | no | no |
| LightmapGI, ReflectionProbe, fog, glow, tonemap | yes | yes | yes (simplified) |
| Debanding | yes | yes | no |

4. Screenshot all three viewpoints: the "before".

## Step 1 — The pass, in order of impact

Each step changes what the next needs. Exact properties and values: `references/settings.md`
(read only the section for the current step).

| # | Change | Problem it solves | Key move | Cost |
|---|---|---|---|---|
| 1 | Sun direction + warmth | Every face equally lit | 20–40° elevation, side-on to main surfaces, warm colour | Direction free; shadows expensive |
| 2 | Sky ambient | Flat grey shadows | `BG_SKY` + `ambient_light_source = SKY`: cool fill vs warm key | Low |
| 3 | Tonemapper | Clipped highlights, muddy colour | AgX (4.4+) or Filmic; exposure after tonemapper; grade after | Low |
| 4 | SSAO (+ light SSIL) | Objects float, no contact | Radius ~1 m; **judge while moving** | Medium |
| 5 | Bounce light | Lifeless shade | Cheapest GI that fits; check albedo saturation first | Medium–high |
| 6 | Depth fog, aerial perspective | No depth | Depth fog layers distance; never hides the path | Low |
| 7–9 | Foliage normals/wind, ground variation, ground cover | Paper cards, frozen world, bare floor | `gamedev-foliage` | Low–medium |
| 10 | Character fill + practical lights | Character lost in shade | Fill light culled to character layer; lights with visible sources | Low w/o shadows |
| 11 | Camera FOV/DOF | Composition | Separate A/B — gameplay trade-off | Low |
| 12 | AA, debanding, vignette/grain | Jaggies, bands, framing | Subtle; Godot has no built-in vignette | Varies |

Greyscale check after step 1: lit and shaded faces of the same building must differ clearly
in value. If not, the sun is wrong and nothing later fixes it.

## Step 2 — Attribute cost per setting (leave-one-out)

From the finished scene, switch **one** setting off at a time, measure GPU ms at every
viewpoint, screenshot. Each setting gets two numbers: cost, and visible change.

1. Add `tools/godot/ablation_capture.gd` to a `Node` (or instantiate it from a `SceneTree`
   script), assign `WorldEnvironment`, sun, camera and viewpoint markers, run. It disables
   vsync, pins the camera, hides UI, pairs each "off" run with a fresh full run (cancels
   drift), adds a noise-floor run, writes screenshots and `ablation.json`, quits.
2. `python tools/godot/ablation_report.py --dir <folder> [--budget-ms 16.6]` ranks cost
   against visible change net of noise and flags **expensive-but-invisible** settings.
3. Reduce quality knobs before presence — table in `references/presets.md`.

Example values (unverified, not yet run in Godot): sun shadows 1.06 ms, MSAA 2× 0.66
ms, depth fog within noise (0.06 ms) — the fog stays, the shadow settings are where savings live.

## Step 3 — Foundation test

Remove the **first** improvement (the sun change) from the finished scene. Correct result:
the scene falls apart, because nothing replaces a good key direction. If other effects "cover"
for it, the stack is too heavy. Same test for any suspect effect: no visible change at the 3
viewpoints → delete it.

## Step 4 — Presets

Presets change quality knobs only; art direction stays identical. Table and AA-by-artifact
guide: `references/presets.md`.

## Verification

- [ ] 3 fixed viewpoints, before/after screenshots at each
- [ ] Greyscale: lit vs shaded faces differ clearly in value
- [ ] Every enabled effect has a written problem it solves
- [ ] Screen-space effects reviewed while the camera moves
- [ ] Ablation report run; nothing both expensive (>0.3 ms) and invisible
- [ ] ms with vsync off, within budget on target hardware
- [ ] Path, enemies, pickups readable through fog at the far viewpoint
- [ ] Foundation test: removing the sun change visibly breaks the scene
- [ ] Presets differ in quality knobs only

## Related

- `gamedev-lighting` — key/fill/rim theory behind steps 1, 2, 10
- `gamedev-foliage` — steps 7–9
- `gamedev-visual-artifacts` — when a setting causes an artifact
- `gamedev-art-direction` — when the assets, not the settings, clash
- `gamedev-performance` — budgets and draw calls

## Knowledge base

T-59 (sun first), T-60 (sky fill), T-61 (tonemapper), T-62 (contact shading in motion),
T-63 (GI and albedo), T-64 (fog for depth), T-68 (fill and practical lights),
T-69 (presence vs quality), T-70 (foundation ablation).
