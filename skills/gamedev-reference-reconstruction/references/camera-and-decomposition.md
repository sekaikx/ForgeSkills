# Camera calibration and decomposition example

Loaded from Steps 2 and 5 of SKILL.md.

## Step 5 - camera calibration

Wrong camera = every judgement is invalid. Match:

- **Focal length / projection.** Portraits and prop shots are often 50–85 mm (low
  distortion); architectural/environment shots 24–35 mm (wide). A 1024×1024 sheet panel with
  minimal convergence is usually 85 mm or orthographic.
- **Height and tilt.** Eye level ≈ 0.93 × H for a standing character shot; prop shots are
  usually at object mid-height.
- **Framing.** Subject occupies the same fraction of frame; feet near the bottom edge.
- **Light direction.** Match the reference's key from the shading on the form, not from
  guesswork. Note shadow softness and whether there is fill.

Capture rule: **same aspect ratio, same subject fraction, same background value.** A white
background against a dark reference defeats visual comparison.

## Step 2 - decomposition example

Character example (matches a modular kit, T-58):
```
1. Body blockout      — head, torso, hips, limbs as volumes at correct landmark heights
2. Garment layers     — shirt, vest, pants, boots (each offsets the body volume)
3. Equipment          — belt, pouches, backpack, bedroll, axe
4. Hair mass          — the single largest silhouette contributor after the body
5. Materials          — palette + roughness; no albedo detail until Step 5 passes
6. Detail pass        — seams, buckles, straps, wear
```
