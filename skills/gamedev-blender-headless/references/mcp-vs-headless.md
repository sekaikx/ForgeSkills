# Headless vs MCP vs computer use

One controlled comparison, one model, fresh session per run (S15). Treat the minutes and
dollar figures as that test's results, not a law. Re-time them if the tool or the model
changes. The decision rule below is what survived the test.

Both headless and the official Blender MCP **write Python**. The difference is a
background process versus a live scene. Computer use clicks the UI and writes no script.

## What the test measured

Same brief and same reference pictures.

| Round | Headless | MCP | Computer use |
|---|---|---|---|
| Crate, 60×40 cm, planks, steel corners | ~9 min, judge 31 | ~3 min, judge 30 | 19 min, ~5× the cost, judge 20, a plain box |
| Cast-iron lamp | ~6 min, judge 30 | ~5.5 min, judge 31, cleaner mesh (8 boundary edges vs 436) | dropped |
| Hand cart with cloth cover | slower, judge picked it because the cloth read as cloth | faster, cloth looked like a plastic shell, 30–30 | dropped |
| Edit: break a wheel, load crates | judge 32 | judge 28, the widest gap | dropped |

The edit round is the important failure. The expectation was that MCP would win because
it can see the object it is changing. It was faster and lost on the damage detail.

Cost of the crate was nearly the same for headless and MCP. Headless felt slower because
it rendered a full image every check. MCP grabbed the viewport.

## Many agents

Five props, one agent each:

- Headless: one Blender per agent, about 97 s in parallel. Five was fine. Ten at once
  crawled the machine.
- MCP, one Blender: a single queue on the main thread. Each agent sent its **whole job
  as one call**, so nothing interleaved. About 103 s. All five props landed stacked in
  one scene, so nobody could see their own object. MCP's viewport advantage disappeared.
- MCP, five Blenders and five ports: works, no waiting, and each agent could see its
  prop. They checked more (26 calls vs 11) and the run took longer. Setup was manual.

## Decision

| Situation | Use |
|---|---|
| A pipeline, many assets, overnight, or CI | Headless. Each agent gets a process. The script remains, so the asset rebuilds with no agent. |
| One prop, you want to watch, mesh cleanliness matters | MCP. Viewport checks are the speed. |
| An edit where damage, cloth, or small parts must read | Headless, unless a new test says otherwise. Do not assume "it can see" means it will win. |
| Clicking Blender like a person | Not for modelling, on this evidence. |

When using MCP for several agents in one Blender: one call per finished job, then separate
the objects. Do not share a viewport and expect a private preview.

Computer-use cost and time in this test do not justify it for mesh work.
