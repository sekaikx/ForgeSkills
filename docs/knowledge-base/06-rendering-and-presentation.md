# Knowledge Base H — Rendering & Presentation

Entries T-59 … T-72. Source S13 demonstrates the full settings-only pass on one Godot village
(same assets, same layout). Godot property names and version notes are `engineering`
additions from the Godot 4.x documentation; the creator shows the editor, not the API.

---

## T-59 — Sun direction first

**Problem.** A scene with good assets reads flat: every visible face of every building is
equally bright.

**Why it works.** Form is read from value differences between faces. A low, side-on key gives
one lit and one shaded face per object; an overhead sun or one behind the camera removes them,
and no later effect restores them.

**When.** First step of any lighting pass. Not for fully interior scenes (use the main
practical light instead).

**Inputs.** The main directional light; 3 fixed viewpoints.

**Steps.**
1. Lower the sun (engineering: 20–40° elevation) and rotate it side-on to the main surfaces.
2. Warm the colour.
3. Greyscale screenshot: lit vs shaded face of one building must differ clearly.

**Fails when.** Effects are stacked on an overhead sun to "add depth" (S13 L536-583 shows the
finished scene collapsing when the sun preset is removed).

**Validate.** Greyscale value difference between faces at every viewpoint.

**Recover.** Re-aim before touching any other setting.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-lighting`.
**Basis.** transcript+.
**Src.** S13 L78-112, L536-583.

---

## T-60 — Sky as the fill light

**Problem.** Shadowed areas are flat grey and the warm sun has nothing to contrast with.

**Why it works.** Real shade is lit by the sky: cool, soft, from above. Sky-sourced ambient
gives warm-key/cool-fill contrast with no extra lights.

**When.** Outdoor scenes. Indoors use probes or GI instead.

**Inputs.** A sky resource; the environment's ambient settings.

**Steps.**
1. Background = sky (blue top, warmer horizon).
2. Ambient source = sky.
3. Lower sky contribution/energy if shadows turn navy (engineering).

**Fails when.** Ambient is so strong that shaded faces match lit faces again (undoes T-59).

**Validate.** Shaded faces cooler than lit faces; value difference from T-59 preserved.

**Recover.** Reduce ambient energy until the T-59 check passes again.

**Skill.** `gamedev-godot-visual-polish`.
**Basis.** transcript+.
**Src.** S13 L113-134.

---

## T-61 — Tonemapper for highlight roll-off

**Problem.** Bright areas clip to white; warm light skews hue; colours look muddy.

**Why it works.** A filmic curve compresses highlights instead of clipping. AgX (Godot 4.4+)
preserves hue in bright regions better than Filmic/ACES.

**When.** After light direction and ambient are set. Exposure after choosing the curve.

**Inputs.** Environment tonemap settings.

**Steps.**
1. Choose AgX (or Filmic where AgX is unavailable/unsuited, e.g. Mobile in 4.4).
2. Adjust exposure.
3. Grade (contrast, saturation, LUT) after tonemapping.

**Fails when.** Exposure is tuned before the curve is chosen, or grading is done through
exposure.

**Validate.** No clipped areas on the brightest lit surface; sun colour keeps its hue.

**Recover.** Reset exposure to 1.0, re-tune after the curve.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-art-direction`.
**Basis.** transcript+.
**Src.** S13 L138-162.

---

## T-62 — Contact shading, judged in motion

**Problem.** Objects float; corners and the bases of props have no darkening.

**Why it works.** SSAO darkens occluded creases; a little SSIL adds short colour bounce.
Both are screen-space, so they change as the camera moves.

**When.** Forward+ renderer. Off on low-end presets.

**Inputs.** Environment SSAO/SSIL settings; a camera path.

**Steps.**
1. Enable SSAO, modest radius (~1 m) and intensity.
2. Add light SSIL.
3. Walk the camera through the scene and watch screen edges and moving objects.

**Fails when.** Judged from still screenshots: halos and edge fading only show in motion.

**Validate.** Contact visible at bases and corners; no halos while moving.

