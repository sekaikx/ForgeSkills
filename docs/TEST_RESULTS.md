# Test results

Everything below was executed. Nothing here is projected or assumed.

Environment: Windows 10.0.19045, Blender 5.2.2 LTS (EEVEE), Python 3.12 (system) and 3.13
(Blender), Pillow + numpy. No Godot or Unity installed.

---

## 1. Library validation — PASS

```
$ python tools/validate_skills.py

SKILL LIBRARY VALIDATION — 20 skills, 58 techniques known
...
ERRORS 0   WARNINGS 0
```

Checks performed: YAML frontmatter parses; `name` matches directory; description length and
use-case signal; every `` `gamedev-*` `` cross-reference resolves; every `` `tools/*.py` ``
path exists on disk; every `T-nn` citation exists in the knowledge base; word-count sanity.

**This check earned its place immediately.** It caught a dangling reference to
`tools/refmatch/palette_report.py`, which had been listed in the reconstruction skill's tool
table but never written. The tool now exists and runs.

---

## 2. Concept-sheet extraction — PASS

```
$ python tools/refmatch/measure_sheet.py --sheet <ref>.png \
      --region 255,25,350,395 --auto-front --out ref_front.png --square --palette
```

Extracted the front turnaround panel and an 8-cluster palette. Palette shares were plausible
(largest cluster = the coat, 20-23%; smallest = skin highlight, 5-6%).

**Failure found and fixed:** the first version isolated the figure using a global background
colour threshold. The panel carries film grain, so stray pixels spread across the entire frame
and the bounding box became the whole panel — every downstream proportion measurement was
garbage. Fixed by switching `compare.py` to flood-fill segmentation (connectivity, not colour
distance) plus connected-component cleanup.

---

## 3. Comparison metrics — PASS after four real bug fixes

The tooling was wrong four times before it was right. Each bug was found by cross-checking a
number against what the eye could see, which is exactly the discipline the skill preaches.

| # | Bug | Symptom | Fix |
|---|---|---|---|
| 1 | Separable convolution indexing | `ValueError` broadcast (512,512) vs (522,512) | explicit reflect padding per axis |
| 2 | Colour-threshold mask | bbox = whole frame; IoU 0.0000 | flood fill from border |
| 3 | Square resize of masks | aspect ratio stretched 3.5x; width profile meaningless | scale by height, centre, pad |
| 4 | Band widths normalized by canvas | concept crop vs padded render never comparable | normalize by subject's own peak width |

Final sanity check — the metrics now behave correctly on known inputs:

```
silhouette IoU      : 0.4628      (0 = no overlap, 1 = identical)
band errors %       : max 57.1
aspect  ref 0.300  test 0.348    ratio 1.157
palette mean dE     : 5.95
```

The palette metric reaching ΔE 5.95 (threshold 12) after correcting the sampled values is the
one clean pass in the reconstruction, and it is real: the render's dominant clusters now land
within a few units of the reference's.

---

## 4. Blender scene validation — PASS

```
$ (live Blender) exec(validate_scene.py); validate(frame=(0.36,0.32,1.84), expect_height=1.80)

objects 46   triangles 15224
  [PASS] no_stray_geometry
  [PASS] no_isolated_objects
  [PASS] height_within_tolerance
  [PASS] above_ground
VALIDATION: PASS
```

**Two real geometry bugs were caught by this gate**, both invisible in a front render:

1. A cylinder helper translated vertices to the target position and *then* applied an object
   rotation. Because the object origin was still at the world origin, the bedroll swung to
   x = 1.40-1.72 m — a metre and a half outside the character. Fixed by building at the
   origin, rotating the mesh data, then setting `object.location`.
2. A taper used `v.co.z *= 0.62` on a mesh whose vertices were in world space, collapsing the
   axe head toward the ground plane instead of tapering about its own centre. Fixed by
   tapering about the feature's centre.

**A third bug was in the validator itself:** `ob.bound_box` is a cached property and reported
the *previous* mesh immediately after a scripted edit, so the gate failed on stale numbers.
Fixed by reading evaluated vertices through the depsgraph. This is now documented in
`gamedev-blender-headless` as a named pitfall.

---

## 5. Reference reconstruction — **FAIL (honest result)**

