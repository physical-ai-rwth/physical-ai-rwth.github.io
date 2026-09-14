#!/usr/bin/env python3
"""
Generate abstract background images for the research topic cards.

Each topic gets its own generative motif, so the seven cards read as a set but
are visually distinct. They sit under a dark gradient veil on the site, so the
art is mid-tone with strong structure rather than high contrast.

    python3 tools/make_topic_bg.py              # all topics
    python3 tools/make_topic_bg.py --only vla   # one

Output: assets/images/research/<slug>.jpg at 1200x900 (4:3).
"""

import argparse
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images", "research")
W, H = 1200, 900

INK = (26, 30, 38)        # near-black with a cool cast
MID = (108, 116, 130)
PALE = (206, 210, 216)
BLUE = (0, 84, 159)       # brand


def base(seed, light=0.86):
    """Soft tonal ground: a few blurred blooms, cool gray."""
    rng = random.Random(seed)
    img = Image.new("RGB", (W, H), tuple(int(c * light) for c in PALE))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(7):
        x, y = rng.randint(-200, W), rng.randint(-200, H)
        r = rng.randint(320, 760)
        v = rng.randint(-30, 18)
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(max(0, PALE[0] + v), max(0, PALE[1] + v), max(0, PALE[2] + v), 120))
    return img.filter(ImageFilter.GaussianBlur(90))


def finish(img, seed, vignette=0.30):
    """Grain + vignette so it reads as a photograph-adjacent surface."""
    a = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    a += rng.normal(0, 3.0, a.shape)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)
    a *= (1.0 - np.clip(r, 0, 1)[..., None] ** 2 * vignette)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ── Motifs ────────────────────────────────────────────────────────
# Each is a loose schematic of what the topic actually is, drawn in a
# technical-illustration register. They sit under a dark veil, so strokes are
# heavy and contrast is pushed further than looks right in isolation.

LINE = INK + (150,)
FAINT = INK + (62,)
ACC = BLUE + (185,)


def _grid(d, step=60, alpha=30):
    for x in range(0, W + 1, step):
        d.line([x, 0, x, H], fill=INK + (alpha,), width=1)
    for y in range(0, H + 1, step):
        d.line([0, y, W, y], fill=INK + (alpha,), width=1)


def _arm(d, ox, oy, angles, seg=96, col=LINE, w=7):
    """Articulated arm: joint circles linked by segments."""
    x, y, a = ox, oy, 0.0
    d.ellipse([x - 13, y - 13, x + 13, y + 13], outline=col, width=w - 3)
    for ang in angles:
        a += math.radians(ang)
        nx, ny = x + math.cos(a) * seg, y + math.sin(a) * seg
        d.line([x, y, nx, ny], fill=col, width=w)
        d.ellipse([nx - 11, ny - 11, nx + 11, ny + 11], outline=col, width=w - 3)
        x, y = nx, ny
    # gripper
    a2 = a + math.radians(-26)
    a3 = a + math.radians(26)
    d.line([x, y, x + math.cos(a2) * 40, y + math.sin(a2) * 40], fill=col, width=w - 2)
    d.line([x, y, x + math.cos(a3) * 40, y + math.sin(a3) * 40], fill=col, width=w - 2)
    return x, y


def vision_language_action(seed):
    """Camera + language tokens + arm: the three things VLA joins up."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    _grid(d, 75, 26)

    # camera, left
    cx, cy = 170, 300
    d.rounded_rectangle([cx - 78, cy - 54, cx + 78, cy + 54], 14, outline=LINE, width=7)
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=LINE, width=6)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=ACC)
    # field of view
    d.line([cx + 78, cy - 30, cx + 205, cy - 96], fill=FAINT, width=3)
    d.line([cx + 78, cy + 30, cx + 205, cy + 96], fill=FAINT, width=3)

    # language tokens, middle column
    tx = 400
    for i, wdt in enumerate([150, 210, 120, 185, 96]):
        ty = 168 + i * 54
        col = ACC if i in (1, 3) else LINE
        d.rounded_rectangle([tx, ty, tx + wdt, ty + 30], 15, outline=col, width=5)

    # arrow into action
    d.line([680, 300, 800, 300], fill=LINE, width=6)
    d.polygon([(800, 286), (830, 300), (800, 314)], fill=LINE)

    _arm(d, 905, 720, [-74, 46, 30])
    return finish(img, seed)


def world_models(seed):
    """A rollout: observed states solid, predicted future dashed."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    _grid(d, 60, 24)

    pts = [(150, 640), (300, 560), (450, 520), (600, 520), (750, 560), (900, 640), (1040, 760)]
    for i, (x, y) in enumerate(pts):
        observed = i <= 3
        col = LINE if observed else ACC
        r = 40 - i * 2
        if observed:
            d.rounded_rectangle([x - r, y - r, x + r, y + r], 10, outline=col, width=6)
        else:                                   # predicted: dashed box
            for (a, b, c, e) in [(x - r, y - r, x + r, y - r), (x - r, y + r, x + r, y + r),
                                 (x - r, y - r, x - r, y + r), (x + r, y - r, x + r, y + r)]:
                steps = 7
                for k in range(0, steps, 2):
                    t0, t1 = k / steps, (k + 1) / steps
                    d.line([a + (c - a) * t0, b + (e - b) * t0,
                            a + (c - a) * t1, b + (e - b) * t1], fill=col, width=5)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=col)

    for i in range(len(pts) - 1):
        col = LINE if i < 3 else ACC
        d.line([pts[i], pts[i + 1]], fill=col, width=4)

    # alternative futures branching from the last observed state
    bx, by = pts[3]
    for dy in (-150, 150):
        d.line([bx, by, bx + 210, by + dy], fill=BLUE + (80,), width=3)
        d.line([bx + 210, by + dy, bx + 400, by + dy * 1.5], fill=BLUE + (60,), width=3)

    # time axis
    d.line([120, 830, 1080, 830], fill=FAINT, width=3)
    for x in range(150, 1081, 150):
        d.line([x, 822, x, 838], fill=FAINT, width=3)
    return finish(img, seed)


