# Knowledge Base D — Effects & Feedback

Entries T-29 … T-34.

---

## T-29 — Study the reference frame by frame before building an effect

**Problem.** Effects built from memory look like generic "orange blob" explosions because
the artist's mental model of an explosion is wrong on timing.

**Why it works.** Watching a real explosion frame by frame reveals the actual distribution
of time: the fire is a tiny fraction of the duration, and most of the effect is dark smoke
and dust. Building from that distribution is what makes it read as real.

**When.** Every impact effect, muzzle flash, dust kick, splash, magic burst.

**Inputs.** Reference footage; frame extraction; a timeline.

**Steps.**
1. Extract frames at native rate.
2. Measure the stages: flash (1–2 frames), fire (≈0.1 s — the source says "the fire lasts
   only a tenth of a second"), then smoke and dust dominate, ending in dark debris.
3. Write down duration fractions per stage.
4. Build layers to those fractions, not to intuition.

**Fails when.** The effect is built as one symmetrical grow-and-fade — the source calls
out exactly this: "GPT's pictures don't move, they just grow and fade" (S10 L273-276).

**Validate.** Side-by-side playback at the same frame rate; stage boundaries within a
couple of frames.

**Recover.** If it reads as fake up close, the missing element is *internal motion* — see
T-30.

**Skill.** `gamedev-vfx-impact`.
**Basis.** transcript.
**Src.** S10 L260-276.

---

## T-30 — Flipbook from real motion beats flipbook from stills

**Problem.** Sprites cut from still images scale and fade but never *churn*, so they look
like moving stickers at close range.

**Why it works.** A short generated video contains true internal motion — turbulent smoke
edges rising, fire licking, debris rotating. Cutting it into 64 frames gives the effect
real motion for the cost of one video.

**When.** Hero effects viewed close: explosions, magic bursts, fire jets, large impacts.

**Inputs.** Video generation on a black background; frame cutter; sprite sheet importer.

**Steps.**
1. Generate a short realistic clip on pure black, single effect, centered.
2. Cut to 64 frames (source measure) at a fixed interval.
3. Pack into an atlas; import as a flipbook with the matching frame rate.
4. Add additive blending for fire, alpha for smoke and dust.
5. Layer with separate timelines per stage (T-29).
6. Compare against the reference footage; iterate.

**Fails when.** The background isn't truly black (alpha fringing on additive blend), or
the effect drifts across frames (keep it centered).

**Validate.** Scrub the sheet: consecutive frames differ in *shape*, not only in scale.

**Recover.** If generation won't produce clean black backgrounds, key out with a
threshold and a matte choke before packing.

**Skill.** `gamedev-vfx-impact`.
**Basis.** transcript.
**Src.** S10 L276-283.

---

## T-31 — Layer an effect into named stages with independent timing

**Problem.** A single particle system tries to be flash, fire, smoke, dust, and debris at
once and looks like soup.

**Why it works.** Each physical stage has different motion, blend mode, and lifespan.
Separating them lets you tune the silhouette of each and layer them in time, which is how
the reference actually behaves.

**When.** Every complex effect.

**Inputs.** The stage timing from T-29; textures or flipbooks per stage.

**Steps.** Build layers in this order, each with its own emitter and lifetime:

1. **Flash** — 1–2 frames, additive, no motion.
2. **Fire** — ~0.1 s, additive, flipbook, fast vertical rise.
3. **Debris** — ballistic, gravity, rotates, collides.
4. **Smoke** — alpha, slow rise, expands, longest life.
5. **Dust** — alpha, hugs the ground, spreads horizontally.

**Fails when.** All layers share one lifetime or one blend mode. Also fails when the
flash is long: the eye then reads it as a light source rather than an instant.

**Validate.** Disable layers one at a time; each layer must be individually defensible.
Full stack must not exceed the reference duration.

**Recover.** If it reads as too clean, add secondary motion: dust kicked by debris, smoke
displaced by the fire's rise.

**Skill.** `gamedev-vfx-impact`.
**Basis.** transcript.
**Src.** S10 L264-273.

---

## T-32 — Destruction by fracturing at the impact point with impulse propagation

**Problem.** Breakable props either shatter everywhere at once or not convincingly.

**Why it works.** Fracturing around the hit point concentrates fragments where the energy
is. A real physics engine (source: Jolt, "the same one they used in Horizon Forbidden
West") then gives each fragment mass so a bottle knocking its neighbor is emergent, not
scripted.

**When.** Glass, crates, shelves, bottles, weak structures.

**Inputs.** Physics engine with convex fragments; a pre-fractured mesh or runtime cut.

**Steps.**
1. On impact, collect the hit point and the shot direction.
2. Generate fragments concentrated around the hit.
3. Apply an impulse along the shot direction, scaled by projectile energy.
4. Let contacts propagate; do not script the chain reaction.
5. Cull fragments after they settle; pool them.

**Fails when.** Fragments are unconstrained (fly through walls) or the whole object
becomes dynamic at once (the shelf collapses before it's hit).

**Validate.** Hit one bottle on a shelf: it and its neighbors react, the shelf stays
until hit, fragments stop within a few seconds.

**Recover.** If performance dies, pre-fracture and swap the intact mesh for the fragment
cluster on impact rather than cutting at runtime.

**Skill.** `gamedev-vfx-impact`, `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S10 L219-229.

---

## T-33 — Screen-level feedback is a bundle, scaled by importance

**Problem.** A hit that already works mechanically still feels weak, and the usual fix is
"more particles," which reads as noise.

**Why it works.** Feel comes from several cheap channels firing inside ~100 ms. Scaling
the whole bundle by event importance keeps footsteps quiet and boss deaths loud.

**When.** Hits, landings, pickups, deaths, ability casts.

**Inputs.** Event hooks; audio; a camera with an offset channel; a time-scale control.

**Steps.**
1. Ensure the event emits a discrete signal (T-06 instrumentation).
2. Assign an importance tier.
3. Fire the tier's bundle: sound, particles, camera trauma, hit-stop, flash, knockback.
4. Keep every element transient and self-restoring.
5. Never move the simulated body — move the camera offset only.

**Fails when.** Hit-stop is implemented with a scaled timer (it never resumes at zero
timescale), or on every frame of a held attack.

**Validate.** Repeat the event 20 times; each time the world returns exactly to rest and
input remains responsive.

**Recover.** If it feels worse after adding channels, remove the weakest channel rather
than boosting the strongest.

**Skill.** `gamedev-vfx-impact` (see also `game-feel` in the base library).
**Basis.** transcript (feedback coordinated with animation/camera in S10 L258-283);
engineering (tier table, trauma math).
**Src.** S10 L256-283.

---

## T-34 — Weapons/turrets should not be the player's only damage source

**Problem.** In a swarm scenario, every threat must be answered by the player, and the
screen becomes unmanageable.

**Why it works.** Deployables convert a spatial problem into a positional one: you place
it, it covers an angle, and you fight elsewhere. This is level/economy design, and it
changes what the effect layer must communicate (turrets need their own tracer/impact
language).

**When.** Wave-based or swarm encounters.

**Inputs.** Placement rules, ammo/energy, a target acquisition rule.

**Steps.**
1. Give the turret a limited arc and rate of fire.
2. Show its coverage (a deliberate visual, not a hidden stat).
3. Give its impacts a distinct color/audio so the player can attribute kills.
4. Budget its effects like a normal actor (T-35 performance).

**Fails when.** The deployable is stronger than the player, so the game plays itself.

**Validate.** Play a wave without using the primary weapon; the encounter must be
survivable but slower.

**Recover.** If it trivializes combat, reduce coverage or ammo before reducing damage.

**Skill.** `gamedev-gameplay-systems`.
**Basis.** transcript.
**Src.** S10 L256-261.
