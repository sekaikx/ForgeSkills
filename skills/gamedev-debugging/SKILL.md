---
name: gamedev-debugging
description: >
  Diagnose broken game and asset work systematically: reproduce, isolate, instrument, bisect
  to a single cause. Use when something fails and the cause is not obvious, when the same bug
  returns, or when a "fix" made it worse.
license: Apache-2.0
compatibility: Engine-agnostic; Blender Python, Godot 4.x, Unity 6.
metadata:
  engine: any
  category: gamedev-workflow
  difficulty: intermediate
---

# Debugging — cause, not symptom

The failure mode this skill prevents: changing things until the symptom disappears, without
ever knowing why. The bug returns and you cannot reproduce the fix.

## When to use

- Something is broken and the cause is not obvious.
- The same bug has returned.
- A fix improved one thing and broke another.
- Metrics disagree with what you see.

## When not to use

- The task simply isn't built yet (that's implementation, not debugging).
- A known typo or trivial syntax error.

## Step 1 — Reproduce, and write down the exact repro

```
REPRO      : <the smallest sequence of actions/steps that shows the bug>
EXPECTED   : <what should happen>
ACTUAL     : <what does happen, with the exact error or measurement>
FREQUENCY  : always | intermittent (n/m) | only under <condition>
LAST KNOWN GOOD : <when did this work>
```

If you cannot reproduce it deterministically, fix the **reproduction** first. Intermittent
bugs are usually one of: a timing/order dependency, a cached/stale value, uninitialized state,
or a race.

"Last known good" is the most valuable line and the most often skipped. It converts debugging
into a bisect.

## Step 2 — Read the whole error, and the line above it

```
[ ] the actual exception type, not just "it failed"
[ ] the full traceback, all frames
[ ] the line ABOVE (a passing line often reveals the bad input)
[ ] the values, not just the names — print them
[ ] stderr as well as stdout (they are different streams; errors often only go to one)
```

In Blender, "Code executed successfully" from an MCP tool does **not** mean the scene is
right. In Godot, a headless run can exit 0 while printing errors. Check the stream explicitly.

## Step 3 — Bisect

The fastest general technique. Two variants:

**Temporal bisect** (code changed): disable half the recent changes, test. Halve again.

**Spatial bisect** (scene/asset broke): hide half the objects, test. Halve again.

```
while candidates > 1:
    disable/test the first half
    if broken: keep first half
    else: keep second half
```

Ten objects -> four steps. Never comment out things one at a time.

## Step 4 — Instrument, don't stare

Add a print that reports the actual state, at the failure point:

```python
print(f"BEFORE: count={len(objs)} scale={scale!r} bounds={bounds}")
```

Print:
- the input values at the boundary,
- the state before and after the suspicious call,
- counts, not just existence (`len()` not `is not None`).

In Blender specifically:

```python
print("objects", len(bpy.data.objects))
print("contact_sheet", [(o.name, o.type) for o in bpy.data.objects])
print("material slots", [m.name if m else None for m in ob.data.materials])
```

**Instrumentation beats breakpoints** in headless contexts and in AI-driven loops, because you
cannot step through interactively.

## Step 5 — Check the classic suspects

These account for most bugs in game/asset work.

| Suspect | Symptom | Check |
|---|---|---|
| **Stale cache** | fix has no effect | reload modules; read evaluated data |
| **Units** | everything 100x off | degrees vs radians, cm vs m |
| **Z-up vs Y-up** | model lies on its face | check import settings |
| **Origin/transform** | object in the wrong place | `matrix_world` vs local |
| **Wrong space** | edits collapse the mesh | `v.co` is local, not world |
| **Off-by-one** | last element missing | `range(n)` vs `range(n+1)` |
| **Division by zero** | NaN geometry, invisible mesh | guard every divisor |
| **Non-normalized quaternion/vector** | drift, wrong rotation | `.normalized()` |
| **Mutation during iteration** | some items skipped | iterate over a copy |
| **Path escaping** | file not found | absolute paths, raw strings on Windows |
| **Encoding** | garbled names | explicit `utf-8` |

### Blender-specific traps

- `ob.bound_box` is cached — reports the previous mesh after an edit. Use the depsgraph.
- `v.co` is local; tapering with world-space absolutes collapses the mesh.
- Translating vertices then rotating the object rotates about the object origin.
- Modules are cached in a live session; `importlib.reload()` after editing.
- Loft rings with differing vertex counts crash the quad band.
- `bpy.ops` depends on context (selection, active object, mode) — prefer direct data API.

### Engine-specific traps

- **Godot**: a scene that runs in the editor can fail headless if it depends on editor-only
  state. `@tool` scripts run in both.
- **Godot**: signals connected in the editor break silently if the target is renamed.
- **Unity**: `Awake`/`Start` order is not guaranteed across objects; do not depend on it.
- **Unity**: domain reload can hide uninitialized static state.

## Step 6 — Fix the cause, then prove the fix

```
[ ] the repro no longer reproduces — from a clean run, not a patched session
[ ] the neighbouring behaviour still works
[ ] a check exists so this cannot silently return
[ ] you can explain WHY it was broken, in one sentence
```

If you cannot state the cause in one sentence, you have not finished debugging — you have only
stopped the symptom.

## Step 7 — When to change method instead

Stop debugging the current approach when:

- the same class of bug has appeared three times,
- the reproduction requires more than a few steps,
- the fix requires changing many unrelated places,
- you are debugging the same line repeatedly.

Those are signals of a wrong decomposition. Go back to the plan and change the approach. This
is not defeat; it is cheaper.

## Debug report format

```
BUG        : <one line>
CAUSE      : <one sentence, the actual mechanism>
FIX        : <what changed>
PROOF      : <the repro now passes; how you verified>
REGRESSION : <what else you checked>
```

## Related

- `gamedev-verification` — proving the fix, not just the absence of the error
- `gamedev-game-testing` — turning the repro into a permanent test
- `gamedev-orchestrator` — when the fix is a re-plan, not a patch

## Knowledge base

T-04 (graybox sequencing and re-scoping), T-06 (instrumented testing), T-37 (iterative
lighting diagnosis), T-52 (multi-angle breaking tests).
