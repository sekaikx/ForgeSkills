# Knowledge Base E — World, Lighting, Camera & Performance

Entries T-35 … T-43.

---

## T-35 — Shadow cost: cull shadow casters, not lights

**Problem.** After adding atmospheric lighting, the game ran under 30 FPS. Turning lights
off doubled the frame rate, which suggested the lights were the problem.

**Why it works.** The real cost was shadow *passes*: every shadow-casting lamp re-renders
the room from that lamp's viewpoint. "For my eyes it was 600 pieces, for the shadows
14,000" (S01 L305-312). Disabling shadow casting on most lights keeps the lighting look
almost entirely and recovers the frame rate (30 → 50 FPS in source).

**When.** Any scene with many small local lights.

**Inputs.** A profiler that separates shadow passes; per-light shadow flags.

**Steps.**
1. Measure FPS with lights on and off to confirm the class of cost.
2. Enable shadows on **one** key light only (the one that defines the space).
3. All other lights: shadow off, slightly boosted range/intensity to compensate.
4. Re-measure; target a specific FPS floor.
5. Check the look: ambient occlusion or contact shadows fill in where shadow casting was
   removed.

**Fails when.** Lights are deleted instead of their shadows — the scene loses its mood.
Also fails when the key light's shadow map resolution is raised to "fix" softness, which
costs far more.

**Validate.** Frame time under budget with the final lighting; visual check that the
scene still reads (no floating objects).

**Recover.** If it still under-performs, the next suspects are shadow *resolution* and the
number of shadow-casting meshes — reduce the map size before removing lights.

**Skill.** `gamedev-lighting`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S01 L296-313.

---

## T-36 — Soft shadows are the most expensive slider in the panel

**Problem.** A shadow-softness setting looks like a small aesthetic tweak and silently
destroys performance.

**Why it works.** Softness is implemented with extra samples/blur taps per shadowed pixel.
Measured in source: pushing softness to maximum took the scene from over 800 FPS to about
40 — "more than half the FPS gone" (S03 L166-176).

**When.** Setting up any directional/sun shadow.

**Inputs.** The light's shadow softness/blur parameter; an FPS overlay.

**Steps.**
1. Establish the frame-time baseline at the intended resolution.
2. Raise softness incrementally, measuring at each step.
3. Stop at the highest value that keeps frame time inside budget.
4. Compensate hardness with shadow-map resolution and distance, not softness.

**Fails when.** Softness is tuned on a small test scene and then applied to the full
level — the cost scales with shadowed pixels.

**Validate.** Same measurement in the real scene, not the test scene.

**Recover.** If softness must stay low for performance, fake softness with a contact-shadow
decal or a baked AO under key objects.

**Skill.** `gamedev-lighting`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S03 L160-178.

---

## T-37 — Lighting iteration: screenshot → diagnose → change one variable

**Problem.** The first lighting pass made "the whole city one big street lamp" — everything
orange, every wall the same color, "nothing for your eye to catch" (S10 L190-200).

**Why it works.** Feeding the render back as an image makes the diagnosis visual and
specific ("50 orange lamps", "every wall the same color"). Fixing the named cause — palette
variation and a focal hierarchy — changes the image far more than nudging intensities.

**When.** Any lighting pass, especially night/neon/interior.

**Inputs.** Screenshot capability; a light inventory (count by type/color).

**Steps.**
1. Capture the current state.
2. Enumerate the lights: count, color, intensity, shadow flag.
3. Name the dominant failure: too many of one hue, no value hierarchy, no focal point.
4. Change **one** of: palette spread, key/fill ratio, intensity falloff, emissive accent.
5. Re-capture from the **same camera**.
6. Repeat until the focal point is unambiguous.

**Fails when.** Several variables change per iteration — then no result is attributable.
Also fails when the reference is a different time of day (see T-38).

**Validate.** Squint test: the focal point must still read. Value histogram must have
separation between foreground, midground, and background.

**Recover.** If it is "better but not what I wanted," the missing property is usually
material response (wet ground → mirror) rather than more lights.

