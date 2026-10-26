# Artifact symptom tables

Find the group, then the row. Each fix names the cause it removes.

## Aliasing and shimmer

| Symptom | Cause | Fix |
|---|---|---|
| Stair-stepped geometry edges | No geometric AA | MSAA 2×/4× (`msaa_3d`), or TAA/FXAA/SMAA |
| Distant textures crawl/moire | Missing mipmaps or nearest filtering | Mipmaps on import; `filter_linear_mipmap_anisotropic`; raise anisotropic level |
| Sparkling highlights on normal-mapped/metal surfaces | Specular aliasing | Keep the screen-space roughness limiter on; TAA; raise roughness on distant/fine detail |
| Foliage edges crawl in motion | Alpha cutout under MSAA does nothing | Alpha-to-coverage, or TAA; lower cutoff in distant mips |
| Thin wires/fences flicker | Sub-pixel geometry | Thicken, fade out by distance, or replace with alpha card |

## Banding

| Symptom | Cause | Fix |
|---|---|---|
| Stepped rings in sky, fog, dark gradients | 8-bit quantisation | `use_debanding` (Forward+/Mobile, very cheap); dither in shader on Compatibility |
| Bands in volumetric fog | Low froxel resolution | Raise volume size/depth, enable filter, or lower density gradient |

## Shadows

| Symptom | Cause | Fix |
|---|---|---|
| Stripes/dots on lit surfaces (acne) | Bias too low | Raise **normal bias** first, then bias |
| Shadow detached from object base (peter-panning) | Bias too high, or geometry too thin | Lower bias; give walls thickness |
| Blurry, blocky shadows near camera | Shadow distance too far for atlas size | Lower `directional_shadow_max_distance`; tune split 1; larger atlas only for hero views |
| Visible line where shadow quality changes | Cascade seam | `directional_shadow_blend_splits` (costs), or move split so seam falls in fog/clutter |
| Shadows vanish abruptly at distance | Max distance cutoff | `directional_shadow_fade_start`; distant baked AO/lightmap |
| Shadow swims when the camera moves | Cascade not stabilised / too soft filter | Default stable cascades; reduce blur; avoid animating the sun every frame |
| Omni/spot shadows blocky or missing | Positional atlas too small or full | Raise `positional_shadow/atlas_size`, fewer shadowed lights |

## Global illumination and screen-space effects

| Symptom | Cause | Fix |
|---|---|---|
| Light leaks through walls/floors | Walls thinner than GI cell | Thicken walls; SDFGI `sdfgi_use_occlusion`; higher VoxelGI subdivision; LightmapGI for static interiors |
| Walls tinted strongly by grass/floor | Over-saturated albedo | Bring albedo into plausible range; lower GI energy second |
| GI changes as the camera moves far | SDFGI cascade scroll | More cascades/ray count, or hide transitions with fog |
| Dark halos around characters | SSAO radius too large | Smaller radius, lower intensity |
| AO/reflections disappear at screen edge | Screen-space has no off-screen data | Accept, reduce strength, or bake AO / add reflection probes |
| Reflections of the sky inside dark interiors | No local reflection source | `ReflectionProbe` per room |

## Temporal and motion

| Symptom | Cause | Fix |
|---|---|---|
| Trails behind moving objects | TAA ghosting / low frame rate | Higher frame rate, MSAA instead, or FSR2 |
| Whole image soft | TAA/FXAA blur | Sharpening, SMAA, or MSAA |
| Objects jitter at high refresh rates | Physics tick ≠ render rate | Enable physics interpolation (Godot 4.3+ 3D); reset it on teleport |
| Camera judders while target moves smoothly | Camera updated in a different loop than the target | Move both in the same loop, or interpolate the camera |
| LOD/vegetation pops | Hard visibility cutoff | Visibility range fade + margin; transition at equal screen size |

## Geometry and colour

| Symptom | Cause | Fix |
|---|---|---|
| Two surfaces flicker through each other (z-fighting) | Coplanar faces or tiny near plane | Offset/merge faces; raise camera `near` (0.05 → 0.1–0.3) |
| Lighting looks inverted/embossed wrong way | Normal map green channel convention | Godot expects OpenGL (Y+): import with *Normal Map Invert Y* for DirectX maps |
| Custom-shader albedo looks washed out | Colour texture sampled as linear | `source_color` hint on albedo samplers only |
| Roughness/normal maps look wrong | Data texture imported as sRGB | Import data maps as linear / normal map mode |
| Sparkle dots from an HDRI sky | Sun pixels too bright | HDR clamp exposure on import |

## Stutter (hitches with good average FPS)

| Symptom | Cause | Fix |
|---|---|---|
| Hitch the first time an effect/material appears | Shader/pipeline compilation | Godot 4.4+ precompiles pipelines and uses ubershaders: load meshes and materials at load time, not mid-play. Compatibility: show each material/effect for one frame behind the loading screen |
| Hitch on entering an area | Synchronous loading on main thread | `ResourceLoader.load_threaded_request`, preload during transitions |
| Regular spikes every few seconds | Allocations/GC or periodic scripts | Pool objects; spread work across frames |
| Fine in editor, hitches in export | Missing pipeline cache or debug overhead | Test exported release builds; first run after a driver update rebuilds caches |

Always measure **worst-frame time**, not just average FPS. A 60 fps average with 80 ms
spikes plays worse than a steady 45.
