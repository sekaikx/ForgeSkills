---
name: gamedev-hook-test
description: >
  Test whether strangers care about a game's hook before building it: short gameplay clips,
  a capsule and a one-line pitch, shown to real people and measured. Use before committing
  months to a concept or a pivot. For desk research on competitors use concept-judge.
license: Apache-2.0
compatibility: Engine-agnostic. Needs a greybox that can be recorded, and accounts on the posting channels.
metadata:
  engine: none
  category: gamedev-direction
  difficulty: intermediate
---

# Hook test — real strangers, before the months

Desk research says what sold for others. It cannot say whether **your** hook stops a stranger
scrolling. This skill puts 3 to 5 short clips of a greybox in front of real people and
measures behaviour. Opinions from friends do not count.

## When to use

- After `gamedev-concept-judge` says BUILD or NARROW, before full production.
- After `gamedev-pivot` picks an option.
- Choosing between two hooks that desk research cannot separate.

## When not to use

- No playable greybox yet. Build the core verb first (2 to 4 weeks at most).
- The game already has a store page with traffic. Use `gamedev-store-page`.

## Hard rules

1. **Behaviour, not praise.** Count watch-through, follows, wishlists, sign-ups and
   "where can I get this" comments. Likes and "looks cool" are vanity.
2. **Gate before posting.** Write the numbers that mean GO, ITERATE or KILL first. If you
   have no baseline of your own, run the same test on a control clip to get one.
3. **Same conditions.** Same channel, same time window, same length, same caption shape.
   Change only the hook.
4. **No invented benchmarks.** An outside rate needs a source and a date, or it cannot gate.
5. **Real footage.** Greybox is fine. Mock-ups and generated art presented as gameplay are not.
6. **Bad news first.** The recap leads with the weakest result.

## Step 1 — Write the hooks (artifact: `hook/brief.md`)

One line per hook: the verb, and the twist in under 12 words. 2 to 3 hooks, never more.
For each, the first 2 seconds of the clip must show the verb, not a logo or a landscape.

## Step 2 — Record (artifact: clips)

3 to 5 clips per hook, 6 to 20 seconds, vertical and horizontal cuts from the same
footage. Gameplay in frame 1. Record the build id.

## Step 3 — Set up measurement (artifact: `hook/plan.md`)

| Hook | Clip | Channel | Link (tracked) | Posted at | Metric | GO | KILL |
|---|---|---|---|---|---|---|---|

Pick one primary number per channel: watch-through rate, profile visits per 1,000 views,
or sign-ups and wishlists per 1,000 views through a tracked link. Write the minimum views
before reading: below it the answer is "insufficient data".

## Step 4 — Run and record (artifact: `hook/results.md`)

Wait the planned window. Record raw counts, not percentages alone. Copy comments that ask
about the game verbatim with their date; count them, do not cherry-pick.

## Step 5 — Decide (artifact: verdict)

Compare hooks on the primary number with `gamedev-playtest-analysis` (two proportions, 95%
interval). Write:

```
WINNER   : <hook> or "no detectable difference"
EVIDENCE : <metric, n views, value, interval> per hook
DECISION : GO / ITERATE (change one thing, retest) / KILL
```

Two ITERATE rounds with no movement means KILL, or back to `gamedev-pivot`.

## Done when

- [ ] Gates were written and dated before the first post.
- [ ] Every hook has raw counts and an interval, or "insufficient data".
- [ ] The decision is GO, ITERATE or KILL, with the number that drove it.
- [ ] `gamedev-critic` was run on the verdict.
