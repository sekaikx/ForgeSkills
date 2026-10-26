"""Rank Godot graphics settings by frame-time cost against how much they change the image.

Reads ablation.json and screenshots written by tools/godot/ablation_capture.gd.

Each "setting off" run is paired with a full run captured just before it, so slow drift
cancels. Noise floor: two back-to-back full runs per view; their difference (GPU ms and image
change) is what the scene does on its own - wind, particles, clocks. Every setting's numbers
are judged against it.

For each setting:
  cost      = mean over views of (paired full GPU ms - GPU ms with the setting off)
  visible   = image change with the setting off, minus the noise floor (worst view);
              mean absolute luminance difference (0-255) and % of pixels changed by > 8
Verdicts:
  noise     |cost| within the timing noise floor; measure longer before deciding
  CUT?      costs >= --expensive-ms but changes almost nothing   -> reduce or remove first
  earns     visible change justifies the cost
  cheap     costs < --cheap-ms and visibly helps
  invisible cheap and changes nothing; delete for clarity

Usage:
  python tools/godot/ablation_report.py --dir <ablation folder> [--budget-ms 16.6] [--strict] [--json]

Exit 1 when the full scene exceeds --budget-ms at any view, or with --strict when any setting
is CUT?. Exit 2 on unreadable input.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PIXEL_DELTA = 8
INVISIBLE_MEAN = 0.5
INVISIBLE_PCT = 1.0


def luminance(path):
    img = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    return img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def image_change(a_path, b_path):
    a, b = luminance(a_path), luminance(b_path)
    if a.shape != b.shape:
        raise SystemExit(f"screenshot sizes differ: {a_path} {a.shape} vs {b_path} {b.shape}")
    d = np.abs(a - b)
    return float(d.mean()), float((d > PIXEL_DELTA).mean() * 100.0)


def view_baseline(folder, v):
    """Full-scene GPU ms and noise floors for one view."""
    start = v["full"]
    end = v.get("full_end")
    if end is None:
        return start["gpu_ms"], 0.0, (0.0, 0.0), [start["shot"]]
    noise_vis = image_change(folder / start["shot"], folder / end["shot"])
    return ((start["gpu_ms"] + end["gpu_ms"]) / 2.0, abs(start["gpu_ms"] - end["gpu_ms"]),
            noise_vis, [start["shot"], end["shot"]])


def analyse(folder, cheap_ms, expensive_ms):
    data = json.loads((folder / "ablation.json").read_text(encoding="utf-8"))
    views = data.get("views") or []
    if not views:
        raise SystemExit("ablation.json has no views - nothing was measured")
    bases = [view_baseline(folder, v) for v in views]
    rows = []
    for name in data.get("toggles", []):
        key = "-" + name
        costs, noises, means, pcts = [], [], [], []
        for v, (full_ms, noise_ms, (nm, npct), refs) in zip(views, bases):
            if key not in v:
                continue
            paired = v.get("full@" + name)
            if paired is not None:
                full_ms, refs = paired["gpu_ms"], [paired["shot"]]
            costs.append(full_ms - v[key]["gpu_ms"])
            noises.append(noise_ms)
            changes = [image_change(folder / r, folder / v[key]["shot"]) for r in refs]
            m, p = min(changes)
            means.append(max(0.0, m - nm))
            pcts.append(max(0.0, p - npct))
        if not costs:
            continue
        cost, noise = float(np.mean(costs)), float(np.mean(noises))
        mean_d, pct = max(means), max(pcts)
        invisible = mean_d < INVISIBLE_MEAN and pct < INVISIBLE_PCT
        if abs(cost) <= noise:
            verdict = "noise"
        elif invisible and cost >= expensive_ms:
            verdict = "CUT?"
        elif cost < cheap_ms:
            verdict = "invisible" if invisible else "cheap"
        else:
            verdict = "earns"
        rows.append({
            "setting": name,
            "cost_ms": round(cost, 3),
            "noise_ms": round(noise, 3),
            "cost_ms_per_view": [round(c, 3) for c in costs],
            "luma_delta_over_noise": round(mean_d, 2),
            "pct_pixels_over_noise": round(pct, 1),
            "verdict": verdict,
        })
    rows.sort(key=lambda r: -r["cost_ms"])
    summary = [{"full_gpu_ms": round(b[0], 3), "noise_ms": round(b[1], 3),
                "noise_luma": round(b[2][0], 2), "noise_pct": round(b[2][1], 1),
                "worst_gpu_ms": round(v["full"].get("gpu_worst_ms", v["full"]["gpu_ms"]), 3)}
               for v, b in zip(views, bases)]
    return data, rows, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True, help="folder with ablation.json and screenshots")
    ap.add_argument("--budget-ms", type=float, help="GPU frame budget for the full scene")
    ap.add_argument("--cheap-ms", type=float, default=0.1)
    ap.add_argument("--expensive-ms", type=float, default=0.3)
    ap.add_argument("--strict", action="store_true", help="exit 1 if any setting is CUT?")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    folder = Path(a.dir)
    if not (folder / "ablation.json").exists():
        print(f"no ablation.json in {folder}", file=sys.stderr)
        return 2
    data, rows, summary = analyse(folder, a.cheap_ms, a.expensive_ms)

    if a.json:
        print(json.dumps({"meta": {k: data.get(k) for k in ("godot", "renderer", "adapter", "resolution")},
                          "views": summary, "settings": rows}, indent=2))
    else:
        print(f"Godot {data.get('godot')}  renderer {data.get('renderer')}  "
              f"{data.get('adapter')}  {data.get('resolution')}")
        for i, s in enumerate(summary):
            print(f"view {i}: full {s['full_gpu_ms']:.3f} ms GPU (worst {s['worst_gpu_ms']:.3f}), "
                  f"noise floor {s['noise_ms']:.3f} ms, {s['noise_luma']:.2f} luma / {s['noise_pct']:.1f}% px")
        print()
        print(f"{'SETTING':<22}{'COST ms':>9}{'NOISE':>8}{'LUMA d':>9}{'PX %':>8}   VERDICT")
        print("-" * 68)
        for r in rows:
            print(f"{r['setting']:<22}{r['cost_ms']:>9.3f}{r['noise_ms']:>8.3f}"
                  f"{r['luma_delta_over_noise']:>9.2f}{r['pct_pixels_over_noise']:>8.1f}   {r['verdict']}")
        print("-" * 68)
        cut = [r["setting"] for r in rows if r["verdict"] == "CUT?"]
        print("expensive and invisible: " + (", ".join(cut) if cut else "none"))
        print("visual change is net of the noise floor; leave-one-out costs of interacting settings do not sum")

    status = 0
    worst_full = max(s["full_gpu_ms"] for s in summary)
    if a.budget_ms is not None and worst_full > a.budget_ms:
        print(f"FAIL: full scene {worst_full:.3f} ms > budget {a.budget_ms} ms", file=sys.stderr)
        status = 1
    if a.strict and any(r["verdict"] == "CUT?" for r in rows):
        status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
