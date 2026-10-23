# Knowledge Base

Transcript-derived technique records. Each entry is a first-class object with the ten
fields the mission requires. Read this before editing any skill that cites an entry.

## How to read an entry

| Field | Meaning |
|---|---|
| **ID** | Stable key (`T-nn`). Skills cite these; do not renumber. |
| **Problem** | The failure the technique prevents. |
| **Why it works** | The mechanism, not the vibe. |
| **When** | Trigger conditions — when *not* to use it matters as much. |
| **Inputs** | What must exist before you start. |
| **Steps** | The executable procedure. |
| **Fails when** | Known failure cases, including the creator's own failed attempts. |
| **Validate** | How you know it worked, in observable terms. |
| **Recover** | What to do when the first pass is wrong. |
| **Skill** | Destination skill file. |
| **Basis** | `transcript` / `transcript+` / `engineering` (see `transcript-sources.md`). |
| **Src** | `Sxx L<start>-L<end>`. |

Duplicate ideas are merged; where two transcripts show the same technique with different
detail, the entry cites both and keeps the stronger implementation detail.

## Taxonomy

```
A. Orchestration & process      01-orchestration-and-verification.md   T-01..T-08
B. Assets, kits & textures      02-assets-and-textures.md              T-09..T-20
C. Motion & animation           03-motion-and-vfx.md                   T-21..T-28
D. Effects & feedback           03-motion-and-vfx.md                   T-29..T-34
E. World, light & camera        04-world-lighting-and-gameplay.md      T-35..T-43
F. Gameplay systems             04-world-lighting-and-gameplay.md      T-44..T-52
```

Coverage matrix (technique → skill → status): `coverage-matrix.md`.

## What the source material is actually about

Twelve videos from one channel documenting a two-person team building a Steam survival
game with AI agents, plus side experiments. The through-line is not "which model is best."
It is **decomposition and verification**: every video that succeeds does so because the
job was cut small, given a concrete reference, and checked by something other than the
model that built it. Every video that fails shows the opposite — one giant prompt, no
reference, no check, and a human noticing the damage in a playtest.

Three durable laws fall out of the corpus, and every skill in this library enforces them:

1. **One job, one session, one test.** (S12 L35-46, S01 L51-73)
2. **A reference beats a description.** (S02 L48-66, S10 L54-59, S11 L39-58)
3. **The builder never signs off on its own work.** (S01 L119-129, S07 L37-44)

## Anti-patterns the transcripts demonstrate

Recorded because a skill that only describes the right path cannot diagnose the wrong one.

| Anti-pattern | What it looked like | Src |
|---|---|---|
| Whole-game prompt | "All looked right, none had a gameplay loop" | S12 L20-24 |
| Text-only asset description | 16 generated walls, 4 usable, random sizes, some with no door | S11 L32-41 |
| Single-image part request | Flat front view produced a solid box — a wall and a box look identical from the front | S11 L44-52 |
| Trusting generation success | Tripo returned 5,000 faces when 3,000 was asked; 4 of 18 models faced backwards | S10 L170-176 |
| Uniform texture allocation | Small post and large roof got the same texture size; 23 materials for 22 parts | S11 L173-197 |
| One-brain swarm | Single flow-field brain for hundreds of ants "wasn't polished" | S10 L230-241 |
| Shadow-blind lighting | 50 identical orange lamps, every wall same color, no focal point | S10 L190-201 |
| Flipbook from stills | Still frames "just grow and fade" — no internal motion | S10 L273-276 |
| Feature without a loop | Building system worked, but "the house had no job" | S04 L45-53 |
| Money-mode animation | Root motion baked in → feet slid in game; spear bent like a bow | S11 L132-142 |
