"""
Reference comparison metrics.

Computes the numbers the reconstruction skill requires:
  - silhouette IoU and per-band width profile
  - subject bounding box match
  - dominant-cluster palette delta-E
  - luminance histogram correlation
  - SSIM / RMSE (advisory only)

Usage:
    python compare.py --ref reference.png --test render.png --out report.json
    python compare.py --ref a.png --test b.png --bands 10 --json

Requires: Pillow, numpy.  SSIM is implemented locally (no scikit-image needed).
"""

import argparse
import json
import math
import sys

import numpy as np
from PIL import Image


# ---------------------------------------------------------------- image loading

def load_rgb(path, size=None):
    im = Image.open(path).convert("RGB")
    if size is not None:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def _quad_basis(h, w):
    """Normalized quadratic basis over the image plane: [1, x, y, x^2, xy, y^2]."""
    y, x = np.mgrid[0:h, 0:w]
    x = x / max(1, w - 1) * 2.0 - 1.0
    y = y / max(1, h - 1) * 2.0 - 1.0
    return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], axis=-1)


def background_fit_mask(rgb, tol=0.055, border_frac=0.05, min_area_frac=0.004):
    """Segment the subject by subtracting a fitted backdrop surface.

    A single median background color fails on any panel with a gradient or a
    lighting falloff — the gradient itself gets flagged as subject and the
    bounding box explodes to the whole frame. Fitting a quadratic surface to the
    border pixels models the gradient, so only real subject pixels survive.
    """
    h, w, _ = rgb.shape
    bw = max(2, int(min(h, w) * border_frac))
    ring = np.zeros((h, w), dtype=bool)
    ring[:bw, :] = ring[-bw:, :] = True
    ring[:, :bw] = ring[:, -bw:] = True

    basis = _quad_basis(h, w)                      # (h, w, 6)
    A = basis[ring]                                # (n, 6)
    resid = np.zeros((h, w), dtype=np.float32)
    for ch in range(3):
        b = rgb[..., ch][ring]
        coef, *_ = np.linalg.lstsq(A, b, rcond=None)
        fitted = basis @ coef                      # (h, w)
        resid += (rgb[..., ch] - fitted) ** 2
    resid = np.sqrt(resid)                          # RGB distance from backdrop

    mask = resid > tol
    # close pinholes
    pad = np.pad(mask, 1, mode="edge")
    acc = np.zeros_like(mask, dtype=np.int8)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            acc += pad[dy:dy + h, dx:dx + w]
    mask = acc >= 5
    return largest_components(mask, min_area_frac)


