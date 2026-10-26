---
name: gamedev-audio-wire
description: >
  Wire chosen sound effects and music to gameplay events, and record the license for each
  file. Use when a game is silent, hits feel weightless, or voice and music need hooking
  up. Does not compose a score.
license: Apache-2.0
compatibility: Engine-agnostic. Uses the project's existing audio bus. No middleware assumed.
metadata:
  engine: none
  category: gamedev-gameplay
  difficulty: basic
---

# Audio wire — pick, then hook

The source builds went silent until a person chose files and the agent attached them to
events that already existed (S14). Older videos only say the files came from a free
library (S01, S09). Choosing files is not a design. This skill is the wiring and the
license check. It is not a composer's workflow, and it does not add a new middleware.

## When to use

- The loop is playable and there is no sound, or sound is one looping file for everything.
- Hits, dodges, or boss telegraphs need to be heard to be fair.
- Voice or music was generated elsewhere and must be cut into the game.

## When not to use

- Writing a score, lyrics, or adaptive music systems with stems and transitions.
- Replacing the engine's audio engine. Use whatever bus the project already has.

## Step 1 — Events before files

List events from the gameplay spec. If the code has no signal for it, there is no sound
yet. Do not invent a parallel trigger that fires "somewhere near" the action.

Minimum once combat or traversal exists:

| Event | Needed for |
|---|---|
| Footstep, surface-specific if surfaces change gameplay | place |
| Primary action (swing, shoot, interact) | confirmation |
| Hit confirmed vs hit blocked or missed | fairness |
| Damage taken | fairness |
| Telegraph of a dangerous attack | fairness, see `gamedev-boss-encounter` |
| Success and failure of the current loop | closure |
| UI move / UI confirm | distinct from hits, quieter |

Music is not on this list until a **state change** exists (menu, explore, fight, victory).
A track under every minute of play hides the telegraph. In the source, music showed up
to mark mood, not to fill silence (S16).

## Step 2 — A manifest, one row per file

```
FILE | EVENT ID | SOURCE URL | LICENSE | CHANGES (trim, pitch) | LOOP (yes/no)
```

Rules:

- The person directing the game picks the recording, or names the library. The agent
  downloads only from that library and writes the URL.
- Free libraries used in the source (Pixabay) still need the license name in the row.
  "Free" is not a license.
- No file ships without a row. No row without a file that exists in the project.
- Do not generate a voice and also keep the room tone, the music bed, and the breaths
  from the source video. Trim to the line. If the voice came from a generated clip, say
  so in SOURCE.

## Step 3 — One event, one playback, on the gameplay frame

Hook the manifest to the signal the gameplay system already emits (hit confirmed, dodge
start, attack windup). Playback starts on that frame, not on a timer that "felt close".

Hits are three layers on one event, or the hit will feel like a click:

1. transient (the impact)
2. body (the material: wood, flesh, stone, metal)
3. short tail

They start together. Hit-stop and the camera impulse, if any, start on the same frame
(`gamedev-vfx-impact`). The tail may outlive the hit-stop. Nothing else may.

Buses, by hand, once: footsteps under movement, UI under gameplay, telegraphs and hits
above both, music on its own bus with a duck while a telegraph plays. Do not leave every
sound on the master at the same volume.

## Step 4 — State music

One cue per state, triggered by the state change, with a short fade. Silence between
states is allowed. Overlapping two full tracks is a bug.

If there is no state machine yet, ship the event sounds and leave music empty. A random
loop is worse than quiet, because it cannot mark the telegraph.

## Step 5 — Hear the difference

- Mute gameplay bus: the loop is still readable, but dodges get worse. If they do not,
  the telegraph is only visual and the sound is decoration. Say so.
- Solo each layer of a hit. If two layers are the same noise, delete one.
- Loop points: the sample's ends match, or it is one-shot. A click at the join fails.
- Clipping: nothing on the master sits against the ceiling during a normal fight.
- License: every played file has a manifest row. A file with no row is removed.

## Gate

```
[ ] manifest row for every file, with source and license
[ ] every combat telegraph and confirmed hit has a sound on that frame
[ ] UI and footsteps are quieter than hits
[ ] music changes only on a state change, or is absent on purpose
[ ] mute test written down: what the player can no longer judge
```

## Related

- `gamedev-vfx-impact` — the visual half of the same frame
- `gamedev-boss-encounter` — telegraphs that must be audible
- `gamedev-gameplay-systems` — the signals you hook, not new ones

## Knowledge base

T-79 (pick files, wire to existing events, keep the license).
