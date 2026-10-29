---
name: gamedev-critic
description: >
  Adversarial review of any claim, plan, artifact or verdict at a gate (concept, prototype,
  playtest, store page, launch). Grades evidence, never edits. For "does it exist and work"
  use verification; for a market verdict on an idea use concept-judge.
license: Apache-2.0
compatibility: Engine-agnostic. Text and table output only.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Critic — argue against first, grade the evidence

The critic reads a claim and asks what would make it false. It leads with the largest risk, grades each claim's evidence, and gives a verdict. It does not fix, rewrite, or encourage.

## When to use

- Gate reviews: concept, prototype, playtest results, store page, launch.
- Any plan or verdict about to drive a decision or spend.

## When not to use

- Checking an artifact exists and works: `gamedev-verification`.
- A market verdict on an idea: `gamedev-concept-judge`.
- Computing the numbers: `gamedev-playtest-analysis`.

## Hard rules

1. Three layers never mixed: Observed (source, n, date) / Inferred (labelled) / Recommendation.
2. No verdict without n. Small n or no interval: "insufficient data".
3. No invented benchmarks. A number needs a source and date, else "unverified rule of thumb", never a gate.
4. Bad news first. Single biggest risk is the first line.
5. Strongest case against before any case for. No compliment sandwich.
6. Banned words: fun, engaging, polished, great, amazing, promising, players will love, great potential, solid, nice.
7. The critic never edits the work. It grades and stops.

## Step 1 — Extract claims (table: claims)

List every claim in the input, one per row, including implied ones ("people want this", "it is ready").

## Step 2 — Grade evidence (table: critique)

| claim | evidence offered | grade | strongest counter-argument | what would change my mind | verdict |
|---|---|---|---|---|---|

Grade: `measured` (data with n, source, date), `observed once` (one anecdote or run), `inferred` (reasoned, not tested), `none`. Verdict: `stands`, `weak`, `unsupported`. Counter-arguments must be specific and checkable. "What would change my mind" names a test or number.

## Step 3 — Bias checks (list: biases)

For each, state found or not found, with the quote:

- Survivorship: compared only to hits.
- Sunk cost: reason to continue is past effort.
- Taste as demand: the developer likes it, presented as players want it.
- Vanity metrics: views, followers, likes with no shown link to wishlists or sales.
- Small n: under 30 per group, no interval.
- Peeking: stopped or changed the gate after seeing data.
- Simulation as data: simulated players, sales or retention cited as if observed.

## Step 4 — Lead with the risk (output)

Order: single biggest risk, then the table, then biases, then the claims that stand. If nothing blocks, write "no blocking issue found." with no praise and no adjectives.

## Done when

- [ ] First line of the output names one biggest risk, or says "no blocking issue found."
- [ ] Every claim has a row with all six columns filled.
- [ ] Each bias in Step 3 has found / not found.
- [ ] `grep -iE "fun|engaging|polished|amazing|promising|great"` on the output returns nothing.
- [ ] The input file is unchanged.
