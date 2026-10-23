# Knowledge Base F — Gameplay Systems

Entries T-44 … T-52.

---

## T-44 — A feature needs a gameplay loop, not just working code

**Problem.** The modular house builder worked perfectly and was deleted. "The house had no
job. You click and it was there. Nothing to carry, nothing to fill, and nothing can go
wrong. It just felt like another city builder, not a survival game" (S04 L45-53).

**Why it works.** Asking "what does the player *do*, and what can go wrong?" before
building filters mechanics that are technically impressive and gameplay-dead. The rebuild
added cost, risk, and carry — the loop — and kept the same visual goal.

**When.** First hour of any mechanic.

**Inputs.** The genre contract; the game's existing verbs.

**Steps.**
1. Write the loop in one sentence: *verb → cost → risk → reward → next decision*.
2. If any slot is empty, the mechanic is decoration.
3. Estimate the rebuild risk of discovering this late — the source spent over a day and
   then deleted it.
4. Only then implement.

**Fails when.** The loop is written after the code so it can be reverse-justified. Write
it first, in the plan (T-01).

**Validate.** A playtester can name why they'd build one structure instead of two right
now. If there's no reason, there's no loop.

**Recover.** If the loop only exists with a second system, build that system first or
reduce scope to where the loop closes.

**Skill.** `gamedev-gameplay-systems`, `gamedev-orchestrator`.
**Basis.** transcript.
**Src.** S04 L20-54.

---

## T-45 — Carry-and-snap construction with hysteresis

**Problem.** Instant-build feels fake, and snapping that engages/disengages at the same
distance flickers on the boundary.

**Why it works.** Carrying makes construction physical and gives failure states. Snap
hysteresis (engage close, release far) removes the flicker that otherwise makes placement
feel broken — "it only lets go when you move much farther away. Otherwise it would just
flicker back and forth right on the edge" (S04 L102-108).

**When.** Base building, furniture placement, any grid snapping.

**Inputs.** Placement grid; a carried item; preview ghost.

**Steps.**
1. Player carries the resource; place a ghost that snaps to the nearest valid socket.
2. Valid sockets are computed from existing geometry, not hardcoded.
3. Engagement radius < release radius (e.g. engage at 1.2 m, release at 2.4 m).
4. On commit, the piece snaps in with a short animated transition, not instantly.
5. Invalid placement shows the reason (too steep, obstructed) rather than a red ghost.

**Fails when.** Engagement and release radii are equal (flicker), or validity is only
checked at commit (player commits an invalid piece).

**Validate.** Walk the boundary slowly; the ghost must not oscillate.

**Recover.** If snapping to the wrong socket, sort candidates by distance **and** facing
dot product.

**Skill.** `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S04 L54-112.

---

## T-46 — Cascading damage state, then physical breakup

**Problem.** Hitting a tree forever isn't gameplay; a tree that shatters on first hit has
no weight.

**Why it works.** A small explicit state machine (six hits, increasing visible damage,
fall on the sixth) gives the player readable feedback and a predictable cost. Breaking the
fallen trunk into three collectible pieces closes the loop into the inventory.

**When.** Resource nodes, breakables, destructibles.

**Inputs.** Health, damage stages, a fall animation, a fracture rule.

**Steps.**
1. Define `hits_to_fall` and the visual stage per hit (cracks, chips, lean).
2. On the final hit, play a fall that respects terrain (no falling through slopes).
3. On ground contact, replace with N collectible pieces.
4. Each piece registers with the inventory system (T-47).
5. Make progress legible without a health bar: geometry change per hit.

**Fails when.** Damage stages are texture swaps only — the silhouette doesn't change and
the player can't read progress from a distance.

**Validate.** Hit six times; count stage changes; confirm exactly one fall and exactly N
pieces, all collectible.

**Recover.** If pieces sink into terrain, spawn them with a small upward offset and let
physics settle.

**Skill.** `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S02 L136-153.

---

## T-47 — Design the inventory as an image, then build it as elements

**Problem.** "An image is just an image. Our game needs an actual interface" — a concept
render cannot be a functioning UI.

**Why it works.** Splitting design (image generation, fast, cheap, exploratory) from
construction (per-element assets, then engine UI) gets the visual quality of generated art
with the controllability of real UI. Delegating element extraction to a separate agent
keeps the implementation session focused.

**When.** Any UI with a distinctive look.

**Inputs.** Image generator; background/slot/frame/icon extraction; engine UI nodes.

**Steps.**
1. Describe style, atmosphere, and how the inventory should feel; generate concepts.
2. Pick one; extract: background, slot plate, frame, button states, item icons.
3. Rebuild in engine as layout + nine-slice frames + slots — never as a single image.
4. Wire data: slot count, stacking, counts, open/close without stopping gameplay.
5. Compare the built UI to the concept at the same aspect ratio.

**Fails when.** The generated concept is used as the actual UI background with widgets
positioned by eye — it breaks at other resolutions.

**Validate.** Resize from 1280×720 to 2560×1440; nothing stretches illegibly. Open/close
while moving; gameplay continues.

**Recover.** If extracted elements don't tile, regenerate with explicit "flat, orthographic,
centered, symmetric" instructions.

