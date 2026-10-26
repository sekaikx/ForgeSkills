---
name: gamedev-visual-iteration
description: >
  Iterate a visual toward a target by measurement: render, compare, rank discrepancies, fix
  one cause, re-render. Use when an asset, scene or shader must match a reference or look,
  or a visual task has stalled.
license: Apache-2.0
compatibility: Engine-agnostic. Tooling in tools/refmatch/ (Pillow + numpy). Works with Blender, Godot, Unity renders.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Visual iteration — close the loop on purpose

Unmeasured visual work converges on "good enough" and then oscillates. The loop here
forces each pass to produce a number and a named defect, so passes either improve the
artifact or get reverted.

## When to use

- An artifact must match a reference image or a described look.
- Three or more visual passes have happened without the result improving.
- The user says it "doesn't look right" and you need to find out what specifically.

## When not to use

- Design exploration where no target exists yet (decide the direction first, *then*
  iterate).
- Purely functional work with no visual criterion.

## The loop

```
1 LOOK      at the current artifact and the target, at native resolution, side by side
2 MEASURE   the metrics that matter for this artifact class
3 RANK      discrepancies by visual importance, worst first
4 PICK      exactly one
5 DIAGNOSE  which layer owns it: geometry | proportion | material | light | camera | detail
6 FIX       one variable in the build script
7 RE-RENDER from the identical camera and settings
8 RECORD    into the ledger; keep or revert based on the numbers AND your eyes
```

Rules that make the difference:

- **One variable per pass.** Change two things and you learn nothing about which worked.
- **Revert failures.** If a fix makes the metric worse and the eye agrees, undo it. Do not
  keep it because it was work.
- **Same camera always.** Re-framing between passes invalidates every comparison.
- **Rank by importance, not ease.** Fixing the buckle when the silhouette is wrong is
  busywork.

## Choosing the metrics by artifact class

| Artifact | Primary | Secondary | Advisory only |
|---|---|---|---|
| Character / creature | silhouette IoU, band width profile, landmark heights | aspect ratio, palette ΔE | SSIM, RMSE |
| Prop | silhouette IoU (higher bar, 0.90), bounding box ratio | palette ΔE, edge detail | SSIM |
| Environment | horizon placement, value structure, vertical rhythm | palette families, depth layers | SSIM |
| Lighting | luminance histogram, key direction, shadow softness | warm/cool split | mean brightness |
| Texture | seam continuity, tile variance, texel density | roughness consistency | sharpness |

**Why SSIM is advisory.** SSIM rewards blur and global tone similarity. A blurred blob can
outscore a sharp, correct model. Never let it override a named structural defect.

## Reading a band width profile

The band profile is the most diagnostic cheap metric for characters and props. Ten
horizontal slices, each width normalized by the figure's own widest band:

- **Top band narrow, reference wide** → head/hood/hair mass is too small.
- **Middle bands wide, reference narrow** → torso/garment is too bulky.
- **Bands 7-9 narrow, reference wide** → the lower garment is missing or too tight; look
  for a coat, skirt, cape or flared trousers.
- **Last band wide, reference narrow** → feet/shadow too large, or the mask is including a
  ground shadow.

Match the *shape of the curve*, not one number. A profile that tracks the reference in
eight of ten bands with one outlier is much better than a uniformly 10%-wrong profile, and
the outlier names the defect.

## Diagnosing by layer

Work down this list; earlier layers invalidate later ones.

1. **Camera.** Wrong focal length or height makes every judgement wrong. Fix first. A
   portrait at 85 mm and a prop at 35 mm are not comparable.
2. **Proportion.** Landmark heights off by >2% of total height. Fix before detail.
3. **Silhouette.** Missing or oversized masses (hood, coat, backpack, hair). This is what
   the eye matches first.
4. **Material.** Base color, roughness, texture scale. Fix value before hue.
5. **Light.** Direction, softness, intensity ratio. Never use lighting to hide a geometry
   error.
6. **Detail.** Seams, wear, straps, buckles. Last, always.

## Common stalls and what they mean

| Stall | Real cause |
|---|---|
| IoU stuck ~0.5, both masks look plausible | A major mass is missing, not mis-shaped |
| Metric improves, eye says worse | Measuring tone, not shape. Fix the metric |
| Every pass changes everything | More than one variable per pass |
| Can't get past 0.7 IoU | Material/light noise dominating the mask; use alpha |
| Profile matches but it still looks wrong | Camera/focal mismatch, or missing micro-detail at silhouette edge |
| Numbers perfect, still uncanny | Proportion ratios right, gesture/pose wrong |

## The ledger

```
| # | Discrepancy | Layer | Severity | Metric before | Fix | Metric after | Status |
|---|-------------|-------|----------|---------------|-----|--------------|--------|
| 1 | no hood | silhouette | HIGH | top band 0.42 vs 0.71 | added hood mass | 0.45 | open |
| 2 | coat missing | silhouette | HIGH | b7 0.53 vs 0.77 | long coat hem | 1.00 | over |
| 3 | too bright | material | MED | ΔE 25.0 | dark palette | ΔE 5.9 | closed |
```

Note row 2: the fix overshot (1.00 vs 0.77). An overshoot is as much a defect as an undershoot
and gets its own pass. Record it rather than declaring victory.

## Guard rails

- Never compare a thumbnail to a full-resolution reference.
- Never let a render's lit backdrop become the silhouette; render with alpha.
- Never change the camera between passes.
- Never tune lighting until the silhouette passes under flat light.
- Never accept "close enough" without writing which criterion is unmet and by how much.

## Tooling

| Tool | Use |
|---|---|
| `tools/refmatch/compare.py` | IoU, band profile, palette ΔE, aspect, SSIM |
| `tools/refmatch/overlay.py` | Three-panel diagnostic sheet (ref / render / overlay) |
| `tools/refmatch/measure_sheet.py` | Extract a clean panel and palette from a concept sheet |
| `tools/blender/render_compare_views.py` | Fixed-camera turnaround renders |
| `tools/blender/validate_scene.py` | Stray geometry and proportion gate |

## Related

- `gamedev-reference-reconstruction` — the specialized form for supplied references
- `gamedev-lighting` — when the defect is in light, not shape
- `gamedev-verification` — evidence discipline
- `gamedev-debugging` — when a pass fails for unclear reasons

## Knowledge base

T-07 (reference-first iteration), T-14 (measure the drawing), T-39 (iterative lighting
diagnosis), T-05 (color bible), T-51 (multi-angle breaking tests).
