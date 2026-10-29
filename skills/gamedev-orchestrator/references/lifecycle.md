# Idea to launch — the phase map

One phase at a time. A phase ends when its gate passes on data, or when the critic says the
evidence is not there. "We like it" never closes a phase.

Thresholds are set **before** the data comes in and written into the phase artifact. Set
them from your own earlier builds where you have them. Any outside number needs a source and
a date, or it is a guess and cannot be a gate.

| # | Phase | Skills | Artifact | Gate (example: set your own numbers first) |
|---|---|---|---|---|
| 0 | Idea | `gamedev-concept-lab` | one loop + one twist, with constraints | fits team, months, engine |
| 1 | Verdict | `gamedev-concept-judge`, `gamedev-critic` | competitor table, BUILD / NARROW / STOP | BUILD, and the critic finds no unsupported claim it rests on |
| 1b | Hook test | `gamedev-hook-test` | 3–5 greybox clips per hook, tracked results | primary number above the gate written before posting |
| 2 | Prototype | `gamedev-orchestrator`, `gamedev-gameplay-systems`, `gamedev-verification` | greybox of the core verb | loop runs end to end, headless check passes |
| 3 | Instrument | `gamedev-telemetry` | event schema + JSONL from one real session | every funnel event fires once in a test run |
| 4 | Bot pass | `gamedev-playtest-agents` | bot and agent JSONL, stuck screenshots | 0 crashes and 0 soft-locks across the planned runs |
| 5 | Human pass | `gamedev-playtest-analysis` | report from `tools/analytics/playtest_report.py` | lower 95% bound of the key funnel step above its threshold |
| 6 | Page | `gamedev-store-page` | page draft + UTM links | visit → wishlist conversion measured on your own traffic |
| 7 | Market | `gamedev-marketing-loop` | beat calendar + recaps | each beat recorded as target vs actual, dead channels cut |
| 8 | Demo / launch | `gamedev-playtest-analysis`, `gamedev-marketing-loop`, `gamedev-critic` | demo funnel, wishlist delta | decision written as KEEP / CHANGE / CUT with n and interval |

## Loops back

- Phase 4 or 5 fails on the core verb: back to phase 2, not to polish.
- Phase 5 says nobody finishes the tutorial: fix the first ten minutes before any art.
- Phase 6 or 7 shows no conversion after a fair try: back to phase 1 with the new data.
  Spending more on marketing a game that does not convert hides the problem.
- A build exists but the idea has no identity: `gamedev-pivot`, then phase 1b.

## What agents can and cannot answer

| Question | Who answers it |
|---|---|
| Can the level be finished? Where do runs get stuck? Does it crash? | bots and agents |
| Where is the difficulty spike? | bots for death rate, then humans to confirm |
| Is it fun? Would you buy it? | humans only, as behaviour: replay, time played, wishlist |
| Will it sell? | nobody before launch. Wishlists and demo funnel are the closest evidence |
