# Knowledge Base G — Performance, Perception & Pipeline

Entries T-53 … T-58.

---

## T-53 — Height-field LOD window that follows the player

**Problem.** A high-resolution dynamic height field over a whole map is impossible; static
baking is impossible because the surface changes.

**Why it works.** Only the ground near the player can be interacted with or seen in detail.
Sample a sliding window (source: ~120 m) at full resolution, and never query the whole map.
The window moves with the character, so cost is constant regardless of map size.

**When.** Deformable ground, snow, sand, mud, water depth.

**Inputs.** A grid resolution; a window size; a world→window transform.

**Steps.**
1. Choose resolution from gameplay need (source: 110,000 cells, 60 Hz).
2. Allocate a fixed buffer for the window only.
3. Recenter the window as the player moves; scroll the data by the delta instead of
   re-evaluating.
4. For distant terrain, use a low-resolution or static version.
5. Write changes (footsteps, wind) into the same buffer (T-43).

**Fails when.** The whole map is evaluated each tick "because the height keeps changing."
The source's reasoning: only ask about what matters now.

**Validate.** Frame cost independent of map size; verify by moving 1 km and comparing tick
time.

**Recover.** If recentering causes hitches, scroll and fill the new edge band asynchronously.

**Skill.** `gamedev-performance`.
**Basis.** transcript.
**Src.** S12 L52-73.

---

## T-54 — Decimate purchased assets to the project's art budget

**Problem.** A realistic asset from an asset store has orders of magnitude more triangles
than a low-poly game needs, and its style doesn't match.

**Why it works.** Decimation removes polygons while preserving silhouette, then the style
gap is closed with materials and scale. Cheaper and more reliable than remodeling.

**When.** Buying or downloading stock assets for a stylized game.

**Inputs.** Source asset with acceptable animation; decimation tool; target budget.

**Steps.**
1. Check the animation set first — animation is harder to replace than geometry.
2. Decimate in stages (source: four stages compared) and pick the lowest that keeps the
   silhouette.
3. Retexture/recolor to the palette (T-05).
4. Verify at gameplay distance, not in the viewport.

**Fails when.** Decimation is pushed until the silhouette changes — the creature stops
reading as itself.

**Validate.** Silhouette overlay before/after at gameplay distance; triangle count within
budget.

**Recover.** If decimation destroys the face or paws, protect those regions and decimate
the body only.

**Skill.** `gamedev-procedural-modeling`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S12 L155-166.

---

## T-55 — Test model tiers per task type, not per reputation

**Problem.** Assuming the most expensive model is the best value; assuming the cheapest is
the best value.

**Why it works.** The source ran the same task across four tiers and found the failure
modes were qualitatively different, not just quality-ranked. Cheap models produced
*structurally* correct but mood-less assets; the expensive one understood the intent.
Cost per accepted asset — not cost per session — was the real number.

**When.** Choosing models for a category of work.

**Inputs.** One representative task; identical prompts; a fixed acceptance metric.

**Steps.**
1. Pick a task with an objective accept/reject test.
2. Run every candidate with the *same* prompt and the same review loop (source notes its
   own comparison was invalid because one model skipped the loop — S08 L139-150).
3. Record: accepted?, defect class, tokens/cost, wall time.
4. Route by category: simple props → cheap tier; mood-critical hero assets → top tier.

**Fails when.** The comparison isn't controlled (different loops, different prompts), which
the creator explicitly flags. Anecdotes then become routing policy.

**Validate.** Re-run one task with the chosen model and confirm the acceptance rate holds.

**Recover.** If results are within noise, choose the cheaper and spend the savings on more
review iterations.

**Skill.** `gamedev-orchestrator`.
**Basis.** transcript.
**Src.** S08 L72-166; S09 L18-143.

---

## T-56 — Asset-library allowances beat blind generation for hard content

**Problem.** Some assets (planets, realistic animals, mocap) are far beyond what generation
or scripting produces at quality.

**Why it works.** Choosing the *one* thing to buy preserves the project's consistency
everywhere else while removing a category of failure. The source did this exactly once, on
purpose, for the planet: "the only ready-made model in this whole project" (S01 L196-201).

**When.** Hero assets whose quality gap is unrecoverable, and mocap.

**Inputs.** Licensing check; art-direction match check.

**Steps.**
1. Define the quality bar the asset must clear.
2. Search libraries (Poly Haven for scans, Sketchfab with attribution, Mixamo/CMU for
   mocap, Pixabay for audio — all used in source).
3. Verify license permits the intended distribution.
4. Match it to the palette and scale; retexture if needed (T-54).
5. Record provenance in the project so shipping compliance is trivial.

**Fails when.** Library assets are mixed without a palette pass — the game then looks
assembled. Budget one integration pass per asset.

**Validate.** Side by side with a generated asset: same scale reference, same light, same
palette family.

**Recover.** If it can't be matched, use it only where the camera won't linger.

**Skill.** `gamedev-orchestrator`, `gamedev-reference-reconstruction`.
**Basis.** transcript.
**Src.** S01 L193-201; S09 L95-105; S03 L190-200.

---

## T-57 — Detail where the camera goes, not where the model is

**Problem.** Effort is spent on geometry the player never sees; the space the player lives
in stays empty.

**Why it works.** The source's review of the game's spaces is explicitly camera-driven: the
bridge and corridor got the most detail because they're walked through; the roof camp got
props because the player climbs there. Conversely, flat shop interiors were rebuilt bigger
because the camera was inside them.

**When.** Any environment pass.

**Inputs.** The actual traversal paths; camera distance per area.

**Steps.**
1. List every place the camera stops or dwells.
2. Rank by dwell time.
3. Allocate detail budget in that order.
4. For seen-from-far areas, use silhouette and lighting only — no micro-detail.
5. Re-run traversal after adding detail to confirm nothing blocks movement.

**Fails when.** Uniform detail everywhere: cost rises and the focal hierarchy flattens.

**Validate.** Screen-space detail count per area roughly matches dwell time.

**Recover.** If an area feels empty, add one large silhouette element before adding many
small props.

**Skill.** `gamedev-orchestrator`, `gamedev-lighting`.
**Basis.** transcript.
**Src.** S01 L140-190; S10 L205-215.

---

## T-58 — The kit is the reuse unit; one number changes the whole set

**Problem.** One monolithic model can't be resized, restyled, or repurposed; and a whole
city built as one mesh cannot be edited.

**Why it works.** A kit of parts with shared grid and sockets means a global change is one
parameter. The source's demonstration: "we change one number, the size of a hut, and every
hut in the village grew all at once. Try doing that with one big model" (S11 L150-158).
The same kit also produced an isometric variant with no new models.

**When.** Any repeated architecture.

**Inputs.** Parts on a grid; a parameter schema; an instancing layer.

**Steps.**
1. Define the kit's parameters (module size, wall height, roof pitch, door width).
2. Every part reads parameters; no part hardcodes a dimension.
3. Place instances by referencing parts, not copies.
4. Camera/mode variants (isometric cutaway, first person) operate on the same instances.
5. Validate that a parameter change preserves all adjacency invariants (T-52).

**Fails when.** Parts are copied and edited individually — the kit silently forks.

**Validate.** Change one parameter; every instance updates; no gaps introduced.

**Recover.** If a part can't follow the parameter, it's not really a kit part. Split it into
a variable part plus a fixed accessory.

**Skill.** `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S11 L112-160; S11 L200-211.
