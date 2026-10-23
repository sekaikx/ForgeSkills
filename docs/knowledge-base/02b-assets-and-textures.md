# Knowledge Base B — Assets, Kits & Textures (part 2)

Entries T-16 … T-20. Continues from `02a-assets-and-textures.md`.

---

## T-16 — Derive roughness and normal from the color map

**Problem.** A flat albedo looks like painted cardboard. Real concrete catches light
unevenly.

**Why it works.** The luminance variation in a photograph *is* surface variation. High
local contrast and dark pits imply roughness and depth. Deriving maps from the albedo
keeps them perfectly registered — no UV mismatch, no second generation step.

**When.** Procedural or generated texture sets where no scan is available.

**Inputs.** Albedo patch, image tool.

**Steps.**
1. **Height/roughness source:** luminance of the albedo.
2. **Normal map:** Sobel gradient of the luminance, strength parameter exposed.
3. **Roughness map:** inverted, blurred luminance remapped to a narrow range around the
   intended value (concrete is rough; do not let it vary to mirror-smooth).
4. **Ambient occlusion (optional):** heavily blurred inverted luminance, used as a
   multiplier in the base color.

**Fails when.** The normal strength is set high by default, producing plastic-looking
micro-contrast. Concrete needs low strength; brick needs higher.

**Validate.** Render the same plane under a moving light. The highlight must *move*, not
sit fixed. `tools/texture/tex_to_maps.py` implements this.

**Recover.** If the surface reads as wet, reduce roughness variance and raise the mean
roughness.

**Skill.** `gamedev-texture-authoring`.
**Basis.** transcript (roughness/normal derived from the same picture); engineering
(Sobel/remap specifics).
**Src.** S10 L113-118; S03 L262-272.

---

## T-17 — Dirt by projection over a clean base

**Problem.** Scripted surfaces are too clean; painted dirt in the albedo destroys the
ability to vary it.

**Why it works.** Treat the generated drawing as a *dirt mask*, not a color. Everything
darker than the clean base becomes dirt; the clean wall remains parametric. Dirt then
composites "like from a projector" on top (S10 L118-124), so it can be scaled, offset,
or removed per instance without regenerating the surface.

**When.** Walls, floors, props needing grime, wear, or stains.

**Inputs.** Clean base material, dirt reference image, a mask derivation.

**Steps.**
1. Generate a clean base texture (flat color with mild noise).
2. Generate or pick a dirt/wear reference.
3. Compute mask = normalize(clean_luma − dirt_luma), clamped at 0.
4. Composite: `albedo = mix(base, dirt_color, mask * strength)`.
5. Feed `mask` into roughness (dirt is rougher) and slightly into height.
6. Tune strength per part; keep it below the point where the shape disappears.

**Fails when.** The dirt reference has different lighting than the base, so the mask
encodes lighting rather than dirt. Use flat-lit references.

**Validate.** Toggle the dirt layer off and on; the underlying shape and tiling must be
unchanged, only the surface response changes.

**Recover.** If dirt looks painted-on, add roughness correlation and lower the albedo
delta.

**Skill.** `gamedev-texture-authoring`.
**Basis.** transcript.
**Src.** S10 L118-124.

---

## T-18 — Texture atlas with UV-density-aware allocation

**Problem.** In a kit, a small post and a big roof get the same texture size, so the post
is over-detailed and the roof is blurry. Plus 23 materials for 22 parts is extra draw
calls.

**Why it works.** A single atlas with space allocated proportional to *world surface
area* equalizes texel density. It also collapses material count, which reduces draw
calls and state changes.

**When.** Any modular kit with more than ~5 parts.

**Inputs.** Per-part textures, per-part world surface area, packing tool.

**Steps.**
1. Measure each part's world surface area.
2. Allocate atlas area proportional to area (square-root allocation for rectangular
   slots).
3. Pack with a bin-packer; record each part's UV rect.
4. Remap each part's UVs into its rect.
5. Split into at most 2–3 atlases by material family (e.g. buildings / environment).
6. Verify with a UV-density heatmap: orange = blurry, blue = wasted pixels.

**Fails when.** Parts are allocated by bounding box instead of surface area — thin long
walls then get far too much space.

**Validate.** UV density ratio between the best and worst part under a stated factor
(e.g. < 1.6×). Material count equals atlas count. `tools/texture/uv_density.py`
computes and reports this.

**Recover.** If one part dominates, split the atlas by object scale class rather than
forcing one atlas.

**Skill.** `gamedev-texture-authoring`, `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S11 L160-200.

---

## T-19 — Polygon budget by baking leaf cards

**Problem.** A single tree at 34,000 triangles is fine alone and impossible in a forest.

**Why it works.** Dense, self-similar geometry (foliage) can be flattened to textured
planes with almost no perceptual loss, while the silhouette-carrying parts (trunk, main
branches) stay 3D. The budget then goes where the eye reads shape.

**When.** Vegetation, hair, fur, grille detail, chain-link, dense repeats.

**Inputs.** High-poly source, bake (albedo + normal), plane cards.

**Steps.**
1. Identify the silhouette carriers — keep them as geometry.
2. Group the rest into clusters; bake each cluster to color + normal.
3. Map clusters onto planes oriented along the dominant view.
4. Cross the planes (2–3 per cluster) so the shape holds from multiple angles.
5. Verify triangle count and appearance at gameplay distance.

**Measured result in source:** birch 34,000 → ~2,800; maple → ~1,500, "keeping the
overall shape and style" (S03 L99-110).

**Fails when.** Cards are used for the silhouette itself, which then reads as flat
cutouts. Also fails when normal maps are baked from a different orientation than the
plane.

**Validate.** Silhouette comparison against the high-poly at gameplay distance; triangle
count under budget; no visible card edges when the camera orbits.

**Recover.** If cards are visible as flat planes, add a third cross-plane or keep one more
level of geometry.

**Skill.** `gamedev-procedural-modeling`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S03 L96-112.

---

## T-20 — Batch generation with resumability and orientation QA

**Problem.** Generating 18 props through a browser means 18 × (upload, configure, wait,
download). And the outputs are not trustworthy: wrong polygon counts, models facing
backwards.

**Why it works.** A text-driven CLI turns the batch into one data file plus one command,
which makes it resumable, cheap to re-run, and checkable. Automated QA on the *output*
catches the errors the generator will not report.

**When.** Any batch of more than ~5 generated assets.

**Inputs.** CLI with API access; per-prop reference images (front/side/back).

**Steps.**
1. Write **one** manifest file: prop name, image paths, settings, output path.
2. Run the batch with concurrency (source used 6 at a time).
3. Persist per-item state so an interrupted run resumes without re-paying.
4. Automated QA per model: real-world size, collision, orientation.
5. Orientation check: inspect from four sides; rotate the ones facing backwards.
6. Only then import into the engine.

**Measured result:** 18 models in ~10 minutes, no clicks; 4 of 18 came back backwards;
requested 3,000 faces, got ~5,000 (S10 L146-176).

**Fails when.** State is kept only in memory — an interruption then restarts the whole
batch and re-bills. Also fails when QA is skipped because "the tool succeeded."

**Validate.** Manifest count == output count; every output passes size/orientation
assertions; re-running after a simulated interruption produces no duplicate charges.

**Recover.** For backwards models, do not regenerate — rotate 180° and record the
correction in the manifest so future runs are correct by default.

**Skill.** `gamedev-blender-headless`, `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S10 L143-176.
