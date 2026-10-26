# Leave-one-out cost attribution for Godot 4 graphics settings.
#
# Attach to any Node in the scene to measure, assign the exports, run the scene.
# For each viewpoint and each enabled setting it renders the full scene and then the scene
# with that one setting off, back to back (paired, so slow drift - streaming, clocks, a camera
# still easing - cancels out). A final extra full run gives the noise floor for both timing
# and screenshots. Records mean/worst GPU and CPU render time and a screenshot per run,
# writes ablation.json next to the screenshots and quits.
# Feed the folder to tools/godot/ablation_report.py.
#
# Override the output folder from the command line: godot --path . -- --ablation-out=C:/tmp/abl
# Measure in a release export or with the editor closed for trustworthy CPU numbers.
# Rendering must be real: --headless uses a dummy renderer and records nothing.
extends Node

@export var world_env: WorldEnvironment
@export var sun: DirectionalLight3D
@export var camera: Camera3D
## Camera is pinned to each marker every frame while measuring (overrides camera rigs).
@export var viewpoints: Array[Node3D] = []
@export var extra_nodes_to_toggle: Array[Node3D] = []
## Hide every CanvasLayer so UI fades do not pollute the screenshot comparison.
@export var hide_ui := true
@export var warmup_frames := 90
@export var sample_frames := 180
@export var out_dir := "user://ablation"

var _vp_rid: RID
var _pin: Variant = null


func _ready() -> void:
	process_priority = 10000
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ablation-out="):
			out_dir = arg.trim_prefix("--ablation-out=")
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	_vp_rid = get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(_vp_rid, true)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))
	if hide_ui:
		for n in get_tree().root.find_children("*", "CanvasLayer", true, false):
			(n as CanvasLayer).visible = false
	await _run()
	get_tree().quit()


func _process(_delta: float) -> void:
	if _pin != null and camera:
		camera.global_transform = _pin


func _toggles() -> Array:
	var env: Environment = world_env.environment if world_env else null
	var vp := get_viewport()
	var t := [
		{"name": "sun_shadows", "obj": sun, "prop": "shadow_enabled", "off": false},
		{"name": "ssao", "obj": env, "prop": "ssao_enabled", "off": false},
		{"name": "ssil", "obj": env, "prop": "ssil_enabled", "off": false},
		{"name": "sdfgi", "obj": env, "prop": "sdfgi_enabled", "off": false},
		{"name": "ssr", "obj": env, "prop": "ssr_enabled", "off": false},
		{"name": "glow", "obj": env, "prop": "glow_enabled", "off": false},
		{"name": "fog", "obj": env, "prop": "fog_enabled", "off": false},
		{"name": "volumetric_fog", "obj": env, "prop": "volumetric_fog_enabled", "off": false},
		{"name": "msaa_3d", "obj": vp, "prop": "msaa_3d", "off": Viewport.MSAA_DISABLED},
		{"name": "screen_space_aa", "obj": vp, "prop": "screen_space_aa", "off": Viewport.SCREEN_SPACE_AA_DISABLED},
		{"name": "taa", "obj": vp, "prop": "use_taa", "off": false},
	]
	for n in extra_nodes_to_toggle:
		if n:
			t.append({"name": "node_" + n.name, "obj": n, "prop": "visible", "off": false})
	return t.filter(func(e): return e["obj"] != null and e["obj"].get(e["prop"]) != e["off"])


func _measure(label: String, view_index: int) -> Dictionary:
	for i in warmup_frames:
		await get_tree().process_frame
	var gpu := 0.0
	var cpu := 0.0
	var worst := 0.0
	for i in sample_frames:
		await RenderingServer.frame_post_draw
		var g := RenderingServer.viewport_get_measured_render_time_gpu(_vp_rid)
		gpu += g
		cpu += RenderingServer.viewport_get_measured_render_time_cpu(_vp_rid)
		worst = maxf(worst, g)
	var shot := "v%d_%s.png" % [view_index, label]
	get_viewport().get_texture().get_image().save_png(out_dir.path_join(shot))
	return {
		"gpu_ms": gpu / sample_frames,
		"cpu_ms": cpu / sample_frames,
		"gpu_worst_ms": worst,
		"shot": shot,
	}


func _run() -> void:
	var toggles := _toggles()
	var views: Array = viewpoints.duplicate() if not viewpoints.is_empty() else [null]
	var report := {
		"format": 2,
		"godot": Engine.get_version_info()["string"],
		"renderer": ProjectSettings.get_setting("rendering/renderer/rendering_method"),
		"adapter": RenderingServer.get_video_adapter_name(),
		"resolution": [get_viewport().size.x, get_viewport().size.y],
		"toggles": toggles.map(func(e): return e["name"]),
		"views": [],
	}
	for vi in views.size():
		_pin = views[vi].global_transform if views[vi] else null
		var view := {}
		for e in toggles:
			var name: String = e["name"]
			view["full@" + name] = await _measure("full_for_" + name, vi)
			var original = e["obj"].get(e["prop"])
			e["obj"].set(e["prop"], e["off"])
			view["-" + name] = await _measure("minus_" + name, vi)
			e["obj"].set(e["prop"], original)
			print("view %d %s: full %.3f -> off %.3f ms GPU" % [vi, name, view["full@" + name]["gpu_ms"], view["-" + name]["gpu_ms"]])
		view["full"] = await _measure("full", vi)
		view["full_end"] = await _measure("full_end", vi)
		print("view %d full %.3f / again %.3f ms GPU (difference = noise floor)" % [vi, view["full"]["gpu_ms"], view["full_end"]["gpu_ms"]])
		report["views"].append(view)
	_pin = null
	var f := FileAccess.open(out_dir.path_join("ablation.json"), FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "  "))
	f.close()
	print("ablation written to ", ProjectSettings.globalize_path(out_dir))
