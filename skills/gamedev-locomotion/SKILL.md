---
name: gamedev-locomotion
description: >
  Make character movement feel good: acceleration curves, coyote time, jump buffering,
  turn response, stamina/sprint and surface transitions. Use when movement feels floaty,
  slippery, unresponsive or "wrong" and the animation is already correct.
license: Apache-2.0
compatibility: Engine-agnostic; examples in Godot 4.x GDScript and generic pseudocode.
metadata:
  engine: any
  category: gamedev-motion
  difficulty: intermediate
---

# Locomotion — the feel layer

Players judge a game in the first three seconds, and those three seconds are movement.
Animation supplies the look; this supplies the feel. They must agree numerically.

## When to use

- The character moves but feels slippery, floaty, heavy or unresponsive.
- Movement is correct but unsatisfying.
- Implementing jump, dash, sprint, slope handling, or surface transitions.

## When not to use

- The animation itself is wrong (fix the clip first — see `gamedev-animation`).
- Vehicles/aircraft with fundamentally different physics.

## The feel parameters

Every one of these should be a named, tunable value — never a magic number in the update
loop.

| Parameter | Meaning | Typical range |
|---|---|---|
| `max_speed` | top ground speed | 3.5-6.0 m/s walk/run, 8-12 sprint |
| `accel` | how fast speed rises | 20-60 m/s² (higher = snappier) |
| `decel` | how fast it drops | 25-70 m/s² |
| `air_control` | fraction of accel while airborne | 0.2-0.6 |
| `turn_rate` | degrees/second toward input dir | 540-1440 (higher = twitchier) |
| `gravity` | downward accel | 20-40 m/s² (game gravity, not 9.81) |
| `jump_velocity` | initial upward | derived from desired height |
| `coyote_time` | grace after leaving ground | 0.08-0.15 s |
| `jump_buffer` | early-press grace | 0.10-0.20 s |
| `fall_gravity_mult` | extra gravity on descent | 1.2-2.0x |
| `terminal_velocity` | max fall speed | 30-60 m/s |

## Deriving jump values from the feel you want

Do not guess `jump_velocity`. Pick the apex height and the time to apex, then solve:

```
h = v0^2 / (2g)          ->  v0 = sqrt(2 * g * h)
t_apex = v0 / g
```

For a 1.1 m jump at gravity 30: `v0 = sqrt(2*30*1.1) = 8.12 m/s`, apex at `0.27 s`. Total
airtime with symmetric gravity ~0.54 s.

**Asymmetric gravity** is the standard trick: fall faster than you rise. Rise at `g`, fall at
`g * 1.6`. This makes jumps feel responsive instead of floaty without shortening them
perceptibly.

## Coyote time and jump buffering

These two fix 90% of "the controls feel unresponsive" complaints, and both are ~10 lines.

```gdscript
var coyote := 0.0
var buffer := 0.0

func _physics_process(delta):
    if is_on_floor():
        coyote = COYOTE_TIME
    else:
        coyote = max(0.0, coyote - delta)

    if Input.is_action_just_pressed("jump"):
        buffer = JUMP_BUFFER
    else:
        buffer = max(0.0, buffer - delta)

    if buffer > 0.0 and coyote > 0.0:
        velocity.y = JUMP_VELOCITY
        buffer = 0.0
        coyote = 0.0
```

**Why it works:** players press jump slightly before landing (buffer) and slightly after
leaving a ledge (coyote). Without them the input is silently dropped and the game feels
broken, even though it is behaving exactly as coded.

## Variable jump height

Holding jump should go higher. Release should cut the rise.

```gdscript
if Input.is_action_just_released("jump") and velocity.y > 0.0:
    velocity.y *= 0.45      # cut the rise to 45%
```

This single multiply gives the player continuous control over arc height and is the
difference between "jump" and "a jump you can aim".

## Acceleration, not instant velocity

Instant velocity change is crisp but weightless. Pure lerp is smooth but mushy. Use a
critically-damped approach or separate accel/decel:

```gdscript
var target = input_dir * max_speed
var rate = accel if target.length() > velocity.length() else decel
velocity.x = move_toward(velocity.x, target.x, rate * delta)
velocity.z = move_toward(velocity.z, target.z, rate * delta)
```

Ground decel should be **faster than accel** (stop crisply, start smoothly). Air accel much
lower, but never zero — zero air control feels like the game took the wheel away.

## Turning

Two options, and the choice is a design decision:

- **Instant facing** (snap to input): responsive, arcade, works for top-down and shooters.
- **Turn rate** (rotate toward input at N deg/s): weighty, third-person, needs a deadzone so
  small stick noise doesn't jitter the character.

If using a turn rate, the character's visual facing and the movement direction must be
decoupled — otherwise strafing looks like the character is skating sideways.

## Surface transitions

Different surfaces need different gait, sound and speed. The failure mode is the *transition*,
not either state:

```
[ ] the clip crossfades over 0.12-0.20 s, not instantly
[ ] the speed change is applied gradually, matching the clip's stride
[ ] footstep audio switches on the first contact AFTER the transition
[ ] dust/particle emitters swap at the transition, not at the next step
```

A hard swap mid-stride produces a visible foot slide. Test with a debug overlay that prints
the current surface and the actual speed.

## Verification (measure, don't feel)

```
[ ] max speed measured in-game equals the configured value
[ ] jump apex measured equals the derived height (±2%)
[ ] time to apex matches the derived value
[ ] coyote and buffer windows verified by dropping inputs at known offsets
[ ] stride length * cycle rate equals actual ground speed (no slide)
[ ] on slopes, speed does not increase going downhill (or clamp it if it should)
```

**Measure in-engine, not by reading the code.** A correct formula with a wrong unit
conversion is the most common bug here (degrees vs radians, per-frame vs per-second).

## Related

- `gamedev-animation` — the clips this must agree with
- `gamedev-gameplay-systems` — dash, stamina, states
- `gamedev-camera` — how movement reads on screen
- `gamedev-debugging` — when movement is broken and the cause is unclear

## Knowledge base

T-22 (movement lab), T-23 (surface transition gait), T-25 (locomotion blending), T-31
(occlusion-based feedback).
