---
name: gamedev-unity-pipeline
description: >
  Wire a Unity 6 project so imported assets land at the right scale, orientation, and
  materials. Use for FBX or glTF import, prefabs, URP or HDRP, and build checks.
license: Apache-2.0
compatibility: Unity 6 (6000.x); URP and HDRP.
metadata:
  engine: unity
  category: gamedev-pipeline
  difficulty: intermediate
---

# Unity pipeline — import settings are the product

Unity's defaults are tuned for its own conventions, not Blender's. Every import is a
conversion, and the conversion is where assets silently break.

## When to use

- Importing Blender assets into Unity.
- Setting up prefabs, materials, URP/HDRP.
- Structuring data with ScriptableObjects.
- Making a project verifiable from the command line.

## Key facts that bite

| Topic | Unity reality |
|---|---|
| Forward axis | Unity is **+Z forward, Y up**; Blender **-Y forward, Z up** |
| FBX axis fix | set "Bake Axis Conversion" on, or export from Blender with `-Z forward, Y up` |
| Units | 1 Unity unit = 1 metre, but **import scale factor** defaults to 1 and files often arrive at 0.01 or 100 |
| Materials | Unity does **not** import Blender node trees; FBX carries only the base color/textures |
| Normals | "Import Normals" vs "Calculate" changes the shading look entirely |
| Scale | a non-1 `Transform.localScale` on a prefab breaks physics, nav and lighting |

## Import checklist

```
[ ] FBX or glTF in Assets/, with the .meta committed
[ ] Model tab (Scene section in Unity 6): Scale Factor 1.0, Convert Units ON, Bake Axis Conversion ON
[ ] Normals: Import (preserve the authored normals)
[ ] Tangents: Calculate Mikktspace
[ ] Materials: extract, then assign a project material (do not use embedded)
[ ] Rig: None for props, Humanoid/Generic for characters
[ ] Animation: clips named, loop time set per clip
[ ] Prefab created with the model as a child, not the root
```

**Verify scale in an empty scene next to a 1x1x1 cube.** An asset that looks right in the
inspector preview can be 100x off in-scene. This is the single most common Unity asset bug.

## Prefab structure

```
Player (root, GameObject)           <- gameplay components, scale 1
├── Body (imported model)           <- visual only, no logic
│   └── Armature
├── Collider (CapsuleCollider)      <- on the root
├── CameraTarget (empty)
└── WeaponMount (empty)             <- attachment point
```

Rules:
- **Gameplay components on the root**, visuals on a child. Never put a Rigidbody on the
  imported model.
- **Scale stays 1** on the root; if the model arrives wrong, fix the import, not the transform.
- **Attachment points are empties**, referenced by scripts — not found by string path at
  runtime.

## Materials

Blender's shader graph does not survive FBX. Expect to rebuild materials in Unity:

```
[ ] base color re-assigned from the sampled palette
[ ] metallic and smoothness set (Lit in URP and HDRP; smoothness = 1 - roughness)
[ ] normal map imported as Normal Map (texture type in the importer)
[ ] textures marked sRGB only for albedo; normal/mask maps NOT sRGB
[ ] shared materials: one material per surface family, not per object
```

That last point is the draw-call lever in Unity. Per-object material instances are the usual
cause of a 400-draw-call scene that should be 60.

## URP vs HDRP vs Built-in

| | Use when | Cost |
|---|---|---|
| URP | almost all stylized/mid-fidelity game work | low, scales to mobile |
| HDRP | photoreal, PC/console target, willing to pay | high, complex |
| Built-in | legacy only | do not start here in Unity 6 |

For the kind of stylized work these skills target, URP is the right default.

## ScriptableObjects for data

Balance numbers, item definitions, enemy stats: ScriptableObjects, not constants in
MonoBehaviours.

```csharp
[CreateAssetMenu(menuName = "Game/Enemy Definition")]
public class EnemyDefinition : ScriptableObject
{
    public string displayName;
    public float maxHealth = 100f;
    public float moveSpeed = 3.5f;
    public float attackDamage = 12f;
    public float attackWindup = 0.6f;
    [Range(0f, 1f)] public float armour = 0.2f;
}
```

Benefits that matter for AI-driven work: designers edit data without touching code, balance
changes diff cleanly in version control, and tests can construct a definition in memory.

**Caveat:** ScriptableObject state persists between play sessions in the editor. Reset runtime
state in `OnEnable` or use a runtime copy, or you will debug a value that "changed by itself".

## Build verification

```
Unity.exe -batchmode -quit -projectPath <path> -logFile build.log -executeMethod BuildScript.Perform
```

```
[ ] exit code 0
[ ] build.log contains no "error CS" or "Build completed with a result of 'Failed'"
[ ] the built player launches (not just the build succeeding)
[ ] assets present at runtime: check the player log for missing-reference warnings
```

Unity's batchmode can report success with a broken player. Always launch the build.

## Common Unity 6 pitfalls

| Symptom | Cause |
|---|---|
| Model 100x too big/small | import Scale Factor |
| Model on its side | Bake Axis Conversion off |
| Pink/magenta materials | shader not compatible with the active render pipeline |
| Everything looks flat | imported material is Built-in Standard into a URP project |
| Physics jitter | non-uniform or non-1 object scale |
| Light leaks | shadow bias, or geometry not marked static |
| NavMesh agents stuck | navmesh not baked for that area, or the agent radius is too large |
| Build works, editor does not (or vice versa) | `#if UNITY_EDITOR` blocks around runtime code |

## Verification checklist

```
[ ] batchmode build exits 0 with clean log
[ ] player launches and loads the scene
[ ] asset scale correct next to a reference cube
[ ] materials are project materials, not embedded
[ ] one full input -> state -> visual loop works in the player
[ ] collision uses simplified shapes
[ ] balance data lives in ScriptableObjects
[ ] no runtime state leaking through ScriptableObject instances
```

## Related

- `gamedev-blender-headless` — the export side, including axis settings
- `gamedev-game-testing` — test structure in Unity
- `gamedev-performance` — draw calls, batching, LOD groups
- `gamedev-lighting` — URP/HDRP light and shadow settings

## Knowledge base

T-09 (scripted pipeline), T-20 (batch CLI with orientation QA), T-06 (instrumented testing).
