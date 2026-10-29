import json

import numpy as np
from PIL import Image

import ablation_report
import compare
import palette_report
import tile_seam_check
import uv_density


def test_uv_density_is_linear_px_per_m(tmp_path):
    # 2 m x 2 m quad (4 m^2) using a 0.5 x 0.5 UV square (0.25 of the atlas)
    obj = tmp_path / "q.obj"
    obj.write_text(
        "v 0 0 0\nv 2 0 0\nv 2 2 0\nv 0 2 0\n"
        "vt 0 0\nvt 0.5 0\nvt 0.5 0.5\nvt 0 0.5\n"
        "f 1/1 2/2 3/3 4/4\n")
    rep = uv_density.report(obj, texel=512)
    # 512 px * 0.5 uv across 2 m = 128 px/m
    assert abs(rep["min_texel_density"] - 128.0) < 0.01


def test_uv_density_scales_linearly_with_texel(tmp_path):
    obj = tmp_path / "q.obj"
    obj.write_text("v 0 0 0\nv 1 0 0\nv 1 1 0\nvt 0 0\nvt 1 0\nvt 1 1\nf 1/1 2/2 3/3\n")
    a = uv_density.report(obj, texel=256)["min_texel_density"]
    b = uv_density.report(obj, texel=512)["min_texel_density"]
    assert abs(b / a - 2.0) < 1e-6


def test_letterbox_color_and_mask_align(tmp_path):
    # wide image: white 40x20 block on black, 200x100
    arr = np.zeros((100, 200, 3), dtype=np.uint8)
    arr[40:60, 80:120] = 255
    p = tmp_path / "wide.png"
    Image.fromarray(arr).save(p)
    size = (128, 128)
    rgb = compare.load_rgb(p, size)
    mask = compare.mask_at_native(p, size)
    lum = rgb.mean(axis=2)
    ys, xs = np.where(mask)
    assert len(ys) > 0
    # every masked pixel is bright in the colour image, and the centroids agree
    assert lum[mask].mean() > 0.8
    bright = lum > 0.5
    assert abs(ys.mean() - np.where(bright)[0].mean()) < 1.5
    assert abs(xs.mean() - np.where(bright)[1].mean()) < 1.5


def test_normalize_mask_wide_subject_not_squeezed():
    mask = np.zeros((100, 400), dtype=bool)
    mask[20:60, 10:390] = True  # 380 wide x 40 tall
    out = compare.normalize_mask(mask, (256, 256))
    ys, xs = np.where(out)
    w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    assert w >= 250
    assert abs(w / h - 380 / 40) < 0.6


def _write_ablation(folder, shots, toggles):
    for name, val in shots.items():
        Image.fromarray(np.full((16, 16, 3), val, dtype=np.uint8)).save(folder / name)
    view = {
        "full": {"gpu_ms": 10.0, "shot": "full.png"},
        "full_end": {"gpu_ms": 10.0, "shot": "full.png"},
    }
    view.update(toggles)
    (folder / "ablation.json").write_text(json.dumps({"toggles": ["a", "b", "c"], "views": [view]}))


def test_ablation_verdicts(tmp_path):
    _write_ablation(
        tmp_path,
        {"full.png": 100, "changed.png": 200},
        {
            "-a": {"gpu_ms": 9.8, "shot": "changed.png"},  # 0.2 ms, visible
            "-b": {"gpu_ms": 9.8, "shot": "full.png"},     # 0.2 ms, invisible
            "-c": {"gpu_ms": 9.5, "shot": "full.png"},     # 0.5 ms, invisible
        })
    _, rows, _ = ablation_report.analyse(tmp_path, 0.1, 0.3)
    verdicts = {r["setting"]: r["verdict"] for r in rows}
    assert verdicts == {"a": "earns", "b": "invisible", "c": "CUT?"}


def test_ablation_corrupt_json_exits_2(tmp_path, monkeypatch):
    (tmp_path / "ablation.json").write_text("{not json")
    monkeypatch.setattr("sys.argv", ["ablation_report.py", "--dir", str(tmp_path)])
    assert ablation_report.main() == 2


def test_flat_tile_is_seamless(tmp_path):
    p = tmp_path / "flat.png"
    Image.fromarray(np.full((32, 32, 3), 128, dtype=np.uint8)).save(p)
    assert tile_seam_check.assess(p)["seamless"]


def test_flat_interior_with_seam_fails(tmp_path):
    arr = np.full((32, 32, 3), 40, dtype=np.uint8)
    arr[:, -1] = 220
    p = tmp_path / "seam.png"
    Image.fromarray(arr).save(p)
    assert not tile_seam_check.assess(p)["seamless"]


def test_hex_to_rgb_shorthand():
    assert palette_report.hex_to_rgb("#fff") == (1.0, 1.0, 1.0)
    assert palette_report.hex_to_rgb("#f00") == palette_report.hex_to_rgb("#ff0000")
