---
name: gamedev-lighting
description: >
  Light a game scene so it reads: key/fill/rim setup, shadow budget, lighting presets,
  mood matching and diagnosis of flat or muddy lighting. Use when a scene is technically lit
  but looks flat, when shadows cost too much, or when the light must match a reference.
license: Apache-2.0
compatibility: Engine-agnostic. Examples for Blender EEVEE/Cycles and Godot 4.x.
metadata:
  engine: any
  category: gamedev-world
  difficulty: intermediate
---

# Lighting — the fastest way to make or ruin a scene

You can spend a week on geometry and lose it all to flat lighting. Conversely, ordinary
geometry under good light reads as a competent asset.

## When to use

- A scene is lit but flat, muddy, or "default".
- Shadow cost is too high for the target frame rate.
- The look must match a reference image's mood.
- Adding time-of-day, interiors, or a lighting preset system.

## When not to use

- Materials whose base color is wrong (lighting cannot fix a bad albedo; it amplifies it).
- Unlit/stylized flat-shaded art where lighting is intentionally absent.

## The three-light minimum

```
KEY    : the primary. Defines form. Off-axis (30-45 deg from camera), above.
FILL   : removes dead shadows. Opposite the key, 1/4 to 1/2 the key's intensity.
RIM    : separates subject from background. Behind, above, cooler than the key.
```

Ratios matter more than absolute values:

| Ratio (key:fill) | Read |
|---|---|
| 1:1 | flat, clinical, product-shot |
| 2:1 | soft natural daylight |
| 4:1 | dramatic, game-standard hero lighting |
| 8:1+ | noir, horror, heavy contrast |

**Rim light is the single highest-value addition** to an otherwise flat scene. It costs one
light and instantly separates the subject from the background.

## Scale-correct light intensity

The most common bug: the same rig reads completely differently at a different asset scale.
Light falls off with distance squared, so a rig built for a 2 m character blows out a 0.2 m
prop.

Scale energy with **distance squared**:

```python
energy = base_energy * (reference_height ** 2)
```

Or simply place lights as multiples of the subject's height, as the tooling here does:

```python
key_pos = (center.x - h * 0.9, center.y - h * 1.3, center.z + h * 0.75)
key_energy = h * h * 12.0
```

That keeps the same look at any scale, which is what makes a rig reusable.

## Shadow budget

Shadows are usually the most expensive part of a lighting setup.

| Technique | Cost | Use when |
|---|---|---|
| Real-time shadow maps | high | hero subject, player-adjacent |
| Distance/light culling | low | any scene with many lights (T-35) |
| Baked lightmaps | zero at runtime | static architecture |
| Contact shadows only | low | props at distance |
| Blob/fake shadows | ~zero | distant or low-priority characters |

**Cull casters by relevance**, not by object type: disable `cast_shadow` on geometry that is
far from the camera, small on screen, or never lit. A scene with 300 shadow casters is almost
always a scene where 250 of them do not matter.

**Softer shadows cost more.** Larger shadow map area or more filter samples = more expensive.
Match softness to the light's physical size, and do not over-soften to hide aliasing — fix the
map resolution instead.

## Diagnosis: why does it look flat?

Work down this list in order.

| Symptom | Likely cause | Fix |
|---|---|---|
| Everything evenly lit, no form | key and fill at similar intensity | raise key:fill ratio |
| Subject merges with background | no rim, similar value | add rim, change background value |
| Muddy browns everywhere | warm key + warm fill, no cool contrast | make fill cooler |
| Washed out highlights | exposure/key too high | lower exposure, not just energy |
| Crushed shadows, no detail | fill absent | add fill, or lift the world ambient |
| Looks "CG" | perfectly uniform color temperature | vary key/fill hue by 1000-2000 K |
| Shadows are black holes | no bounce/sky contribution | minimal world light, 0.02-0.05 |

**The value test:** convert the render to greyscale. If you cannot see the form in greyscale,
color is hiding a lighting problem.

## Matching a reference's mood

Read these five values off the reference before placing a light:

```
1. KEY DIRECTION   — from the shadow direction on a known form
2. KEY HEIGHT      — from the length of shadows
3. CONTRAST RATIO  — from the darkest and lightest lit areas
4. COLOR SPLIT     — warm key / cool fill, or the inverse
5. AMBIENT LEVEL   — how much detail survives in shadow
```

Then reproduce those five, not an exact light rig. The rig that produces them is irrelevant;
the five numbers are the target.

Note that concept art is often lit *brighter and more dramatically* than the final game will
be. Matching it exactly can produce an unplayable scene. Match mood, then pull contrast back
to a playable level.

## Lighting presets

Ship lighting as data, not as scene state:

```python
PRESETS = {
    "day":     dict(key=(1.0, 0.96, 0.90), key_ev=0.0, fill=0.30, ambient=0.06, fog=(0.7, 0.8, 0.9)),
    "dusk":    dict(key=(1.0, 0.72, 0.50), key_ev=-0.4, fill=0.35, ambient=0.04, fog=(0.75, 0.55, 0.45)),
    "overcast":dict(key=(0.90, 0.93, 1.00), key_ev=-0.2, fill=0.70, ambient=0.10, fog=(0.65, 0.70, 0.75)),
    "night":   dict(key=(0.55, 0.68, 1.00), key_ev=-1.2, fill=0.20, ambient=0.02, fog=(0.10, 0.14, 0.22)),
}
```

A preset should be **fully applicable** — key color/intensity, fill ratio, ambient, fog color
and density, exposure. A half-applied preset produces the classic "night mode that is just
dimmer" look.

## Verification

```
[ ] form is readable in greyscale
[ ] key:fill ratio matches the intended look (measure pixel values on a sphere)
[ ] subject separates from background at the furthest gameplay distance
[ ] no shadow acne or peter-panning at the gameplay camera distance
[ ] frame time with shadows on is within budget
[ ] every preset applies completely and is visually distinct
[ ] the darkest gameplay area still allows navigation
```

## Related

- `gamedev-texture-authoring` — materials before lighting
- `gamedev-camera` — exposure and framing interactions
- `gamedev-performance` — shadow and light budgets
- `gamedev-visual-iteration` — the loop for matching a reference

## Knowledge base

T-35 (shadow caster culling), T-36 (shadow softness cost), T-37 (iterative lighting
diagnosis), T-38 (lighting presets), T-39 (roughness vs texture scale under light).
