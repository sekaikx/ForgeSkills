---
name: gamedev-vfx-impact
description: >
  Build hit feedback and effects that land: layered impact FX, hitstop, impact-triggered
  screen shake, fracture, flipbook VFX, turrets. Use when combat feels weightless or
  effects read as noise. For camera rig or follow-motion problems use camera.
license: Apache-2.0
compatibility: Engine-agnostic timings (unmeasured in any engine); the one code sample is GDScript.
metadata:
  engine: any
  category: gamedev-feedback
  difficulty: intermediate
---

# VFX and impact — make hits land

"Weightless combat" is not a missing particle. It is a **timing and layering** problem:
impacts need to occupy a specific set of milliseconds with a specific set of signals.

## When to use

- Attacks connect but feel weak, floaty, or unreadable.
- Effects look like noise rather than impact.
- Adding destruction, screen feedback, or deployables.

## When not to use

- The hit doesn't connect at all (that's a collision/design bug).
- Ambient/environmental VFX with no gameplay meaning (different problem).

## The impact timeline

A single hit is a ~250 ms budget. Layering is what makes it read.

```
t=0      HIT CONFIRMS
         - damage number / health tick applied
         - hitstop (freeze animation 40-90 ms; longer = heavier)
         - hit spark / flash at the contact point
t=0-60   DIRECTION READS
         - directional spray or slash arc, aligned to the hit normal
         - brief emissive flash on the struck surface
t=40-140 SHOCKWAVE / DEBRIS
         - expansion from the point, decelerating
         - small debris, decals
t=80-200 SCREEN RESPONSE
         - camera shake (decaying, 2-5 px amplitude, 6-12 Hz)
         - chromatic/vignette pulse for heavy hits only
t=150-250 SOUND + SETTLE
         - transient at t=0, tail layered after
         - decal persists, particles fade
```

**Rule:** the biggest visual should be in the first 60 ms. Anything that peaks after 150 ms
reads as a separate event.

## Hitstop: the cheapest weight in games

Freeze both attacker and target for 40-90 ms on connect. It converts "two objects overlapped"
into "something was struck".

```gdscript
func apply_hitstop(duration: float) -> void:
    Engine.time_scale = 0.0
    await get_tree().create_timer(duration, true, false, true).timeout
    Engine.time_scale = 1.0
```

Durations by weight class: light 35-50 ms, medium 60-75 ms, heavy 90-130 ms. Never exceed
~150 ms; beyond that it reads as a frame drop.

Do not use hitstop on: continuous damage (DoT ticks), environmental damage, or anything the
player must react to within the freeze.

## Screen shake that doesn't nauseate

```
amplitude : 2-5 px for medium hits, 8-12 px for heavy
frequency : 6-12 Hz (higher reads as vibration, lower as camera drift)
decay     : exponential, 0.15-0.30 s total
direction : biased along the hit normal, not pure random
```

Random per-frame jitter is the amateur version. Use noise with a decaying envelope, and
**always** offer a "reduce/disable screen shake" setting — it is an accessibility requirement,
not a nicety.

## Layering rules

| Layer | Purpose | Budget |
|---|---|---|
| Core flash | instant "it connected" | 1-2 frames |
| Directional spray | where the hit came from | 80-150 ms |
| Debris/chunks | physicality | 300-800 ms |
| Decal | persistent evidence | until fade, 5-20 s |
| Screen | player's body reads it | 150-250 ms |
| Audio | transient + tail | transient at 0, tail 200-600 ms |

If you add a layer without removing something, you are adding noise. Six simultaneous bright
elements read as a bright smear; three well-timed ones read as an impact.

## Flipbook VFX from video

Hand-authored flipbooks (64 frames from a rendered or shot effect) are often cheaper and
better-looking than a particle system for a specific moment.

```
1. render/record the effect at the final screen size, on a black or alpha background
2. slice into a grid (8x8 = 64 frames), preserving a consistent frame size
3. pack into a single sheet at the target resolution
4. drive UV offset by frame index; do NOT use per-frame textures
5. author the timing curve: the sheet is uniform, playback should not be
```

Playback rate matters: uniform frame playback makes an explosion look like a slideshow. Use a
curve — fast at the start, slowing at the end.

## Fracture and destruction

```
[ ] pre-fracture at author time, not at impact time (runtime fracture = frame spike)
[ ] chunks are clustered, not uniform cubes
[ ] impulse direction biased away from the impact normal
[ ] angular velocity randomized per chunk (seeded)
[ ] chunk count budget: 8-25 for a prop, 40-80 for a structure
[ ] chunks despawn or merge after settling (they are not permanent)
[ ] a low-poly "intact" mesh is swapped out before fracture spawns
```

Uniform cube chunks are instantly readable as fake. Variation in size and shape is what sells
it, and size variation is cheap — generate 3-4 sizes and vary scale per chunk.

## Deployables (turrets, traps)

Deployables need three distinct states, each with its own feedback:

| State | Feedback |
|---|---|
| Deploying | mechanical motion + dust + a short "arming" sound |
| Active | idle hum, subtle light pulse, aim tracking motion |
| Firing | muzzle flash, recoil, tracer, shell casing, sound |
| Destroyed | fracture + smoke + a distinct power-down sound |

A turret that only looks different when firing is unreadable at a glance. The *state* must be
legible from the silhouette or the light colour.

## Verification

```
[ ] impact reads in a single 250 ms window (record and scrub frame by frame)
[ ] the largest element peaks in the first 60 ms
[ ] hitstop is felt but does not feel like a stutter
[ ] effects are visible against both bright and dark backgrounds
[ ] particles are lit consistently with the scene (or deliberately unlit)
[ ] total overdraw within budget at the worst-case frame
[ ] a "reduce effects" setting exists and works
```

Record the effect at 60 fps and step through frames. Any effect you cannot name frame by frame
is noise.

## Related

- `gamedev-animation` — the action clips the effects attach to
- `gamedev-camera` — shake as a camera concern
- `gamedev-gameplay-systems` — damage events that trigger feedback
- `gamedev-performance` — particle and overdraw budgets

## Knowledge base

T-28 (frame-by-frame VFX analysis), T-29 (64-frame flipbooks), T-30 (layered FX timing),
T-32 (fracture impulse destruction), T-33 (screen feedback tiers), T-34 (turrets and
deployables).
