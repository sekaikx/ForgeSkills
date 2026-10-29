# Usage

How to actually use these skills, and the fastest path from a request to a verified result.

## Installation

Drop `.agents/skills/gamedev-*` into whatever directory your agent reads skills from. The
layout is standard: one directory per skill, one `SKILL.md` each, with YAML frontmatter.

```
.agents/skills/
  gamedev-orchestrator/SKILL.md
  gamedev-verification/SKILL.md
  ...
```

Tools live in `tools/` and are referenced by relative path from the repository root. If you
move the skills, either keep `tools/` in the same relative position or edit the paths.

Dependencies:

```
pip install pillow numpy
```

Blender is only needed for the `tools/blender/*` scripts.

---

## Quick start: three scenarios

### "Build me this game idea"

1. **orchestrator** — write the six-line contract. Do not skip this; the whole point is that
   the brief becomes falsifiable.
2. **blockout** the core loop at measured scale. No materials.
3. One system at a time, each self-reporting.
4. **vfx-impact**, **lighting**, **camera** for feel — last.
5. **verification** — every ACCEPT line gets a measurement.

Load one skill at a time. Loading five produces mush.

### "Make this look like this reference"

1. **reference-reconstruction** — measure the sheet before modelling. Fill in the landmark
   table; unmeasured rows become defects.
2. **blender-headless** for the build mechanics.
3. `render_compare_views.py` → `compare.py` → `overlay.py`, in that order.
4. **visual-iteration** — one variable per pass, rank by importance, revert failures.

### "It's broken"

1. **debugging** — repro, then bisect, then instrument. Never change things until the symptom
   disappears.
2. **game-testing** — turn the repro into a test so it cannot come back.
3. **verification** — prove the fix on a clean run.

---

## The tools, concretely

### Compare a render to a reference

```bash
python tools/refmatch/compare.py \
    --ref explorer_character/out/ref_front.png \
    --test explorer_character/out/alpha_front.png \
    --kind character \
    --out report.json
```

Output:

```
silhouette IoU      : 0.4628
band widths  ref   : [0.7092, 0.5532, 0.8014, 0.9716, 1.0, 0.9787, 0.7021, 0.766, 0.9291, 0.9645]
band widths  test  : [0.4207, 0.9724, 0.9586, 0.9724, 0.9862, 1.0, 1.0, 0.531, 0.5172, 0.4897]
band errors  %     : [28.85, 41.92, 15.72, 0.08, 1.38, 2.13, 29.79, 23.5, 41.19, 47.48]
aspect  ref 0.300  test 0.283    ratio 0.943
palette mean dE    : 14.85
lum hist corr      : -0.4079
```

**How to read it:** ignore the overall pass/fail first. Look at the band profile. Bands that
are too narrow near the bottom mean a missing lower garment; bands too wide in the middle mean
an over-bulky torso. The profile names the defect; the IoU just scores it.

### See what's wrong

```bash
python tools/refmatch/overlay.py \
    --ref explorer_character/out/ref_front.png \
    --test explorer_character/out/alpha_front.png \
    --out explorer_character/out/diag_sheet.png
```

Three panels: reference, render, and a silhouette overlay (red = reference only, cyan = render
only, white = agreement). This is the fastest way to understand a bad IoU.

### Get a clean reference panel and palette

```bash
python tools/refmatch/measure_sheet.py --sheet sheet.png \
    --region 255,25,350,395 --auto-front --out ref_front.png --square --palette
```

### Check a palette against a render, per role

```bash
python tools/refmatch/palette_report.py --extract ref.png --out palette.json
python tools/refmatch/palette_report.py --palette palette.json --render out/front.png
```

Reports each named colour's nearest render cluster and its ΔE. This is what catches "the vest
is grey instead of brown" without you having to notice it by eye.

### Derive maps from a single albedo, and check the tiling

