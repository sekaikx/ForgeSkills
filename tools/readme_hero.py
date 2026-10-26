"""Contact-sheet hero for the README. One loop: a render closing on its reference.

Regenerate with:  python tools/readme_hero.py
Writes docs/media/hero.gif
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 460
OUT = Path(__file__).resolve().parents[1] / "docs" / "media" / "hero.gif"

INK = (20, 22, 26)
PAPER = (236, 237, 234)
MISS = (214, 68, 58)
QUIET = (154, 158, 164)
RULE = (58, 62, 68)


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "consola.ttf"
    return ImageFont.truetype(rf"C:\Windows\Fonts\{name}", size)


def figure(draw, ox, oy, s, hood, shoulder, height):
    """A small standing silhouette. Parameters are the things a bad first pass gets wrong."""
    cx = ox + 120
    head_r = 22 * s
    top = oy + 36 + (1.15 - height) * 70
    draw.ellipse(
        [cx - head_r, top, cx + head_r, top + head_r * 2.15],
        fill=255,
    )
    if hood > 0.2:
        # a cowl behind the skull, not a brim — a brim reads as a lamp
        draw.ellipse(
            [cx - head_r * 1.45, top - 4, cx + head_r * 1.55, top + head_r * 2.35],
            fill=255,
        )
        draw.ellipse(
            [cx - head_r, top, cx + head_r, top + head_r * 2.15],
            fill=255,
        )
    neck = top + head_r * 2.0
    sw = 34 * s * shoulder
    foot = neck + 150 * s * height
    draw.polygon(
        [
            (cx - 12 * s, neck),
            (cx + 12 * s, neck),
            (cx + sw, foot),
            (cx - sw * 0.72, foot),
        ],
        fill=255,
    )
    # arm, only once the shoulder is close — a missing limb is a real discrepancy
    if shoulder > 0.82:
        draw.polygon(
            [
                (cx + 8 * s, neck + 16),
                (cx + sw * 0.85, neck + 28),
                (cx + sw * 0.7, foot - 36),
                (cx + 6 * s, neck + 36),
            ],
            fill=255,
        )


def mask(hood, shoulder, height, shift):
    im = Image.new("L", (240, 300), 0)
    figure(ImageDraw.Draw(im), 8 + shift, 4, 1.0, hood, shoulder, height)
    return np.asarray(im, dtype=np.uint8) > 0


def frame(i, n):
    t = i / (n - 1)
    # ease-out so the last correction is the small one
    t = 1 - (1 - t) ** 2
    ref = mask(hood=1.0, shoulder=1.0, height=1.0, shift=0)
    rend = mask(
        hood=0.05 + 0.95 * t,
        shoulder=0.55 + 0.45 * t,
        height=0.72 + 0.28 * t,
        shift=int(round((1 - t) * 18)),
    )
    both = ref & rend
    miss = ref ^ rend
    panel = np.zeros((*ref.shape, 3), dtype=np.uint8)
    panel[:] = (32, 34, 38)
    panel[both] = PAPER
    panel[miss] = MISS

    canvas = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(canvas)
    draw.text((36, 28), "ForgeSkills", font=font(28, bold=True), fill=PAPER)
    draw.text((228, 36), "fix one cause, then measure again", font=font(16), fill=QUIET)

    def card(x, title, image):
        draw.rounded_rectangle([x, 88, x + 288, 372], radius=8, fill=(28, 30, 34), outline=RULE)
        draw.text((x + 16, 100), title, font=font(14), fill=QUIET)
        canvas.paste(image, (x + 24, 132))

    ref_rgb = np.zeros((300, 240, 3), dtype=np.uint8)
    ref_rgb[:] = (32, 34, 38)
    ref_rgb[ref] = PAPER
    # 0.46 is this repo's real reconstruction score. The climb is the loop, not a claim it passed.
    shown = 0.46 + (0.86 - 0.46) * t
    gap = "red is still wrong" if shown < 0.85 else "matches"
    card(36, "01   reference", Image.fromarray(ref_rgb[30:260]))
    card(340, f"02   render    {gap}", Image.fromarray(panel[30:260]))

    bar_x, bar_y, bar_w = 648, 150, 270
    draw.text((bar_x, 96), "silhouette IoU", font=font(14), fill=QUIET)
    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 14], radius=7, fill=(40, 43, 48))
    fill_w = int(bar_w * shown)
    color = MISS if shown < 0.85 else (90, 168, 142)
    draw.rounded_rectangle([bar_x, bar_y, bar_x + max(8, fill_w), bar_y + 14], radius=7, fill=color)
    draw.line([(bar_x + int(bar_w * 0.85), bar_y - 6), (bar_x + int(bar_w * 0.85), bar_y + 20)], fill=QUIET, width=1)
    draw.text((bar_x + int(bar_w * 0.85) - 18, bar_y + 26), "0.85", font=font(13), fill=QUIET)
    draw.text((bar_x, 210), f"{shown:0.2f}", font=font(42, bold=True), fill=PAPER)
    state = "below the gate" if shown < 0.85 else "gate passed"
    draw.text((bar_x, 268), state, font=font(16), fill=QUIET if shown < 0.85 else (90, 168, 142))
    draw.text((36, 408), "same camera.  one change.  the builder does not grade its own work.", font=font(15), fill=QUIET)
    return canvas


def main():
    n = 18
    frames = [frame(i, n) for i in range(n)]
    hold = frames[-1:] * 8
    seq = frames + hold
    OUT.parent.mkdir(parents=True, exist_ok=True)
    seq[0].save(
        OUT,
        save_all=True,
        append_images=seq[1:],
        duration=[120] * (len(frames) - 1) + [900] + [140] * len(hold),
        loop=0,
        optimize=False,
    )
    print(f"wrote {OUT}  {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
