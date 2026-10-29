---
name: gamedev-pivot
description: >
  Decide what to do with a project that already has code and assets but no identity or
  traction: keep, cut to one mode, or pivot to a new concept that reuses the most. Use when
  a build exists and the idea feels wrong. For a fresh idea with no build, use concept-lab.
license: Apache-2.0
compatibility: Engine-agnostic. Needs read access to the project and web search.
metadata:
  engine: none
  category: gamedev-direction
  difficulty: advanced
---

# Pivot — salvage the build, not the idea

Months of work make an idea feel proven. They prove the team can build, not that anyone
wants the game. This skill separates the two: what the project **is** (systems, assets,
skills) from what it **sells** (a hook someone would click). Then it scores options on reuse
and on evidence, and picks one.

## When to use

- A playable build exists, and its owner or its testers say it has no identity.
- The project grew two or more modes that compete for the same months.
- Market research already exists and points away from the current concept.

## When not to use

- No build yet. Use `gamedev-concept-lab`, then `gamedev-concept-judge`.
- The concept is fine and one system is broken. Use `gamedev-debugging` or `gamedev-orchestrator`.

## Hard rules

1. **Sunk cost is not a reason.** "We already built X" can lower an option's cost. It can
   never raise its score.
2. **Simulated players are not data.** Persona reports, simulated sales and simulated
   retention are hypotheses. Label them so, and do not let them decide a pivot.
3. **Three layers, never mixed:** Observed (source, n, date) / Inferred / Recommendation.
4. **One game.** The output is one recommended concept, plus what gets cut. "Do both" is not
   an option unless both ship from the same core loop.
5. **Bad news first.** The first line of the verdict names what is not working, with the
   evidence for it.

## Step 1 — Inventory what exists (artifact: `pivot/inventory.md`)

| Kind | Item | Size (files, lines, count) | State: shipped-quality / works / prototype / broken |
|---|---|---|---|

List systems (movement, fishing, building, saves, UI, telemetry, QA), content (areas,
characters, items), assets (models, animation, audio), and pipeline (tests, trailer tools).
Count, do not describe. Mark anything only one person can run.

## Step 2 — Find the hook that is already there (artifact: table)

For each system, answer: can it be shown in a 6-second clip with no explanation? Does it
have a verb a stranger could name ("panning", "holding the wall")? Rows with two yeses are
hook candidates. A pretty place with no verb is not a hook.

## Step 3 — Read the evidence you already have (artifact: table)

Collect every real signal: market research, store tests, wishlists, human playtests,
telemetry. Grade each one with `gamedev-critic`. Discard anything graded `none`. If the only
player evidence is simulated, write "no player evidence yet" in capitals.

## Step 4 — Generate 3 to 5 options (artifact: `pivot/options.md`)

Always include **keep as is** and **cut to one mode** as options, so the change has to beat
them. Each new option is one sentence: who does what, under what limit, and what they get.

| Option | Hook verb | Reuse % (from Step 1) | New work (weeks) | Closest shipped games (price, reviews, date) | Evidence grade | Biggest risk |
|---|---|---|---|---|---|---|

Pull competitor rows with `gamedev-concept-judge`. A single breakout hit is survivorship,
not a market. Cite at least three games per option, including one that did badly.

## Step 5 — Decide, then test cheaply (artifact: verdict)

Pick the option with the best evidence. Break ties on reuse. Then write:

```
PICK       : <option>, one sentence
CUT        : <systems and content that leave the build, by name>
KEEP       : <reused systems>
TEST FIRST : gamedev-hook-test, gate written before the clips go out
KILL IF    : <the number that ends this option>
```

No code moves until the hook test passes. A pivot that skips the test is a second guess.

## Done when

- [ ] `pivot/inventory.md` has counts, not adjectives.
- [ ] Every evidence row has a grade. Simulated data is labelled simulated.
- [ ] The options table includes keep-as-is and cut-to-one-mode.
- [ ] The verdict names what is cut and a kill number.
- [ ] `gamedev-critic` was run on the verdict and found no unsupported claim it rests on.
