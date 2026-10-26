# Token efficiency

"Skills add tokens" is true for one part of a skill and false for the rest. This page measures
both sides: what the library costs in context, and what it saves by preventing wasted work.

Measure it yourself: `python tools/token_budget.py` (uses `tiktoken` if installed, otherwise
~4 characters per token).

## What a skill costs, and when

| Part | When it is loaded | Rule in this library |
|---|---|---|
| `name` + `description` | Every conversation, for routing | Routing text only, ≤ 110 tokens (validator warns) |
| `SKILL.md` body | Only when the agent picks the skill | Steps and hard rules, ≤ 2,100 tokens (validator warns) |
| `references/*.md` | Only when a step names that file | Long tables, thresholds, templates |
| `assets/*`, `tools/*` | Copied or executed, normally not read | Code the agent would otherwise write from scratch |

## Measured

`python tools/token_budget.py` uses about 4 characters per token unless `tiktoken` is installed.
The table below is chars/4 from that script.

| | 24 skills, before this trim | 28 skills, after |
|---|---:|---:|
| Always loaded (all descriptions) | 1,530 | 1,564 |
| Largest skill body | 2,063 | 2,063 |
| Typical task (descriptions + 2 median bodies) | — | 4,552 |

Both columns are chars/4, measured with `token_budget.py` in the same way. Four new
descriptions cost about 216 tokens. Cutting the longest old descriptions paid for almost
all of that, so the library grew by four skills and **+34** always-on tokens. New bodies
are 1,038–1,351 tokens. Competitor tables, the MCP timing board, and the store-scan rules
sit in `references/` and load only when that step runs.

Earlier notes in this file cited 1,506 and 1,663. Those came from a different counter.
They are retired. Do not add them to this table.

## Where skills save tokens

A skill's body costs ~1,500 tokens once. The things it prevents cost far more:

- **Re-running the engine.** One Godot scene load in the benchmark project takes 60–90 s and
  produces thousands of log lines. A skill that says "one launch for all viewpoints, grep the
  log" removes whole iterations.
- **Writing measurement tools from scratch.** Without `tools/godot/ablation_capture.gd` an
  agent writes its own frame-time harness — a few hundred lines it then debugs (this library's
  own first version measured nonsense until fixed; see `LIMITATIONS.md` §12).
- **Wrong-direction iterations.** The visual-polish pass is ordered by impact; an agent that
  tunes fog before fixing the sun direction redoes the fog later.
- **False success, then rework.** Verification gates catch a broken result before it is
  reported, instead of after a user finds it.

## Habits the skills enforce

Stated once in `gamedev-orchestrator` ("Working cheaply") and applied everywhere:

1. Run the tool, read its summary table, not raw logs.
2. Copy shipped assets and tools; don't retype them.
3. Load only the `references/` section the current step names.
4. Batch engine launches; redirect output to a file and grep it.
5. Grep before reading; read large files by line range.

## Benchmark evidence

See `docs/BENCHMARK_WOODS.md` for the agent-effort comparison on a real Godot game (tool
calls, file reads, engine launches and wall time, with and without the skills).
