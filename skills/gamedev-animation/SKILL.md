---
name: gamedev-animation
description: >
  Rig and animate characters and creatures: build skeletons by script, skin geometry,
  author locomotion and action clips, and retarget between rigs. Use when a model needs to
  move, when animation looks stiff or sliding, or when clips must be shared across
  characters.
license: Apache-2.0
compatibility: Blender 4.2+/5.x (armatures, constraints, NLA). Clips export to Godot/Unity via glTF.
metadata:
  engine: blender
  category: gamedev-motion
  difficulty: advanced
---

# Animation — rigs that carry motion

Bad animation is almost never a keyframe problem. It is a rig problem, a timing problem, or
a foot-plant problem. Fix in that order.

## When to use

- A character or creature must move.
- Locomotion looks floaty, stiff, or sliding.
- Clips must transfer between characters of different proportions.
- Props must follow bones (a weapon in a hand, a pouch on a belt).

## When not to use

- Static props.
- Pure VFX motion (see `gamedev-vfx-impact`).

## Step 1 — Rig for the motion, not for the model

Decide the joint set from what must move:

| Character | Minimum joints |
|---|---|
| Simple biped | root, hips, spine, chest, neck, head, 2x (shoulder, elbow, wrist), 2x (hip, knee, ankle) |
| Stylized quadruped | + 2x (toe), tail chain |
| Insect | 6 legs x 3-4 joints, thorax, abdomen |
| Mech | rigid segments with visible pivots, no skinning needed |

**Rule:** every joint the animation needs must exist before any keyframing. Adding a joint
mid-animation invalidates every clip.

## Step 2 — Build the rig by script, with rigid joints first

For mechanical or stylized characters, rigid segments parented to bones often beat skinning —
it is more robust and reads better than a badly weighted soft mesh.

```python
def build_armature(name, joints):
    """joints: ordered list of (bone_name, head_xyz, tail_xyz, parent_name)."""
    arm = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, arm)
    col.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    created = {}
    for bname, head, tail, parent in joints:
        b = arm.edit_bones.new(bname)
        b.head, b.tail = head, tail
        if parent:
            b.parent = created[parent]
            b.use_connect = False          # explicit control over connection
        created[bname] = b
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob
```

`use_connect=False` matters: connected bones force a shared head position, which silently
moves joints you thought you had placed.

**Bone naming** must be stable and semantic: `thigh_L`, `shin_L`, `foot_L`. Retargeting and
mirroring both depend on it.

## Step 3 — Skinning

Automatic weights are a starting point, never the answer.

```
[ ] every vertex has at least one non-zero weight
[ ] no vertex is influenced by more than 4 bones (engine limit)
[ ] weights are normalized
[ ] joints bend without collapsing: check elbow, knee, shoulder, hip at 90 deg
[ ] rigid parts (armour, buckles) are 100% to one bone, not blended
```

Rigid parts blended across joints is the classic "melting armour" defect. Either weight them
fully to one bone or make them separate objects parented to that bone.

## Step 4 — Timing is the animation

The difference between amateur and professional is timing and spacing, not pose choice.

| Motion | Typical duration | Notes |
|---|---|---|
| Idle breath | 2.5-4.0 s loop | subtle, 1-2% scale/rotation |
| Walk cycle | 0.9-1.2 s (2 steps) | contact, down, pass, up x2 |
| Run cycle | 0.6-0.8 s | adds airtime, forward lean |
| Jump | anticipation 0.15 s, rise 0.30 s, fall 0.35 s, land 0.20 s | the anticipation is what sells it |
| Attack windup | 0.20-0.45 s | longer = heavier |
| Hit reaction | 0.15-0.30 s | instant feedback |
| Death | 0.8-1.5 s | |

**The four keys of a walk cycle**, per step: contact (heel down, opposite toe off), down
(weight absorbed, lowest hips), pass (legs together, highest hips except running), up
(push off). If you only key contact poses, the walk looks like a slideshow.

## Step 5 — Foot planting (the anti-slide rule)

Sliding feet ruin an otherwise good locomotion set. Two defences:

1. **Match stride to speed.** Stride length `S` metres per cycle, cycle time `T` seconds,
   so `speed = 2S / T` for a two-step cycle. If the character moves at 4.0 m/s, the stride
   and cycle must satisfy that equation. Any mismatch is visible sliding.
2. **Author in place, drive speed from the clip** (root motion) or **scale playback rate** to
   the actual speed. Never let the animation and the movement code disagree.

```
speed_mps = (2 * stride_m) / cycle_s
```

Changing `speed_mps` in the controller without changing the clip is the single most common
cause of "my walk looks wrong".

## Step 6 — Blending and state

Animation state belongs in the controller, not in the clip:

```
Idle <-> Walk <-> Run        (blend by speed, crossfade 0.12-0.20 s)
      \-> Jump (one-shot, interruptible on land)
      \-> Attack (one-shot, blocks locomotion or not, per design)
      \-> Hit (one-shot, additive, never blocks input)
```

Crossfade durations: 0.10-0.15 s for responsive locomotion, 0.20-0.30 s for weighty
characters. A 0.5 s crossfade makes everything feel underwater.

## Step 7 — Retargeting

Sharing clips across characters of different proportions:

- **Same bone names and hierarchy** is the cheapest path. Standardize early.
- **Handling different proportions**: retarget rotation, not translation, then fix the root
  height.
- **Always validate**: a retargeted clip can produce hip drift, foot sinks, or arm
  hyperextension. Check the extremes (jump apex, deep crouch, full swing).
- **Preserve the source clip**; retargeted copies are derived data.

## Verification

```
[ ] clip loops without a pop: last frame ~= first frame for cyclic clips
[ ] feet contact the ground plane (min foot Z within 5 mm of 0 across the cycle)
[ ] stride matches the controller speed
[ ] no joint exceeds a plausible range (elbow < 160 deg, knee < 150 deg)
[ ] rigid attachments stay attached across the full range
[ ] exported clip count and names match the source
```

Loop check, numerically:

```python
pop = max(abs(a - b) for a, b in zip(first_pose_values, last_pose_values))
assert pop < tolerance        # tolerance ~0.001 for rotations in radians
```

## Related

- `gamedev-locomotion` — the controller side that must agree with the clip
- `gamedev-blender-headless` — scripting rigs and bakes
- `gamedev-procedural-modeling` — the geometry being skinned
- `gamedev-vfx-impact` — effects layered onto action clips

## Knowledge base

T-21 (procedural rigid-joint rigs), T-22 (movement lab), T-23 (surface transition gait
diagnosis), T-24 (insect tripods), T-25 (locomotion blending), T-26 (retargeting libraries),
T-27 (bone attachment constraints).
