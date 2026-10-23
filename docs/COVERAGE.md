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

## Coverage summary

| Skill | ● core | ○ referenced | Techniques covered |
|---|:--:|:--:|:--:|
| orchestrator | 3 | 4 | 7 |
| verification | 2 | 3 | 5 |
| visual-iteration | 2 | 4 | 6 |
| debugging | 2 | 1 | 3 |
| game-testing | 1 | 2 | 3 |
| reference-reconstruction | 5 | 3 | 8 |
| blender-headless | 3 | 4 | 7 |
| procedural-modeling | 3 | 3 | 6 |
| modular-kit | 4 | 3 | 7 |
| texture-authoring | 4 | 1 | 5 |
| animation | 4 | 2 | 6 |
| locomotion | 2 | 3 | 5 |
| vfx-impact | 5 | 2 | 7 |
| lighting | 4 | 3 | 7 |
| camera | 1 | 4 | 5 |
| world-from-data | 4 | 1 | 5 |
| gameplay-systems | 8 | 2 | 10 |
| performance | 5 | 3 | 8 |
| godot-pipeline | 0 | 3 | 3 |
| unity-pipeline | 0 | 3 | 3 |

Every one of the 58 techniques is covered as core by at least one skill. Group 1's T-08 (pose
reference fixing) is referenced only, which is deliberate — it is a working habit rather than
a procedure, and its one rule (fix the pose before judging the model) is stated inline in
`visual-iteration`.

## Gaps in the technique set itself

The 58 techniques came from 12 transcripts and are not a complete game-development curriculum.
Notable absences:

- audio design and music
- narrative, dialogue, quests
- networking and multiplayer
- save/load architecture
- UI layout and accessibility
- monetization and live-ops
- localization
- build distribution and store pipelines

Skills for several of these exist elsewhere in the environment (`audio-design`,
`save-systems`, `dialogue-systems`, `game-ui-ux`) but are not part of this library's tested
set and are not cited against these transcripts.
