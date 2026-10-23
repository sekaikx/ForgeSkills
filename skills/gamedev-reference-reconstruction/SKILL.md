---
name: gamedev-reference-reconstruction
description: >
  Rebuild a supplied reference image as an actual 3D asset in a real engine or DCC tool,
  matching its silhouette, proportions, camera, palette, materials and lighting rather than
  producing something merely "inspired by" it. Use when the user hands over a concept sheet,
  turnaround, prop photo or environment painting and wants that specific thing built. Includes
  measurable acceptance criteria, a discrepancy ledger, and a mandatory re-render loop.
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

| Input | Required | Notes |
|---|---|---|
| Reference image | yes | Full sheet or single view. More views = better. |
| Target scale | yes | Real-world height/size. Derive from the sheet if it has a scale bar; otherwise state an assumption explicitly. |
| Target engine/DCC | yes | Blender 5.x + Godot 4.x covered here. |
| Style class | yes | Realistic / stylized / low-poly / hand-painted. Changes the poly budget and detail rules. |
| Polygon budget | no | Default below. |

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

Fill this table from the image. Do not skip rows; unmeasured rows become the defects later.

**Character sheet**

| Property | How to measure | Record |
|---|---|---|
| Total height | Top of head → sole | `H` px |
| Head height | Top of skull → chin | `h` px |
| Head count | `H / h` | typically 7.0–8.0 |
| Eye line | Fraction of `H` from ground | ~0.93 for adults |
| Shoulder span | Deltoid to deltoid | fraction of `H` (~0.23–0.26) |
| Shoulder height | Fraction of `H` | ~0.82 |
| Elbow | Fraction of `H` | ~0.63 |
| Wrist | Fraction of `H` | ~0.48 |
| Hip / crotch | Fraction of `H` | ~0.47–0.50 |
| Knee | Fraction of `H` | ~0.28 |
| Ankle | Fraction of `H` | ~0.06 |
| Foot length | Side view | fraction of `H` (~0.15) |
| Silhouette features | Named, ordered by how much they define identity | hair mass, hood, backpack, axe, boot bulk |
| Palette | Sample swatches | hex + role |

**Environment sheet:** horizon line, ground plane, dominant vertical rhythm (architecture),
silhouette skyline, atmospheric depth layers (near/mid/far), light direction and color
temperature, ground material.

**Prop sheet:** overall bounding box ratio (w:h:d), primary/secondary/tertiary forms, bevel
radii, material families, defining detail that makes it recognizable.

Use `tools/refmatch/measure_sheet.py` to get panel crops and a palette in one pass — but
**verify by eye**; auto-measured landmarks are a starting point, not the answer.

## Step 2 — Decompose into buildable components

Split by *independent, testable* pieces, ordered dependency-first.

Character example (matches a modular kit, T-58):
```
1. Body blockout      — head, torso, hips, limbs as volumes at correct landmark heights
2. Garment layers     — shirt, vest, pants, boots (each offsets the body volume)
3. Equipment          — belt, pouches, backpack, bedroll, axe
4. Hair mass          — the single largest silhouette contributor after the body
5. Materials          — palette + roughness; no albedo detail until Step 5 passes
6. Detail pass        — seams, buckles, straps, wear
```

**Rule:** each component must be individually renderable and comparable to its own region of
the reference. If you cannot isolate it in a render, it is not a component.

## Step 3 — Choose the implementation method per component

| Component | Method | Why |
|---|---|---|
| Body volumes at measured landmarks | Parametric script (bmesh/primitives + measured dims) | Deterministic, adjustable by number |
| Garments that follow the body | Offset/shrinkwrap of body volumes + silhouette profile | Silhouette is what reads |
| Repeated/parametric detail (straps, pouches, buckles) | Procedural generators with parameters | Consistent, cheap to vary |
| Distinctive one-off shape (axe head, unique hair) | Custom mesh generation | Procedural cannot invent identity |
| Organic face | Subdiv + shape sculpt-ish displacement, or import a base mesh | Hand-authoring by code is a trap |
| Surface detail | Procedural shader + texture maps | T-16/T-17 |

**Do not force procedural generation on a distinctive silhouette.** The sheet's identity
lives in the hair mass, the hood/cape, the backpack profile and the axe — those get explicit
geometry, not a "generic humanoid + noise."

## Step 4 — Build pass 1 at real scale

Non-negotiable conventions:

1. **1 Blender unit = 1 metre.** Verify `scene.unit_settings`.
2. **Origin at the ground between the feet**, +Z up, character faces **-Y** (Blender
   convention) so a front view camera sits at -Y looking +Y.
3. **Build the blockout first, at landmark heights.** No materials, no detail.
4. **Every dimension comes from Step 1's fractions × `H`.** No eyeballed numbers.
5. **Name objects by component** (`Body_Torso`, `Vest`, `Pack_Roll`) so the comparison step
   can select them.
6. **Write the whole build as a script and save it.** "When the roof is wrong, fix one line
   and run it again" (knowledge base T-09). Iteration = edit a number, re-run.

Minimum blockout acceptance: render a gray silhouette from the reference's camera angle and
compare against the reference's silhouette **before** any material work.

## Step 5 — Camera calibration (do this before judging anything)

Wrong camera = every judgement is invalid. Match:

- **Focal length / projection.** Portraits and prop shots are often 50–85 mm (low
  distortion); architectural/environment shots 24–35 mm (wide). A 1024×1024 sheet panel with
  minimal convergence is usually 85 mm or orthographic.
- **Height and tilt.** Eye level ≈ 0.93 × H for a standing character shot; prop shots are
  usually at object mid-height.
- **Framing.** Subject occupies the same fraction of frame; feet near the bottom edge.
- **Light direction.** Match the reference's key from the shading on the form, not from
  guesswork. Note shadow softness and whether there is fill.

