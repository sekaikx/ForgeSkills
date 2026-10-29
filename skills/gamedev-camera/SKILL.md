---
name: gamedev-camera
description: >
  Design game cameras: focal length and framing, third/first-person rigs, follow with
  deadzone and look-ahead, collision, cinematic moves, camera-side shake trauma. Use when
  the view is nauseating or the camera fights the player. For hit-impact feedback use vfx-
  impact.
license: Apache-2.0
compatibility: Engine-agnostic camera theory and numbers; no engine-specific code.
metadata:
  engine: any
  category: gamedev-world
  difficulty: intermediate
---

# Camera — the player's only window

Half of "this looks bad" is actually "this is framed badly". Camera decisions are cheap to
change early and expensive to change after content is authored around them.

## When to use

- Choosing FOV/focal length and framing.
- Building third-person, first-person, top-down or isometric rigs.
- The camera feels nauseating, jittery, or obstructive.
- Adding shake, zoom, or cinematic sequences.

## When not to use

- Fixed-camera puzzle games where the camera is part of the design contract.
- Pure UI work.

## Focal length / FOV by genre

| Genre | Focal (35 mm equiv) | Horizontal FOV | Why |
|---|---|---|---|
| First person | 20-28 mm | 90-110° | peripheral awareness, speed |
| Third person action | 35-50 mm | 60-75° | subject + surroundings |
| Third person cinematic | 50-85 mm | 40-55° | compression, intimacy |
| Top-down / isometric | orthographic or very long | — | no perspective distortion |
| Character showcase | 85-135 mm | 25-35° | flattering proportions, no distortion |

**Portrait rule:** at 85 mm or longer, faces and bodies read as intended. At 24 mm, a nose
doubles in size. Never judge a character model from a wide lens.

FOV also sets motion sickness risk: above ~100° with fast movement, a meaningful share of
players feel unwell. Offer an FOV slider.

## The third-person rig

```
PIVOT     : at the character's chest/head, not the feet
DISTANCE  : 3.0-5.0 m for action, 1.5-2.5 m for intimate
HEIGHT    : slightly above the pivot, looking down 5-15 deg
SHOULDER  : offset 0.3-0.6 m so the character doesn't block the crosshair
COLLISION : spherical cast from pivot to desired position; pull in, never clip through
SPRING    : position smoothing with a fast attack and slower release
```

**The spring is where feel lives.** Snapping the camera to the target every frame transmits
every animation jitter. A critically-damped spring at ~0.08-0.15 s removes the jitter and
reads as intentional.

```gdscript
# exponential smoothing, framerate independent
var t = 1.0 - exp(-follow_speed * delta)
camera.global_position = camera.global_position.lerp(target_pos, t)
```

Using `lerp(a, b, 0.1)` per frame is framerate-dependent and will feel different at 60 vs
144 Hz. Use the exponential form.

## Look-ahead and deadzone

- **Deadzone**: a small region around the character where the camera does not move. Prevents
  micro-jitter and constant motion during small inputs. Start at 0.3-0.6 m.
- **Look-ahead**: offset the camera toward the movement direction, 0.3-0.8 m, ramped over
  0.2-0.4 s. Shows more of where the player is going.

Both need to be **velocity-driven, not input-driven**, so they behave correctly when the
character is pushed or on a moving platform.

## Camera collision

```
[ ] sphere-cast from the pivot to the desired position
[ ] pull the camera to the first hit minus a small buffer (0.2 m)
[ ] never let the near plane intersect geometry (check near clip vs buffer)
[ ] if pulled very close, fade or hide the character (avoid seeing inside the head)
[ ] restore distance smoothly, not instantly (prevent "camera pumping")
```

Instant restore after leaving a wall is a common source of nausea. Use a slower outward rate
than the inward one.

## Shake that reads as impact

```
amplitude : 1-3 px subtle, 4-8 px medium, 10-16 px heavy
frequency : 6-14 Hz
decay     : exponential over 0.15-0.35 s
source    : directional (along the hit normal) for combat, radial for explosions
```

Implement as a **trauma** value with noise, not raw random offsets:

```
trauma += hit_amount            # clamp 0..1
offset = max_offset * trauma^2 * noise(time * freq)
trauma -= decay * dt
```

Squaring the trauma makes small hits nearly imperceptible and big hits dramatic — that is the
curve you want. Always expose a shake intensity setting.

## Cinematic camera moves

For cutscenes and trailers, the rules are different from gameplay:

| Shot | Move | Duration |
|---|---|---|
| Establishing | slow dolly or crane | 4-8 s |
| Reveal | orbit or push-in | 3-6 s |
| Tension | slow push in | 4-10 s |
| Impact | quick 2-4 frame whip + settle | 0.3-0.6 s |
| Farewell | pull back and up | 5-10 s |

Never combine a fast move with a fast subject move; the eye cannot track both. One element
moves fast, the other holds.

## Verification

```
[ ] the subject is readable at the furthest gameplay distance
[ ] the crosshair/target point is never occluded by the character
[ ] no camera clipping through walls across the full playable area
[ ] FOV is adjustable and the setting persists
[ ] shake is disableable/reducible
[ ] the frame rate does not change the camera feel (test at 30, 60, 144)
```

## Related

- `gamedev-lighting` — what the camera exposes
- `gamedev-locomotion` — movement that the camera must follow
- `gamedev-vfx-impact` — shake as feedback
- `gamedev-reference-reconstruction` — camera calibration for comparisons

## Knowledge base

T-14 (measuring a drawing, includes camera derivation), T-33 (screen feedback tiers), T-38
(lighting presets which pair with camera presets).
