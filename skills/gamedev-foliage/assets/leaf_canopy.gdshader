// Canopy (radial) normals + vertex-colour-weighted wind for alpha-cutout leaf cards.
// COLOR.r: 0 trunk/branch base .. 1 outer leaves. Orbit the tree to verify back faces.
shader_type spatial;
render_mode cull_disabled;

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic;
uniform float alpha_cutoff : hint_range(0.0, 1.0) = 0.5;
uniform vec3 canopy_center = vec3(0.0, 4.0, 0.0);   // object space
uniform vec3 canopy_radii = vec3(2.5, 2.0, 2.5);    // ellipsoid
uniform float radial_blend : hint_range(0.0, 1.0) = 0.85;
uniform sampler2D wind_noise : filter_linear_mipmap, repeat_enable;
uniform vec2 wind_dir = vec2(1.0, 0.3);
uniform float wind_strength = 0.08;
uniform float wind_speed = 0.05;

void vertex() {
	vec3 radial = normalize((VERTEX - canopy_center) / canopy_radii);
	NORMAL = normalize(mix(NORMAL, radial, radial_blend));

	vec3 world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float gust = textureLod(wind_noise, world.xz * 0.02 + wind_dir * TIME * wind_speed, 0.0).r;
	float weight = COLOR.r;                       // 0 = trunk/branch base, 1 = outer leaves
	VERTEX.xz += normalize(wind_dir) * (gust - 0.5) * 2.0 * wind_strength * weight;
	VERTEX.y += sin(TIME * 2.3 + world.x + world.z) * 0.01 * weight;
}

void fragment() {
	vec4 tex = texture(albedo_tex, UV);
	ALBEDO = tex.rgb;
	ALPHA = tex.a;
	ALPHA_SCISSOR_THRESHOLD = alpha_cutoff;
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
