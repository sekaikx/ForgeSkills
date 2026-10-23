# Knowledge Base A — Orchestration & Process

Entries T-01 … T-08. Format spec in `README.md`.

---

## T-01 — One job, one fresh session

**Problem.** A single long session accumulates nine unrelated jobs, the model re-reads
all of them every turn, and output quality degrades while token cost climbs.
The creator's own words: sessions "all looked right, but none of them had a gameplay
loop" (S12 L20-24).

**Why it works.** Context is the model's working memory. Unrelated earlier jobs are
noise that increases the chance of editing the wrong file and re-deriving decisions
already made. Isolating a job means the context is exactly the job, its reference, and
its constraints.

**When.** Every implementation job. Not for open design conversation, which needs
accumulated context.

**Inputs.** A decomposed plan with one task per line, each independently testable.

**Steps.**
1. The planning model writes the plan. Each task gets: goal, files touched, acceptance
   test, and what it must *not* touch.
2. Each task runs in its own session with only: the task, the reference, and the
   project conventions.
3. The session ends with a test. Failure sends *the task* back, never the whole plan.
4. Record the result in the task list before opening the next session.

**Fails when.** Tasks are sliced by file rather than by verifiable outcome — a task
"edit player.gd" has no test, so it can never pass or fail. Slice by behavior.

**Validate.** Every task in the plan has a named test. No session produces more than
one artifact plus its test.

**Recover.** If a session sprawls, stop it, split the remaining work into new tasks,
and restart from the last passing test.

**Skill.** `gamedev-orchestrator`.
**Basis.** transcript.
**Src.** S12 L35-46; S01 L51-73; S02 L183-193.

---

## T-02 — The gauntlet loop (independent critic, measured)

**Problem.** The model that wrote the code believes the code is fine. Self-review
reproduces the same blind spot.

**Why it works.** Separating generation from judgment removes the incentive to declare
success. Adding a *number* (dimensions, triangle count, silhouette overlap) prevents the
critic from arguing aesthetics and gives both sides the same pass/fail signal.

**When.** Any job with an objective measurement: wall kits, props, textures, layouts.
Not worth the round-trip for a one-line fix.

**Inputs.** A critic with a different prompt (ideally different model), the artifact, the
reference, and a written acceptance metric.

**Steps.**
1. Builder produces the artifact and a render.
2. Critic receives artifact + render + reference + metric. It does not see the builder's
   reasoning.
3. Critic returns `PASS` or `FAIL` plus **at least two specific fixes** (the creator's
   rule: "Fail means another round with at least two fixes").
4. On FAIL, builder applies the fixes and returns to step 2.
5. On PASS, a human makes the final call.

**Fails when.** The critic is given the builder's rationale — it then audits the
argument instead of the artifact. Also fails when the metric is vague ("looks good"),
which turns the loop into theater.

**Validate.** The loop terminates. If it never terminates, the metric is not measurable
and must be replaced before continuing.

**Recover.** If the critic keeps failing on the same item, the item is mis-specified.
Fix the spec, not the artifact.

**Skill.** `gamedev-orchestrator`, `gamedev-visual-iteration`.
**Basis.** transcript.
**Src.** S07 L37-44; S01 L119-129; S08 L131-150.

---

## T-03 — Orchestrator plus specialists

**Problem.** One model doing planning, modeling, mechanics and review produces mediocre
work in every category and burns budget on the wrong things.

**Why it works.** Roles map to different context shapes: the planner holds the whole
project, a specialist holds one artifact. Splitting lets cheap models handle simple
assets and expensive models handle ambiguity.

**When.** Multi-day projects. Overkill for a single scene.

**Inputs.** A model inventory with each model's observed strengths and cost.

**Steps.** Assign exactly one responsibility per model, then dispatch per task:

