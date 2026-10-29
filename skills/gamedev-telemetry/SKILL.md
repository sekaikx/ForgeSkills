---
name: gamedev-telemetry
description: >
  Design and add playtest event logging before running any playtest. Use when a build
  needs funnel, death, quit or stuck data, or an event log is missing fields. To read
  the data and decide, use playtest-analysis.
license: Apache-2.0
compatibility: Godot 4.x (GDScript) and Unity 6 (C#). Local JSONL files only, no network.
metadata:
  engine: none
  category: gamedev-workflow
  difficulty: intermediate
---

# Telemetry — log the question before the playtest

Data you did not log cannot be recovered after the session. This skill designs a small
event schema, writes it to a local JSONL file, and proves the events fire. It does not
analyse anything.

## When to use

- A playtest is planned and no events are recorded yet.
- A report shows missing steps, empty death causes, or sessions with no end.

## When not to use

- You already have a log and need a verdict. Use `gamedev-playtest-analysis`.
- You want to test the game logic. Use `gamedev-game-testing`.

## Hard rules

1. **One question per event.** If you cannot write the question it answers, do not log it.
2. **Name events as past-tense facts:** `level_1_done`, `death`, `quit`. Not `level_1`, not `tryLevel`.
3. **Every line carries build id and player kind** (`human`, `bot`, `agent`). Without them the data cannot be compared or kept apart.
4. **Local JSONL first.** One JSON object per line, append only. No service until the local file answers a question.
5. **Privacy.** No names, emails, device ids, IPs, or free text typed by the player. Player id is a random string made at install. Logging is opt-in and the player can see what is logged.
6. **Log facts, not scores.** Do not log "fun" or any rating the code invents.

## Step 1 — Write the schema file

Create `telemetry_schema.md` next to the game. Each row: event, the question it answers, fields.

Every line:
`{"t": seconds since session start, "session": id, "player": id, "kind": "human|bot|agent", "build": "0.3.1", "event": name, ...}`

Required: `session_start`, `session_end`, one `<step>_done` per funnel step.
Optional: `death {cause, x, y, level}`, `quit {level}`, `stuck {x, y, level}`.
Write the funnel order in the file; `tools/analytics/playtest_report.py --funnel` takes the same list.

## Step 2 — Add the logger

Godot 4 (GDScript), autoload `Telemetry`:

```gdscript
var _path := "user://events.jsonl"
var _t0 := Time.get_ticks_msec()
func log_event(event: String, props := {}) -> void:
    var e := {"t": (Time.get_ticks_msec() - _t0) / 1000.0, "session": session_id,
        "player": player_id, "kind": "human", "build": "0.3.1", "event": event}
    e.merge(props)
    var f := FileAccess.open(_path, FileAccess.READ_WRITE)
    if f == null:
        f = FileAccess.open(_path, FileAccess.WRITE)
    f.seek_end()
    f.store_line(JSON.stringify(e))
```

Unity (C#):

```csharp
// JsonUtility cannot name a field "event", so serialise props, then add the fixed fields by hand.
[System.Serializable] class Props { public string cause; public string level; public float x, y; }
static void Log(string ev, Props p = null) {
    string extra = p == null ? "" : "," + JsonUtility.ToJson(p).Trim('{', '}');
    string line = "{\"t\":" + Time.realtimeSinceStartup.ToString("F2", CultureInfo.InvariantCulture)
        + ",\"session\":\"" + SessionId + "\",\"player\":\"" + PlayerId + "\",\"kind\":\""
        + Kind + "\",\"build\":\"" + Application.version + "\",\"event\":\"" + ev + "\"" + extra + "}";
    File.AppendAllText(Path.Combine(Application.persistentDataPath, "events.jsonl"), line + "\n");
}
```

Set `kind` from a launch flag, never hard-code it: bots and agents must write `bot` or `agent`.

## Step 3 — Prove the events fire

Run one session through every funnel step, die once, quit once. Then check the file:

```
grep -c session_start events.jsonl
grep -o '"event":"[a-z_0-9]*"' events.jsonl | sort | uniq -c
python3 tools/analytics/playtest_report.py events.jsonl --funnel tutorial_done,level_1_done
```

Every required event appears. `session_end` fires on quit and on crash-free exit. Save the output as `telemetry_check.txt`. If the report exits 2, fix the file first.

## Done when

- [ ] `telemetry_schema.md` exists, every event has a question.
- [ ] One test session produced a file with every required event (`telemetry_check.txt`).
- [ ] Every line has `build` and `kind`; `grep -v '"kind"' events.jsonl` prints nothing.
- [ ] No personal data in the file; opt-in is shown before the first session.
- [ ] `playtest_report.py` reads the file with exit 0.

## Related

- `gamedev-playtest-analysis` — reads this log and produces the verdict
- `gamedev-game-testing` — repeatable tests; bots that play write the same schema
