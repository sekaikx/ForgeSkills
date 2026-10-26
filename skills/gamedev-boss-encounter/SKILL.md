---
name: gamedev-boss-encounter
description: >
  Build a boss or set-piece fight as timed attacks with telegraphs, hit windows, and
  lock-on. Use for a boss, elite, or scripted duel. Not for ordinary enemies or the
  rest of combat.
license: Apache-2.0
compatibility: Engine-agnostic. Data-driven attacks. Hit reactions pair with gamedev-vfx-impact.
metadata:
  engine: none
  category: gamedev-gameplay
  difficulty: intermediate
---

# Boss encounter — rules before spectacle

A boss fight fails when the player cannot tell what is dangerous **right now**. Moves,
particles, and a health bar do not fix that. The fight is a timeline: telegraph, active
hurt, recovery. Everything else hangs off that timeline.

Source of the rules: a full AI-built boss in Unreal where the fight only became readable
once attacks had limits, per-move hitboxes, and a visible active window (S16). Ordinary
enemy steering stays in `gamedev-gameplay-systems`.

## When to use

- Designing or implementing a boss, mini-boss, or one scripted duel.
- A fight exists but feels random, endless, or unfair.

## When not to use

- Trash mobs, swarms, inventory, or the overall game loop.
- A creature that only needs a walk cycle. Use `gamedev-animation`.

## Step 1 — Write the attack list before any animation

One row per move. No row, no move.

```
ID | WINDUP s | ACTIVE start-end s | RECOVERY s | RANGE | ARC deg | REPEAT BAN | TELLS (sound + shape)
```

Rules that shipped in the source fight, and that you should break only with a reason:

- No long idle, and not so fast the dodge never fits in the windup.
- Never the same attack three times in a row.
- Start an attack only when the player is inside the arc. Do not swing at empty air and
  call it pressure.
- Each attack has its own hurt volume. The volume is on only inside ACTIVE.

Player side, in the same spec: lock-on button, a dodge with a defined iframe window, and
what a hit on the boss must do (flinch, hit-stop, spark, camera, one impact sound).

## Step 2 — Put the timeline in data

The selector and the hitboxes read the table. They do not embed timings in animation
clips. A clip can be late; the table is the authority.

Selector, in order:

1. Drop any move that just happened twice.
2. Drop any move whose range or arc does not contain the player.
3. Pick among what remains. If nothing remains, play a short idle or a reposition, not a
   random swing.
4. Log `id, start time, active window` every cast.

A 60-second sample must show zero triple-repeats. That log is the test.

## Step 3 — Show the window

A debug draw: skeleton or hurt volumes, lit only while ACTIVE. If you cannot see why a
dodge worked, you cannot tune the fight. Ship with the draw behind a flag, not deleted.

Dodge test, by a human or a bot that dodges when the windup starts: every attack in the
list is avoided at least once using only the telegraph. Hits that land during RECOVERY
are bugs.

## Step 4 — Motion serves the table

Poses first, in-betweens second (S16). Draw or block the windup pose, the hit pose, and
the recovery pose. Generate or mocap only the blend between them. If a generated clip
breaks a joint (the source roar threw an arm), fix that joint's curve. Do not regenerate
the whole fight.

Lock-on changes locomotion. While locked, moving backward is a backward walk that still
faces the target, not a 180° turn. If the move set cannot face and travel separately,
say so and drop lock-on until it can. A lock that spins the body is worse than no lock.

Clip ranges stay inside `gamedev-animation` (elbow and knee limits). This skill only
requires the three poses to read at the camera distance the fight uses.

## Step 5 — Feel, after the timeline passes

Do not polish a fight that fails step 3. Then layer, once, with `gamedev-vfx-impact`:

- a short hit-stop on a landed player hit
- a flinch on the boss pose
- sparks or debris at the contact
- camera impulse, with a reduce-motion path
- one real impact recording, not a reused UI click

A "power" move (shockwave, beam, slam) is particles with a count, a motion, and a colour
over life. A textured card that grows and fades reads as a picture, which is the failure
the source threw out. Wire the sound in `gamedev-audio-wire` to the same frame as the
hit-stop.

## Gate

```
[ ] every move has windup / active / recovery in data
[ ] 60 s log: no attack id three times in a row
[ ] hurt volume off outside its active window (assert on the timeline, not by eye)
[ ] each move dodged at least once from the telegraph alone
[ ] locked movement faces the target while travelling backward
[ ] hit-stop, flinch, and impact sound share one frame
```

## Related

- `gamedev-gameplay-systems` — spec-first combat for everything that is not this duel
- `gamedev-vfx-impact` — hit-stop, shake, particles
- `gamedev-animation` — joint limits and pose-first clips
- `gamedev-audio-wire` — the impact and the telegraph sounds
- `gamedev-camera` — shake and framing; the lock target lives here

## Knowledge base

T-76 (attack grammar and hit windows), T-77 (lock-on facing), T-78 (key poses, then
in-betweens; fix a broken joint in place).