def flood_background_mask(rgb, step_tol=0.030, drift_tol=0.10, min_area_frac=0.002):
    """Segment by flood-filling the backdrop from the borders.

    Thresholding against a fitted background fails whenever the backdrop carries a
    gradient, a vignette, or film grain: parts of the backdrop exceed the tolerance
    and get classified as subject, which inflates the bounding box and destroys
    every proportion metric downstream.

    Flood fill is connectivity-based instead. Starting at the border, a pixel joins
    the background if it is within `step_tol` of its already-accepted neighbour AND
    within `drift_tol` of the border's own colour. Smooth gradients pass; a hard
    edge onto the subject stops the fill. This is the robust option for concept
    panels, and it needs no scipy.
    """
    h, w, _ = rgb.shape
    border_idx = []
    for x in range(w):
        border_idx.append((0, x))
        border_idx.append((h - 1, x))
    for y in range(h):
        border_idx.append((y, 0))
        border_idx.append((y, w - 1))

    seed = np.median(np.array([rgb[y, x] for y, x in border_idx]), axis=0)

    bg = np.zeros((h, w), dtype=bool)
    stack = []
    for y, x in border_idx:
        if not bg[y, x]:
            bg[y, x] = True
            stack.append((y, x))

    while stack:
        y, x = stack.pop()
        cur = rgb[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if ny < 0 or ny >= h or nx < 0 or nx >= w or bg[ny, nx]:
                continue
            nxt = rgb[ny, nx]
            if (np.linalg.norm(nxt - cur) <= step_tol
                    and np.linalg.norm(nxt - seed) <= drift_tol):
                bg[ny, nx] = True
                stack.append((ny, nx))

    mask = ~bg
    # drop specks of grain that survived away from the subject mass
    return largest_components(mask, min_area_frac)


def subject_mask(rgb, bg_tol=0.055, border_frac=0.02, min_area_frac=0.004, alpha=None,
                 method="flood"):
    """Foreground mask.

    Prefers an exact alpha channel when supplied (a transparent render is ground
    truth). Otherwise flood-fills the backdrop from the border, which survives
    gradients that defeat a colour threshold.
    """
    if alpha is not None:
        return largest_components(alpha > 0.5, min_area_frac)
    if method == "fit":
        return background_fit_mask(rgb, tol=bg_tol, min_area_frac=min_area_frac)
    return flood_background_mask(rgb, min_area_frac=min_area_frac)


def largest_components(mask, min_area_frac=0.004):
    """Keep connected components above a size threshold. Pure numpy, no scipy."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    out = np.zeros_like(mask, dtype=bool)
    min_area = max(16, int(mask.sum() * min_area_frac))
    ys, xs = np.where(mask)
    visited = np.zeros((h, w), dtype=bool)
    for sy, sx in zip(ys, xs):
        if visited[sy, sx]:
            continue
        cur += 1
        stack = [(sy, sx)]
        visited[sy, sx] = True
        comp = []
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        if len(comp) >= min_area:
            for y, x in comp:
                out[y, x] = True
            lab_arr = comp
    return out


def normalize_mask(mask, size=(512, 512)):
    """Crop to the tight subject box, then scale by HEIGHT and center horizontally.

    Resizing straight to a square stretches aspect ratio, which destroys the
    meaning of the width profile: a tall thin figure would report near-full width
    at every band. Scale isotropically on height so band widths stay physical.
    """
    box = tight_crop(mask)
    if box is None:
        return np.zeros((size[1], size[0]), dtype=bool)
    y0, y1, x0, x1 = box
    sub = mask[y0:y1, x0:x1]
    h, w = sub.shape
    target_h, target_w = size[1], size[0]
    scale = target_h / max(1, h)
    new_w = max(1, min(target_w, int(round(w * scale))))
    im = Image.fromarray((sub * 255).astype(np.uint8)).resize((new_w, target_h), Image.LANCZOS)
    arr = np.asarray(im) > 127
    out = np.zeros((target_h, target_w), dtype=bool)
    left = (target_w - new_w) // 2
    out[:, left:left + new_w] = arr
    return out


def tight_crop(mask):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


# ---------------------------------------------------------------- core metrics

def silhouette_iou(mask_a, mask_b):
    inter = np.logical_and(mask_a, mask_b).sum()
    union = np.logical_or(mask_a, mask_b).sum()
    return float(inter / union) if union else 0.0


def band_widths(mask, bands=10):
    """Width of the subject at N bands, normalized by the subject's own max width.

    Normalizing per-band by the canvas width is wrong: it reports how much of the
    *frame* is filled, so a tight concept crop and a padded render never line up.
    Dividing by the subject's own widest band makes the profile resolution- and
    framing-independent.
    """
    crop = tight_crop(mask)
    if crop is None:
        return [0.0] * bands
    y0, y1, x0, x1 = crop
    sub = mask[y0:y1, x0:x1]
    h, w = sub.shape
    raw = []
    for i in range(bands):
        a = int(h * i / bands)
        b = max(int(h * (i + 1) / bands), a + 1)
        row = sub[a:b, :]
        cols = np.where(row.any(axis=0))[0]
        raw.append(float(cols.max() - cols.min() + 1) if len(cols) else 0.0)
    peak = max(raw) if raw else 0.0
    return [round(v / peak, 4) if peak else 0.0 for v in raw]


def band_errors(wa, wb):
    return [round(abs(a - b) * 100.0, 2) for a, b in zip(wa, wb)]


def bbox_report(mask_a, mask_b):
    """Compare subject aspect ratio (width / height), not absolute pixels.

    Comparing pixel widths across two images with different native resolutions and
    framing is meaningless — a 98x372 concept crop and a 1024x1024 render have no
    common pixel scale. Aspect ratio is the resolution-independent quantity, so
    that is what gets reported.
    """
    ca, cb = tight_crop(mask_a), tight_crop(mask_b)
    if ca is None or cb is None:
        return {}
    ha, wa_ = ca[1] - ca[0], ca[3] - ca[2]
    hb, wb_ = cb[1] - cb[0], cb[3] - cb[2]
    ar_a, ar_b = wa_ / max(1, ha), wb_ / max(1, hb)
    return {
        "aspect_ref": round(ar_a, 4),
        "aspect_test": round(ar_b, 4),
        "aspect_ratio": round(ar_b / ar_a, 4) if ar_a else 0.0,
        "height_px": [ha, hb],
    }


def _kmeans(pixels, k=8, iters=18, seed=3):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pixels), size=min(k, len(pixels)), replace=False)
    centers = pixels[idx].copy()
    for _ in range(iters):
        d = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for j in range(len(centers)):
            sel = pixels[lab == j]
            if len(sel):
                centers[j] = sel.mean(axis=0)
    d = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    lab = d.argmin(axis=1)
    counts = np.bincount(lab, minlength=len(centers))
    order = np.argsort(-counts)
    return centers[order], counts[order] / max(1, counts.sum())


def _srgb_to_lab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = c @ m.T
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def palette_report(rgb_a, mask_a, rgb_b, mask_b, k=8):
    pa = rgb_a[mask_a]
    pb = rgb_b[mask_b]
    if len(pa) < k or len(pb) < k:
        return {}
    ca, wa = _kmeans(pa, k)
    cb, wb = _kmeans(pb, k)
    la, lb = _srgb_to_lab(ca), _srgb_to_lab(cb)
    dist = np.linalg.norm(la[:, None, :] - lb[None, :, :], axis=2)
    # each cluster in A matched to its nearest in B, weighted by A's share
    nearest = dist.min(axis=1)
    mean_de = float((nearest * wa).sum())
    worst = float(nearest.max())
    return {
        "mean_delta_e": round(mean_de, 2),
        "worst_cluster_delta_e": round(worst, 2),
        "palette_ref": [(_hex(c), round(float(w), 3)) for c, w in zip(ca, wa)],
        "palette_test": [(_hex(c), round(float(w), 3)) for c, w in zip(cb, wb)],
    }


def _hex(c):
    return "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in np.clip(c, 0, 1))


def luminance_histogram(rgb, mask, bins=32):
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    vals = lum[mask]
    if len(vals) == 0:
        return np.zeros(bins)
    h, _ = np.histogram(vals, bins=bins, range=(0.0, 1.0))
    h = h.astype(np.float64)
    s = h.sum()
    return h / s if s else h


def hist_correlation(a, b):
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _gaussian_kernel(size=11, sigma=1.5):
    ax = np.arange(size) - size // 2
    g = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    g /= g.sum()
    return g


def _conv_sep(img, g):
    """Separable convolution, same size out. Horizontal then vertical pass."""
    k = len(g)
    pad = k // 2
    h, w = img.shape
    # horizontal: out[y, x] = sum_i g[i] * img[y, x + i - pad]
    p = np.pad(img, ((0, 0), (pad, pad)), mode="reflect")
    tmp = np.zeros_like(img)
    for i in range(k):
        tmp += g[i] * p[:, i:i + w]
    # vertical: out[y, x] = sum_i g[i] * tmp[y + i - pad, x]
    p2 = np.pad(tmp, ((pad, pad), (0, 0)), mode="reflect")
    out = np.zeros_like(img)
    for i in range(k):
        out += g[i] * p2[i:i + h, :]
    return out


def ssim(gray_a, gray_b):
    g = _gaussian_kernel()
    mu_a, mu_b = _conv_sep(gray_a, g), _conv_sep(gray_b, g)
    va = _conv_sep(gray_a ** 2, g) - mu_a ** 2
    vb = _conv_sep(gray_b ** 2, g) - mu_b ** 2
    cov = _conv_sep(gray_a * gray_b, g) - mu_a * mu_b
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    num = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
    den = (mu_a ** 2 + mu_b ** 2 + c1) * (va + vb + c2)
    return float(np.mean(num / np.maximum(den, 1e-12)))

# ---------------------------------------------------------------- CLI

THRESHOLDS = {
    "iou_prop": 0.90,
    "iou_character": 0.85,
    "band_err_pct": 5.0,
    "delta_e_mean": 12.0,
    "hist_corr": 0.80,
    "bbox_pct": 3.0,
}


def load_alpha(path, size=None):
    """Read alpha if the file has one. A transparent render is ground truth."""
    im = Image.open(path)
    if im.mode not in ("RGBA", "LA"):
        return None
    a = im.convert("RGBA").split()[-1]
    if size is not None:
        a = a.resize(size, Image.LANCZOS)
    return np.asarray(a, dtype=np.float32) / 255.0


def mask_at_native(path, size, alpha=None):
    """Segment at the image's NATIVE resolution, then resample with aspect intact.

    Two bugs get avoided here. First, resizing before segmenting blurs a flat
    backdrop into a gradient and floods the mask. Second, resizing the mask straight
    onto a square canvas stretches aspect ratio, so a tall figure reports a wide
    silhouette and the aspect check fails on arithmetic alone. Scale by height and
    pad horizontally.
    """
    im0 = Image.open(path)
    w0, h0 = im0.size
    rgb0 = np.asarray(im0.convert("RGB"), dtype=np.float32) / 255.0
    if alpha is None:
        a0 = None
        if im0.mode in ("RGBA", "LA"):
            a0 = np.asarray(im0.convert("RGBA").split()[-1], dtype=np.float32) / 255.0
    else:
        a0 = np.asarray(
            Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8)).resize((w0, h0),
                                                                                 Image.LANCZOS),
            dtype=np.float32) / 255.0

    m0 = subject_mask(rgb0, alpha=a0)

    th, tw = size[1], size[0]
    scale = th / max(1, h0)
    nw = max(1, min(tw, int(round(w0 * scale))))
    cm = np.asarray(Image.fromarray((m0 * 255).astype(np.uint8)).resize((nw, th), Image.LANCZOS))
    out = np.zeros((th, tw), dtype=bool)
    left = (tw - nw) // 2
    out[:, left:left + nw] = cm > 127
    return out


def evaluate(ref_path, test_path, kind="character", bands=10, size=(512, 512),
             out_json=None, ref_alpha=None, test_alpha=None):
    ref = load_rgb(ref_path, size)
    test = load_rgb(test_path, size)
    ra = ref_alpha if ref_alpha is not None else load_alpha(ref_path, size)
    ta = test_alpha if test_alpha is not None else load_alpha(test_path, size)
    ma = mask_at_native(ref_path, size, alpha=ra)
    mb = mask_at_native(test_path, size, alpha=ta)
    mask_source = ("alpha" if ta is not None else "keyed") + "/" + \
                  ("alpha" if ra is not None else "keyed")

    # shape metrics on bounding-box-normalized masks: framing must not count as error
    na, nb = normalize_mask(ma, size), normalize_mask(mb, size)
    iou = silhouette_iou(na, nb)
    wa, wb = band_widths(na, bands), band_widths(nb, bands)
    berr = band_errors(wa, wb)
    bbox = bbox_report(ma, mb)
    pal = palette_report(ref, ma, test, mb)
    hist = hist_correlation(luminance_histogram(ref, ma), luminance_histogram(test, mb))

    ga = 0.2126 * ref[..., 0] + 0.7152 * ref[..., 1] + 0.0722 * ref[..., 2]
    gb = 0.2126 * test[..., 0] + 0.7152 * test[..., 1] + 0.0722 * test[..., 2]
    s = ssim(ga, gb)
    rmse = float(np.sqrt(np.mean((ref - test) ** 2)))

    iou_thr = THRESHOLDS["iou_prop"] if kind == "prop" else THRESHOLDS["iou_character"]
    checks = {
        "silhouette_iou": (round(iou, 4), iou_thr, iou >= iou_thr),
        "band_max_err_pct": (max(berr), THRESHOLDS["band_err_pct"],
                             max(berr) <= THRESHOLDS["band_err_pct"]),
        "mean_delta_e": (pal.get("mean_delta_e", 999), THRESHOLDS["delta_e_mean"],
                         pal.get("mean_delta_e", 999) <= THRESHOLDS["delta_e_mean"]),
        "luminance_hist_corr": (round(hist, 4), THRESHOLDS["hist_corr"],
                                hist >= THRESHOLDS["hist_corr"]),
    }
    for k in ("aspect_ratio",):
        if k in bbox:
            dev = abs(bbox[k] - 1.0) * 100
            checks[f"aspect_dev_pct"] = (round(dev, 2), THRESHOLDS["bbox_pct"],
                                         dev <= THRESHOLDS["bbox_pct"])

    report = {
        "ref": ref_path,
        "test": test_path,
        "kind": kind,
        "mask_source": mask_source,
        "silhouette_iou": round(iou, 4),
        "band_widths_ref": [round(v, 4) for v in wa],
        "band_widths_test": [round(v, 4) for v in wb],
        "band_errors_pct": berr,
        "band_max_err_pct": max(berr),
        "bbox": bbox,
        "palette": pal,
        "luminance_hist_corr": round(hist, 4),
        "ssim_advisory": round(s, 4),
        "rmse_advisory": round(rmse, 4),
        "checks": {k: {"value": v[0], "threshold": v[1], "pass": bool(v[2])}
                   for k, v in checks.items()},
        "overall_pass": all(v[2] for v in checks.values()),
    }
    if out_json:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    return report


def print_report(r):
    print("=" * 66)
    print(f"REF  {r['ref']}")
    print(f"TEST {r['test']}   kind={r['kind']}")
    print("-" * 66)
    print(f"silhouette IoU      : {r['silhouette_iou']:.4f}")
    print(f"band widths  ref   : {r['band_widths_ref']}")
    print(f"band widths  test  : {r['band_widths_test']}")
    print(f"band errors  %     : {r['band_errors_pct']}   max {r['band_max_err_pct']:.2f}")
    if r["bbox"]:
        b = r["bbox"]
        print(f"aspect  ref {b['aspect_ref']:.3f}  test {b['aspect_test']:.3f}"
              f"  ratio {b['aspect_ratio']:.3f}   h_px {b['height_px']}")
    p = r["palette"]
    if p:
        print(f"palette mean dE    : {p['mean_delta_e']:.2f}   worst {p['worst_cluster_delta_e']:.2f}")
        print(f"  ref  clusters    : {p['palette_ref']}")
        print(f"  test clusters    : {p['palette_test']}")
    print(f"lum hist corr      : {r['luminance_hist_corr']:.4f}")
    print(f"SSIM (advisory)    : {r['ssim_advisory']:.4f}   RMSE {r['rmse_advisory']:.4f}")
    print("-" * 66)
    for name, c in r["checks"].items():
        mark = "PASS" if c["pass"] else "FAIL"
        print(f"  [{mark}] {name:24s} {c['value']:>8}  (need {c['threshold']})")
    print("-" * 66)
    print("OVERALL:", "PASS" if r["overall_pass"] else "FAIL")
    print("=" * 66)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--kind", default="character", choices=["character", "prop", "environment"])
    ap.add_argument("--bands", type=int, default=10)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = evaluate(a.ref, a.test, kind=a.kind, bands=a.bands, out_json=a.out)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print_report(rep)