def active_perception(seed):
    """A sensor choosing where to look: cone sweeps, occlusion behind."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    _grid(d, 75, 22)

    ox, oy = 210, 700
    # discarded viewpoints
    for ang in (-104, -86, -50, -30):
        a = math.radians(ang)
        d.line([ox, oy, ox + math.cos(a) * 760, oy + math.sin(a) * 760], fill=FAINT, width=3)
    # chosen cone
    a1, a2 = math.radians(-74), math.radians(-56)
    d.polygon([(ox, oy),
               (ox + math.cos(a1) * 820, oy + math.sin(a1) * 820),
               (ox + math.cos(a2) * 820, oy + math.sin(a2) * 820)],
              fill=BLUE + (34,))
    for a in (a1, a2):
        d.line([ox, oy, ox + math.cos(a) * 820, oy + math.sin(a) * 820], fill=ACC, width=5)

    # sensor
    d.rounded_rectangle([ox - 52, oy - 34, ox + 52, oy + 34], 12, outline=LINE, width=7)
    d.ellipse([ox - 16, oy - 16, ox + 16, oy + 16], fill=ACC)

    # occluder, and the unknown region behind it
    d.rectangle([560, 250, 610, 470], fill=INK + (120,))
    d.polygon([(610, 250), (610, 470), (1080, 300), (1080, 120)], fill=INK + (26,))
    for i in range(9):                        # hatching over the unknown
        d.line([640 + i * 50, 140, 700 + i * 50, 420], fill=INK + (40,), width=2)

    # the target, partly revealed
    d.ellipse([700, 300, 790, 390], outline=LINE, width=6)
    d.arc([700, 300, 790, 390], -60, 120, fill=ACC, width=8)
    return finish(img, seed)


def structured_memory(seed):
    """An addressed memory bank: slots, some written, retrieval links."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)

    cols, rows = 9, 6
    cw, ch, x0, y0 = 96, 96, 150, 170
    filled = set()
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * cw, y0 + r * ch
            d.rectangle([x, y, x + cw - 14, y + ch - 14], outline=FAINT, width=3)
            if rng.random() < 0.30:
                filled.add((c, r))
                inset = 14
                d.rectangle([x + inset, y + inset, x + cw - 14 - inset, y + ch - 14 - inset],
                            fill=INK + (95,))
    # index ticks down the left
    for r in range(rows):
        d.line([x0 - 40, y0 + r * ch + 30, x0 - 14, y0 + r * ch + 30], fill=LINE, width=4)

    # retrieval: a query touching a few slots
    qx, qy = 1075, 120
    d.ellipse([qx - 16, qy - 16, qx + 16, qy + 16], fill=ACC)
    picks = sorted(filled)[:4]
    for (c, r) in picks:
        tx, ty = x0 + c * cw + (cw - 14) / 2, y0 + r * ch + (ch - 14) / 2
        d.line([qx, qy, tx, ty], fill=BLUE + (110,), width=3)
        d.rectangle([x0 + c * cw, y0 + r * ch,
                     x0 + c * cw + cw - 14, y0 + r * ch + ch - 14], outline=ACC, width=5)
    return finish(img, seed)


