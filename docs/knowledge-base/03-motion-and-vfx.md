# Knowledge Base C — Motion, Rigging & Animation

Entries T-21 … T-28.

---

## T-21 — Procedural character from rigid parts (no skeleton, no keyframes)

**Problem.** Rigging and animating a character is the usual blocker for an AI agent: bone
weights, pose libraries, and export pipelines are all error-prone. Meanwhile the creator
wanted to know whether AI could do the "hard way."

**Why it works.** If the body is 41 separate solid pieces joined at 17 explicit joints,
the pose is a pure function of code evaluated every frame. There is no skinning to break,
no animation file to corrupt, and the whole character is inspectable and diffable.

**When.** Stylized/robotic characters, first-person bodies, prototypes, or when rigging
tools are unavailable. Not for realistic human deformation.

**Inputs.** Part meshes with known dimensions, a joint hierarchy spec (parent, pivot
position, axis).

**Steps.**
1. Model the body as discrete parts. Assign each a parent and a pivot.
2. Build a joint graph in data: `{name, parent, local_pivot, offsets}`.
3. Each frame: compute a target pose (angles per joint), then resolve transforms
   root→leaf.
4. Add IK for feet/hands where contact matters.
5. Validate by stepping the pose one joint at a time.

**Fails when.** The joint graph is authored implicitly in code with no data file — then
there is nothing to inspect or tune. Also fails when parts are not watertight at joints,
so limbs visibly separate when bent.

**Validate.** At extreme joint angles, no visible gap between parent and child (overlap
the geometry slightly at each joint). The whole skeleton can be posed by setting numbers,
not by editing meshes.

**Recover.** If joints gap, extend the child part's geometry into the parent's volume
rather than shortening the part.

**Debugging bonus.** Build a "one leg at a time" step button before fixing any gait.
The creator did exactly this: "the first thing I asked was not a fix — it was a button
that moves the animal one leg at a time. So I can stop everything and see what it is
really doing" (S01 L334-340).
**Skill.** `gamedev-animation`, `gamedev-blender-headless`.
**Basis.** transcript.
**Src.** S01 L202-232; S01 L334-340.

---

## T-22 — Gait built in the movement lab, then validated in context

**Problem.** A walk cycle tuned in a viewport looks correct and falls apart in the game
on stairs, slopes, and turns.

**Why it works.** The lab removes variables (flat ground, fixed camera, one straight
line) so the gait can be iterated fast; then re-testing in the real level exposes the
interaction between gait and terrain that the lab cannot show.

**When.** Any new locomotion set.

**Inputs.** An empty test room with a straight line and a configurable slope/step set.

**Steps.**
1. Iterate in the lab. Keep every attempt as a numbered state — the creator kept "eight
   attempts, including the ones that were wrong" (S01 L232-235) so progress could be
   compared.
2. Compare attempt *n* against *n−1*; keep the best.
3. Move into the real level and test slopes, stairs, doorways, and turns.
4. Only ship when both the lab and the level pass.

**Fails when.** Only the lab is tested (looks great, breaks on stairs) or only the level
is tested (no way to isolate which variable broke).

**Validate.** Pass criteria named per environment: no foot slide on flat, no limb
interpenetration on stairs, no skating on turns.

**Recover.** If the lab passes and the level fails, the problem is in the controller or
terrain query, not the animation (see T-23).

**Skill.** `gamedev-animation`, `gamedev-locomotion`.
**Basis.** transcript.
**Src.** S01 L228-244.

---

## T-23 — Diagnose flying/broken gaits at surface transitions

**Problem.** Spiders "for the first few seconds looked solid, and then they just started
flying."

**Why it works.** The creator avoided the instinct to rewrite the walk. He isolated the
*failure condition*: "The problem is on every surface change. Floor to wall, wall to
ceiling." On a transition, the body leads and the legs cannot keep up, so contact breaks
and the IK/planting produces impossible positions.

**When.** Any multi-legged or wall-climbing character; also slopes and ledges for bipeds.

**Inputs.** The step-through debug control (T-21), a scene with the transition.

**Steps.**
1. Reproduce at the transition, not on flat ground.
2. Step one limb at a time through the transition.
3. Identify whether the body transform moves before contact is re-established.
4. Fix one of: body advance rate, leg reach limits, contact-reacquisition trigger.
5. Re-test the same transition.

**Fails when.** The nav/path system is changed instead — that alters *where* it goes,
not why the legs detach.

**Validate.** Travel across every transition type in both directions with no frame where
a supporting limb is beyond reach.

**Recover.** If the reach limit cannot cover the transition, the body must slow at
transitions. Accept a slower traversal rather than broken contact.

**Skill.** `gamedev-locomotion`, `gamedev-animation`.
**Basis.** transcript.
**Src.** S01 L330-348.

---

## T-24 — Insect gait: two tripods, planted feet, step length from travel

**Problem.** Legs animate but slide; the walk doesn't read as insect.

**Why it works.** Real insects move in two alternating tripods — three feet planted while
three step. Planting guarantees no slide. Deriving the step length from distance travelled
means a faster bug automatically takes bigger steps, which is self-consistent at any
speed.

**When.** Insects, crabs, mechs, and any 6+ legged creature.

**Inputs.** Per-leg IK; a body-relative step cycle.

**Steps.**
1. Group legs into tripod A (front-left, mid-right, rear-left) and tripod B (the rest).
2. Contact rule: while a tripod is planted, its feet are world-locked.
3. Advance the body; when a stepping leg's remaining reach falls below a threshold, place
   its next foot forward.
4. Step trigger from travel: "the next step starts when the body has gone half a step"
   (S10 L249-251).
5. Scale step length with speed so cadence and stride stay consistent.

