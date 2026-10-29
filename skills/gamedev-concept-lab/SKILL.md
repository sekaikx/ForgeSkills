---
name: gamedev-concept-lab
description: >
  Invent a few game concepts only after constraints and a market scan. Use when asked for
  game ideas, what to make next, or to write up a new concept. Asks the binding questions
  first. To assess an existing idea or pitch use concept-judge.
license: Apache-2.0
compatibility: Engine-agnostic. Needs web search before any idea is recommended.
metadata:
  engine: none
  category: gamedev-direction
  difficulty: intermediate
---

# Concept lab — ideas after questions

Five ideas with competitors beat twenty ideas with adjectives. This skill will not pitch
until it knows who is building, for how long, and what they refuse to make.

## When to use

- "What game should I make?"
- "Give me ideas" / "I need a hook."
- A direction was rejected and a different verb is needed.

## When not to use

- One idea already exists and needs a verdict. Use `gamedev-concept-judge`.
- The game is chosen and you are implementing it.

## Step 1 — Ask once

Ask these in one message. If the user already answered one, do not ask it again.

1. How many people, how many months, which engine?
2. What do you already have (code, assets, audience, a finished prototype)?
3. What will you not make (genre, tone, online, camera)?
4. How long should one session be?
5. Does day one need other players, or is it single-player?
6. What full price would you be willing to put on the store?

If they say "just give me ideas" or "whatever", do not dump a list. Reply with the
questions. The only exception: a field they already filled.

If they refuse to answer after that, assume out loud and mark every assumption:

- 1–3 people, under 9 months
- the engine they already use, else the one their assets are in
- single-player
- a price you will replace with store data in step 2, not a number you like

## Step 2 — Scan before you invent

Search the store for verbs their constraints allow. Read `references/scan.md`. Fill at
least eight shipped games: name, year, price, review volume, the verb, the complaint that
repeats. Use the evidence rules in `gamedev-concept-judge` (its evidence reference): date
every fact, quotes verbatim, no invented counts.

From that table, write three lines:

- **Crowded:** verbs you could name three times from the last 24 months.
- **Served but complained about:** a verb people play, with a repeated complaint your
  constraints could answer.
- **Out of scope:** anything that needs netcode, a new engine, or a content volume they
  cannot finish. Those are not ideas.

## Step 3 — Five concepts, one twist each

Produce at most five. Each one is a **shipped loop plus one twist**, not a new genre and
not a stack of genres ("cozy roguelike survival crafting extractor").

For each:

```
PITCH      : one sentence a stranger can repeat
VERB       : what they do every 30 seconds
TWIST      : the one rule that is not in the three closest games
AUDIENCE   : who already plays those games
COMPETITORS: 3 names with price and review volume, dated
WHY BUY    : one sentence that is not "better graphics"
PRICE      : inside the observed band
SLICE      : what exists after 2 weeks (one level, one rule)
KILL IF    : a number from a stranger test
CLIP       : a moment ordinary play produces, with no scripted trailer
NOT BUILDING: at least three tempting extras
```

Reject your own concept before showing it if:

- the twist is a theme, a palette, or a camera
- you cannot name three real competitors
- the slice needs a second system to be fun
- day-one multiplayer was not requested

## Step 4 — Rank and pick one

Order by evidence, not by how new it sounds:

1. The complaint you quoted is one this twist removes.
2. The team can finish the slice with what they already have.
3. The clip is the rule itself, visible without explanation.

Recommend **one**. Say the other four are not a backlog. Building two ideas "to see"
is how small teams ship neither.

## Step 5 — Stop

Tell the user to run `gamedev-concept-judge` on that one concept before any production
skill. Do not open the orchestrator, do not list assets, do not pick a camera, until
that verdict is BUILD or the experiment's continue-number is hit.

## Output

The assumptions, the crowded/served/out-of-scope lines, five blocks, then:

```
RECOMMEND : <name>
BECAUSE   : <the complaint it answers, with source>
NEXT      : concept-judge on this pitch only
```

## Related

- `gamedev-concept-judge` — the verdict, with the scoring rubric
- `gamedev-orchestrator` — only after a BUILD verdict

## Knowledge base

T-81 (constrained ideation). T-80 is the judge's market pass; follow it, don't skip it.
