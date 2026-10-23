# Knowledge Base B — Assets, Kits & Textures (part 1)

Entries T-09 … T-15. Continued in `02b-assets-and-textures.md`.

---

## T-09 — Headless Blender scripting (no MCP)

**Problem.** Agents that cannot drive a GUI stall on 3D work. MCP-based control adds a
brittle transport layer and a session the agent must keep alive.

**Why it works.** Blender ships a Python interpreter. The agent writes a `.py` file and
Blender runs it with `-b` (background). The artifact is a saved `.blend`, so the process
is reproducible, diffable, and versionable in Git (S07 L36-37).

**When.** Any generated geometry. This is the primary 3D path in the source corpus.

**Inputs.** A Blender executable path; a working directory; a naming convention.

**Steps.**
1. Agent writes a script that builds the object *and* saves the `.blend`.
2. Run: `blender -b -P build.py -- --out out/prop.blend`.
3. Script prints measurements (bounds, triangle count) to stdout for verification.
4. Version the script, not just the output. "Every line adds one piece. So when the roof
   is wrong, I don't touch the mesh — I fix one line and run it again" (S12 L87-92).

**Fails when.** The script depends on GUI state, active object, or operator context.
Use direct data API (`bpy.data.meshes.new`, `bmesh`) instead of `bpy.ops` where possible;
operators need correct context and fail silently in background mode.

**Validate.** Re-running the script from a clean Blender produces the same mesh. Bounds
and triangle count printed and asserted.

**Recover.** If the script fails only in background mode, it used a context-dependent
operator. Replace with data API or wrap in `bpy.context.temp_override(...)`.

**Skill.** `gamedev-blender-headless`.
**Basis.** transcript.
**Src.** S01 L94-105; S07 L30-37; S08 L60-70; S12 L87-92.

---

## T-10 — Draw it, don't describe it (multi-view part generation)

**Problem.** Text prompts for 3D parts return random sizes and wrong topology. One flat
front image returns a solid box, because "from the front, a wall and a box look exactly
the same" (S11 L44-52).

**Why it works.** Image-to-3D needs to resolve the depth axis. Front + side (and often
mirrored side) gives the generator enough silhouette information to infer thickness.
Two orthographic views on a plain dark background remove ambiguity about what is object
and what is background.

**When.** Every part of a modular kit; every prop whose thickness matters.

**Inputs.** Image generator; image-to-3D tool that accepts multi-view input.

**Steps.**
1. Generate the part **twice**: front view and side view.
2. Plain/dark background, single object, nothing else in frame (S11 L54-59).
3. Add mirrored side if the tool supports three views.
4. Feed all views in one request.
5. Request clean quads and an explicit polygon budget.
6. Verify the door hole exists, the wall has thickness, and the silhouette matches.

**Fails when.** Views are inconsistent in scale or framing — the generator then averages
them. Generate both views from the same description and same style prompt.

**Validate.** Front render of the model overlaps the front reference; side render
overlaps the side reference; thickness is non-zero and within tolerance.

**Recover.** If the door comes out blocked, do not attempt mesh edits — the creator tried
twice and "both times it stayed closed" (S11 L42-45). Regenerate with a clearer side view.

