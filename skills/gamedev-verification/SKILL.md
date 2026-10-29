---
name: gamedev-verification
description: >
  Prove work is finished before claiming it, by inspecting the actual result. Use before
  reporting done, before handoff, or when a tool said success and you have not looked. For
  writing repeatable tests use game-testing.
license: Apache-2.0
compatibility: Engine-agnostic. Examples for Godot 4.x, Unity 6, Blender 4.x/5.x.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Verification — evidence before claims

A tool exiting 0 means a process ran. It does not mean the artifact is correct. Every claim
of completion needs evidence that a skeptical stranger could re-check.

## When to use

- About to say "done", "fixed", "working", "passing".
- A build/export/render command returned success.
- After a refactor, before moving to the next feature.
- Any time you have not actually *looked* at the output.

## When not to use

- Mid-implementation exploration (verify at the boundary, not every keystroke).
- Pure documentation edits with no runtime behaviour.

## The four levels of evidence

Always climb to the highest level the task warrants. Most false completion claims stop at
level 1.

| Level | Evidence | Proves |
|---|---|---|
| 1 | Command exited 0 | A process ran |
| 2 | Artifact exists, non-trivial size | Something was produced |
| 3 | Artifact loads/parses, structure is correct | It is well-formed |
| 4 | Behaviour is observed and measured | It actually works |

**Level 4 examples:** the render compared against the reference with a number; the scene
loaded in-engine and the player moved 4.0 m in 1.0 s; the exported GLB imported back with the
expected material count and forward axis.

## Verification checklist by artifact type

### 3D asset (Blender → engine)

```
[ ] scale: bounds measured in metres, height matches the target within 2%
[ ] orientation: forward axis is the documented one (Blender -Y  ->  engine convention)
[ ] origin: at the ground between the feet / at the base of the prop
[ ] no stray geometry: every object inside the intended envelope
[ ] no isolated objects: nothing floating far from the body mass
[ ] materials: count and names survive export; textures are packed or copied
[ ] topology: tri count within budget; no non-manifold explosion
[ ] import test: load in the target engine, not just the exporter's log
[ ] re-import gate: after writing the delivery file (OBJ/GLB/FBX), load that file fresh and
    measure bounds/silhouette from the loaded geometry — never from the in-memory mesh or an
    intermediate profile array you used to build it
[ ] orientation sanity: for rotationally symmetric props, the radius-max row as a fraction of
    height (0 = base, 1 = top) must match the reference within ~0.10; a value near 1.0 − ref
    usually means the profile was flipped when mapping image rows to world Y
```

Do not trust `ob.bound_box` right after a script edits a mesh — it is cached and reports the
previous mesh. Read evaluated vertices through the depsgraph, or the validation passes on
stale numbers.

### Render / visual output

```
[ ] rendered from the calibrated camera, same aspect and subject fraction as the target
[ ] alpha channel exists (exact silhouette) rather than guessing from a lit backdrop
[ ] compared numerically: silhouette IoU, band widths, palette delta-E
[ ] looked at with your own eyes at native resolution, not a thumbnail
[ ] the largest discrepancy is named, not averaged away
```

### Engine scene (Godot / Unity)

```
[ ] headless run exits 0 AND stderr has no errors (warnings reviewed, not ignored)
[ ] the scene opens, not just the project
[ ] each system prints its own state on boot (instrumentation, not guesswork)
[ ] one full loop executed: input -> state change -> visible result
[ ] the loop executed at the target frame budget, measured
[ ] no reliance on the editor having been open: a clean run reproduces
```

### Code change

```
[ ] the changed path was exercised, not just imported
[ ] a failing case was constructed and now passes
[ ] nothing else regressed: neighbouring behaviour re-checked
[ ] no debug prints or hardcoded paths left behind
```

## The false-success catalogue

These are the specific ways this kind of work lies to you. Each has a one-line antidote.

| Claim | Why it is false | Antidote |
|---|---|---|
| "Script executed successfully" | It ran; the output may be an empty scene | Assert object count / tri count after |
| "Export completed" | A file was written; it may be empty or axis-flipped | Re-import and measure |
| "Render saved" | The camera may be pointed at nothing | Open the image; check subject coverage > 5% |
| "No errors" | Errors were swallowed or logged to a file you didn't read | Check stderr explicitly |
| "Tests pass" | The tests don't cover the changed path | Name the test that covers the change |
| "Metrics improved" | The metric measured the wrong thing | Sanity check that a worse artifact scores worse |
| "It looks right" | Judged from a thumbnail or a stale file | Re-read the artifact at native size |

## Rules

1. **Never claim a number you did not measure.** If you estimate, say "estimated".
2. **Never cite a file you did not open after generating it.** Overwriting is silent.
3. **Always state the gate and its result**, even when it passed:
   `silhouette IoU 0.4628 (need 0.85) → FAIL`.
4. **Report partial results honestly.** "4 of 6 criteria pass, aspect fails at 15.7%" is
   useful. "Done" is not.
5. **A passing metric that contradicts your eyes is a broken metric.** Investigate before
   trusting either.

## Verification report format

```
TASK        : <what was to be done>
CLAIM       : <what you are asserting>
EVIDENCE    : <level 4 observations, with paths and numbers>
NOT VERIFIED: <anything you could not test, and why>
CONFIDENCE  : high | medium | low — because <reason>
```

The `NOT VERIFIED` line is mandatory. A report without it is almost always hiding something.

## Related

- `gamedev-game-testing` — constructing the tests themselves
- `gamedev-debugging` — when verification fails and the cause is not obvious
- `gamedev-orchestrator` — where gates are defined

## Knowledge base

T-06 (instrumented testing), T-02 (gauntlet loop), T-07 (reference-first), T-52 (multi-angle
breaking tests).