| Role | Responsibility | Observed in source |
|---|---|---|
| Orchestrator / planner | Decides *what* and *why*; hands out work; checks returns | S01 L45-50, S12 L10-13 |
| Mechanics builder | Gameplay code, state machines | S12 L13-16 |
| Blender / geometry | Procedural meshes, kit parts | S12 L16-18, S01 L131-136 |
| Aesthetics / Blender | Materials, silhouette, mood | S12 L18-19, S08 L113-120 |
| Critic / reviewer | Pass/fail, independent | S07 L37-44 |
| QA / playtest | Runs the build, reports | S01 L56-73 |

**Fails when.** The orchestrator writes code. It then loses the global view and becomes
a slow specialist. Also fails when one model is assumed better at everything: the
creator's own asset test found a cheaper model produced a *worse value* per dollar
(S08 L150-166).

**Validate.** Each dispatched job returns an artifact the orchestrator can verify without
re-running the job.

**Recover.** If a specialist underperforms on a category repeatedly, move that category
to another model rather than adding more prompt text.

**Skill.** `gamedev-orchestrator`.
**Basis.** transcript.
**Src.** S12 L8-19; S01 L44-50; S08 L60-100.

---

## T-04 — Plan → blueprint → graybox → art, in that order

**Problem.** Building art before the layout is proven produces beautiful rooms that are
the wrong size, and a rebuild.

**Why it works.** Each stage answers exactly one question and can be tested alone:
plan = is it worth building; blueprint = are the dimensions right; graybox = is it
navigable at player scale; art = does it read correctly. Changing an answer at stage *n*
is cheap only while stages *n+1…* have not happened.

**When.** Every space: level, station, city block, house interior.

**Inputs.** An idea, an image generator, a first-person or third-person controller.

**Steps.**
1. Talk through the intent with the planner; get a blueprint (top-down drawing).
2. Build simple gray blocks. Walk it in first person "just to feel how big everything
   is" (S10 L46-51). No materials.
3. Generate look targets over the graybox and pick one mood (S10 L51-55).
4. Only then replace blocks with modular pieces.

**Fails when.** Art is applied to a graybox whose proportions were never validated.
Also fails when the blueprint is skipped in favor of vibes: proportion errors discovered
after art exist cost a full rebuild.

**Validate.** A player can traverse from every entry point to every exit at intended
scale before any material is assigned.

**Recover.** If a space feels wrong after art, measure against the graybox and the
blueprint to find which stage drifted. Rebuild that stage only.

