# Persona card template

One card per persona. Fill every field before the run. Save as `personas/<id>.md` and record the card hash in the run plan.

```
id:               casual_newcomer
skill_level:      1-5 (1 = never played the genre, 5 = expert)
genre_experience: none | some | veteran  (name two reference games, or "none")
goal:             reach end of level 1 | find the exit | collect 10 items
time_budget_s:    600     # wall-clock cap per run
patience_s:       45      # give up after this long with no progress
input_limits:     keyboard only | no hints | may read the tutorial text
knowledge:        what the persona knows at start (controls shown? goal shown?)
quit_rule:        quits after 3 deaths in the same room
```

## Persona set (starter)

| id | skill | experience | patience | goal |
|---|---|---|---|---|
| newcomer | 1 | none | 30 s | finish level 1 |
| average | 3 | some | 60 s | finish level 1 |
| expert | 5 | veteran | 120 s | finish level 1 under par time |
| lost | 2 | some | 20 s | find the exit without hints |

## Agent report format (observations only)

```
persona: newcomer   run: 14   seed: 88213   build: a1b2c3d
t=00:12  moved right, picked up key        shot: shots/14_0012.png
t=01:05  stalled 22 s at door; tried: interact, jump, move left
t=01:40  died (spikes, room 3)             shot: shots/14_0140.png
outcome: did not reach goal (time budget)
stalled_at: door in room 2
```

Forbidden in a report: ratings, "fun", "boring", "satisfying", "I enjoyed", recommendations to the designer. State what happened and what was tried.