Capture rule: **same aspect ratio, same subject fraction, same background value.** A white
background against a dark reference defeats visual comparison.

## Step 6 — Compare, rank, fix, re-render (the loop)

Run this loop until `ACCEPT` is met. Never fix two unrelated things in one iteration.

```
1. RENDER   from the calibrated camera → out/pass_<n>.png
2. COMPARE  tools/refmatch/compare.py --ref <ref> --test out/pass_<n>.png
3. RANK     list discrepancies by visual importance (not by ease of fixing)
4. PICK     the single largest discrepancy
5. DIAGNOSE which layer owns it:
              geometry | proportions | material | lighting | camera | silhouette detail
6. FIX      one variable in the build script
7. RE-RENDER from the SAME camera
8. RECORD   into the discrepancy ledger (below)
```

### Acceptance criteria — pick the applicable set and write the thresholds in Step 0

**Silhouette** (highest weight — this is what the eye matches first)
- IoU of subject masks ≥ **0.90** for props, ≥ **0.85** for characters at matched framing.
- Landmark heights within **2% of `H`**.
- Width profile at 10 horizontal bands within **5%** at each band.

**Proportions**
- Head count within **±0.2 heads**.
- Shoulder span within **±4% of `H`**.

**Camera**
- Subject bounding box matches reference within **3%** in each of x/y size and x/y center.

**Palette / material**
- Mean ΔE (CIE76) between the 8 dominant clusters ≤ **12**.
- Value (luminance) histogram correlation ≥ **0.80**.

**Perceptual (secondary signal only)**

`compare.py` also reports SSIM and a downscaled RMSE. These are **advisory**. A high SSIM
with the wrong anatomy is a failure; state that in the ledger explicitly. Never let a
similarity score overrule a named structural defect.

## Step 7 — When the first attempt cannot be fixed

Do not iterate a broken approach forever. After **two** rounds of the same class of failure,
change method:

| Symptom | Change |
|---|---|
| Silhouette won't converge by tweaking volumes | The decomposition is wrong — re-read Step 2 and split the offending component |
| Limbs/props are always misproportioned | Scale assumption is wrong — re-derive `H` |
| Everything looks flat/plastic | Materials and lighting, not geometry — do T-39 (roughness + texture scale) |
| Looks right in render, wrong in engine | Import settings, color management, or scale — verify before "fixing" geometry |
| Generated asset is close but unusable | Do not patch meshes. Regenerate with a better reference (T-10/T-12) |
| Facial features are uncanny | Stop hand-modeling: use a base head mesh and only adjust proportions |

## The discrepancy ledger

Keep it in the task log. Columns exactly as below; no prose substitutes.

```
| # | Discrepancy | Layer | Severity | Evidence (metric) | Fix applied | Re-render result | Status |
|---|-------------|-------|----------|-------------------|-------------|------------------|--------|
| 1 | Hair mass too flat on top | geometry | HIGH | top-of-head band width -14% | raised crown volume +0.03 m | -3% | closed |
| 2 | Vest reads grey not brown | material | HIGH | ΔE 21 on torso cluster | palette correction | ΔE 9 | closed |
| 3 | Feet too small | proportions | MED | foot length 0.12H vs 0.15H | foot length 0.27 m | 0.15H | closed |
```

**Revert rule:** if a fix makes the metric worse and the eye agrees, revert it and record the
revert. Do not keep a change because it was expensive to make.

## Guard rails (violations are the most common failure mode)

- **Never substitute a different design.** If the model sheet has an olive hood, an olive
  hood goes on. If you cannot do it, say so and mark it as an open limitation.
- **Never declare success off a generator's exit code.** A successful glTF export proves the
  file exists, nothing more.
- **Never compare against a thumbnail you mentally upscaled.** Crop and view the reference
  region at native resolution.
- **Never tune lighting to hide a geometry error.** Compare silhouette first, with flat
  lighting.
- **Never keep iterating on a metric that stopped moving.** If three consecutive rounds
  change the score by <1%, the bottleneck is elsewhere.

## Output contract

Report exactly this when done:

```
ASSET      : <name>  |  <tri count> tris  |  <file path>
SCALE      : <metres>  |  units verified: yes/no
REFERENCE  : <path>
CAMERA     : <focal mm, height, distance, angle>
ACCEPT     : silhouette IoU <x>, landmark err <y>%, ΔE <z>  → PASS/FAIL per criterion
LEDGER     : <n> discrepancies, <m> closed, <k> open
OPEN       : <list any unmet criterion + why>
EVIDENCE   : <render paths>
```

## Tools

| Script | Purpose |
|---|---|
| `tools/refmatch/measure_sheet.py` | Panel crops, palette extraction, landmark helper |
| `tools/refmatch/compare.py` | Silhouette IoU, band widths, palette ΔE, bounding box, SSIM (advisory) |
| `tools/refmatch/palette_report.py` | Named palette file → hex + ΔE against an asset render |
| `tools/blender/character_blockout.py` | Parametric human blockout from measured fractions |
| `tools/blender/render_compare_views.py` | Fixed-camera renders (front/side/back/three-quarter) for a turnaround |

## Related skills

- `gamedev-modular-kit` — when the reference is a building/village to be built from parts.
- `gamedev-blender-headless` — the scripted build/execute mechanics used here.
- `gamedev-visual-iteration` — the general loop this skill specializes.
- `gamedev-texture-authoring` — materials and derived maps.
- `gamedev-lighting` — lighting the result to match the reference's mood.

## Knowledge base

T-05 (color bible), T-07 (reference-first), T-10 (multi-view), T-12 (negation), T-14
(measure the drawing), T-19 (budget via baked cards), T-58 (kit as reuse unit).