**Fails when.** Feet are animated in body space — they then slide with the body. Also
fails when the step trigger is time-based: speed changes then desynchronize stride.

**Validate.** Zero world-space movement of any planted foot. At 2× speed, step length
doubles and cadence is unchanged (or cadence rises and stride holds — pick one rule and
assert it).

**Recover.** If feet still slide, the contact flag is being cleared before the foot is
re-planted.

**Skill.** `gamedev-locomotion`.
**Basis.** transcript.
**Src.** S10 L241-251.

---

## T-25 — Blend locomotion states instead of switching

**Problem.** Walk→run is an instant hard cut. "It works but the change is pretty sudden."

**Why it works.** An animation tree blends the two clips and drives the blend parameter
from actual speed, so the transition is continuous. Turning also blends rather than
snapping direction.

**When.** Walk/run/idle on any biped. Also strafe sets.

**Inputs.** Animation clips sharing a skeleton; an animation tree.

**Steps.**
1. Put walk and run in a blend space parameterized by speed.
2. Drive the parameter from measured speed, not from input intent, so acceleration is
   visibly gradual.
3. For turning, instead of snapping facing, follow a smooth curve and keep blending
   while the character turns (S07 L68-73).
4. Raise blend time for heavy characters, lower it for agile ones.

**Fails when.** The blend parameter is driven by input magnitude — the character reaches
full run *before* it accelerates, so feet slide during acceleration. Drive from velocity.

**Validate.** Capture the transition at 30 fps; the walk/run ratio must change monotonically
with speed in every frame.

**Recover.** If the blend region is too narrow, the animation snaps in the middle of the
transition. Widen the speed range mapped across the blend.

**Skill.** `gamedev-animation`.
**Basis.** transcript.
**Src.** S07 L53-73.

---

## T-26 — Retarget library motion; don't hand-author what exists

**Problem.** Recreating a chopping or archery motion from scratch with an agent produced
"cutting meat with a cleaver."

**Why it works.** Mocap libraries already solved timing, weight, and follow-through.
Retargeting maps that motion onto a different skeleton, preserving the physics the model
would have to invent.

**When.** Human characters. The creator explicitly says this: "at least for human
characters, using an existing animation as a starting point can save you a lot of time"
— and notes it gets harder for animals and unusual motion (S02 L125-133).

**Inputs.** Rigged character; source motion (Mixamo, CMU mocap); retarget step.

**Steps.**
1. Find a clip close to the target; don't search for a perfect one.
2. Retarget to the target skeleton and proportions.
3. Correct hand/foot contacts — the most common retarget failure.
4. Smooth the transition from and to idle (S02 L113-116).
5. Bake so it plays back reliably in-engine.

**Fails when.** Root motion is baked in and the game also drives the character forward —
that produces the exact defect seen in S11: "the walk moved him forward by itself, so in
the game his feet were sliding" (S11 L132-137). Convert to in-place and drive movement
from the controller, measuring real foot speed.

**Validate.** In game, at stated speed, feet do not slide; the attack lands where the
animation says.

**Recover.** If retargeting fights the proportions badly, adjust the source proportions
first or pick a clip from a more similar rig.

**Skill.** `gamedev-animation`, `gamedev-locomotion`.
**Basis.** transcript.
**Src.** S02 L92-133; S04 L77-83; S11 L132-142.

---

## T-27 — Attachments must follow the animating bone

**Problem.** A spear "bent like a bow with every step" because it was attached to a bone
that moved relative to the hand.

**Why it works.** A held object must be a child of the *hand* bone, or be rigidly
constrained to it, with no independent animation of its own.

**When.** Weapons, tools, carried props, anything the character grips.

**Inputs.** Bone hierarchy; attachment socket.

**Steps.**
1. Attach to the hand bone, not to a forearm or spine bone.
2. Set a single socket transform; do not re-key it per frame.
3. Disable inherited scale from the bone if the model must not stretch.
4. Test during walk, run, jump, and attack.

**Fails when.** The weapon is parented to the mesh object and thus follows object
transform only — it then lags. Or the weapon has shape keys/scales inherited.

**Validate.** Frame-by-frame during all animations: the weapon's local offset from the
hand bone is constant.

**Recover.** If the bone hierarchy itself is broken, rebuild the socket on a dedicated
attachment bone.

**Skill.** `gamedev-animation`.
**Basis.** transcript.
**Src.** S11 L138-142; S02 L36-47.

---

## T-28 — Hide what blocks the camera

**Problem.** Going behind a tree or under a roof hides the player; interiors become
unplayable.

**Why it works.** Two complementary techniques: (a) raycast from camera to player and
fade anything the ray hits; (b) for interiors, remove the roof and the front wall when
the player enters. Both preserve the sense of place while never losing the player.

**When.** Third-person games; any interior that shares exterior space.

**Inputs.** Camera, character transform, colliders with a "view blocker" flag.

**Steps.**
1. Each frame, raycast camera→player.
2. Collect hits; fade their material via a dissolve parameter (not by disabling the
   object — it then pops).
3. Restore over a short duration when no longer blocking.
4. For houses used as single spaces, detect the interior volume and hide designated
   "cutaway" parts (roof, front wall).
5. For isometric, hide the roof and near walls of the *room containing the player*.

**Fails when.** Objects are hard-toggled invisible, which reads as a glitch. Also fails
when a whole tree disappears when only a thin branch blocks.

**Validate.** Move through a dense area and an interior; the player's silhouette is
always visible; nothing pops.

**Recover.** If fading is too aggressive, reduce the ray thickness or only fade objects
above a size threshold.

**Skill.** `gamedev-camera`.
**Basis.** transcript.
**Src.** S04 L122-128; S12 L173-185; S11 L203-211.