Target: reconstruct the hooded explorer from the supplied concept sheet at 1.80 m.

Measured, best pass:

| Criterion | Threshold | Measured | Result |
|---|---|---|---|
| silhouette IoU | ≥ 0.85 | 0.4628 | **FAIL** |
| band max error | ≤ 5% | 57.1% | **FAIL** |
| palette mean ΔE | ≤ 12 | 5.95 | PASS |
| luminance hist corr | ≥ 0.80 | 0.32 | **FAIL** |
| aspect ratio deviation | ≤ 3% | 15.7% | **FAIL** |

Scale and structural validity did pass: 1.782 m against a 1.80 m target (+1.0% error), no
stray geometry, no isolated objects, 15,224 triangles.

### What went wrong, concretely

1. **The lower silhouette is wrong.** Reference bands 7-9 measure ~0.33-0.39 m wide; the build
   measures ~0.14-0.15 m. The reference's coat hem reaches mid-calf and flares; the built hem
   stops at the knee. The measured fix (hem radius 1.08x hip width) was applied but the last
   comparison still showed the lower bands 24-45% narrow — the coat exists but does not read
   as the reference's silhouette.
2. **Top band too narrow.** Reference 0.71, build 0.45. The hood is present but smaller than
   the reference's, which is a large, dominant shape.
3. **Value structure is inverted.** Luminance correlation 0.32 while palette ΔE passes: the
   colours are right but the *distribution* is not — the render is too evenly lit, lacking the
   reference's deep shadow mass.
4. **The band profile overshoots in the middle.** After enlarging the coat, bands 3-6 went from
   too narrow to slightly too wide (1.00 vs 0.77-0.97). An overshoot is as much a defect as an
   undershoot and needs its own pass.

### Why it stopped here

The remaining gap is not a parameter tweak. Reaching IoU 0.85 on this reference needs the
hood, coat and hair authored as modelled volumes with correct *shapes*, not scaled
primitives — that is a different class of work from parametric blockout. Continuing to nudge
radii would have been the exact anti-pattern the skill warns about: two rounds of the same
class of failure means change method, not parameters.

The ledger in `gamedev-visual-iteration` documents this correctly: fixes that overshot are
recorded as overshoots, not victories.

---

## 6. Renders produced

| File | What |
|---|---|
| `view_front/side/three_quarter.png` | Lit renders, 85 mm, three-point rig |
| `alpha_front/side/back/three_quarter.png` | Transparent-film renders for exact silhouettes |
| `diag_sheet.png` | Three-panel diagnostic (reference / render / overlay) |
| `ref_front.png` | Extracted reference panel |
| `palette_ref.json` | Eight-cluster palette from the reference |

---

## Not tested

| Claim | Status |
|---|---|
| Godot 4.x import and headless verification | **not run** — no Godot installed |
| Unity 6 import, URP setup, batchmode build | **not run** — no Unity installed |
| Rigs, skinning, animation clips | **not run** — no armature was built |
| VFX timings, hitstop, screen shake | **not run** — timings are from the transcripts and documented practice, not measured in an engine |
| Terrain/road/river generation | **not run** — algorithms specified, no implementation executed |
| Texture derivation and atlas packing | **not run** — no baking was performed |
| Performance budgets | **not measured** — the figures given are typical ranges, not measurements from this project |

These are labelled as specifications in their skills, not as verified recipes. See
`LIMITATIONS.md`.

---

## 7. Skills-library distribution copy — PASS

The library was copied to a standalone layout (Desktop/game-design-skills/) and re-validated
in place.

`
$ python tools/validate_skills.py
SKILL LIBRARY VALIDATION — 20 skills, 58 techniques known
ERRORS 0   WARNINGS 0
`

**Two validator bugs surfaced during the move**, both cases of a check silently passing
because it found nothing to check:

1. The scan only looked in .agents/skills/. In the standalone layout the skills live in
   skills/, so the validator found **zero skills and reported PASS**. A validator that
   passes on an empty set is worse than no validator. Fixed by accepting both layouts and
   treating an empty scan as a fatal error.
2. The knowledge-base lookup was hardcoded to docs/gamedev/, which does not exist in the
   standalone layout, so the technique-citation check was silently disabled. Fixed with a
   parent-directory fallback.

Both are now documented as the reason validate() returns a fatal field.
