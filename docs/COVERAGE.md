# Coverage matrix

Every skill against every knowledge-base technique. `●` = technique is the core of the
skill · `○` = referenced or applied in passing · blank = not used.

Technique IDs are defined in [`knowledge-base/README.md`](knowledge-base/README.md) and traced
to transcripts in [`transcript-sources.md`](transcript-sources.md).

## Group 1 — Orchestration and verification (T-01 – T-08)

| Technique | Orchestrator | Verification | Visual-iter | Debugging | Testing |
|---|:--:|:--:|:--:|:--:|:--:|
| T-01 orchestration roles | ● | ○ | | | |
| T-02 gauntlet loop | ● | ● | ○ | | |
| T-03 multi-model division | ● | | | | |
| T-04 graybox sequencing | ● | ○ | | ● | |
| T-05 colour bible | ○ | | ● | | |
| T-06 instrumented testing | ○ | ● | | ● | ● |
| T-07 reference-first iteration | ○ | ○ | ● | | |
| T-08 pose reference fixing | | | ○ | | |

## Group 2 — Assets and textures (T-09 – T-20)

| Technique | Ref-recon | Blender | Proc-model | Mod-kit | Texture |
|---|:--:|:--:|:--:|:--:|:--:|
| T-09 headless script iteration | ○ | ● | ○ | ○ | ○ |
| T-10 multi-view drawing constraints | ● | | | | |
| T-11 grid scale | ● | ● | ● | ● | ○ |
| T-12 negative constraints | ● | | ○ | | |
| T-13 three-way pipeline comparison | ○ | ○ | | | |
| T-14 measure the drawing | ● | ● | | | |
| T-15 roughness + normal from albedo | | | | | ● |
| T-16 projected dirt | | | | | ● |
| T-17 roughness vs texture scale | ○ | | | | ● |
| T-18 atlas allocation | | | | ● | ● |
| T-19 leaf card baking | | | ● | ○ | ● |
| T-20 batch CLI with orientation QA | ○ | ● | | ○ | |

## Group 3 — Motion and VFX (T-21 – T-34)

| Technique | Animation | Locomotion | VFX-impact | Camera |
|---|:--:|:--:|:--:|:--:|
| T-21 procedural rigid-joint rigs | ● | | | |
| T-22 movement lab | ○ | ● | | |
| T-23 surface transition gait | ○ | ● | | |
| T-24 insect tripods | ● | ○ | | |
| T-25 locomotion blending | ● | ● | | |
| T-26 retargeting libraries | ● | | | |
| T-27 bone attachment constraints | ● | | ○ | |
| T-28 frame-by-frame VFX analysis | | | ● | |
| T-29 64-frame flipbooks | | | ● | |
| T-30 layered FX timing | | | ● | |
| T-31 occlusion raycast fading | | ○ | | ● |
| T-32 fracture impulse | | | ● | |
| T-33 screen feedback tiers | | | ● | ● |
| T-34 turrets and deployables | | | ● | |

## Group 4 — World, lighting, gameplay (T-35 – T-52)

| Technique | Lighting | Camera | World | Gameplay | Perf |
|---|:--:|:--:|:--:|:--:|:--:|
| T-35 shadow caster culling | ● | | | | ○ |
| T-36 shadow softness cost | ● | | | | ○ |
| T-37 iterative lighting diagnosis | ● | | | | |
| T-38 lighting presets | ● | ○ | | | |
| T-39 roughness vs texture scale | ● | | | | |
| T-40 geoportal elevation grids | | | ● | | |
| T-41 spline roads | | | ● | | |
| T-42 offline river flow | | | ● | | |
| T-43 footprint paint buffer | | | ● | ○ | |
| T-44 gameplay loop test | | | | ● | |
| T-45 carry and snap hysteresis | | | | ● | |
| T-46 cascading damage stages | | | | ● | |
| T-47 inventory UI extraction | | | | ● | |
| T-48 spec-first combat balance | | | | ● | |
| T-49 visible aim shadow | | | | ● | |
| T-50 swarm steering vs flow fields | | | | ● | ○ |
| T-51 bot nav validation | | | ○ | ● | |
| T-52 11-way breaking quality tests | ○ | | | ● | ○ |

## Group 5 — Performance and pipeline (T-53 – T-58)

| Technique | Performance | Mod-kit | Blender | Godot | Unity |
|---|:--:|:--:|:--:|:--:|:--:|
| T-53 height-field LOD window | ● | | | | |
| T-54 asset decimation | ● | | ○ | | |
| T-55 model tier testing | ● | ○ | | | |
| T-56 asset library allowance | ● | ● | | | |
| T-57 camera-centric detail budgeting | ● | ○ | | ○ | ○ |
| T-58 parameterized kit reuse | ○ | ● | ○ | | |

## Group 6 — Rendering and presentation (T-59 – T-72)

