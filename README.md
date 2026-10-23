# ForgeSkills

20 game-development skills for AI coding agents. Each one is a procedure with gates — what to do, in what order, what to measure, and what counts as done — plus the Python tooling that makes the claims checkable.

Built for agents that write code, drive Blender, and ship game assets, not for chatting about game design.

```
measure → build → render → compare → fix one thing → repeat
```

---

## What's in here

| Group | Skills |
|---|---|
| **Workflow core** | `gamedev-orchestrator`, `gamedev-verification`, `gamedev-visual-iteration`, `gamedev-debugging`, `gamedev-game-testing` |
| **Assets** | `gamedev-reference-reconstruction`, `gamedev-blender-headless`, `gamedev-procedural-modeling`, `gamedev-modular-kit`, `gamedev-texture-authoring` |
| **Motion and feel** | `gamedev-animation`, `gamedev-locomotion`, `gamedev-vfx-impact` |
| **World and presentation** | `gamedev-lighting`, `gamedev-camera`, `gamedev-world-from-data` |
| **Systems and shipping** | `gamedev-gameplay-systems`, `gamedev-performance`, `gamedev-godot-pipeline`, `gamedev-unity-pipeline` |

Full index with one-line descriptions: [`docs/README.md`](docs/README.md).

### The skills, individually

<details>
<summary><b>Workflow core</b> — start here</summary>

| Skill | Solves |
|---|---|
| `gamedev-orchestrator` | A one-line brief that has to become a staged, gated build. Turns the request into a six-line contract and refuses to start while any line is blank. |
| `gamedev-verification` | "It said success" without evidence. Artifact-level proof, engine smoke tests, and the specific ways AI game work reports false success. |
| `gamedev-visual-iteration` | Visual work that stalls after several passes. Render, compare, rank discrepancies, fix one cause, re-render. |
| `gamedev-debugging` | A failure whose cause is not obvious, or a fix that made it worse. Reproduce, isolate, instrument, bisect to one cause. |
| `gamedev-game-testing` | Turning "it works" into a test: headless smoke runs, state-machine assertions, visual regression, loop tests. |

</details>

<details>
<summary><b>Assets</b> — modelling, texturing, kits</summary>

| Skill | Solves |
|---|---|
| `gamedev-reference-reconstruction` | A supplied concept sheet or turnaround that must be rebuilt as the actual asset, not something "inspired by" it. Includes measurable acceptance criteria and a discrepancy ledger. |
| `gamedev-blender-headless` | Scripted Blender: builds, batch renders, exports. Covers the 4.x/5.x API differences that break scripts. |
| `gamedev-procedural-modeling` | Geometry from parameters — lofts, capsules, sweeps, scattered props. And when *not* to go procedural. |
| `gamedev-modular-kit` | Environments from reusable parts: grid rules, pivots, shared atlas, parameterized variants. |
| `gamedev-texture-authoring` | PBR maps derived from one albedo, seamless tiling, texel density, atlases. |

</details>

<details>
<summary><b>Motion and feel</b></summary>

| Skill | Solves |
|---|---|
| `gamedev-animation` | Rigging and skinning by script, authoring clips, retargeting between rigs. |
| `gamedev-locomotion` | Movement that feels floaty, slippery or unresponsive when the animation is already correct. |
| `gamedev-vfx-impact` | Combat that feels weightless. Layered impact FX, hitstop, screen response, fracture. |

</details>

<details>
<summary><b>World and presentation</b></summary>

| Skill | Solves |
|---|---|
| `gamedev-lighting` | Scenes that are technically lit but read flat. Key/fill/rim, shadow budget, mood matching. |
| `gamedev-camera` | A view that is nauseating, unreadable, or fighting the player. |
| `gamedev-world-from-data` | Terrain, roads and rivers built from elevation data instead of by hand. |

</details>

<details>
<summary><b>Systems and shipping</b></summary>

| Skill | Solves |
|---|---|
| `gamedev-gameplay-systems` | Enemies, combat with damage stages, inventory, spawning, spec-first balance. |
| `gamedev-performance` | Frame budgets: draw calls, LOD, occlusion, texture memory, detail by screen size. |
| `gamedev-godot-pipeline` | Godot 4.x scene structure, import settings, autoloads, headless verification. |
| `gamedev-unity-pipeline` | Unity 6 import settings, prefabs, URP/HDRP, ScriptableObject data, build checks. |

