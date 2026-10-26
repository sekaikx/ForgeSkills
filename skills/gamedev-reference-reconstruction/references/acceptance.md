# Acceptance thresholds, recovery, ledger, report

Loaded from Steps 0, 6 and 7 of SKILL.md.

## Acceptance criteria — pick the applicable set and write the thresholds in Step 0

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

## Step 7 - change method after two failed rounds

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
