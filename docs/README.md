# AI Game Development Skills Library

20 executable skills for AI agents doing game and 3D asset work, plus the tooling that makes
their claims checkable. Every technique traces back to the 12 analysed transcripts — see
[`transcript-sources.md`](transcript-sources.md) and the
[`knowledge-base/`](knowledge-base/README.md).

## What this is

Not a prompt collection. Each skill is a **procedure with gates**: what to do, in what order,
what to measure, what counts as done, and the specific ways the work fails.

Three rules hold across the whole library:

1. **Measure, don't eyeball.** Every visual claim has a number attached.
2. **One variable per iteration.** Change two things and you learn nothing.
3. **Evidence or silence.** "Script executed successfully" is not evidence the artifact is right.

## The skills

### Workflow core — start here

| Skill | Use it for |
|---|---|
| [orchestrator](../skills/gamedev-orchestrator/SKILL.md) | Turning a one-line brief into staged work with gates |
| [verification](../skills/gamedev-verification/SKILL.md) | Proving work is done before claiming it |
| [visual-iteration](../skills/gamedev-visual-iteration/SKILL.md) | Closing the loop on any visual target |
| [debugging](../skills/gamedev-debugging/SKILL.md) | Finding the cause instead of the symptom |
| [game-testing](../skills/gamedev-game-testing/SKILL.md) | Tests for logic, state, scenes and renders |

### Assets

| Skill | Use it for |
|---|---|
| [reference-reconstruction](../skills/gamedev-reference-reconstruction/SKILL.md) | Rebuilding a supplied image as real 3D |
| [blender-headless](../skills/gamedev-blender-headless/SKILL.md) | Scripted builds, renders, exports |
| [procedural-modeling](../skills/gamedev-procedural-modeling/SKILL.md) | Geometry from parameters |
| [modular-kit](../skills/gamedev-modular-kit/SKILL.md) | Environments from reusable parts |
| [texture-authoring](../skills/gamedev-texture-authoring/SKILL.md) | PBR maps, tiling, atlases, density |

### Motion and feel

| Skill | Use it for |
|---|---|
| [animation](../skills/gamedev-animation/SKILL.md) | Rigs, skinning, clips, retargeting |
| [locomotion](../skills/gamedev-locomotion/SKILL.md) | Movement that feels right |
| [vfx-impact](../skills/gamedev-vfx-impact/SKILL.md) | Hit feedback, destruction, screen response |

### World and presentation

| Skill | Use it for |
|---|---|
| [lighting](../skills/gamedev-lighting/SKILL.md) | Light rigs, shadow budgets, presets |
| [camera](../skills/gamedev-camera/SKILL.md) | Framing, follow rigs, shake |
| [world-from-data](../skills/gamedev-world-from-data/SKILL.md) | Terrain, roads, rivers from height data |

### Systems and shipping

| Skill | Use it for |
|---|---|
| [gameplay-systems](../skills/gamedev-gameplay-systems/SKILL.md) | Enemies, combat, inventory, balance |
| [performance](../skills/gamedev-performance/SKILL.md) | Budgets, LOD, draw calls |
| [godot-pipeline](../skills/gamedev-godot-pipeline/SKILL.md) | Godot 4.x import and wiring |
| [unity-pipeline](../skills/gamedev-unity-pipeline/SKILL.md) | Unity 6 import and wiring |

## Tooling

Real scripts, not snippets. All run.

| Tool | Purpose | Deps |
|---|---|---|
| [`tools/validate_skills.py`](../tools/validate_skills.py) | Lint this library: frontmatter, cross-refs, tool paths | stdlib |
| [`tools/refmatch/compare.py`](../tools/refmatch/compare.py) | Silhouette IoU, band profile, palette ΔE, aspect, SSIM | Pillow, numpy |
| [`tools/refmatch/overlay.py`](../tools/refmatch/overlay.py) | Three-panel diagnostic sheet | Pillow, numpy |
| [`tools/refmatch/measure_sheet.py`](../tools/refmatch/measure_sheet.py) | Clean panel + palette from a concept sheet | Pillow, numpy |
| [`tools/refmatch/palette_report.py`](../tools/refmatch/palette_report.py) | Named palette vs render, per-role ΔE | Pillow, numpy |
| [`tools/blender/character_blockout.py`](../tools/blender/character_blockout.py) | Parametric human blockout from fractions | Blender |
| [`tools/blender/render_compare_views.py`](../tools/blender/render_compare_views.py) | Fixed-camera turnaround renders | Blender |
| [`tools/blender/validate_scene.py`](../tools/blender/validate_scene.py) | Stray geometry and proportion gate | Blender |
| [`tools/blender/explorer_common.py`](../tools/blender/explorer_common.py) | Loft/capsule/box builders | Blender |
| [`tools/blender/explorer_build.py`](../tools/blender/explorer_build.py) | Garment/equipment pass | Blender |
| [`tools/texture/tex_to_maps.py`](../tools/texture/tex_to_maps.py) | Roughness, normal, cavity maps from one albedo | Pillow, numpy |
| [`tools/texture/tile_seam_check.py`](../tools/texture/tile_seam_check.py) | Wrap-boundary continuity, plus a tiled preview | Pillow, numpy |
| [`tools/texture/uv_density.py`](../tools/texture/uv_density.py) | Per-part texel density from an OBJ | stdlib |

## Typical chains

**Reference → asset**
```
measure_sheet  →  character_blockout  →  validate_scene  →  render_compare_views
      →  compare + overlay  →  fix one thing  →  repeat
```

**Brief → playable**
```
orchestrator (contract + gates)  →  blockout  →  systems  →  integration
      →  vfx/lighting/camera polish  →  headless smoke test  →  evidence
```

**Broken thing**
```
debugging (repro, bisect, instrument)  →  game-testing (permanent test)
      →  verification (prove it, including regressions)
```

## Status, honestly

See [`TEST_RESULTS.md`](TEST_RESULTS.md) for what was actually executed, and
[`LIMITATIONS.md`](LIMITATIONS.md) for what is missing, unproven, or failed.

Short version: the workflow and tooling skills are exercised. The engine pipeline skills
(Godot, Unity) are **written from documented behaviour but were not run** — no engine was
installed in this environment, so treat their checklists as a specification to verify on first
use, not as tested recipes.