</details>

---

## Install

Skills are folders containing a `SKILL.md`. Every agent below reads that layout, so installation is a file copy — no build step, no package manager.

Clone once:

```bash
git clone https://github.com/sekaikx/ForgeSkills.git
cd ForgeSkills
```

### Claude Code

Claude Code reads `~/.claude/skills/<name>/SKILL.md` for personal skills and `.claude/skills/<name>/SKILL.md` for project skills.

**Personal — available in every project on this machine:**

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -r skills/gamedev-* ~/.claude/skills/

# Windows (PowerShell)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item skills\gamedev-* -Destination "$env:USERPROFILE\.claude\skills" -Recurse
```

**Project — committed with the repo, shared with anyone who clones it:**

```bash
mkdir -p .claude/skills
cp -r ../ForgeSkills/skills/gamedev-* .claude/skills/
git add .claude/skills && git commit -m "Add ForgeSkills game dev skills"
```

Claude loads them automatically when a request matches a skill's `description`, or you can call one directly with `/gamedev-orchestrator`. Restart the session if `~/.claude/skills` did not exist when it started.

### Cursor

Cursor discovers `.agents/skills/`, `.cursor/skills/`, and the user-level `~/.agents/skills/` and `~/.cursor/skills/`. It also reads `.claude/skills/`, so the Claude Code project install above works unchanged.

```bash
# project, shared via git
mkdir -p .agents/skills
cp -r ../ForgeSkills/skills/gamedev-* .agents/skills/

