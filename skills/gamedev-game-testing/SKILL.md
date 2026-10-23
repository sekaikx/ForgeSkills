---
name: gamedev-game-testing
description: >
  Write tests for games and 3D assets: headless smoke tests, state-machine assertions,
  visual regression against a reference, and automated loop tests. Use when setting up
  verification for a project, when a bug should never return, or when "it works" needs
  to be demonstrable.
license: Apache-2.0
compatibility: Engine-agnostic. Godot 4.x headless, Blender Python, Python + Pillow/numpy.
metadata:
  engine: any
  category: gamedev-workflow
  difficulty: intermediate
---

# Game testing — make "it works" checkable

Games resist unit testing because most behaviour is visual and stateful. It is still testable
if you test the right layers: pure logic, then state transitions, then artifacts, then
rendered output.

## When to use

- A bug was fixed and must not return.
- Setting up a project's verification story.
- A gameplay system needs proof it behaves.
- An asset pipeline needs a gate.

## When not to use

- Exploratory prototype work where the design is still moving (test after the design
  settles).

## The four test layers

Test from the bottom up. Most game test suites fail because they only have the top layer.

| Layer | What | Speed | Value |
|---|---|---|---|
| 1. Pure logic | damage formulas, inventory rules, economy | ms | highest |
| 2. State machines | transitions, guards, event emission | 10-100 ms | high |
| 3. Headless integration | scene boots, systems wire up, loop runs | 0.5-5 s | high |
| 4. Visual regression | render matches reference within tolerance | seconds | medium |

## Layer 1 — Pull logic out of the engine

The single biggest testability win: put rules in plain functions/classes with no engine
dependency.

```python
def damage_after_mitigation(raw, armour, resistance=0.0):
    """Pure: no engine types, no globals, fully testable."""
    return max(0.0, raw * (1.0 - armour / (armour + 100.0)) * (1.0 - resistance))
```

Then the engine script is a thin adapter. The formula is now testable in milliseconds, and
balance changes are data edits.

```python
assert damage_after_mitigation(100, 0) == 100
assert damage_after_mitigation(100, 100) == 50
assert damage_after_mitigation(100, 100, 0.5) == 25
assert damage_after_mitigation(0, 50) == 0
```

Those four assertions catch nearly every balance regression.

## Layer 2 — State machine assertions

Test transitions and signal emission, not visuals:

```gdscript
func test_damage_stages() -> void:
    var d := Damageable.new()
    d.max_integrity = 100.0
    d.integrity = 100.0

    var stages: Array = []
    d.stage_changed.connect(func(o, n): stages.append([o, n]))

    d.apply_damage(40.0)          # 60 -> damaged
    assert(d.stage == 1)
    d.apply_damage(30.0)          # 30 -> critical
    assert(d.stage == 2)
    d.apply_damage(40.0)          # 0 -> destroyed
    assert(d.integrity == 0.0)
    assert(stages.size() == 2)
```

Test **the boundaries specifically**: exactly at a threshold, one unit below, one above.
Off-by-one at a stage boundary is the classic gameplay bug.

## Layer 3 — Headless integration

Boot the real scene without a display and assert it reached a running state:

```
godot --headless --path <project> --quit-after 1
godot --headless --path <project> --script tests/smoke.gd
```

What to assert:

```
[ ] process exit code is 0
[ ] stderr contains no "ERROR" / "SCRIPT ERROR" lines
[ ] the expected nodes exist after one frame
[ ] each system reports a valid initial state
[ ] one scripted action produces one expected state change
```

Parsing stderr is essential: Godot can exit 0 while printing script errors.

```python
def assert_clean(output: str) -> None:
    bad = [l for l in output.splitlines() if "ERROR" in l or "SCRIPT ERROR" in l]
    assert not bad, "engine reported errors:\n" + "\n".join(bad[:20])
```

## Layer 4 — Visual regression

Compare against a stored reference with a tolerance, never exact equality.

```python
report = compare.evaluate(ref="refs/hero_front.png", test="out/render.png",
                          kind="character", size=(512, 512))
assert report["silhouette_iou"] >= 0.85, report["silhouette_iou"]
assert report["band_max_err_pct"] <= 8.0, report["band_err_pct"]
```

Rules that keep visual tests useful:

- **Store the reference image** in the repo, small.
- **Render deterministically**: fixed camera, fixed light rig, fixed seed, transparent film.
- **Assert shape before colour.** Colour drift is expected across driver/GPU changes; shape
  should not drift.
- **Use a tolerance**, and write down why. Exact match tests break on every driver update and
  get deleted.
- **Update the reference only when the change was intentional**, and say so in the commit.

## Layer 4b — Asset validation (pre-render gate)

Cheap structural checks that catch most broken assets before any visual test:

```
[ ] scale: bounds height within 2% of target
[ ] origin at the ground plane
[ ] no geometry below z=0 or outside the intended envelope
[ ] no isolated objects far from the body mass
[ ] tri count within budget
[ ] material count and names as expected
[ ] no zero-area faces / no NaN vertex coordinates
```

These run in milliseconds and catch the failures that are expensive to debug visually.

## The loop test (per gameplay system)

```
1. set up a known initial state
2. perform a scripted action
3. assert the resulting state
4. assert the feedback signal fired
5. tear down cleanly (no leaked nodes)
```

**Prove the test works**: break the rule deliberately and confirm the test fails. A test that
cannot fail is documentation, not a test.

## What not to test

- Frame-perfect visual details (brittle, low value).
- Third-party engine behaviour.
- Anything you would have to rewrite the code to make testable — fix the architecture instead
  (that is layer 1's whole point).

## CI shape

```
fast   (< 30 s) : layer 1 + 2 on every change
medium (< 3 m)  : layer 3 on every push
slow   (< 10 m) : layer 4 + asset gates nightly
```

## Related

- `gamedev-verification` — evidence discipline and the false-success catalogue
- `gamedev-debugging` — turning a repro into a test
- `gamedev-gameplay-systems` — the systems being tested
- `gamedev-visual-iteration` — the metrics visual tests reuse

## Knowledge base

T-06 (instrumented testing), T-41 (gameplay loop test), T-48 (bot nav validation), T-51/T-52
(breaking and multi-angle tests).
