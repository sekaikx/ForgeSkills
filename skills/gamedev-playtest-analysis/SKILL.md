---
name: gamedev-playtest-analysis
description: >
  Turn playtest logs and comments into KEEP/CHANGE/CUT decisions with sample sizes and
  intervals. Use after a playtest, or to compare two builds. To add logging first use
  telemetry; to judge an unbuilt idea use concept-judge.
license: Apache-2.0
compatibility: Python 3.8+ for tools/analytics/playtest_report.py. Engine-agnostic.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Playtest analysis — decide from data, bad news first

A funnel with no sample size is a story. This skill turns a JSONL event log and written
feedback into a verdict table. It never says the game is good; it says what the data supports.

## When to use

- A playtest finished and you must decide what to change.
- Two builds exist and you must say whether the newer one is better.

## When not to use

- No events were logged. Use `gamedev-telemetry` first.
- The game is not built yet. Use `gamedev-concept-judge`.

## Hard rules

1. **Three layers, never mixed.** Observed (source, n, date). Inferred (labelled). Recommendation.
2. **Decide the metric and threshold before opening the data.** Write them in `questions.md` and do not edit after.
3. **Gate on the lower 95% interval bound, not the point estimate.** 65% of 20 players is not 65%.
4. **Minimum n is 30 per step.** Below it write "insufficient data" and the decision is NEED MORE DATA. Never a trend.
5. **Humans and bots never pooled.** Bots show the game can be finished. Only humans show it is worth finishing.
6. **One change per build comparison.** Two changes in one build means you learn nothing about either.
7. **Bad news first.** Lead with the biggest drop-off or failed gate.
8. **No invented benchmarks.** Compare against your own previous build. An outside number needs a source and date and is never a gate.
9. **Do not peek and stop.** Fix n before the run. See `references/stats.md`.
10. **Banned without evidence:** "fun", "engaging", "polished", "players will love", "great potential".

## Step 1 — Write the questions

`questions.md`: for each question, the metric, the threshold, and the minimum n.
Example: "Do players finish level 1?" `level_1_done` step conversion, lower bound >= 0.60, n >= 30.

## Step 2 — Run the report

```
python3 tools/analytics/playtest_report.py events.jsonl --funnel tutorial_done,level_1_done,level_2_done --out report.md
python3 tools/analytics/playtest_report.py events.jsonl --funnel ... --compare 0.3.0,0.3.1
python3 tools/analytics/playtest_report.py events.jsonl --funnel ... --gate "level_1_done>=0.6"
```

Exit 1 means the gate failed. Exit 2 means the input is broken: fix the log, not the report.
Read the biggest drop-off first. Keep `report.md`.

## Step 3 — Read comments the same way

Put every comment in `feedback.md` with its session id. Count comments per theme. Quote
verbatim with the session id. One loud comment never outweighs the funnel: if three
of 30 players mention a theme, write "3/30", not "players say". Link a theme to the funnel
step it explains, as Inferred.

## Step 4 — Write the verdict table

Use the template in `references/stats.md`. One row per question: metric, n, value, 95%
interval, threshold, decision (KEEP, CHANGE, CUT, NEED MORE DATA). Save as `verdict.md`.
Start the file with the worst row.

## Step 5 — Plan the next build

Choose one change for the worst row. Write what number would show it worked, and the n
needed, before building. Re-run the report on the new build with `--compare`.

## Done when

- [ ] `questions.md` is dated before `report.md`.
- [ ] `report.md` has human and bot sections apart, each with n.
- [ ] `verdict.md` has every question and a decision; none without n and an interval.
- [ ] Every quote has a session id and a count.
- [ ] The gate command was run and its exit code written down.

## Related

- `gamedev-telemetry` — creates the log this reads
- `gamedev-concept-judge` — the earlier, pre-build verdict
- `gamedev-game-testing` — bots that generate the bot half of the data
