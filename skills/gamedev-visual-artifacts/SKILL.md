---
name: gamedev-visual-artifacts
description: >
  Find the cause of a rendering artifact or stutter by symptom: shimmer, banding, shadow
  acne, light leaks, screen-space halos, ghosting, z-fighting, popping, shader hitches,
  jitter. Use when something on screen looks wrong or hitches.
license: Apache-2.0
compatibility: Engine-agnostic method; settings named for Godot 4.x with Unity equivalents where useful.
metadata:
  engine: any
  category: gamedev-workflow
  difficulty: intermediate
---

# Visual Artifacts and Stutter

An artifact has exactly one cause more often than people expect. Find it by isolation, fix
that, and do not add a blur, fog or post effect to hide it — hiding moves the artifact
somewhere you will find it later at a worse time.

## When to use

- Flicker, crawl, stripes, halos, leaks, ghosts, pops or hitches on screen.
- "It looks fine in the editor but wrong in game" (or the reverse).
- A visual problem appeared after enabling a setting.

## When not to use

- The scene is artifact-free but flat or dull — `gamedev-godot-visual-polish`.
- Low average FPS with no visual defect — `gamedev-performance`.
- A logic or gameplay bug — `gamedev-debugging`.

## Step 1 — Isolate before fixing

1. **Reproduce at a fixed camera** (save it as a marker). Note whether it needs motion —
   many artifacts only exist in motion (shimmer, ghosting, screen-space edges, jitter).
2. **Classify**: still image, camera motion only, object motion only, first time seen only.
3. **Toggle one thing at a time**: AA mode, SSAO/SSIL/SSR, GI, fog, shadows, post. The
   artifact disappears when its cause is off. `tools/godot/ablation_capture.gd` automates
   leave-one-out with screenshots.
4. **Use the engine's debug views** (Godot: Perspective menu > Display Advanced — Normal
   Buffer, Shadow Atlas, SSAO, SDFGI Probes, Overdraw; Unity: Frame Debugger / Rendering
   Debugger).
5. Fix the cause. Re-check at the same marker, in motion if it needed motion.

## Step 2 — Look up the symptom

Full tables, grouped (aliasing/shimmer, banding, shadows, GI and screen-space, temporal and
motion, geometry and colour, stutter): `references/symptoms.md`. Read only the group that
matches the classification from Step 1. The most common cases:

| Symptom | Cause | Fix |
|---|---|---|
| Distant textures crawl | No mipmaps / nearest filter | Mipmaps; anisotropic linear-mipmap filtering |
| Stripes on lit surfaces (acne) | Shadow bias too low | Raise **normal bias** first |
| Blurry, blocky shadows near camera | Shadow distance too far for atlas | Lower `directional_shadow_max_distance` |
| Light through walls | Walls thinner than GI cell | Thicken; SDFGI occlusion; lightmaps indoors |
| Halos, AO vanishing at screen edge | Screen-space limits | Smaller radius; bake AO or add probes |
| Hitch first time an effect appears | Shader/pipeline compilation | Load materials at load time (4.4+ precompiles) |
| Jitter at high refresh rates | Physics tick ≠ render rate | Physics interpolation (4.3+) |

Always measure **worst-frame time** for stutter, not average FPS: a 60 fps average with 80 ms
spikes plays worse than a steady 45.

## Step 3 — Confirm the fix

1. Same marker, same motion: artifact gone.
2. The fix did not create a new artifact elsewhere (check the other viewpoints).
3. Frame time recorded before and after — a fix that costs 3 ms needs to be a conscious
   decision.

## Verification

- [ ] Reproduced at a fixed marker before changing anything
- [ ] Classified as still / camera motion / object motion / first-seen
- [ ] Cause found by toggling one setting at a time (named in the fix note)
- [ ] Fixed at the cause; no blur, fog or post added purely to hide it
- [ ] Re-checked at the marker in the same motion, plus the other viewpoints
- [ ] Worst-frame time compared before/after for stutter fixes

## Related

- `gamedev-godot-visual-polish` — the settings that usually introduce these artifacts
- `gamedev-debugging` — the isolate/bisect method in general
- `gamedev-performance` — frame budgets and spikes
- `gamedev-foliage` — alpha and LOD artifacts specific to vegetation
- `gamedev-texture-authoring` — mipmaps, colour space, texel density

## Knowledge base

T-62 (screen-space effects in motion), T-72 (symptom-first isolation), T-69 (cost per
setting).
