# Godot visual polish — per-step settings

Load the section for the step you are on. Property names are Godot 4.x `Environment`,
`DirectionalLight3D` and `Viewport` properties unless stated.

## 1. Sun: direction first, then colour

`DirectionalLight3D`: lower it to **20–40° elevation** and rotate it so the main surfaces the
player looks at have **one lit face and one shaded face**. An overhead sun or a sun behind the
camera lights every visible face equally — that is the flat look. Warm the colour
(e.g. `Color(1.0, 0.85, 0.7)`), then set `light_energy` so the brightest lit surface sits just
under clipping after step 3.

Check: in a greyscale screenshot, two faces of the same building differ clearly in value.

## 2. Sky as the fill light

`background_mode = BG_SKY` with a `ProceduralSkyMaterial` (blue `sky_top_color`, warmer
`sky_horizon_color`), then `ambient_light_source = SKY`. Shaded faces take a cool tint against
the warm sun — warm key, cool fill, no extra lights. Too blue or too bright: lower
`ambient_light_sky_contribution` (below 1.0 blends toward `ambient_light_color`) or
`ambient_light_energy`.

`PhysicalSkyMaterial` for physically driven time of day (slightly more expensive);
`PanoramaSkyMaterial` for an HDRI — enable HDR clamp exposure on import if the HDRI sun
sparkles.

## 3. Tonemapper and exposure

`tonemap_mode`: `LINEAR` clips; `REINHARD` is dull; `FILMIC`/`ACES` contrasty; **`AGX` (4.4+)**
best preserves hue in highlights (no orange→yellow skew). In 4.4 AgX fixes the white point and
suits Mobile poorly; 4.5+ adds AgX white/contrast controls. With Filmic/ACES raise
`tonemap_white` to ~6–8 for bright outdoor scenes.

`tonemap_exposure` applies *before* the curve: change it after choosing the tonemapper.
`adjustment_*` and colour correction (1D gradient or 3D LUT) run *after* tonemapping — grade
there.

## 4. Contact shading

`ssao_enabled`, modest `ssao_radius` (~1 m) and `ssao_intensity`; a little `ssil_enabled` for
short colour bounce. Screen-space: fades at screen edges, changes as objects leave view —
**judge while the camera moves**. Project Settings > Rendering > Environment > SSAO/SSIL
quality and half size are the cost knobs.

## 5. Bounce light

| Need | Choice | Notes |
|---|---|---|
| Static level, baking OK | `LightmapGI` | Cheapest at runtime; Mobile/Compat OK |
| Static geometry, moving lights | `VoxelGI` | Bounded volume; thin walls leak |
| Large/open, dynamic, Forward+ | SDFGI (`sdfgi_enabled`) | Most expensive; `sdfgi_use_occlusion` against leaks; half-res GI |
| Reflections only | `ReflectionProbe` (update Once) | Cheapest; no diffuse bounce |

Albedo discipline: bounce carries surface colour; saturated bright grass tints walls green.
No pure 0 or 1 colour channels; foliage rarely above ~0.6 in any channel.

## 6. Fog

`fog_enabled`; in 4.3+ pick `fog_mode` exponential or depth. Depth fog (`fog_depth_begin`,
`fog_depth_end`, `fog_depth_curve`) layers distance; `fog_aerial_perspective` (needs a sky)
tints far objects with the sky; `fog_sun_scatter` glows toward the sun; height fog
(`fog_height`, `fog_height_density`) for ground mist. Volumetric fog is separate and
expensive (Forward+): Rendering > Environment > Volumetric Fog > Volume Size / Volume Depth.

Fog must not hide the path, enemies or pickups.

## 10. Character fill and practical lights

`OmniLight3D` on the player with `light_cull_mask` limited to the character's render layer.
Lanterns as `OmniLight3D` (shadows off unless hero), emissive window materials, fires. Every
light has a visible source.

## 11. Camera

Narrower FOV pulled back flattens perspective; far DOF via `CameraAttributesPractical`. Both
change gameplay visibility — A/B them separately from lighting.

## 12. Finishing

AA by artifact (see `presets.md`), `use_debanding` (cheap; sky/fog bands), subtle
vignette/grain/dust. Godot has no built-in vignette or grain: full-screen `ColorRect` shader on
a `CanvasLayer`, or a `CompositorEffect`. Noticeable at a glance = too strong.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Lots of effects, still flat | Sun overhead or behind camera | Step 1 first |
| Shadows navy blue | Sky contribution too strong | Lower `ambient_light_sky_contribution` / energy |
| Orange sun turns yellow-white | Filmic/ACES hue skew | AgX, or lower exposure |
| Walls tinted green | Saturated albedo + GI | Desaturate albedo, then lower GI energy |
| Pretty still, ugly in motion | Screen-space effects judged from stills | Judge SSAO/SSIL/SSR moving |
| "Optimised" but still slow | Measured capped FPS | vsync off, measure ms |
| Path vanishes in mist | Height fog dense near ground | Raise `fog_height` / lower density |
| Setting has no effect | Renderer lacks the feature | Renderer table in SKILL.md |
