---
name: gamedev-gameplay-systems
description: >
  Implement gameplay systems: enemy behaviour, combat with damage stages, inventory, carry
  and snap, wave spawning, and spec-first balance. Use when building enemies, combat,
  items, or any system whose rules must be legible and testable.
license: Apache-2.0
compatibility: Engine-agnostic; Godot 4.x GDScript examples, portable to Unity 6.
metadata:
  engine: any
  category: gamedev-gameplay
  difficulty: advanced
---

# Gameplay systems — rules that hold up

A gameplay system is a set of rules plus the feedback that makes them legible. Systems that
work in isolation and break together are the norm; the fix is contract-first design and a
loop test.

## When to use

- Implementing enemies, combat, inventory, crafting, waves, or progression.
- Balance work that keeps drifting.
- Systems that "work" but feel unclear to the player.

## When not to use

- Pure presentation work.
- A single trigger or scripted event, which is content, not a system.

## Step 1 — Write the spec before the code

For every system, write these five things. If you cannot, the system is not designed yet.

```
PURPOSE   : what decision this system asks the player to make
INPUTS    : what the player and the world feed in
STATE     : the minimal state that must persist
RULES     : the transitions, in order of evaluation
FEEDBACK  : how the player knows the state changed
```

Example, a cascading damage system:

```
PURPOSE   : decide when to retreat vs commit
INPUTS    : hit type, hit location, current stage
STATE     : integrity 0..100, stage enum
RULES     : 100..67 intact | 66..34 damaged (speed -20%) | 33..1 critical (smoke, speed -40%)
            | 0 destroyed (fracture + no control)
FEEDBACK  : visual damage decals, smoke, audio pitch, movement speed, HUD bar
```

**Damage stages beat a single health bar** because they communicate *how bad it is* without
the player reading a number. Three stages is the sweet spot; five is unreadable.

## Step 2 — One script per system, self-reporting

Each system should be a self-contained script that:

- owns its own state,
- emits events rather than reaching into other systems,
- can be run alone,
- **prints its state on demand** (instrumentation, not guesswork).

```gdscript
extends Node
class_name Damageable

signal stage_changed(old_stage: int, new_stage: int)
signal destroyed

@export var max_integrity := 100.0
var integrity := 100.0
var stage := 0

func apply_damage(amount: float) -> void:
    if integrity <= 0.0:
        return                    # already destroyed: no re-fire
    integrity = clampf(integrity - amount, 0.0, max_integrity)
    var new_stage := _stage_for(integrity)
    if new_stage != stage:
        var old := stage
        stage = new_stage
        stage_changed.emit(old, new_stage)
    if integrity <= 0.0:
        destroyed.emit()

func _stage_for(i: float) -> int:   # 0 intact, 1 damaged, 2 critical, 3 destroyed
    if i <= 0.0: return 3
    if i < 34.0: return 2
    if i < 67.0: return 1
    return 0

func debug_state() -> String:
    return "integrity=%.1f stage=%d" % [integrity, stage]
```

`debug_state()` is not optional. Every system needs a one-line state readout or you will debug
by staring at the screen.

## Step 3 — Enemy behaviour: prefer steering to state soup

For many enemies at once, **flow fields or steering** beat per-agent pathfinding. For
individual smart enemies, a small FSM is right.

| Count | Technique |
|---|---|
| 1-10 smart | FSM + navmesh |
| 10-100 | steering behaviours + local avoidance |
| 100-1000+ | flow field / vector field |
| swarms | boids: separation, alignment, cohesion |

FSM states should be **few and behaviourally distinct**: idle, patrol, alert, chase, attack,
stunned, dead. If a state has no unique behaviour, it is a flag, not a state.

Validation for nav: place agents at many positions and confirm each can reach the player
(see T-50). A navmesh that looks complete routinely has disconnected islands.

## Step 4 — Carry and snap with hysteresis

Anything the player picks up and places (resources, building parts, inventory drag) needs
hysteresis, or it flickers between attached and free.

```
attach when distance < 0.30 m
detach when distance > 0.55 m
```

The gap between the two thresholds is the hysteresis band. Using a single threshold produces
visible flicker at the boundary — the object attaches, moves a millimetre, detaches, reattaches.

Also required for carry systems:
- the carried object must not collide with the carrier,
- the carry point must be in front of the camera, not inside the body,
- dropping must place the object on the ground plane, not at the player's feet inside geometry.

## Step 5 — Combat balance from a spec

Never tune by trial and error across many sessions. Write the intended numbers first:

```
TTK (time to kill) : 1.6 s vs a standard enemy
Player DPS         : 40
=> enemy HP        : 64
Enemy attack        : 12 dmg, 1.1 s telegraphed windup
=> player survives : 8 hits from full
```

Then check the spec against the design intent ("forgiving", "punishing") and adjust the
*spec*, not the code. Balance changes should be data edits.

Feedback requirements for combat legibility:
- **telegraph** every enemy attack (windup animation, color, or sound) for 0.4-1.2 s,
- **confirm** every hit that lands (see `gamedev-vfx-impact`),
- **project the aim** visibly (a shadow, a laser, an arc) so the player can predict.

## Step 6 — Inventory and UI from the item definition

Derive UI from the item data, never hardcode slots:

```gdscript
class ItemDef:
    var id: String
    var display_name: String
    var icon: Texture2D
    var stack_max: int
    var category: String
```

The UI reads the definition; adding an item requires no UI change. Hardcoded slot layouts are
why inventory work becomes a rewrite.

## Step 7 — The loop test

Every gameplay system needs one **end-to-end loop test** that a script can run:

```
1. spawn the player at a known position
2. spawn a known enemy/object
3. perform a scripted action (move, attack, pick up)
4. assert the state transition occurred
5. assert the feedback fired (signal received)
6. tear down
```

If the loop cannot be automated, add the smallest instrumentation that makes it checkable. A
system with no loop test is a system that will regress silently.

## Verification checklist

```
[ ] every system exposes debug_state()
[ ] damage/state transitions emit signals, not direct calls
[ ] hysteresis bands exist on every attach/detach
[ ] every enemy attack is telegraphed
[ ] nav validation: agents from many spawn points can reach the goal
[ ] balance numbers live in data, not code
[ ] one automated loop test per system
[ ] the loop test fails when you deliberately break a rule (prove the test works)
```

That last line matters: a test that always passes is worse than no test.

## Related

- `gamedev-locomotion` — player movement the systems sit on
- `gamedev-vfx-impact` — feedback for every state change
- `gamedev-game-testing` — constructing the loop tests
- `gamedev-debugging` — when a system fails only in combination

## Knowledge base

T-41 (gameplay loop test), T-42 (carry and snap hysteresis), T-43 (cascading damage stages),
T-44 (inventory UI element extraction), T-45 (spec-first combat balance), T-46 (visible aim
shadow), T-47 (swarm steering vs flow fields), T-48 (bot nav validation), T-49/T-50 (breaking
tests), T-51 (11-way quality tests).