def cognitive_alignment(seed):
    """Two minds, two structures, correspondences drawn between them."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)

    # human, left
    hx, hy = 235, 300
    d.ellipse([hx - 62, hy - 62, hx + 62, hy + 62], outline=LINE, width=7)
    d.arc([hx - 118, hy + 60, hx + 118, hy + 300], 200, 340, fill=LINE, width=7)
    # robot, right
    rx, ry = 965, 300
    d.rounded_rectangle([rx - 62, ry - 58, rx + 62, ry + 58], 14, outline=LINE, width=7)
    d.ellipse([rx - 28, ry - 16, rx - 8, ry + 4], fill=LINE)
    d.ellipse([rx + 8, ry - 16, rx + 28, ry + 4], fill=LINE)
    d.line([rx, ry - 58, rx, ry - 92], fill=LINE, width=5)
    d.ellipse([rx - 9, ry - 108, rx + 9, ry - 90], fill=ACC)
    d.arc([rx - 112, ry + 60, rx + 112, ry + 290], 200, 340, fill=LINE, width=7)

    # matching concept graphs
    left = [(360, 470), (300, 610), (430, 690), (520, 560)]
    right = [(840, 470), (900, 610), (770, 690), (680, 560)]
    for pts in (left, right):
        for i, pa in enumerate(pts):
            for pb in pts[i + 1:]:
                d.line([pa, pb], fill=FAINT, width=3)
        for (x, y) in pts:
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=INK + (130,))
    for a, b in zip(left, right):              # the alignment itself
        d.line([a, b], fill=BLUE + (120,), width=3)
    return finish(img, seed)


def imitation_rl(seed):
    """One demonstrated path, many explored ones, a single goal."""
    img = base(seed); d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)
    _grid(d, 75, 22)

    start, goal = (170, 730), (1030, 230)
    d.ellipse([start[0] - 20, start[1] - 20, start[0] + 20, start[1] + 20], fill=LINE)
    d.ellipse([goal[0] - 34, goal[1] - 34, goal[0] + 34, goal[1] + 34], outline=ACC, width=7)
    d.ellipse([goal[0] - 13, goal[1] - 13, goal[0] + 13, goal[1] + 13], fill=ACC)

    def bez(p0, p1, p2, n=60):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
                for t in (i / n for i in range(n + 1))]

    # exploration
    for _ in range(11):
        ctrl = (rng.uniform(350, 850), rng.uniform(120, 800))
        d.line(bez(start, ctrl, goal), fill=INK + (52,), width=3)
    # the demonstration
    d.line(bez(start, (520, 330), goal), fill=LINE, width=9)
    # reward samples along the way
    for _ in range(16):
        x, y = rng.uniform(240, 980), rng.uniform(180, 760)
        r = rng.choice([5, 7, 9])
        d.ellipse([x - r, y - r, x + r, y + r], outline=BLUE + (95,), width=3)
    return finish(img, seed)


def medical_robotics(seed):
    """An instrument on a planned path, over layered anatomy contours."""
    img = base(seed, light=0.9); d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W + 1, 40):
        d.line([x, 0, x, H], fill=INK + (22,), width=1)
    for y in range(0, H + 1, 40):
        d.line([0, y, W, y], fill=INK + (22,), width=1)

    # concentric tissue contours
    cx, cy = 690, 520
    for i, rr in enumerate(range(90, 360, 52)):
        d.ellipse([cx - rr * 1.25, cy - rr, cx + rr * 1.25, cy + rr],
                  outline=INK + (52 + i * 12,), width=4)

    # planned instrument path with entry point
    d.line([180, 130, cx, cy], fill=ACC, width=6)
    for k in range(0, 11, 2):                  # depth ticks along the path
        t0, t1 = k / 11, (k + 0.6) / 11
        d.line([180 + (cx - 180) * t0, 130 + (cy - 130) * t0,
                180 + (cx - 180) * t1, 130 + (cy - 130) * t1], fill=BLUE + (230,), width=9)
    d.ellipse([150, 100, 210, 160], outline=LINE, width=6)

    # target reticle
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], outline=ACC, width=6)
    d.line([cx - 92, cy, cx + 92, cy], fill=ACC, width=4)
    d.line([cx, cy - 92, cx, cy + 92], fill=ACC, width=4)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=ACC)

    # tolerance callout
    d.line([cx + 58, cy - 130, cx + 250, cy - 130], fill=LINE, width=3)
    d.line([cx + 58, cy - 138, cx + 58, cy - 122], fill=LINE, width=3)
    d.line([cx + 250, cy - 138, cx + 250, cy - 122], fill=LINE, width=3)
    return finish(img, seed, vignette=0.22)


TOPICS = [
    ("vision-language-action",     vision_language_action, 11),
    ("world-models",               world_models,           23),
    ("active-perception",          active_perception,      37),
    ("structured-memory",          structured_memory,      41),
    ("cognitive-alignment",        cognitive_alignment,    53),
    ("imitation-rl",               imitation_rl,            7),
    ("medical-robotics",           medical_robotics,       71),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="slug to regenerate (default: all)")
    ap.add_argument("--quality", type=int, default=84)
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files (they may be real photographs)")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    todo = [t for t in TOPICS if not args.only or t[0] == args.only]
    if not todo:
        print(f"No topic matching {args.only!r}. Known: "
              + ", ".join(t[0] for t in TOPICS), file=sys.stderr)
        return 1

    for slug, fn, seed in todo:
        path = os.path.join(OUT, slug + ".jpg")
        # These filenames now hold real lab photography. Generated placeholder
        # art must never silently replace it.
        if os.path.exists(path) and not args.force:
            print(f"  {slug:<26} exists — skipped (use --force to overwrite)")
            continue
        img = fn(seed)
        img.save(path, quality=args.quality, optimize=True, progressive=True)
        print(f"  {slug:<26} {os.path.getsize(path) // 1024:>4} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
