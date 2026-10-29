---
name: gamedev-orchestrator
description: >
  Plan a multi-stage game or asset task, or a whole game from idea to launch: stages, which
  skills apply, data gates. Use at the start of any non-trivial game task, or when one is
  stalling or sprawling.
license: Apache-2.0
compatibility: Engine-agnostic. Works with Godot 4.x, Unity 6, Blender 4.x/5.x.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Orchestrator — from brief to verified build

The job is not to write the most code. It is to **close the loop**: every stage has an
input, an output artifact, and a gate that proves the output is real.

## When to use

- Any request with more than ~3 distinct deliverables ("build a game", "make this whole
  system", "rebuild this reference").
- A task that has stalled, or where attempts keep failing on the same class of problem.
- Complex multi-stage work — this skill plans the stages; `gamedev-visual-iteration`
  executes the per-artifact loop; `gamedev-verification` proves the result.

## When not to use

- Single-file edits, one function, one bug fix.
- Pure questions ("how does X work") — answer directly.

## Step 1 — Write the brief as a contract

Convert the request into six lines before touching tools. Refuse to start while any is
blank or says "TBD".

```
DELIVERABLE : <what exists at the end, as an artifact, not an activity>
RUNTIME     : <engine + version, or DCC-only>
SCOPE-IN    : <the 3-7 things that must work>
SCOPE-OUT   : <what is deliberately not being built>
ACCEPT      : <measurable pass criteria per scope-in item>
BUDGET      : <time, poly, draw calls, files — whichever binds>
```

**Why the contract matters.** Vague briefs don't fail loudly, they fail by expanding.
"Build a survival game" has no gate, so it never completes. "Player gathers wood, crafts an
axe, chops a tree, tree falls with VFX over 1.2 s, 60 fps at 1080p" has three gates and can
be finished.

If the user's brief is a single sentence, still write this table, then state your
assumptions out loud. That is the whole point — an unstated assumption is the defect you
will debug in an hour.

**New game, not a new task.** If nobody has decided the game is worth making, stop and use
`gamedev-concept-judge` (an idea exists) or `gamedev-concept-lab` (it does not). Do not
spend stages 4–8 on a pitch with no verdict. If two greyboxes already exist, play both
and keep one before any art (T-74): the source threw out two worlds after playing them.

**Idea to launch.** For a whole game, not one task, run the phase map in
`references/lifecycle.md`: idea, verdict, prototype, playtest, page, marketing, launch. Each
phase ends at a gate graded by `gamedev-critic` on data, not on how the team feels.

## Step 2 — Decompose into stages with artifacts

Each stage must own **one artifact** and **one gate**. A stage without an artifact is not a
stage, it is a wish.

| Stage | Artifact | Gate |
|---|---|---|
| 1. Plan | `docs/brief.md` contract table | every field filled, no TBD |
| 2. Reference | measured landmark/palette table | numbers recorded, not adjectives |
| 3. Blockout | gray-box scene / silhouette render | proportions within tolerance, camera calibrated |
| 4. Systems | one script/resource per system | each system runs alone, prints its own state |
| 5. Content | assets placed, materials applied | scene validates, no stray geometry |
| 6. Integration | playable loop | loop completes without error, in-engine |
| 7. Polish | VFX/audio/feedback | timing budget documented |
| 8. Verification | test log + screenshots | every ACCEPT item has evidence |

**Ordering rule:** build the thing that is hardest to change *first*. Scale and camera
before materials. Systems before content. Content before polish. Polish is the cheapest to
redo and the most tempting to start with — do it last.

## Step 3 — Pick the sub-skill per stage

| If the stage is… | Use |
|---|---|
| Measuring a supplied image, rebuilding it faithfully | `gamedev-reference-reconstruction` |
| Scripted Blender build/render/export | `gamedev-blender-headless` |
| Procedural meshes, kits, modular pieces | `gamedev-procedural-modeling`, `gamedev-modular-kit` |
| Textures, PBR maps, tiling | `gamedev-texture-authoring` |
| Rigs, skinning, animation clips | `gamedev-animation` |
| Player/enemy movement feel | `gamedev-locomotion` |
| Hit feedback, particles, screenshake | `gamedev-vfx-impact` |
| Light rigs, mood, shadow budget | `gamedev-lighting` |
| Framing, FOV, camera rigs | `gamedev-camera` |
| Enemies, combat, inventory, loops | `gamedev-gameplay-systems` |
| A boss or set-piece duel | `gamedev-boss-encounter` |
| Silence, impacts, music cues | `gamedev-audio-wire` |
| Terrain/roads/rivers from height data | `gamedev-world-from-data` |
| LODs, budgets, draw calls | `gamedev-performance` |
| Godot project wiring | `gamedev-godot-pipeline` |
| Unity project wiring | `gamedev-unity-pipeline` |
| Something is broken | `gamedev-debugging` |
| Proving it works | `gamedev-verification`, `gamedev-game-testing` |
| Events the build must log | `gamedev-telemetry` |
| Bots and agents playing the build | `gamedev-playtest-agents` |
| Playtest numbers into a decision | `gamedev-playtest-analysis` |
| Store page, capsule, trailer | `gamedev-store-page` |
| Wishlists, channels, launch beats | `gamedev-marketing-loop` |
| Grading any claim at a gate | `gamedev-critic` |

Load one at a time. Loading five produces mush.

## Step 4 — Run the loop per artifact

```
PLAN    the single change or build
DO      execute it (script it, so it is repeatable)
CHECK   run the stage gate -> artifact + measured evidence
JUDGE   pass | fail | unclear
ACT     pass -> next stage.  fail -> fix ONE cause.  unclear -> improve the gate, not the artifact
```

**Two-failure rule.** If the same stage fails twice for the same reason, do not try a third
variation. Stop, re-read the stage's assumptions, and change method. Three attempts at the
same approach is the signature of a wrong decomposition.

## Step 5 — Gate discipline (the part that actually matters)

A gate must be **runnable by someone else** and **falsifiable**.

| Bad gate | Good gate |
|---|---|
| "Looks good" | "silhouette IoU ≥ 0.85 vs `ref_front.png`" |
| "Runs fine" | "`godot --headless --quit` exits 0; no errors in output" |
| "Movement feels good" | "walk 4.0 m/s, jump apex 1.1 m, coyote 0.10 s — all measured in-game" |
| "Asset is optimized" | "≤ 12k tris, ≤ 40 meshes, draw calls ≤ 60" |
| "Textures are done" | "tile seam max gradient step ≤ 3/255 across the seam column" |

If you cannot write a gate, the stage is under-specified. Sharpen it before building.

## Working cheaply (tokens and wall time)

- **Run the tool, read its summary.** Measurement scripts print a verdict table; read that,
  not raw logs. Redirect engine output to a file and grep it.
- **Copy shipped assets, don't retype them** (shaders in `assets/`, tools in `tools/`).
- **Load references on demand** — only the `references/` section the current step names.
- **Batch engine launches.** One launch captures every viewpoint; a scene load costs a minute.
- **Grep before read; read by line range** in large projects and long docs.

## Failure modes and the fix

| Symptom | Cause | Fix |
|---|---|---|
| Endless polishing of stage 3 | No gate, so "done" is a feeling | Write the numeric gate |
| Everything breaks at integration | Stages verified in isolation only | Add an integration gate at stage 6 |
| Same error three times | Wrong decomposition or wrong assumption | Stop; change method, not parameters |
| Scope creeping every message | No SCOPE-OUT line | Write it, restate it to the user |
| Works in DCC, broken in engine | No engine-side gate | Gate every import, not just the source |
| Agent reports success, artifact is wrong | Gate was the generator's exit code | Gate on the artifact: render it, load it, measure it |

## Output contract

At the end of an orchestrated task, report:

```
DELIVERABLE : <path(s)>
STAGES      : <n> run, <n> gated, <n> passed first try
ACCEPT      : per item -> measured value -> PASS/FAIL
EVIDENCE    : <render/test/log paths>
OPEN        : <anything not met, with why>
NEXT        : <the single highest-value next step>
```

Never report a stage as passed without naming the artifact and the measurement that
proves it.

## Related

- `gamedev-visual-iteration` — the per-artifact loop in detail
- `gamedev-verification` — evidence discipline
- `gamedev-debugging` — when a gate fails and the cause is unclear

## Knowledge base

T-01 (orchestration roles), T-02 (gauntlet loop), T-03 (multi-model division of labour),
T-06 (instrumented testing), T-07 (reference-first iteration), T-74 (kill a greybox before art).
