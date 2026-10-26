# Transcript Sources

Every technique in this library is tagged with a source ID from this table.

## Why line numbers, not timestamps

The supplied files are DownSub auto-generated caption exports. The `.txt` files contain
**no timestamps** — the `[English (auto-generated)]` header means the caption track was
auto-transcribed and flattened to plain prose. No `.srt`/`.vtt` was supplied.

So citations use `source-id L<start>-L<end>`: the actual line range in the working copy.
You can verify any citation directly:

```powershell
Get-Content _transcripts\t10.txt | Select-Object -Index 185..215
```

Working copies live in `_transcripts/` (ASCII names, byte-identical to the Downloads
originals; created only so tooling that mangles brackets can read them).

**If timestamps are required,** re-export the captions as `.srt` from the original video
and map line → cue. Nothing in the library depends on the timestamp format, only on the
citation resolving to a real passage.

## Source map

| ID | Original filename (in `C:\Users\Malgus\Downloads`) | Lines | Primary subject |
|----|---------------------------------------------------|-------|-----------------|
| S01 | `[English (auto-generated)] AI Built This Space Game From Scratch — Here's Exactly How [DownSub.com].txt` | 412 | Multi-model orchestration, Blender headless via Python, procedural astronaut rig, lighting presets, FPS debugging, procedural spider gait, modular wall kit |
| S02 | `[English (auto-generated)] Building a Game for Steam with AI - Tree Chopping & Inventory [DownSub.com].txt` | 227 | Weapon hand slot, reference-driven pose fixing, Mixamo retarget, tree damage state machine, inventory design→implementation split |
| S03 | `[English (auto-generated)] Can AI Build a Game Good Enough for Steam [DownSub.com].txt` | 214 | Stylized vegetation, triangle budget via baked leaf cards, terrain from elevation data, shadow-softness cost, procedural road shader |
| S04 | `[English (auto-generated)] Can AI Make Building Fun [DownSub.com].txt` | 158 | Building system rejection and rebuild, carry-based construction, snap hysteresis, Mixamo/CMU mocap sourcing, view-blocker transparency, log cutouts |
| S05 | `[English (auto-generated)] Claude Opus 5.5 Looks Insane. But Can It Code My Game [DownSub.com].txt` | 136 | Spec-first bow combat, prompt as design interrogation, ASCII/2D aim shadow feedback, staged delegation, deliberate deferral of animation |
| S06 | `[English (auto-generated)] How Claude and GPT Brought a Quiet Valley to Life [DownSub.com].txt` | 88 | Valley from Blender geometry to Godot shader, shape-variety note, river shader, interior detail pass, yard composition |
| S07 | `[English (auto-generated)] I Stole a Mountain for My Game [DownSub.com].txt` | 178 | Asset reference workflow, gauntlet loop with critic agent, animation tree blending, spline road from repeated segment, offline river simulation, example-driven rock fixing |
| S08 | `[English (auto-generated)] I Used Astra to Make 3D Assets for My First Game [DownSub.com].txt` | 185 | Headless Blender scripting, model-tier comparison (Luna/Terra/Soul/Astra), cost vs. quality, mood as the discriminator |
| S09 | `[English (auto-generated)] Is Opus 5.5 the Best AI Model Yet [DownSub.com].txt` | 143 | Comparative benchmarks: clockmaker diorama, snow physics, hunting game; cost tables; asset-library allowances |
| S10 | `[English (auto-generated)] Is This Really AI Insane Opus 5.5 GameDev Workflow [DownSub.com].txt` | 291 | The densest source: GPT→Blender→texture pipeline, measured drawings, seamless tiling, dirt-by-projection, quality test that breaks things 11 ways, Tripo CLI batching + orientation QA, lighting iteration loop, Jolt destruction, swarm AI vs per-agent AI, explosion reference→sprite-sheet→video flipbook |
| S11 | `[English (auto-generated)] Stop Asking AI for Whole Houses - Opus 5.5 + Tripo [DownSub.com].txt` | 235 | Five kit rules: draw don't describe, real size grid, negate what you don't want, test with a body, texture atlas + UV density heatmap |
| S12 | `[English (auto-generated)] Stop Asking AI To Build The Whole Game At Once [DownSub.com].txt` | 187 | One-job-one-session, color bible, height-field LOD around player, footprint texture paint buffer, lighting preset panel, decimation of purchased assets, occlusion fading |
| S13 | `[English (auto-generated)] Why 3D Games Look Bad in Godot [DownSub.com].txt` | 610 | Settings-only Godot makeover of one village (same assets): sun direction, sky ambient, AgX, SSAO/SSIL, SDFGI and albedo bleed, depth fog vs path readability, radial leaf normals, vertex-colour wind, MultiMesh grass, character fill and practical lights, presence-vs-quality optimisation, foundation ablation |
| S14 | `[English (auto-generated)] How I Built a Game With AI [DownSub.com].txt` | 223 | Three thrown-away worlds, keep one after play, measured colour match, reactor defence purpose, human-picked audio, autopilot caught a win that never damaged the objective |
| S15 | `[English (auto-generated)] Blender MCP vs Headless - I Tested Both With AI [DownSub.com].txt` | 236 | Same briefs through headless Python, official Blender MCP, and computer use: speed, blind judge, mesh cleanliness, parallel agents, when the script left behind matters |
| S16 | `[English (auto-generated)] I Made a Full Boss Fight in Unreal Engine With AI [DownSub.com].txt` | 235 | Boss attack grammar, hit windows, lock-on facing, pose-first motion, snow displacement, kit-split architecture, Niagara instead of cards, impact recordings |

## Attribution discipline

Each knowledge-base entry has a **Basis** field:

- `transcript` — the creator states or demonstrates it. Citation required.
- `transcript+` — the creator does it, and this library adds explicit parameters,
  acceptance thresholds, or failure diagnosis they did not state. Both parts marked.
- `engineering` — added by this library from general engine/production knowledge.
  Never attributed to the creator.

The creator's videos never name several concrete numbers a downstream agent needs
(triangle budgets, tolerance in cm, snap hysteresis distance, color-difference metric).
Those are `engineering` additions and are labelled as such so nothing is fabricated onto
the source.
