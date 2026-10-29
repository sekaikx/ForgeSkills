---
name: gamedev-playtest-agents
description: >
  Run bots and persona-driven agent players against a build to produce telemetry: crashes,
  soft-locks, unreachable goals, stall points, death rates. Use before human playtests. For
  analysing the numbers use playtest-analysis; for fun or appeal you need humans.
license: Apache-2.0
compatibility: Engine-agnostic. Snippet for Godot 4.x. Needs a build id and the telemetry JSONL schema.
metadata:
  engine: any
  category: gamedev-workflow
  difficulty: intermediate
---

# Playtest agents — play the build, emit data, no opinions

Bots and agent players run the game many times and write events. They answer "can it be done, where does it break, where do players stall". They do not answer "is it good". Output is telemetry, not review.

## When to use

- A playable build exists and you want crash, soft-lock and reachability data before humans see it.
- Checking difficulty spikes by death rate and confusion points where a persona stalls.

## When not to use

- Questions of fun, appeal, feel, or purchase intent. Use human players.
- Writing regression tests for a known bug: `gamedev-game-testing`.
- Checking that one artifact exists and works: `gamedev-verification`.

## Hard rules

1. Three layers never mixed. Observed: events, with run count and build id. Inferred: labelled "inference". Recommendation: separate section.
2. No verdict without n. State runs, rate and an interval (e.g. 0 crashes in 200 runs: 95% upper bound about 1.5%). Under 30 runs per persona say "insufficient data".
3. No invented benchmarks. Gates come from your own baseline or are labelled "unverified rule of thumb" and set before running.
4. Bad news first: crashes, soft-locks, unreachable goals lead the report.
5. Agents report observations only. No ratings, no "fun 8/10", no "engaging", "polished", "great potential".
6. Agents never replace humans for feel, fun, appeal, or willingness to buy.
7. Every run is reproducible: seed, build id, persona card hash recorded.

## What each tier can and cannot answer

| Tier | Can answer | Cannot answer |
|---|---|---|
| Bots (random, greedy) | crash, soft-lock, goal reachable, stuck spots, death rate by area | anything about a person |
| Agent players | where a persona stalls, what it tried, confusion points, death rate by skill | fun, appeal, purchase intent |
| Humans | all of the above plus feel and fun, at higher cost and lower n | n in the hundreds |

## Step 1 — Run plan (file: `playtest/plan.md`)

Write before any run: build id, tiers, N runs per tier or persona, seed list, time budget, gates. Example gates, decided now: 0 crashes in 200 bot runs; each agent persona reaches the end of level 1 in at least X% of runs, X chosen from your last build's rate, not from an industry number. Changing a gate after seeing data is peeking: record it as a new plan.

## Step 2 — Bots (headless, many runs)

- Monkey: random valid inputs each frame. Finds crashes and soft-locks.
- Goal bot: greedy or scripted path toward the goal. Finds unreachable goals and broken progression.
- Stuck rule: position unchanged for N seconds (choose N, write it in the plan) emits a `stuck` event and a screenshot, then the bot tries a recovery input; if still stuck after M tries, end the run as `softlock`.
- Run headless: `godot --headless --path <project> -- --bot=goal --seed=N --telemetry=out/bot_N.jsonl`

```gdscript
extends Node
@export var stuck_after_s := 8.0
var _last_pos := Vector2.ZERO
var _still := 0.0
var _out: FileAccess
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
    _rng.seed = 88213                      # record in plan
    _out = FileAccess.open("user://bot.jsonl", FileAccess.WRITE)
    _emit("run_start")

func _physics_process(delta: float) -> void:
    var p: Node2D = get_tree().get_first_node_in_group("player")
    if p == null: return
    Input.action_release("move_left"); Input.action_release("move_right")
    Input.action_press("move_right" if _rng.randf() > 0.3 else "move_left")
    if _rng.randf() < 0.02: Input.action_press("jump")
    else: Input.action_release("jump")
    if p.global_position.distance_to(_last_pos) < 1.0: _still += delta
    else: _still = 0.0; _last_pos = p.global_position
    if _still >= stuck_after_s:
        _emit("stuck", {"x": p.global_position.x, "y": p.global_position.y})
        get_viewport().get_texture().get_image().save_png("user://stuck_%d.png" % Time.get_ticks_msec())
        _still = 0.0

func _emit(ev: String, extra := {}) -> void:
    var d := {"t": Time.get_ticks_msec() / 1000.0, "session": "bot-88213",
        "player": "bot", "kind": "bot", "build": "a1b2c3d", "event": ev}
    d.merge(extra)
    _out.store_line(JSON.stringify(d)); _out.flush()
```

## Step 3 — Agent players (persona cards)

An agent drives the game through an input API, or screenshots plus inputs. Fill a card per persona from `references/personas.md` (skill level, goal, patience, time budget, genre experience). Run each persona the planned number of times with different seeds. Keep the list of what it tried at each stall.

## Step 4 — Telemetry and evidence

Every run writes JSONL in the `gamedev-telemetry` schema: `{"t","session","player","kind","build","event",...}` with `kind` `"bot"` or `"agent"`. Take a screenshot at every `stuck`, `softlock` and `death` event and put its path in the event. Agent reports are timestamped events plus screenshot path, what it tried, where it stalled. Format in `references/personas.md`.

## Step 5 — Hand off

Pass the JSONL files and `plan.md` to `gamedev-playtest-analysis` for rates, intervals and difficulty curves. Stuck or death hot spots found here are Observed; why they happen is Inferred until a human or a test confirms it.

## Done when

- [ ] `playtest/plan.md` exists with build id, N, seeds, gates, written before runs.
- [ ] `wc -l` of the JSONL files matches the planned run count; every line has `kind` and `build`.
- [ ] Every `stuck`, `softlock`, `death` event has an existing screenshot file.
- [ ] Report lists crashes and soft-locks first, with n and interval.
- [ ] `grep -iE "fun|engaging|polished|[0-9]/10"` on agent reports returns nothing.
- [ ] Report states what the agents could not answer.
