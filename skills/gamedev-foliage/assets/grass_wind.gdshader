// Ground-cover grass: root-to-tip colour, wind bend weighted by tip^2, normals bent up.
// COLOR.r: 0 at root .. 1 at tip. Use on a MultiMesh with cast_shadow off.
shader_type spatial;
render_mode cull_disabled;

uniform vec3 root_color : source_color = vec3(0.18, 0.32, 0.10);
uniform vec3 tip_color : source_color = vec3(0.45, 0.62, 0.22);
uniform sampler2D wind_noise : filter_linear_mipmap, repeat_enable;
uniform vec2 wind_dir = vec2(1.0, 0.2);
uniform float wind_speed = 0.06;
uniform float bend = 0.25;

varying float tip;

void vertex() {
	tip = COLOR.r;                                  // 0 at root, 1 at tip
	vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float gust = textureLod(wind_noise, world.xz * 0.03 + wind_dir * TIME * wind_speed, 0.0).r;
	VERTEX.xz += normalize(wind_dir) * (gust - 0.4) * bend * tip * tip;
	NORMAL = normalize(mix(NORMAL, vec3(0.0, 1.0, 0.0), 0.7));
}

void fragment() {
	ALBEDO = mix(root_color, tip_color, tip);
}