| Technique | Visual polish | Foliage | Artifacts | Art direction | Lighting | Performance |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| T-59 sun direction first | ● | | | | ○ | |
| T-60 sky as fill light | ● | | | | ○ | |
| T-61 tonemapper roll-off | ● | | | ○ | | |
| T-62 contact shading judged in motion | ● | | ○ | | | |
| T-63 GI and albedo discipline | ● | | | ○ | | |
| T-64 fog for depth, not hiding | ● | | | | | |
| T-65 canopy normals | ○ | ● | | | | |
| T-66 vertex-colour wind | | ● | | | | |
| T-67 instanced ground cover, clear paths | ○ | ● | | | | ○ |
| T-68 character fill and practical lights | ● | | | | ○ | |
| T-69 presence vs quality | ● | | ○ | | | ○ |
| T-70 foundation ablation | ● | | | | | |
| T-71 asset cohesion pass | | | | ● | | |
| T-72 symptom-first isolation | | | ● | | | |

## Coverage summary

| Skill | ● core | ○ referenced | Techniques covered |
|---|:--:|:--:|:--:|
| orchestrator | 5 | 3 | 8 |
| verification | 2 | 3 | 5 |
| visual-iteration | 2 | 2 | 4 |
| debugging | 2 | 0 | 2 |
| game-testing | 2 | 0 | 2 |
| reference-reconstruction | 4 | 4 | 8 |
| blender-headless | 5 | 3 | 8 |
| procedural-modeling | 2 | 2 | 4 |
| modular-kit | 4 | 5 | 9 |
| texture-authoring | 5 | 2 | 7 |
| animation | 5 | 3 | 8 |
| locomotion | 3 | 2 | 5 |
| vfx-impact | 6 | 1 | 7 |
| lighting | 5 | 4 | 9 |
| camera | 2 | 1 | 3 |
| world-from-data | 4 | 1 | 5 |
| gameplay-systems | 9 | 1 | 10 |
| performance | 5 | 7 | 12 |
| godot-pipeline | 0 | 1 | 1 |
| unity-pipeline | 0 | 1 | 1 |
| godot-visual-polish | 9 | 2 | 11 |
| foliage | 3 | 0 | 3 |
| visual-artifacts | 1 | 2 | 3 |
| art-direction | 1 | 2 | 3 |
| concept-judge | 1 | 1 | 2 |
| concept-lab | 1 | 1 | 2 |
| boss-encounter | 3 | 0 | 3 |
| audio-wire | 1 | 0 | 1 |

Every technique from T-01 through T-72 is covered as core by at least one skill except two:
T-08 (pose reference fixing) and T-13 (three-way pipeline comparison). Both are referenced
only, which is deliberate. T-08 is a working habit rather than a procedure, and its one rule
(fix the pose before judging the model) is stated inline in `visual-iteration`. T-13 is a
comparison method used while choosing a pipeline, not a step a skill performs. T-73 through
T-81 (group 7) are all covered as core.

## Group 7 — Direction, bosses, sound (T-73 – T-81)

| Technique | Judge | Lab | Orchestrator | Testing | Blender | Boss | Animation | Audio |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| T-73 headless vs MCP vs click | | | | | ● | | | |
| T-74 kill a greybox before art | | | ● | | | | | |
| T-75 autopilot the designer's win | | | | ● | | | | |
| T-76 boss attack timeline | | | | | | ● | | |
| T-77 lock-on facing | | | | | | ● | | |
| T-78 key pose, then in-between | | | | | | ● | ○ | |
| T-79 wire picked audio | | | | | | | | ● |
| T-80 market evidence before build | ● | ○ | | | | | | |
| T-81 constraints, then one idea | ○ | ● | | | | | | |

T-43 (footprint buffer) also cites S16 for snow that displaces, not only darkens. That did
not need a new id.

## Re-check of S01–S13

The original caption files were searched again for audio, bosses, UI, saves, multiplayer,
store pages, and tutorials.

- Already in the technique set: greybox order, questions before combat code (S05), free
  libraries for sound and motion (T-56), footprint buffers (T-43), palette measurement.
- Mentioned, but not a procedure, so still not their own technique: a one-beat story
  (meteor, S01) and "downloaded sound effects from Pixabay" with no event list (S01
  L359-362, S09 L99-101). S14 and S16 are what turned that mention into T-79.
- An unreported tree flicker (S09) is the existing rule that the builder does not sign off.
- Still no procedure in the corpus for dialogue, networking, save/load, a store page, or
  localization. Those stay gaps. They were not skipped by accident.

## Gaps in the technique set itself

The first 58 techniques came from 12 transcripts. T-59–T-72 came from the Godot rendering
video. T-73–T-79 came from three later videos (S14–S16). T-80 and T-81 are engineering:
the build videos never decide whether a game should exist.

Still absent as procedures:

- narrative, dialogue, and quests (S01 states a story in a few lines and does not design one)
- audio *composition* and adaptive music (wiring is T-79; writing a score is not)
- networking and multiplayer
- save/load architecture
- UI layout and accessibility (aim shadows and inventory extraction already live in gameplay)
- monetization and live-ops
- localization
- build distribution and store pipelines

Skills for several of these exist elsewhere in the environment (`audio-design`,
`save-systems`, `dialogue-systems`, `game-ui-ux`) but are not part of this library's tested
set and are not cited against these transcripts.
