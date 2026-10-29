---
name: gamedev-reference-reconstruction
description: >
  Rebuild a reference image as a real 3D asset matching its silhouette, proportions and
  palette, with measured acceptance. Use when given a concept sheet, turnaround or photo
  and asked to build that specific thing from scratch. For stalled iteration on an
  existing asset use visual-iteration.
license: Apache-2.0
compatibility: Engine-agnostic. Measured with tools/refmatch/*.py (Python 3.10+, Pillow, numpy). Blender 4.x/5.x and Godot 4.x bindings included.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: advanced
---

# Reference → 3D Reconstruction

Turn a reference image into geometry that matches it, measured rather than guessed.

**Completion is not "the asset was generated."** Completion is: rendered from a comparable
camera, compared against the reference, discrepancies ranked and closed, acceptance criteria
met or a documented limitation reached.

## When to use

- The user supplies an image and wants *that* object/character/environment built.
- You must match an existing art direction (concept sheet, turnaround, prop photo).
- A prior attempt produced something "inspired by" the reference but visibly different.

**When not to use:** the user wants an original design (use `frontend-design`-style
direction, not reconstruction); or the target is a pure UI/layout task.

## Inputs

Required: the reference image (more views = better), target scale (from a scale bar, or a
stated assumption), target engine/DCC (Blender 5.x + Godot 4.x covered), style class
(realistic / stylized / low-poly / hand-painted — changes poly budget and detail). Optional:
polygon budget.

## Step 0 — Declare the contract before touching geometry

Write these six lines into the task log. Every later decision refers back to them.

```
TARGET      : <one-sentence description of the exact asset>
SCALE       : <height in metres, or bounding size>
STYLE       : <realistic | stylized-realistic | low-poly | hand-painted>
POLY BUDGET : <triangles>
CAMERA      : <focal length mm, height, distance, angle — mirrored from the reference>
ACCEPT      : <measurable pass criteria, see Step 6>
```

If scale is not given, derive it: character sheets assume ~1.75–1.85 m for an adult; props
assume the human hand/head in the sheet as a ruler. **State the assumption.** Never silently
invent a scale — every proportion downstream depends on it.

## Step 1 — Read the reference as data, not as a picture

Measure every row of the sheet for the reference type (character, environment, prop) —
full tables with typical values: `references/measurement.md`. Unmeasured rows become the
defects later.

Use `tools/refmatch/measure_sheet.py` to get panel crops and a palette in one pass — but
**verify by eye**; auto-measured landmarks are a starting point, not the answer.

## Step 2 — Decompose into buildable components

Split by *independent, testable* pieces, ordered dependency-first.

Example decomposition (body, garments, equipment, hair, materials, detail):
`references/camera-and-decomposition.md`.

**Rule:** each component must be individually renderable and comparable to its own region of
the reference. If you cannot isolate it in a render, it is not a component.

## Step 3 — Choose the implementation method per component

Parametric scripts for measured volumes, offsets for garments, procedural generators for
repeated detail, explicit custom geometry for identity-defining shapes. Table:
`references/measurement.md`.

**Do not force procedural generation on a distinctive silhouette.** The sheet's identity
lives in the hair mass, the hood/cape, the backpack profile and the axe — those get explicit
geometry, not a "generic humanoid + noise."

## Step 4 — Build pass 1 at real scale

Non-negotiable conventions:

1. **1 Blender unit = 1 metre.** Verify `scene.unit_settings`.
2. **Origin at the ground between the feet**, +Z up, character faces **-Y** (Blender
   convention) so a front view camera sits at -Y looking +Y. If the brief or delivery format
   names a different up axis (OBJ/glTF and most engines use +Y up), the brief wins.
3. **Image rows grow downward.** When measuring from the reference, world height is
   `(ground_row - row) / pixels_per_metre`. Drop the minus sign and the asset is built upside
   down while every 2D measurement of your profile still looks correct.
4. **Build the blockout first, at landmark heights.** No materials, no detail.
5. **Every dimension comes from Step 1's fractions × `H`.** No eyeballed numbers.
6. **Name objects by component** (`Body_Torso`, `Vest`, `Pack_Roll`) so the comparison step
   can select them.
7. **Write the whole build as a script and save it.** "When the roof is wrong, fix one line
   and run it again" (knowledge base T-09). Iteration = edit a number, re-run.

Minimum blockout acceptance: render a gray silhouette from the reference's camera angle and
compare against the reference's silhouette **before** any material work.

**Measure the exported file, not the thing you built it from.** Export the mesh, then
re-import that exact file (or rasterise the projected vertices of the loaded OBJ) and run the
silhouette comparison on *that*. Comparing your intermediate profile array, your preview
rasteriser, or the in-memory mesh will happily report a perfect match while the written file
is axis-flipped, mis-scaled, or empty — the single most common way this task reports false
success.

## Step 5 — Camera calibration (do this before judging anything)

Wrong camera = every judgement is invalid. Match focal length/projection, camera height and
tilt, subject fraction of frame, light direction, aspect ratio and background value before
comparing anything. Checklist with typical values: `references/camera-and-decomposition.md`.

## Step 6 — Compare, rank, fix, re-render (the loop)

Run this loop until `ACCEPT` is met. Never fix two unrelated things in one iteration.

```
1. EXPORT   the delivery mesh (e.g. vase.obj) — this is what gets graded
2. RE-LOAD  that file; rasterise or render its silhouette (not your build script's arrays)
3. COMPARE  tools/refmatch/compare.py --ref <ref> --test out/pass_<n>.png
4. RANK     list discrepancies by visual importance (not by ease of fixing)
5. PICK     the single largest discrepancy
6. DIAGNOSE which layer owns it:
              geometry | proportions | material | lighting | camera | silhouette detail
7. FIX      one variable in the build script
8. RE-RENDER from the SAME camera (still from the re-loaded delivery file)
9. RECORD   into the discrepancy ledger (below)
```

Acceptance thresholds (silhouette IoU >= 0.90 props / 0.85 characters, landmarks within 2%
of `H`, mean palette dE <= 12; SSIM advisory only) and how to state them in Step 0:
`references/acceptance.md`.

## Step 7 — When the first attempt cannot be fixed

Do not iterate a broken approach forever. After **two** rounds of the same class of failure,
change method:

After **two** rounds of the same failure class, change method — symptom-to-change table in
`references/acceptance.md`.

## The discrepancy ledger

One row per discrepancy: number, discrepancy, layer, severity, metric evidence, fix, re-render
result, status. Revert a fix that makes the metric worse. Format and example:
`references/acceptance.md`.

## Guard rails (violations are the most common failure mode)

- **Never substitute a different design** — if you cannot build a feature, mark it open.
- **Never declare success off an exit code** — an export proves the file exists, nothing more.
- **Never judge from a thumbnail** — view the reference region at native resolution.
- **Never tune lighting to hide geometry errors** — silhouette first, flat lighting.
- **Stop iterating a stalled metric** — three rounds under 1% change: the bottleneck is elsewhere.

## Output contract

Report asset, scale, reference, camera, per-criterion PASS/FAIL, ledger counts, open items and
evidence paths — template in `references/acceptance.md`.

## Tools

`tools/refmatch/compare.py` (IoU, band widths, palette dE, bbox; SSIM advisory),
`tools/refmatch/measure_sheet.py`, `tools/refmatch/palette_report.py`,
`tools/blender/character_blockout.py`, `tools/blender/render_compare_views.py` — purposes in
`references/measurement.md`.

## Related skills

- `gamedev-modular-kit` — when the reference is a building/village to be built from parts.
- `gamedev-blender-headless` — the scripted build/execute mechanics used here.
- `gamedev-visual-iteration` — the general loop this skill specializes.
- `gamedev-texture-authoring` — materials and derived maps.
- `gamedev-lighting` — lighting the result to match the reference's mood.

## Knowledge base

T-05 (color bible), T-07 (reference-first), T-10 (multi-view), T-12 (negation), T-14
(measure the drawing), T-19 (budget via baked cards), T-58 (kit as reuse unit).
