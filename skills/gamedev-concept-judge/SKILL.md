---
name: gamedev-concept-judge
description: >
  Judge a game idea before building it, using dated competitor prices, review counts, and
  player complaints. Use when asked if a game is worth making, who would buy it, what to
  cut, or whether a pitch should change.
license: Apache-2.0
compatibility: Engine-agnostic. Needs web search. No store account required.
metadata:
  engine: none
  category: gamedev-direction
  difficulty: intermediate
---

# Concept judge — evidence before a build

A pitch feeling strong is not demand. This skill produces a verdict a publisher could
argue with: what was observed, what was inferred, and what to do. It does not promise
sales or virality.

## When to use

- "Would people play this / pay for this?"
- "How do we make this idea better?"
- A new game is about to consume months, and nobody has named the competitors.

## When not to use

- The game is already chosen and the task is a system, asset, or bug. Use
  `gamedev-orchestrator`.
- There is no idea yet. Use `gamedev-concept-lab`, then come back.

## Hard rules

1. **No verdict before the market pass.** If search is unavailable, say the verdict is
   blocked. Do not fill the gap with taste.
2. **Three layers, never mixed.** Observed (source + date). Inferred (your reading,
   labelled). Recommendation (what to do). "Not on the page I opened" is not "they don't
   have it."
3. **No motive.** "They added co-op" is a fact. "Because co-op prints money" is a guess.
4. **Confidence.** High = the same complaint in 3+ independent sources from the last 12
   months. Medium = two sources, or one segment. Low = a single review. Do not build a
   persona, or a sentence that starts "players want", from fewer than 5 independent points.
5. **Vanity is not demand.** Views, likes, and "looks cool" do not count. Wishlists,
   demo play time, people asking the price, and strangers replaying without being asked do.
6. **Do not agree to be agreeable.** If the closest shipped game already does the verb,
   say so.
7. **Psychology explains risk. It is not data.** You may name loss aversion, status-quo
   bias, paradox of choice, peak-end, or jobs-to-be-done. You may not score with them.

Full templates, source list, and the attribution for these rules: `references/evidence.md`.

## Step 1 — One sentence, or four questions

Restate the game as: who does what, under what limit, and what they get.

If you cannot, ask only these, then stop until answered:

- Who is it for, and what do they already play?
- How long is one session?
- What does the player do every 30 seconds?
- What do they lose when they fail?

## Step 2 — Market pass

Open real pages. Record **five** alternatives that compete for the same evening, including
games in another genre that satisfy the same urge (mastery, collection, chaos, calm).

For each, on the day you look: name, store URL, price, review count, percent positive,
one strength, one repeated complaint as a short verbatim quote with the source. If a field
is missing, write "not observed", not a guess.

Then three verbatim lines of buyer language (reviews, forums). If you find none, write
"no buyer language found" and lower confidence. Do not invent quotes.

## Step 3 — Score, each line sourced

Score 1–10. Every score is tagged Observed or Inferred. Rubric definitions are in
`references/evidence.md`. The eight lines:

1. Can a stranger state the hook in one sentence after two seconds of footage?
2. How different is the **verb** from the closest shipped game, not the theme?
3. Why buy this instead of that game this month?
4. Is the core action fun before upgrades, unlocks, and story?
5. What will the trailer promise that the first hour does not deliver?
6. Can the stated team ship the promised length in the stated months?
7. After the first win, what is the next reason to start again?
8. Does ordinary play create a moment people can post, without a staged trailer?

A theme swap ("same loop, nicer art") caps line 2 at 4.

## Step 4 — Verdict

One of:

- **BUILD** a named slice (one map, one verb, one session). Not the whole dream.
- **NARROW** — the idea survives only if a specific cut is accepted. Name the cut.
- **STOP** — the verb is already well served, or the scope cannot ship. Say what to do
  instead: a smaller game, or a different verb.

Always include:

- the single strongest version, in one sentence
- three cuts (features that sound good and do not serve the verb)
- three risks
- one experiment cheaper than a month of production, with a number that continues and a
  number that kills (playtesters who continue unprompted, or wishlists from a real page —
  not likes)

Price: recommend a number inside the band of the five prices you observed. Leaving that
band requires an Observed reason (length, online play, or a feature those games lack).
A very low price does not prove demand. People who only take it because it is almost free
are not the buyers of the real price.

## Step 5 — Hand off

Production skills run after **BUILD**, or after the experiment hits its continue number.
Until then, do not design content, cameras, or asset lists for the uncommitted version.

## Output

```
VERDICT     : BUILD slice | NARROW | STOP
GAME        : <one sentence>
EVIDENCE    : 5 rows (url, date, price, reviews, quote)
SCORES      : 8 lines, each Observed or Inferred, with the source
STRONGEST   : <the version to actually make>
CUTS        : 3
RISKS       : 3
EXPERIMENT  : <what, continue-if, kill-if>
PRICE       : <number> inside <observed band>  |  outside because <observed reason>
UNPROVEN    : <claims you refused>
```

## Related

- `gamedev-concept-lab` — when there is no idea yet
- `gamedev-orchestrator` — after the verdict is BUILD
- `gamedev-game-testing` — the experiment, once a greybox exists

## Knowledge base

T-80 (market evidence before a build decision).