**Skill.** `gamedev-lighting`, `gamedev-visual-iteration`.
**Basis.** transcript.
**Src.** S10 L184-208.

---

## T-38 — Lighting presets exposed as data, with a control panel

**Problem.** Tuning lighting inside the engine is slow for the agent and invisible to the
human; and the same scene must support many moods.

**Why it works.** Named presets (day, night, maintenance, emergency, brownout, blackout)
turn mood into a selection. Exposing the parameters as a panel lets the human iterate
without touching code, and gives the agent an objective list to validate.

**When.** Any project where the same space is revisited at different times/states.

**Inputs.** A light rig; a preset resource; optional debug panel.

**Steps.**
1. Define presets by intent, not by numbers: "emergency = ceiling off, red is the only
   color left" (S01 L290-294).
2. Implement each as data: per-light color/intensity/enabled/shadow.
3. Transitions interpolate between presets.
4. Preserve readability in the darkest preset: "blackout, but it never goes fully black —
   you are left with a line on the floor and the door" (S01 L294-300).
5. Expose sliders for exposure, fog density, key intensity, fog color.

**Fails when.** Presets are hard-coded in scene files, so they cannot be diffed or
validated. Also fails when the darkest preset actually reaches zero — the player is lost.

**Validate.** For every preset, the player can identify the exit. Capture each preset from
a fixed camera and confirm the frame is not clipped to black.

**Recover.** If a preset is unreadable, raise the floor light (emissive strips) before
raising global exposure.

**Skill.** `gamedev-lighting`.
**Basis.** transcript.
**Src.** S01 L274-300; S12 L130-150.

---

## T-39 — Roughness and texture scale beat texture choice

**Problem.** The project tried code-generated textures, then compared against scanned
PBR sets. The surprise: the deciding factor was not which texture, but how big it was on
the wall.

**Why it works.** "Same panel, wrong scale, and it reads as concrete" (S01 L268-272).
Roughness is the parameter that changes perceived material class; tiling scale sets
perceived object size. Both dominate albedo detail.

**When.** Every material pass; especially before buying or generating more textures.

**Inputs.** A reference material; tiling controls; roughness map.

**Steps.**
1. Fix the object's real size.
2. Set tiling so one texture repeat equals a real-world dimension (e.g. 1 m of concrete).
3. Set roughness mean and variance from the reference's highlight behavior.
4. Only then adjust albedo.
5. Validate with a moving light.

**Fails when.** Tiling is tuned by eye on a flat plane and then applied to walls of
different sizes.

**Validate.** Two walls of different sizes show the same physical feature size.

**Recover.** If it still reads wrong, the material is the wrong *class* (metal vs stone),
not the wrong texture.

**Skill.** `gamedev-texture-authoring`, `gamedev-lighting`.
**Basis.** transcript.
**Src.** S01 L255-273.

---

## T-40 — Terrain from real elevation data; edits stored separately

**Problem.** Hand-built terrain never feels like a real place, and the source game is
explicitly based on a real mountain range.

**Why it works.** Elevation data *is* the real landscape. Treating it as a height grid —
"think of an image, except each pixel stores a height instead of a color" — then
triangulating gives authentic landforms for free. Keeping edits in a separate layer means
roads can be cut without destroying the original.

**When.** Any game set in a real location, or any terrain needing believable large-scale
erosion shapes.