**Recover.** Smaller radius, lower intensity; bake AO for static hero areas.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-visual-artifacts`.
**Basis.** transcript+.
**Src.** S13 L175-198.

---

## T-63 — Bounce light and albedo discipline

**Problem.** Shade looks lifeless; or, after enabling GI, walls turn green.

**Why it works.** GI carries surface colour into nearby shade. Bright saturated albedo (grass)
bleeds onto neighbours; the fix is the albedo, not the GI.

**When.** After contact shading. Pick the cheapest GI that fits (lightmaps < VoxelGI < SDFGI).

**Inputs.** Albedo values of the large surfaces; renderer.

**Steps.**
1. Enable the chosen GI.
2. Check large surfaces' albedo: no pure 0/1 channels, foliage rarely above ~0.6.
3. Lower GI energy only after albedo is plausible.

**Fails when.** GI energy is cranked to fix flatness that T-59 should have fixed.

**Validate.** Shade has subtle colour; no neighbour tinted by an obvious source.

**Recover.** Desaturate the bleeding albedo.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-art-direction`.
**Basis.** transcript+.
**Src.** S13 L199-222.

---

## T-64 — Fog for depth, never for hiding

**Problem.** Far objects are as crisp as near ones; the scene has no depth layers.

**Why it works.** Aerial perspective — distance lowers contrast and shifts toward the sky
colour — is one of the strongest depth cues.

**When.** Outdoor scenes with depth. Volumetric fog only when light shafts matter.

**Inputs.** Environment fog; a sky for aerial perspective.

**Steps.**
1. Depth fog starting beyond the play space.
2. Aerial perspective tinted from the sky.
3. Check the walkable route at the far viewpoint.

**Fails when.** Ground mist hides the path (S13 L250-262: the road disappears).

**Validate.** Layers separate; path, enemies and pickups still readable.

**Recover.** Push fog start out, lower height-fog density near routes.

**Skill.** `gamedev-godot-visual-polish`.
**Basis.** transcript.
**Src.** S13 L230-262.

---

## T-65 — Canopy normals for leaf cards

**Problem.** Trees read as flat pictures: separate light/dark patches across the canopy.

**Why it works.** Each card faces a different direction, so each is lit differently. Normals
pointing from the canopy centre outward light the canopy as one volume.

**When.** Alpha-card foliage. Not solid-mesh trees.

**Inputs.** Canopy centre and extents; foliage material.

**Steps.**
1. Replace card normals with `normalize(vertex - centre)` (bake or shader).
2. Blend slightly toward original normals.
3. Orbit the tree to check back faces.

**Fails when.** Back-face normals end up inverted (engineering: Godot flips them with culling
disabled).

**Validate.** Canopy has one lit side and one shaded side from every angle.

**Recover.** Toggle the back-face flip; lower blend.

**Skill.** `gamedev-foliage`.
**Basis.** transcript+.
**Src.** S13 L285-322.

---

## T-66 — Wind weighted by vertex colour

**Problem.** The world looks like a photograph — nothing moves.

**Why it works.** Small vertex motion reads as life. Weights keep roots planted; world-space
noise makes gusts travel across neighbours.

**When.** Grass, leaves, flowers.

**Inputs.** Vertex colour weights (dark root, light tip); a noise texture.

**Steps.**
1. Paint weights.
2. Offset vertices by scrolling world-space noise × weight.
3. Keep amplitudes small; drive by `TIME`.

**Fails when.** No weights (whole plant slides) or per-object random phase (no gusts).

**Validate.** Roots fixed, tips move, neighbours move together.

**Recover.** Square the weight to pin roots harder; lower amplitude.

**Skill.** `gamedev-foliage`.
**Basis.** transcript.
**Src.** S13 L323-345.

---

## T-67 — Instanced ground cover with clear paths

**Problem.** Bare ground between props; or a dense field that costs too much and buries the
route.

**Why it works.** Instancing draws thousands of blades in few calls; visibility ranges and no
shadows bound the cost; a density mask keeps routes readable.

**When.** Grass, flowers, clutter.

**Inputs.** A blade mesh; a placement mask excluding paths.

**Steps.**
1. MultiMesh (source: 20,000 instances), chunked (engineering).
2. Visibility range with fade; shadows off.
3. Leave paths clear.

**Fails when.** One MultiMesh for the whole map (never culled), or grass on the path.

**Validate.** Frame time with/without recorded; route readable.

**Recover.** Lower visibility end and density before removing.

**Skill.** `gamedev-foliage`.
**Basis.** transcript+.
**Src.** S13 L346-395.

---

## T-68 — Character fill and practical lights

**Problem.** The character disappears in shade; night areas are dead.