**Skill.** `gamedev-orchestrator`, `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S10 L43-55; S01 L76-91.

---

## T-05 — Color bible as a contract

**Problem.** Every asset independently picks "a different shade of gray," and the game
has no visual identity.

**Why it works.** A small named palette is a *constraint*, not a suggestion. Any asset
can be checked against it mechanically, so inconsistency is detectable rather than
arguable.

**When.** Start of any project with more than one asset author.

**Inputs.** Reference images; an image generator; a place to store the palette.

**Steps.**
1. Generate reference images for the intended mood.
2. Extract a palette: 6–10 named colors with hex values and intended roles (base, accent,
   emission, danger, sky, ground).
3. Publish it as a plain data file the pipeline reads — not a screenshot.
4. Every model's material must use palette colors or documented neutrals.
5. When the scene moves to a different time of day, **translate** every color rather than
   inventing a new palette (S12 L28-32).

**Fails when.** The palette is defined after assets exist; retrofitting fails because
the art direction was already implicit. Also fails when the palette has 20 entries — a
palette that permits everything constrains nothing.

**Validate.** Automated: sample each asset's dominant colors and confirm they lie within
a stated ΔE tolerance of palette entries.

**Recover.** If assets consistently violate the palette, the palette is wrong for the
project. Revise it before generating more assets.

**Skill.** `gamedev-reference-reconstruction`, `gamedev-texture-authoring`.
**Basis.** transcript.
**Src.** S01 L36-42; S12 L28-32.

---

## T-06 — Test with instrumentation first, eyes second

**Problem.** A human playtest at the end catches everything late; a model's "it works"
catches nothing.

**Why it works.** Two independent signals: a script that measures state (did the
character move? did the door open? distance travelled) and screenshots read by a reviewer
(this room is too dark). Numbers catch logic; images catch looks.

**When.** Every feature with observable state.

**Inputs.** Game must be launchable headless or windowed with scriptable input.

**Steps.**
1. Write a script that launches the game and simulates real input: walk the hallway, try
   the door (S01 L60-66).
2. Print pass/fail per check.
3. The same script captures screenshots at fixed moments.
4. A separate agent reads the screenshots and reports defects in plain language.
5. Human makes the final call.

**Fails when.** Only screenshots are checked — a scene can look correct while the
interaction is broken. Only numbers are checked — geometry can be wrong while every
assertion passes.

**Validate.** The test fails when the feature is removed. If it passes either way, it is
not a test.

**Recover.** If a check can't be automated, state that explicitly and substitute
structured manual steps, never a silent skip.

**Skill.** `gamedev-game-testing`, `gamedev-verification`.
**Basis.** transcript.
**Src.** S01 L56-74; S11 L120-149.

---

## T-07 — Reference-first asset iteration

**Problem.** Text descriptions of visual work produce plausible-but-wrong results, and
each retry with more words produces a different kind of wrong.

**Why it works.** A reference image carries silhouette, proportion, and material
simultaneously — three things prose serializes badly. The creator's axe grip improved
only when he "gave the agent an actual reference image of someone holding the axe"
(S02 L48-56).

**When.** Any visual asset, pose, or composition.

**Inputs.** An image generator plus a curated reference.

**Steps.**
1. Describe the style, generate candidates, iterate on *images* until one is right.
2. Ask for *one object on a plain background* — that isolates the target (S07 L26-30).
3. For 3D: provide front **and** side views (S11 L54-59).
4. Build against the reference.
5. Compare render to reference; fix the largest discrepancy; repeat.

**Fails when.** The reference shows the wrong thing at the right style, or one view only
(a front view cannot convey thickness — T-10). Also fails when the reference is a
composite scene: too many variables to attribute a discrepancy.

**Validate.** Side-by-side at matched framing; named discrepancies, not "close enough."

**Recover.** Regenerate the reference with the defect named explicitly, rather than
patching the asset.

**Skill.** `gamedev-reference-reconstruction`.
**Basis.** transcript.
**Src.** S02 L48-66; S07 L20-44; S11 L54-59.

---

## T-08 — Visual reference is the cheapest fix for a bad pose

**Problem.** The agent's first animation/pose attempt is anatomically wrong — arm bent
"like he's trying to hold a TV under his armpit" (S02 L72-76).

**Why it works.** Pose is spatial, and words like "natural" and "relaxed" map to no
joint angles. A reference image gives the agent the shoulder rotation, elbow bend, and
wrist orientation at once.

**When.** Character holds, swings, grips, sits, climbs.

**Inputs.** The rigged character, an image generator, a pose reference.

**Steps.**
1. Capture the bad pose in the actual game camera.
2. Generate or find a reference of the intended pose from a similar angle.
3. Give the agent the render *and* the reference, and ask for the delta in joint terms.
4. Re-render from the same camera.
5. Iterate position and rotation until the contact is plausible.

**Fails when.** The reference is from a very different camera angle — the agent then
matches the image's projection rather than the pose.

**Validate.** Check contact points: hand wraps the grip, fingers don't intersect the
handle, wrist is not inverted, elbow is below shoulder for a downward swing.

**Recover.** If joint-level fixes fight each other, the hand slot itself is wrong —
rebuild the attachment transform before animating. (This is exactly the sequence in
S02 L36-66: fix the slot, *then* the swing.)

**Skill.** `gamedev-animation`, `gamedev-reference-reconstruction`.
**Basis.** transcript.
**Src.** S02 L36-90.