```bash
python tools/texture/tex_to_maps.py --albedo wall.png --out out/wall --strength 0.4 --ao
python tools/texture/tile_seam_check.py --image wall.png --out out/tile_preview.png
python tools/texture/uv_density.py --obj kit.obj --texel 2048
```

`tex_to_maps.py` writes roughness, tangent-space normal and an optional cavity map. `strength`
is the only control that matters: concrete sits near 0.4, brick near 1.0, above 2.0 looks like
plastic. `tile_seam_check.py` compares the wrap edge against the interior distribution and
exits nonzero on a visible seam. `uv_density.py` reports px/m per OBJ group and fails when the
spread between parts exceeds `--max-ratio`.

### Gate a Blender scene

```python
import validate_scene, importlib
importlib.reload(validate_scene)
rep = validate_scene.validate(expect_height=1.80)
validate_scene.print_report(rep)
```

Catches stray geometry, isolated objects, wrong scale and geometry below the floor — all
before wasting a render.

### Render a turnaround from a fixed camera

```python
import render_compare_views as rcv, importlib
importlib.reload(rcv)
rcv.render_turnaround("out/", views=["front", "side", "three_quarter"])
```

Renders with transparent film by default when you set `film_transparent`, which gives an exact
silhouette. **Always use alpha for comparison.** Keying a lit backdrop cost hours in this
project's own development.

---

## Blender execution patterns

**Headless:**

```bash
blender -b -P tools/blender/explorer_build.py -- --height 1.80
```

**Live session (MCP or console)** — note the reload, or you will debug a fix that is already
on disk:

```python
import sys, importlib
sys.path.insert(0, r"...\tools\blender")
import explorer_common, explorer_build
importlib.reload(explorer_common)
importlib.reload(explorer_build)
explorer_build.build_explorer(1.80)
```

**Loading a script without running its `__main__`:**

```python
ns = {"__name__": "not_main"}
exec(compile(open(script, encoding="utf-8").read(), script, "exec"), ns)
ns["build"](1.80)
```

---

## Writing a new skill for this library

Follow the existing structure; it is not arbitrary.

1. **Frontmatter** — `name` must equal the directory name. `description` must say *when to use
   it*, in the first sentence, because that is what an agent matches on.
2. **`## When to use` / `## When not to use`** — both, always. The negative case is what stops
   a skill from being applied where it does not belong.
3. **Numbered steps with outputs** — a step without an artifact is a wish.
4. **A verification section** — checkboxes that someone else could run.
5. **`## Knowledge base`** — cite the `T-nn` techniques it derives from.
6. **`## Related`** — cross-reference with backticks so the validator can resolve them.

Then:

```bash
python tools/validate_skills.py
```

It will fail on missing cross-references, missing tool paths, malformed frontmatter, and
citations to techniques that do not exist. **That check is not decorative** — it caught a
dangling `palette_report.py` reference during this library's own build.

---

## Common mistakes with this library

| Mistake | Why it fails |
|---|---|
| Loading five skills at once | Contradictory advice, no clear procedure |
| Skipping the orchestrator contract | The task expands until it never finishes |
| Comparing renders from different cameras | Every metric is meaningless |
| Keying a lit backdrop for a mask | Grain and gradients destroy the bounding box |
| Trusting "executed successfully" | It means a process ran, not that the scene is right |
| Nudging one parameter a third time | Three attempts at the same approach = wrong method |
| Reporting a passing metric you did not measure | The one thing that makes the whole library worthless |

---

## Where to go next

- [`README.md`](README.md) — the index of the skills
- [`TEST_RESULTS.md`](TEST_RESULTS.md) — what was actually run, including the failure
- [`LIMITATIONS.md`](LIMITATIONS.md) — read this before trusting a skill
- [`COVERAGE.md`](COVERAGE.md) — skill × technique matrix
- [`knowledge-base/README.md`](knowledge-base/README.md) — the 81 techniques