# or personal, all projects
mkdir -p ~/.cursor/skills
cp -r ../ForgeSkills/skills/gamedev-* ~/.cursor/skills/
```

Type `/` in Agent chat to pick a skill by name.

### Other agents

Any tool that implements the Agent Skills layout reads these as-is:

| Tool | Path |
|---|---|
| Codex | `.codex/skills/` or `~/.codex/skills/` |
| Windsurf, Cline, Roo | Point the skill/rule directory at `skills/`, or copy the folders in |
| Anything else | A folder per skill, `SKILL.md` inside, YAML frontmatter with `name` and `description` |

If your agent only supports a single rules file, concatenate the skills you need rather than all twenty — the descriptions are written to be matched against, and a wall of text defeats that.

### Put the tooling where the skills expect it

Skill bodies reference scripts as `tools/refmatch/...` and `tools/texture/...`, relative to the repo root. If you copied skills somewhere else, either keep a `ForgeSkills/` checkout next to the project and reference it by absolute path, or symlink `tools/`:

```bash
ln -s ~/ForgeSkills/tools ./tools          # macOS / Linux
```

```powershell
New-Item -ItemType Junction -Path .\tools -Target "$env:USERPROFILE\ForgeSkills\tools"
```

Nothing breaks if you skip this — the skills still contain the full procedure — but the measurement steps need the scripts.

---

## Requirements

```bash
pip install pillow numpy
```

| Component | Needs |
|---|---|
| All skills | Nothing |
| `tools/refmatch/*`, `tools/texture/tex_to_maps.py`, `tile_seam_check.py` | Python 3.10+, Pillow, numpy |
| `tools/texture/uv_density.py` | Python 3.10+ (stdlib only) |
| `tools/blender/*` | Blender 4.2+ or 5.x |
| Godot / Unity pipeline skills | The engine — not required to read the skill |

---

## Tooling

Real scripts with CLIs, not snippets. Each exits nonzero on a failed check, so they drop into CI.

| Script | What it measures |
|---|---|
| `tools/validate_skills.py` | Lints this library: frontmatter, name/directory match, cross-references, tool paths, technique citations |
| `tools/refmatch/compare.py` | Silhouette IoU, 10-band width profile, palette ΔE, aspect ratio, luminance histogram correlation, SSIM (advisory) |
| `tools/refmatch/overlay.py` | Three-panel diagnostic sheet: reference, render, disagreement map |
| `tools/refmatch/measure_sheet.py` | Clean panel crop and palette out of a concept sheet |
| `tools/refmatch/palette_report.py` | Named colour roles against a render, per-role ΔE |
| `tools/texture/tex_to_maps.py` | Roughness, tangent-space normal, cavity map from one albedo |
| `tools/texture/tile_seam_check.py` | Wrap-boundary continuity against the interior distribution |
| `tools/texture/uv_density.py` | Per-part texel density from an OBJ, flags spread |
| `tools/blender/character_blockout.py` | Parametric human blockout from measured fractions |
| `tools/blender/render_compare_views.py` | Fixed-camera turnaround renders with alpha |
| `tools/blender/validate_scene.py` | Stray geometry, scale, geometry below the floor |
| `tools/blender/explorer_build.py` | Worked example: garment and equipment pass |

Typical chain for a reference-to-asset job:

```
measure_sheet → character_blockout → validate_scene → render_compare_views
     → compare + overlay → fix one cause → repeat
```

---

## Verify it

```bash
python tools/validate_skills.py
```

```
SKILL LIBRARY VALIDATION — 20 skills, 58 techniques known
[OK  ] gamedev-animation                 1016 words
...
ERRORS 0   WARNINGS 0
```

The validator is not decorative. It caught a dangling tool reference during this library's own build, and it caught itself silently passing on an empty directory — which is now a hard failure, because a check that passes on an empty set is not a check.

---

## Using a skill

Skills are loaded by description match. You do not need to name them:

> "Rebuild this character sheet as a 3D model."

`gamedev-reference-reconstruction` matches, and its procedure takes over: measure the reference, build to the measurements, render from the same camera, compare numerically, close the largest discrepancy, repeat until the acceptance criteria pass or the budget runs out.

Naming a skill explicitly forces it:

> "Use `gamedev-orchestrator` and plan this out before writing code."

The core loop skills are designed to chain:

| You want | Run |
|---|---|
| A brief turned into staged work | `gamedev-orchestrator` |
| An asset that matches a picture | `gamedev-reference-reconstruction` → `gamedev-visual-iteration` |
| A visual task that is stuck | `gamedev-visual-iteration` |
| Proof the work is done | `gamedev-verification` |
| A bug found, not guessed at | `gamedev-debugging` → `gamedev-game-testing` |

---

## Design rules

Three rules hold across all twenty skills:

1. **Measure, don't eyeball.** Every visual claim carries a number.
2. **One variable per iteration.** Change two things and you learn nothing.
3. **Evidence or silence.** "Script executed successfully" is not evidence the artifact is right.

---

## Honest status

Read [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) before trusting this with real work.

- **Exercised:** workflow discipline, Blender scripting pitfalls, comparison and texture tooling. Real bugs were found and fixed while building it.
- **Written but not executed:** the Godot and Unity pipeline skills. No engine was installed where they were authored, so their checklists are a specification to verify on first use.
- **Failed its own test:** the reference reconstruction in this repo reached silhouette IoU 0.46 against a required 0.85. It is documented rather than removed, because the tooling correctly identified and quantified the failure. See [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md).

---

## Repository layout

```
ForgeSkills/
├── skills/                    20 skills, one folder each
│   └── gamedev-<name>/SKILL.md
├── tools/
│   ├── validate_skills.py
│   ├── refmatch/              reference-vs-render comparison
│   ├── texture/               PBR maps, tiling, texel density
│   └── blender/               scripted build, render, validation
└── docs/
    ├── README.md              index of all 20 skills
    ├── USAGE.md               worked command lines
    ├── TEST_RESULTS.md        what was run, including what failed
    ├── LIMITATIONS.md         blind spots and unverified claims
    ├── COVERAGE.md            skill × technique matrix
    ├── transcript-sources.md  technique → source traceability
    └── knowledge-base/        58 techniques, T-01 … T-58
```

---

## Contributing

A skill earns its place by being specific enough to disagree with. When adding one:

1. `name` must equal the directory name.
2. The first sentence of `description` states *when to use it* — that is what the agent matches on.
3. Include both `## When to use` and `## When not to use`. The negative case is what stops misapplication.
4. Every step produces an artifact. A step without an artifact is a wish.
5. Verification checkboxes must be runnable by someone else.
6. Cross-reference other skills in backticks so the validator can resolve them.

Then run `python tools/validate_skills.py` and get zero errors.

---

## License

Apache-2.0. See [`LICENSE`](LICENSE).
