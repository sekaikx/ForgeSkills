# Quality presets and cost knobs

Presets change **quality knobs only**. Sun angle, palette, fog colour and grade stay
identical across presets — otherwise Low is a different art direction, not a cheaper one.

## Presence vs quality

| Effect | Presence (keep) | Quality knobs (reduce first) |
|---|---|---|
| Sun | direction, colour, energy | `directional_shadow_mode` 4→2 splits; `directional_shadow_max_distance` to gameplay need (default 100); `directional_shadow_blend_splits` off; Project Settings `lights_and_shadows/directional_shadow/size` 4096→2048; `soft_shadow_filter_quality` Soft Low or Hard |
| SSAO / SSIL | enabled | quality level, half size |
| SDFGI | enabled | fewer cascades, half resolution, lower probe ray count, frames to converge |
| Fog | depth fog | volumetric off, or smaller volume size/depth |
| AA | some AA | MSAA 4×→2×; TAA→FXAA/SMAA on Low |
| Ground cover | near-camera grass | density, visibility range end, shadows off |
| Omni/spot lights | the light | shadows off; `positional_shadow/atlas_size` |

## Preset table

| Knob (runtime API) | Low | Medium | High |
|---|---|---|---|
| Shadow atlas (`RenderingServer.directional_shadow_atlas_set_size`) | 1024 | 2048 | 4096 |
| Soft shadows (`RenderingServer.directional_soft_shadow_filter_set_quality`) | Hard | Soft Low | Soft Medium |
| Shadow splits / max distance | 2 / 40 m | 2 / 80 m | 4 / 120 m |
| SSAO / SSIL | off / off | on, half / off | on / on |
| GI | Lightmap or probe | SDFGI half-res | SDFGI |
| AA (`Viewport.msaa_3d`, `screen_space_aa`, `use_taa`) | FXAA | MSAA 2× | MSAA 4× or TAA |
| Grass visibility end | 25 m | 50 m | 80 m |
| Volumetric fog | off | off | on |

## AA by artifact

- MSAA: geometry edges only; add alpha-to-coverage for foliage cutouts.
- TAA (Forward+): fixes specular and alpha shimmer; blurs and ghosts at low frame rates.
- FXAA: cheapest, soft. SMAA (4.5+): between FXAA and TAA.
- FSR2 at native scale: sharper than TAA, more expensive.
- Debanding: nearly free, fixes gradient steps; not on Compatibility.