**Why it works.** A fill light restricted to the character's layer keeps them readable without
relighting the world. Lights with visible sources (lanterns, windows) make darkness intentional.

**When.** Third-person games; any scene with dark areas.

**Inputs.** Render layers; light cull masks; emissive materials.

**Steps.**
1. Small fill light on the player, cull mask = character layer.
2. Lanterns and emissive windows where the world implies light.

**Fails when.** The fill lights the environment too (flattens T-59) or lights have no source.

**Validate.** Character readable in shade; every light traceable to an object.

**Recover.** Tighten the cull mask; lower fill energy.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-lighting`.
**Basis.** transcript+.
**Src.** S13 L396-423.

---

## T-69 — Separate presence from quality when optimising

**Problem.** The game got slow after polishing; the instinct is to delete whole effects.

**Why it works.** An effect's look (sun direction, colour) and its cost (shadow resolution,
soft filtering, samples, distance) are different knobs. Cutting quality keeps the look.

**When.** Any time frame time is over budget after a visual pass.

**Inputs.** Fixed viewpoints; vsync off; per-setting measurements.

**Steps.**
1. Measure each setting's cost leave-one-out (engineering: `tools/godot/ablation_capture.gd`).
2. Reduce quality knobs: shadow resolution, soft-shadow quality, AA samples, grass distance.
3. Re-measure; remove presence only for settings that are expensive and invisible.

**Fails when.** Measured against a monitor cap (S13 L508-515: "75 fps" hides the real
headroom), or the sun is removed to save shadows.

**Validate.** Frame time within budget; viewpoint screenshots unchanged at gameplay distance.

**Recover.** If a reduction is visible, step back one quality level.

**Skill.** `gamedev-godot-visual-polish`, `gamedev-performance`, `gamedev-visual-artifacts`.
**Basis.** transcript+.
**Src.** S13 L455-536.

---

## T-70 — Foundation ablation

**Problem.** Many effects are on and nobody knows which ones matter.

**Why it works.** Removing one change from the finished result shows whether others
compensate. A good foundation (sun) cannot be replaced; a redundant effect changes nothing.

**When.** After the pass is complete.

**Inputs.** Finished scene; the same viewpoints.

**Steps.**
1. Remove the first improvement; compare.
2. Repeat for any suspect effect.
3. Delete effects whose removal changes nothing.

**Fails when.** Effects are kept "because they are on".

**Validate.** Each remaining effect has a visible job at some viewpoint.

**Recover.** If removing the foundation changes little, the base was weak — redo T-59.

**Skill.** `gamedev-godot-visual-polish`.
**Basis.** transcript.
**Src.** S13 L536-605.

---

## T-71 — Asset cohesion pass

**Problem.** Mixed asset packs read as a collage ("asset store look") even when each asset is
good.

**Why it works.** Cohesion comes from shared rules — shape, value, palette roles, material
ranges, texel density — applied cheapest-first: shared light and grade, then palette, then
materials, then density, then shapes.

**When.** Assets from several sources in one scene.

**Inputs.** A one-page art bible; palette; texel density targets.

**Steps.**
1. Write checkable rules.
2. Unify light/grade; remap palette; normalise materials; fix density; replace off-shape
   assets.
3. Measure (greyscale, palette ΔE, texel density).

**Fails when.** A stylisation shader is applied to some assets only.

**Validate.** Same-hand test on 6 random assets; palette report passes.

**Recover.** Go one step further down the cheapest-first list.

**Skill.** `gamedev-art-direction`.
**Basis.** engineering.
**Src.** none (engineering; S12 color bible is the nearest transcript practice).

---

## T-72 — Symptom-first artifact isolation

**Problem.** A visual artifact gets hidden with blur, fog or post instead of fixed.

**Why it works.** Most artifacts have one cause. Toggling one setting at a time at a fixed
camera finds it; classification by motion (still / camera / object / first-seen) narrows it.

**When.** Any flicker, crawl, leak, halo, pop or hitch.

**Inputs.** A fixed camera marker; the setting list.

**Steps.**
1. Reproduce at a marker; classify.
2. Toggle one setting at a time.
3. Fix the cause; re-check at the marker in the same motion.

**Fails when.** Several settings are changed at once.

**Validate.** Artifact gone at the marker and at other viewpoints; frame time recorded.

**Recover.** Bisect the setting list.

**Skill.** `gamedev-visual-artifacts`.
**Basis.** engineering.
**Src.** none (engineering).
