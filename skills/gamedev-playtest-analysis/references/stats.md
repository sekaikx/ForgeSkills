# Stats notes and verdict template

## Verdict table template

Write the worst row first.

| Question | Metric | n | Value | 95% interval | Threshold | Decision |
|---|---|---|---|---|---|---|
| Do humans finish level 1? | level_1_done step conversion (humans) | 89 | 65.2% | 54.8% - 74.3% | lower bound >= 60% | CHANGE |
| Is build 0.3.1 better at level 2? | level_2_done, 0.3.0 vs 0.3.1 | 24 / 31 | - | p not computed | n >= 30 each | NEED MORE DATA |

Decisions:
- KEEP: lower bound meets the threshold, n at or above minimum.
- CHANGE: interval is wholly or mostly below the threshold; name the one change.
- CUT: the feature fails its gate in two builds and the comments do not argue otherwise.
- NEED MORE DATA: n below minimum or the interval straddles the threshold. State n to reach.

## Wilson interval

For k successes out of n, with z = 1.96:
centre = (p + z^2/2n) / (1 + z^2/n), half-width = z * sqrt(p(1-p)/n + z^2/4n^2) / (1 + z^2/n).
Works at small n and at p near 0 or 1, where the plain p +/- z*sqrt(p(1-p)/n) fails.
Check: 50 of 100 gives 40.4% to 59.6%. 0 of 10 gives 0% to 27.8%.

## Two-proportion test

Pooled p = (k1+k2)/(n1+n2). z = (p2 - p1) / sqrt(p(1-p)(1/n1 + 1/n2)). Two-sided p-value = erfc(|z|/sqrt 2).
p < 0.05 means the difference is unlikely to be chance alone. It does not mean the change is large or
that the cause is your change: players in the two builds must be comparable (same recruitment, same kind).
Check: 50/100 vs 70/100 gives z = 2.89, p = 0.0039.

## Why not peek and stop

Running the test after every new player and stopping when p < 0.05 produces false "wins" far more
often than 5%. Fix the sample size before the run, look once. If you must look early, treat it as
a progress note, not a verdict.

## Other limits

- Playtesters recruited from friends or a forum are not a random sample. Say who they were.
- Many steps and many builds means many tests; some will pass by luck. Pre-register the few that matter.
- Players who quit before `session_start` logs are invisible. Write that as a limit.