**Skill.** `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S02 L155-197.

---

## T-48 — Spec-first ability design, with the model interrogating you

**Problem.** Combat systems built from a one-line request end up either generic or
unbalanceable.

**Why it works.** Writing the spec *as a conversation with open questions* surfaces
decisions the human hadn't made. The source's bow spec is a complete balance document
before any code: hold-to-draw, growing aim shadow, spread from draw strength, string
durability, no random crits, explicit cancel rules.

**When.** Any ability with more than one input and one output.

**Inputs.** A written spec; open questions; a target image of the result.

**Steps.**
1. Write intent plus open questions; let the model ask back.
2. Resolve to rules with numbers: draw time, damage curve, spread, durability, cooldowns.
3. Convert the spec into a **visual target** ("the spec literally became a prompt" —
   S05 L60-64) so the implementation has an image to match.
4. Implement mechanics only; explicitly defer art/animation.
5. Test each rule independently.

**Fails when.** The spec is a wish list without numbers — then balance is invented during
implementation, which is untestable.

**Validate.** Each rule maps to an observable test: quick shot is weak and wide; full draw
is strong and tight; over-hold breaks the string; cancel is penalty-free.

**Recover.** If a rule can't be tested, it's not specified. Rewrite it as a trigger and an
observable outcome.

**Skill.** `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S05 L14-58.

---

## T-49 — Make hidden systems visible (the aim shadow)

**Problem.** Spread and power are invisible, so misses feel unfair and "you can aim
perfectly and still miss" feels like the game cheated.

**Why it works.** Projecting the shot's outcome onto the ground turns a spreadsheet into a
readable object: length = distance, width = spread, color = string health. The creator
explicitly rejects a hidden dice roll: "you always see it, no hidden dice" (S05 L40-45).

**When.** Any projectile with spread, charge, or falloff.

**Inputs.** A ground-projected mesh/decal; the same math the projectile uses.

**Steps.**
1. Compute the projectile's predicted landing/impact region.
2. Draw it as a decal that grows with charge and widens with spread.
3. Drive its color from a state the player cares about (durability, cooldown).
4. Use *the same* function for the visual and the real projectile — never two codepaths.

**Fails when.** The decal is a rough approximation of the real spread — then it lies, which
is worse than hiding it.

**Validate.** Fire 100 shots at full draw; every impact lies inside the displayed region.
Repeat at minimum draw.

**Recover.** If the region is unreadable, reduce it to a simple ellipse rather than a
complex shape.

**Skill.** `gamedev-gameplay-systems`, `gamedev-vfx-impact`.
**Basis.** transcript.
**Src.** S05 L22-46.

---

## T-50 — Swarm: one brain vs many simple brains

**Problem.** Hundreds of agents with independent pathfinding is expensive; a single shared
flow field looked unpolished in practice.

**Why it works.** The source tried a shared flow field ("one big map of arrows... every bug
just follows the arrow under its feet") and rejected it — the mass of small ants looked
bad. It then moved to a few thousand agents each with a simple local brain and the same
goal, arriving from different directions and flanking.

**When.** Hordes, crowds, ambient flocks.

**Inputs.** Cheap local steering; a shared goal (the player); separation.

**Steps.**
1. Choose the model by *look*, not by cost: flow field for uniform mass movement, per-agent
   steering for organic encirclement.
2. Give each agent the same target but a different approach vector offset.
3. Add separation so they don't stack.
4. Cap the population to what the frame budget allows (source: "a few thousand at most").
5. Verify no conga line: agents must not all arrive from one direction.

**Fails when.** Per-agent pathfinding is used for thousands of agents (cost) or a flow field
is used where individual silhouettes matter (reads as a single organism).

**Validate.** Watch a spawn: approach vectors spread across at least three quadrants; no
two agents occupy the same cell.

**Recover.** If cost explodes, stagger AI updates (update 1/N agents per frame) before
reducing count.

**Skill.** `gamedev-gameplay-systems`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S10 L229-256.

---

## T-51 — Procedural road/spline/terrain systems must be verifiable by a bot

**Problem.** A hand-placed village can look fine and be impossible to walk through; the
player falls into water or gets stuck on a step.

**Why it works.** A navigation bot that traverses from A to B turns "is it navigable?" into
a binary result. The source used it on a generated village and on a station's stairs and
galleries ("just to check you can really get everywhere").

**When.** Generated or modular level geometry.

**Inputs.** Navmesh or collision; a bot controller; a route.

**Steps.**
1. Define entry and exit points.
2. Run the bot with a timeout; log where it stalls.
3. Fix the geometry at the stall point (step too high, gap too wide, collider missing).
4. Re-run until it completes every route.
5. Keep the run as a regression test.

**Fails when.** The bot teleports or uses a different collision layer than the player — then
it validates a game nobody plays.

**Validate.** Bot uses the same collision and movement as the player character.

**Recover.** If the bot can't be built, use automated raycast sweeps along the intended
route and assert clearance.

**Skill.** `gamedev-game-testing`, `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S10 L133-138; S11 L120-149.

---

## T-52 — Break it on purpose: a quality test that tries to fail

**Problem.** Gaps between modular pipes were only found by looking. Looking doesn't scale
to a whole city.

**Why it works.** The creator asked for a test that "breaks things on purpose 11 times, and
it catches every single one" (S10 L128-133). A negative test suite proves the invariant
holds under adversarial conditions, which a visual check cannot.

**When.** Every invariant in a modular/generated system: adjacency, containment, collision,
reachability.

**Inputs.** The invariant, stated numerically; the ability to perturb the system.

**Steps.**
1. State the invariant: "no gap > 2 mm between connected parts."
2. Enumerate 8–12 deliberate violations: remove a part, scale one by 1.01, rotate slightly,
   place an overlapping duplicate, misalign to the grid, etc.
3. Each violation must be detected. A test that passes on a broken system is not a test.
4. Run on the real generated output, not a hand-made case.
5. Keep it as a gate before any import into the engine.

**Fails when.** The test only asserts the happy path (e.g. "parts exist"). It must assert
the failure condition.

**Validate.** Every injected violation is caught; zero false negatives.

**Recover.** If a violation isn't caught, the tolerance is too loose — tighten it until the
violation fails, then verify real output still passes.

**Skill.** `gamedev-verification`, `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S10 L124-136.