**Skill.** `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S11 L22-58.

---

## T-11 — Every part on the same real-size grid

**Problem.** Kit parts hang in the air; posts float above water; walls don't meet.

**Why it works.** Each drawing has its own implicit scale, so each generated part gets
its own arbitrary scale. A shared real-world grid (metres) makes parts *agree* by
construction. The residual error is millimetres, which a snap pass removes.

**When.** Any kit that must tile: walls, walkways, platforms, stairs, roofs.

**Inputs.** A declared grid (e.g. 0.25 m), a target real size per part type.

**Steps.**
1. Write the intended real size of each part in the plan (wall 3.0 × 2.5 × 0.2 m).
2. After generation, measure each part's world bounding box.
3. Scale to the target size; assert the result is within tolerance.
4. Snap the part's origin/corner to the grid.
5. Verify adjacency: two walls placed side by side share an edge with zero gap.

**Fails when.** Only the bounding box is scaled — a part with an odd shape gets
stretched. Prefer uniform scale plus a documented per-axis correction.

**Validate.** Automated: for every adjacent pair, gap ≤ tolerance (2 mm). Print the
worst gap.

**Recover.** If a part cannot reach target size without distortion, regenerate it with
the target size stated in the prompt.

**Skill.** `gamedev-modular-kit`.
**Basis.** transcript.
**Src.** S11 L71-93.

---

## T-12 — Tell it what you don't want

**Problem.** The generated roof looks fine in the reference drawing but in 3D "almost a
third of every roof is just holes" — light, rain, and the camera see straight through.

**Why it works.** Generators satisfy the visible positive prompt and ignore what the
prompt never mentions. Negative constraints close the specific gap that the positive
description leaves open.

**When.** Whenever a part has a hidden face, a closed volume, or an interior.

**Inputs.** The defect found by inspecting the model from a view the reference didn't
show.

**Steps.**
1. Inspect every part from at least top and bottom, not just the reference angle.
2. Name the defect as a constraint: "no gaps, also from below" (S11 L107-110).
3. Regenerate with that sentence added.
4. Re-inspect the same view.

**Fails when.** Constraints are stated vaguely ("solid") instead of physically
("no gaps visible from below; closed volume").

**Validate.** Raycast or render from the previously-broken angle; no light leaks.

**Recover.** If the generator can't honor it, cap the hole procedurally in the modeling
script rather than accepting it.

**Skill.** `gamedev-modular-kit`, `gamedev-reference-reconstruction`.
**Basis.** transcript.
**Src.** S11 L96-112.

---

## T-13 — Three-way part comparison: image-to-3D vs scripted vs hybrid

**Problem.** Choosing one asset pipeline by reputation, then discovering after 40 parts
that every one needs manual repair.

**Why it works.** Each method has a different failure signature, and the failure that
matters depends on downstream needs (grid fit, look control, iteration cost).

**When.** Before committing a project to one pipeline.

**Inputs.** One representative part, three attempts, one comparison render.

**Steps.** Build the same part three ways and judge on *close-up* and *fit*, not the
distant hero shot:

| Method | Strength | Failure | Verdict in source |
|---|---|---|---|
| Image→3D (Tripo) | Fastest by far; looks great at distance | Detail floats off the surface (AC unit ~1 m proud of the wall); painted into one texture so look control is low; scale/grid wrong per part | Good for small details only |
| Scripted Blender | Exact shapes, perfect grid | Surface is code-generated, so "way too clean" — no real dirt | Shapes only |
| Hybrid: scripted mesh + generated textures | Exact shape **and** real dirt | More setup | **Winner** — the project rule |

Resulting rule: "Every wall piece from Blender with the GPT textures and Tripo only for
the small details" (S10 L86-89).

**Fails when.** The comparison is done on one easy part. Use a part with a hole, a bevel,
and a dirt gradient.

**Validate.** All three at the same camera distance and same lighting.

**Recover.** If hybrid loses on a specific part type, keep a per-part-type decision
table rather than one global rule.

**Skill.** `gamedev-modular-kit`, `gamedev-blender-headless`.
**Basis.** transcript.
**Src.** S10 L57-89.

---

## T-14 — Measure the drawing: build to the painted proportions

**Problem.** The scripted mesh is "correct" but doesn't match the concept art: window in
the wrong place, shopfront wrong height.

**Why it works.** The reference image already encodes the proportions the art direction
wants. Reading landmark positions off the image and driving the build script with them
turns art direction into numbers.

**When.** Any part whose concept art must be matched rather than merely inspired.

**Inputs.** Reference image, image measurement (landmark pixel coords), build script.

**Steps.**
1. Measure landmarks in the reference: wall top/bottom, window rect, door rect, AC unit
   rect, expressed as fractions of image height/width.
2. Convert fractions to metres using the declared real size.
3. Drive the script from those numbers — the script "measures the GPT drawing, so every
   part goes exactly where GPT painted it" (S10 L96-101).
4. Render from the same framing; overlay; measure error in fractions.

**Fails when.** Perspective in the reference is ignored — a photo with strong perspective
does not have linear fractions. Use orthographic or near-orthographic references.

**Validate.** Landmark error under a stated tolerance (e.g. 3% of image height).

**Recover.** If error is systematic (all landmarks shifted), the reference framing was
mis-estimated; recalibrate the frame before adjusting individual landmarks.

**Skill.** `gamedev-modular-kit`, `gamedev-reference-reconstruction`.
**Basis.** transcript.
**Src.** S10 L91-101.

---

## T-15 — Seamless tiling by half-offset blend

**Problem.** A generated 1 m texture patch has edges. Two side by side show a visible line.

**Why it works.** Offsetting a copy by half the texture size puts the original edges in
the *middle*, where they can be cross-faded. The result wraps in both directions.

**When.** Any tileable surface: concrete, tiles, shutters, ground.

**Inputs.** One generated patch; an image tool (numpy/Pillow is enough).

**Steps.**
1. Offset the image by (w/2, h/2) with wrap.
2. Cross-fade the seam region with a mirrored copy.
3. Verify: tile 2×2 and check for a visible grid.

**Fails when.** The patch contains a large unique feature (a poster, a stain) that
becomes an obvious repeated motif after tiling. Generate patches with low macro-variance.

**Validate.** Tiled 4×4, downscale, high-pass filter, and check for periodic spikes at
tile boundaries. `tools/texture/tile_seam_check.py` does this.

**Recover.** If the seam persists, the fade width is too narrow relative to the
low-frequency content. Widen the blend or generate a patch with less low-frequency
contrast.

**Skill.** `gamedev-texture-authoring`.
**Basis.** transcript.
**Src.** S10 L106-113.
