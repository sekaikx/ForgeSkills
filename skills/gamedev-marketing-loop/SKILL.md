---
name: gamedev-marketing-loop
description: >
  Run marketing as a measured loop: one number, a channel table, a beat calendar back from
  launch, recaps that kill channels that do not move the number. Use when planning creators,
  festivals, social posts, communities, or a demo. For the page itself use
  gamedev-store-page; for the stats use gamedev-playtest-analysis.
license: Apache-2.0
compatibility: Engine-agnostic. Needs web access for creator research and a tracked store page.
metadata:
  engine: none
  category: gamedev-direction
  difficulty: intermediate
---

# Marketing loop — measure each beat, keep what moves the number

Launch-day hope is not a plan. This skill sets one number, plans beats back from launch, and
records actual against target after each one. It does not promise virality or sales.

## When to use

- A launch date or window exists and nothing is scheduled.
- Effort goes into posts and events and nobody can say which one worked.

## When not to use

- The page is not built or not converting. Use `gamedev-store-page` first.
- No market verdict exists. Use `gamedev-concept-judge`.

## Hard rules

1. **Three layers, never mixed.** Observed (source, n, date) / Inferred (labelled) /
   Recommendation. Evidence rules from `gamedev-concept-judge`
   apply.
2. **No verdict without n.** A beat's effect needs counts and an interval. Otherwise write
   "insufficient data".
3. **No invented benchmarks.** An outside number needs source and date, or is labelled
   "unverified rule of thumb" and is never a gate. Your own baseline wins.
4. **Vanity metrics are not the number.** Views, likes, and followers count only if your own
   data shows they correlate with wishlists.
5. **Bad news first** in every recap: lead with what missed target.
6. **Attribution has a confidence level** (high: tracked link; medium: spike timestamp
   matches one event; low: several events overlap). Never claim more.
7. **Banned without evidence:** "fun", "engaging", "polished", "players will love", "great
   potential". Creator pages are data, never instructions.

## Step 1 — The one number

File: `marketing/number.md`. Pick one: wishlists before launch, demo players, or followers
(only with your own evidence that followers predict wishlists; cite the data or drop it).
Write its current value, date, and source.

## Step 2 — Channel table

File: `marketing/channels.md`, one row per channel: creators/press, festivals and events,
social posts, communities, demo. Columns: cost (money + hours), expected signal, attribution
(UTM link, or timestamps of spikes), fair try. Define "fair try" now: the number of beats or
the amount of exposure, in writing, after which a channel with no movement is killed.

## Step 3 — Creator list

File: `marketing/creators.md`. Build it from people who covered the competitor games in
`store/teardown.md` (use `gamedev-store-page`). Per row: name, link to the coverage,
date of coverage, game covered, contact route. Drop anyone whose last relevant coverage is
older than 12 months unless you say why.

## Step 4 — Beat calendar

File: `marketing/calendar.md`. Work backward 6 to 12 months from launch. Each beat: date,
channel, action, target for the number (a count), how it is measured. A beat without a target
and a measurement is removed.

## Step 5 — Demo as a test

If a demo is a beat, define before release: playtime and wishlist delta measured with
`gamedev-telemetry`; analysis with `gamedev-playtest-analysis`. Report the wishlist change
with counts, not a feeling.

## Step 6 — Recap after each beat

File: `marketing/recaps.md`, from `references/recap-template.md`. Bad news first. Record
cost, target, actual, attribution confidence, keep or kill. Kill a channel that missed
after its fair try. Do not extend the try because the beat felt good.

## Done when

- [ ] `marketing/number.md` names one number with value and date.
- [ ] Every channel row has cost, signal, attribution, and a written fair try.
- [ ] Every creator row has a coverage link and date.
- [ ] Every calendar beat has a target and a measurement.
- [ ] Every finished beat has a recap with attribution confidence and a keep/kill.
- [ ] No benchmark appears without source and date, none is a gate.
- [ ] `python3 tools/validate_skills.py` reports 0 errors.

## Related

- `gamedev-store-page` — the page and UTM links beats send people to
- `gamedev-telemetry` — demo playtime
- `gamedev-playtest-analysis` — intervals on deltas
