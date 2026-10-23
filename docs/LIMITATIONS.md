# Limitations

What this library does not do, what was not verified, and where the advice degrades. Read this
before trusting a skill with a task.

---

## 1. Engine skills are untested specifications

`gamedev-godot-pipeline` and `gamedev-unity-pipeline` were written from documented engine
behaviour. **No Godot or Unity installation existed in the environment where they were
authored**, so not a single step in either skill was executed.

They are structured as checklists precisely so they can be verified on first use. Treat every
`[ ]` as unproven until you have run it. The most likely places for error:

- exact import-setting labels (Unity's importer UI wording changes between versions)
- glTF/FBX axis handling specifics
- headless command-line flags

The *concepts* (verify scale in-scene, keep gameplay components off the visual root, parse
stderr because exit 0 lies) are robust. The *keystrokes* are not verified.

---

## 2. The reconstruction in this repo failed its own criteria

The explorer character reached silhouette IoU 0.4628 against a required 0.85. See
`TEST_RESULTS.md` for the full breakdown.

This is included rather than hidden because it demonstrates the library's actual value: the
tooling found and quantified the failure, and found four genuine bugs in the tooling itself
along the way. But nobody should read the reference-reconstruction skill as "this produced a
matching asset". It did not.

**What would be needed to pass:** hood, coat and hair as modelled volumes with authored
shapes rather than scaled primitives; then the same measured loop. Roughly, that is a
different task, not another iteration.

---

## 3. The metrics have specific blind spots

### Silhouette IoU
- **Insensitive to internal structure.** A silhouette-perfect blob scores 1.0.
- **Punishes legitimate pose differences.** A reference in a relaxed pose and a model in a
  T-pose will fail even if the model is correct.
- **Depends entirely on segmentation quality.** A mask that leaks into the background
  produces meaningless numbers — this library's tooling had exactly that bug four times.

### Band width profile
- **Ignores the vertical distribution of mass within a band.** Two very different shapes can
  match the same 10-number profile.
- **Sensitive to the top/bottom crop.** If the reference crop includes a shadow and the render
  does not, every band shifts.

### Palette ΔE
- **Passes on wrong materials with right colours.** It compares colour clusters, not material
  response. A matte brown and a glossy brown score identically.
- **Depends on clustering stability.** K-means with different seeds can produce different
  cluster sets; the reported ΔE moves by a few units between runs.

### SSIM / RMSE
Advisory only, and should stay that way. SSIM rewards blur. A soft, wrong render can beat a
sharp, right one.

### What none of them measure
- Whether the thing is *fun*.
- Whether the animation *reads* (timing, weight).
- Whether the lighting is *appropriate*, as opposed to similar.
- Whether the topology will survive rigging or deformation.

---

## 4. The procedural approach has a hard ceiling

Parametric blockout with primitives is excellent for proportion, scale and layout. It is weak
at:

- **organic surfaces** (faces, hands, foliage, cloth folds) — primitives read as primitives
- **distinctive silhouettes** — a signature hood or hair mass needs authored shape
- **anything the reference's identity depends on** — which is usually exactly the part that
  makes the asset recognizable

The library says this in `gamedev-procedural-modeling` ("do not force procedural generation on
a distinctive silhouette"). The explorer build is the cautionary example: parametric volumes
got the proportions to within 1% and the silhouette to 46% IoU.

---

## 5. Timing and feel numbers are from documented practice

Figures like "hitstop 40-90 ms", "coyote time 0.08-0.15 s", "crossfade 0.10-0.20 s" come from
the analysed transcripts and general game-development practice. They were **not measured in a
running game** in this project.

They are good starting points, not laws. Every one of them should be tuned against the actual
game with the actual input latency of the target platform. A mobile game at 30 fps needs
different windows from a 144 Hz desktop game.

---

## 6. Performance figures are typical ranges, not measurements

Budgets like "≤ 200 draw calls", "1-3 M triangles", "≤ 1.5 GB texture memory" are industry-typical
starting points for desktop. They were not measured on any target hardware here.

Always measure where the game will actually run. A budget derived from someone else's hardware
is a guess.

---

## 7. Placeholder content and scope

- **20 skills, not more.** Areas not covered at all: audio design, narrative/dialogue systems,
  multiplayer/networking, save systems, UI/UX layout, monetization, localization, build
  distribution. `game-ui-ux`, `audio-design`, `save-systems`, `dialogue-systems` and similar
  skills exist elsewhere in the environment but are not part of this library's tested set.
- **No project templates.** The `docs/gamedev/templates/` directory is empty. Every skill
  describes structure rather than shipping a starter project.
- **The tooling is Python + Blender only.** No Godot or Unity automation scripts exist.

---

## 8. Where the skills actively conflict

These are deliberate tensions, and applying both literally will confuse you:

| Tension | Resolution |
|---|---|
| `game-testing` says test everything; `orchestrator` says ship in stages | Test at gates, not continuously. Prototype first, test once the design stops moving. |
| `performance` says budget first; `orchestrator` says build blockout first | Budget the *target*, build the blockout, then measure against the budget. Do not optimise blockout geometry. |
| `verification` says prove everything; `prototype` work moves fast | Verification level scales with commitment. A prototype needs level 3 (it loads); a shipped system needs level 4 (measured behaviour). |
| `reference-reconstruction` says match exactly; `gameplay-systems` says readability first | Match the reference's *assets*; adapt its *lighting and framing* to gameplay needs. Concept art is not a screenshot. |

---

## 9. Known bugs and rough edges

| Area | Issue | Workaround |
|---|---|---|
| `compare.py` | Flood fill is pure Python: ~1.5 s per 512² image on a full panel | Acceptable for iteration; use alpha masks where possible (instant) |
| `compare.py` | K-means is seeded but cluster count affects ΔE by a few units | Fix `--k` across a comparison series |
| `compare.py` | Only handles one subject per image | Pre-crop sheets with `measure_sheet.py` |
| `validate_scene.py` | Envelope is passed manually; wrong envelope = false pass | Derive the envelope from the measured proportions |
| `explorer_build.py` | Tuned for one specific reference, not a general character generator | Treat as an example, not a library |
| `render_compare_views.py` | Camera framing is height-based; wide props need manual framing | Set `lens_mm` and `margin` explicitly |

---

## 10. The honest summary

**Solid:** the workflow discipline (orchestrator, verification, visual-iteration, debugging,
testing), the Blender scripting pitfalls, and the comparison tooling — all exercised, with
real bugs found and fixed.

**Reasonable but unverified:** lighting, camera, locomotion, VFX, animation, modular kits,
texture authoring — written from transcripts and practice, not executed in an engine.

**Weak:** engine pipelines (untested), the reconstruction outcome (failed its criteria), and
anything requiring organic or signature-shaped geometry.

---

## 11. The validator can still be fooled

During the distribution copy, validate_skills.py found zero skills and printed
ERRORS 0 WARNINGS 0. Two separate silent-pass bugs, both now fixed:

- the scan was hardcoded to .agents/skills/, so the skills/ layout scanned nothing
- the technique lookup was hardcoded to docs/gamedev/, so citations went unchecked

Both are now hard failures. The general lesson is in gamedev-verification and worth
repeating: **a check that passes on an empty set is not a check.** Any validator should assert
that it found the thing it was meant to validate, not merely that nothing errored.
