# Reference measurement tables

Loaded from Step 1 and Step 3 of SKILL.md.

## Step 1 - what to measure

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

## Step 3 - implementation method per component

| Component | Method | Why |
|---|---|---|
| Body volumes at measured landmarks | Parametric script (bmesh/primitives + measured dims) | Deterministic, adjustable by number |
| Garments that follow the body | Offset/shrinkwrap of body volumes + silhouette profile | Silhouette is what reads |
| Repeated/parametric detail (straps, pouches, buckles) | Procedural generators with parameters | Consistent, cheap to vary |
| Distinctive one-off shape (axe head, unique hair) | Custom mesh generation | Procedural cannot invent identity |
| Organic face | Subdiv + shape sculpt-ish displacement, or import a base mesh | Hand-authoring by code is a trap |
| Surface detail | Procedural shader + texture maps | T-16/T-17 |

## Tools

| Script | Purpose |
|---|---|
| `tools/refmatch/measure_sheet.py` | Panel crops, palette extraction, landmark helper |
| `tools/refmatch/compare.py` | Silhouette IoU, band widths, palette ΔE, bounding box, SSIM (advisory) |
| `tools/refmatch/palette_report.py` | Named palette file → hex + ΔE against an asset render |
| `tools/blender/character_blockout.py` | Parametric human blockout from measured fractions |
| `tools/blender/render_compare_views.py` | Fixed-camera renders (front/side/back/three-quarter) for a turnaround |