**Inputs.** Elevation dataset (source used Poland's geoportal), OSM for roads/streams, a
mesh builder.

**Steps.**
1. Download elevation for the target area; note resolution and size (source: 8×8 km,
   height data ≈2.5 MB).
2. Build a grid mesh from the heights; connect into triangles.
3. Store modifications (flattening for roads, cuts) as a separate delta layer.
4. Place OSM-derived roads/streams into the *modified* surface.
5. Chunk the terrain for streaming.

**Fails when.** Edits are baked into the height data — then the original is lost and
re-importing changes everything.

**Validate.** Compare a render against a real map/satellite image: ridge lines and valley
positions match.

**Recover.** If the terrain is too coarse at player scale, add detail noise only in the
near field; do not raise global resolution.

**Skill.** `gamedev-world-from-data`.
**Basis.** transcript.
**Src.** S03 L184-209; S07 L76-82.

---

## T-41 — Roads along splines; ground stays authoritative

**Problem.** Roads modeled as geometry cut into terrain are painful to move and break at
slope changes.

**Why it works.** A spline defines the route; a short straight road module is repeated and
bent along it, and it sits *on top of* the terrain. "We never touch it directly. The road
sits on top, so we can make it wider or move it to the side, and the ground just follows"
(S07 L108-116).

**When.** Any path/road/river/rail network.

**Inputs.** Spline from map data; one modular road segment; terrain height query.

**Steps.**
1. Build one short, straight, tileable road segment.
2. Sample the spline; instance the segment; orient to the tangent.
3. Conform to terrain height at both ends, and add cross-slope handling.
4. Blend edges (gravel, leaves) to hide the seam with the ground.
5. Keep the terrain as the height authority so the player never stands inside the road.

**Fails when.** The spline is in 2D and the terrain is 3D — the road then floats or sinks
on slopes. Sample height along the spline, not at endpoints only.

**Validate.** Walk the road at every curvature extreme; no gaps at the edge, no step
underfoot.

**Recover.** If tiles visibly repeat, offset UVs per instance and vary edges.

**Skill.** `gamedev-world-from-data`.
**Basis.** transcript.
**Src.** S07 L102-116.

---

## T-42 — Precompute water flow offline; ship a texture

**Problem.** Simulating a river at runtime is expensive and unstable.

**Why it works.** Water flow on a static riverbed doesn't change. Simulating once and
baking depth+direction into a texture makes runtime cost near zero, and gives the shader
(foam, waves) the *actual* current rather than a scrolling UV illusion.

**When.** Rivers, streams, waterfalls, drainage.

**Inputs.** Riverbed mesh, a grid solver (source: cell-by-cell flow into tiny squares),
cell size, inflow.

**Steps.**
1. Tessellate the riverbed into cells.
2. Per cell store depth and flow direction only (the source's two properties).
3. Pour water in at the top; solve downhill propagation per cell.
4. Iterate until stable.
5. Bake depth+direction to a texture; the game samples it.
6. Validate: start from an empty dry bed — "the water ended up in exactly the same place"
   (S07 L131-136).

**Fails when.** Solver resolution is finer than the texture — detail is lost. Match them.

**Validate.** Runtime: water slows in pools, speeds over steps, splits around islands.
Bake time in the source was about one minute for the whole river.

**Recover.** If flow leaks out of the bed, the boundary condition is wrong; clamp edges to
zero flow.

**Skill.** `gamedev-world-from-data`.
**Basis.** transcript.
**Src.** S07 L116-152.

---

## T-43 — Footprint and snow tracks as one paint buffer

**Problem.** Individual footprint objects (or individual snow-displacement meshes) explode
in count and cost.

**Why it works.** A single fixed-size texture acts as the memory. Every actor paints into
it; the world reads it; weather erases it. "A thousand tracks cost the same as one"
(S12 L76-83).

**When.** Snow, mud, sand, dust; blood pools; any accumulating surface marks.

**Inputs.** A render target; world→UV projection; decay function.

**Steps.**
1. Create one texture covering the active play area (source: LOD window around player).
2. Project world position to UV; write foot shape / displacement.
3. Read it in the ground shader for depth darkening and normal perturbation.
4. Apply decay (wind/snow refill) as a slow global fade.
5. Move the window with the player, scrolling the buffer.

**Fails when.** The buffer covers the whole map — resolution becomes useless. Use a
moving window (T-53).

**Validate.** Walk a long path; marks persist, then fade; frame cost unchanged by track
count. Where the ground should physically give (snow you sink into), the buffer also
displaces the surface, on the order of 10 cm, not only a darker texture (S16 L79-87).

**Recover.** If marks swim when the window moves, scroll UVs with the window origin.

**Skill.** `gamedev-vfx-impact`, `gamedev-performance`.
**Basis.** transcript.
**Src.** S12 L73-83; S16 L79-87 (displacement, not a colour-only snow texture).
