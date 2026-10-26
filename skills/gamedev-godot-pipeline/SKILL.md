---
name: gamedev-godot-pipeline
description: >
  Wire a Godot 4.x project: scene/node structure, exported scenes and resources, import
  settings for 3D assets, autoloads, input map and headless verification. Use when the
  target engine is Godot and assets must arrive intact and run.
license: Apache-2.0
compatibility: Godot 4.2+ (4.3/4.4 differences noted).
metadata:
  engine: godot
  category: gamedev-pipeline
  difficulty: intermediate
---

# Godot pipeline — assets that survive the trip

Most Godot problems are import problems, not engine problems. Get the import right and the
rest is ordinary scene work.

## When to use

- Importing 3D assets (from Blender) into a Godot project.
- Setting up scene structure, autoloads, input map.
- Making a project verifiable headless.
- Godot 4.x specifics that differ from older tutorials.

## Key facts that bite

| Topic | Godot 4.x reality |
|---|---|
| Forward axis | glTF imports with **+Z forward**; Blender's -Y forward maps correctly if exported as glTF with default settings |
| Units | 1 Godot unit = 1 metre; verify, do not assume |
| Coordinate system | right-handed, **Y up** (Blender is Z up; the glTF exporter handles it) |
| Materials | imported as `StandardMaterial3D` from glTF PBR; check roughness/metallic survived |
| Scale | an object with a non-1 import scale fights physics and cameras — apply it |
| Resources | `.tscn` scenes, `.tres` resources, both text and diffable — prefer them to binary |

## Import checklist for a 3D asset

```
[ ] file in res:// with a sensible path (res://assets/<category>/<name>.glb)
[ ] .import file committed alongside (it holds the settings)
[ ] import scale = 1.0, object scales applied in Blender
[ ] the mesh appears at the expected size in a fresh scene (compare to a 1 m cube)
[ ] origin at the ground, so placing it on y=0 works
[ ] materials: base color, roughness, metallic present; textures linked
[ ] animation clips named and listed
[ ] collision added where needed (Godot does not generate it for you)
```

**Always verify in a fresh scene**, not in the import preview. Preview uses different
lighting and framing, and an asset can look correct there and be 100x too large in-scene.

## Node structure that scales

```
Main (Node3D)
├── World (Node3D)
│   ├── NavigationRegion3D
│   ├── Geometry (Node3D)
│   └── Props (Node3D)
├── Player (CharacterBody3D)
│   ├── CollisionShape3D
│   ├── Model (Node3D)          # the imported visual
│   └── CameraRig (Node3D)
├── Systems (Node)
│   ├── GameState
│   └── Spawner
└── UI (CanvasLayer)
```

Rules:
- **Separate the visual model from the physics body.** The model is a child; never make the
  imported scene the `CharacterBody3D` itself.
- **Systems are nodes, not globals** where possible, so they can be disabled in tests.
- **Autoloads for truly global state only** (settings, save, event bus). Autoload sprawl makes
  headless testing impossible.

## Input map

Define actions in Project Settings > Input Map, never read raw keys in gameplay code.

```
move_forward, move_back, move_left, move_right  -> WASD / arrows / left stick
jump, attack, interact, sprint, pause
```

Gameplay code:

```gdscript
var dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
```

This makes rebinding, controller support and automated tests all work without touching
gameplay code.

## Materials and roughness

glTF carries PBR values. Verify after import:

```gdscript
for child in model.find_children("*", "MeshInstance3D", true, false):
    for i in child.mesh.get_surface_count():
        var m := child.get_active_material(i)
        print("%s[%d] %s rough=%.2f metal=%.2f" % [
            child.name, i, m.resource_name if m else "<none>",
            m.roughness if m else -1.0, m.metallic if m else -1.0])
```

If roughness reads 1.0 everywhere, the map did not survive — usually a missing texture path or
an unpacked image.

## Headless verification

```
godot --headless --path . --quit-after 2
godot --headless --path . --script res://tests/smoke.gd
```

`--quit-after 2` runs two frames then exits; enough to catch boot-time errors. `--script` runs
an arbitrary `SceneTree`/`MainLoop` script for real assertions.

Always parse the output — exit code 0 does not mean clean:

```python
import subprocess, sys
p = subprocess.run([GODOT, "--headless", "--path", ".", "--quit-after", "2"],
                   capture_output=True, text=True, timeout=120)
out = p.stdout + p.stderr
errors = [l for l in out.splitlines() if "ERROR" in l or "SCRIPT ERROR" in l]
if p.returncode != 0 or errors:
    print("\n".join(errors[:20]) or out[-2000:])
    sys.exit(1)
```

## Physics and collision

Godot does not generate collision from a visual mesh. For each imported asset:

- **Static props**: `StaticBody3D` + a simplified collision shape (box, capsule, or a
  decimated convex hull, never the render mesh).
- **Characters**: `CharacterBody3D` + a capsule, with the model as a child.
- **Interactables**: an `Area3D` sized to the interaction range.

Using the render mesh as a collision shape is the most common cause of mystery physics cost.

## Common Godot 4 pitfalls

| Symptom | Cause |
|---|---|
| Model is tiny/huge | import scale, or unapplied object scale in Blender |
| Model lies on its side | wrong exporter axis setting |
| Character falls through floor | collision layer/mask mismatch, or no collision shape |
| Materials all grey | textures not imported, or paths broken after a move |
| Works in editor, fails headless | dependency on editor-only state or `@tool` assumptions |
| Signals do nothing | connected to a renamed/removed node |
| Navigation unused | navmesh not baked, or region not set to the right layer |
| Animation not playing | clip name mismatch, or the AnimationPlayer is on a different node |

## Verification checklist

```
[ ] project boots headless with exit 0 and no ERROR lines
[ ] asset appears at correct scale next to a 1 m reference cube
[ ] origin at ground: placing at y=0 stands it on the floor
[ ] materials show expected color/roughness
[ ] one full input -> state -> visual loop runs
[ ] collision present and cheaper than the render mesh
[ ] input actions defined, not raw keys
[ ] no autoload required for basic testing
```

## Related

- `gamedev-blender-headless` — the export side
- `gamedev-locomotion` — the movement code that runs here
- `gamedev-game-testing` — headless test structure
- `gamedev-performance` — budgets measured in this engine
- `gamedev-godot-visual-polish` — environment, lighting and post once the scene is wired
- `gamedev-visual-artifacts` — shimmer, acne, leaks, shader hitches

## Knowledge base

T-09 (scripted pipeline), T-20 (batch CLI with orientation QA), T-06 (instrumented testing).
