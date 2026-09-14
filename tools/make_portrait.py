#!/usr/bin/env python3
"""
Turn an arbitrary photo into a studio-style team portrait: subject centred on a
soft gray gradient, cropped to a fixed aspect ratio.

    python3 tools/make_portrait.py photo.jpg --out assets/images/team/yuli-wu.jpg
    python3 tools/make_portrait.py raw/ --out-dir assets/images/team/   # batch

Pipeline
  1. Detect the face (OpenCV Haar, frontal then profile).
  2. Scale and crop so the head sits at a consistent size and height.
  3. Separate subject from background with GrabCut, seeded from the face box.
  4. Feather the matte and composite onto a gray gradient.

Animated GIFs keep their animation. The crop and the cut-out are computed once
from the first frame and reused for every frame — per-frame segmentation would
flicker. The cost is that the matte cannot follow a moving subject, so for a GIF
with much motion prefer --keep-bg.

Background replacement is approximate — GrabCut is a general segmenter, not a
matting model, so fine hair detail can be lost. Check each result. Use
--keep-bg when the source already has a clean studio backdrop; it then only
crops and positions, which is always safe.

Requires: opencv-python, pillow, numpy.
"""

import argparse
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

# Grays chosen to sit with the site palette (page bg #F5F5F2)
TOP = (239, 239, 236)
BOTTOM = (214, 214, 209)
GLOW = (250, 250, 248)

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".gif")


def parse_ratio(text):
    """'4:3' -> (4, 3) as width, height."""
    try:
        w, h = (float(p) for p in text.replace("x", ":").split(":"))
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except Exception:
        raise argparse.ArgumentTypeError(f"bad ratio {text!r}; use e.g. 4:3")


def load_frames(path):
    """Return ([BGR frames], [durations ms], is_animated). PIL handles GIF."""
    im = Image.open(path)
    animated = getattr(im, "n_frames", 1) > 1
    frames, durations = [], []
    if not animated:
        rgb = im.convert("RGB")
        return [cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)], [0], False

    for i in range(im.n_frames):
        im.seek(i)
        rgb = im.convert("RGB")
        frames.append(cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR))
        durations.append(im.info.get("duration", 80))
    return frames, durations, True


def detect_face(bgr):
    """Return the most prominent face box, or None."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    base = cv2.data.haarcascades
    for name in ("haarcascade_frontalface_default.xml",
                 "haarcascade_frontalface_alt2.xml",
                 "haarcascade_profileface.xml"):
        cascade = cv2.CascadeClassifier(base + name)
        if cascade.empty():
            continue
        faces = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=6,
                                         minSize=(max(40, gray.shape[0] // 18),) * 2)
        if len(faces):
            # largest wins — group shots and background faces stay secondary
            return max(faces, key=lambda f: f[2] * f[3])
    return None


def gradient(w, h, face_cx=None, face_cy=None):
    """Vertical gray ramp plus a soft glow behind the head."""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    base = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        base[..., c] = TOP[c] * (1 - t) + BOTTOM[c] * t

    cx = w * 0.5 if face_cx is None else face_cx
    cy = h * 0.42 if face_cy is None else face_cy
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.72)) ** 2)
    glow = np.clip(1.0 - r, 0, 1) ** 2.1

    out = base.copy()
    for c in range(3):
        out[..., c] = base[..., c] * (1 - glow * 0.55) + GLOW[c] * (glow * 0.55)
    return np.clip(out, 0, 255).astype(np.uint8)


def plan(shape, face, out_w, out_h, face_frac, face_y, fit=False):
    """Work out scale and crop offset once, so every frame gets the same one."""
    H, W = shape[:2]

    if fit:
        # Show the whole frame: match the height and let the sides fall short.
        # apply_plan fills the gap by extending the photo's own background, which
        # keeps a head intact that a cover-crop would slice off.
        scale = out_h / H
        ox = int(round((W * scale - out_w) / 2))
        oy = 0
        nf = None
        if face is not None:
            x, y, fw, fh = face
            nf = (int(x * scale) - ox, int(y * scale) - oy,
                  int(fw * scale), int(fh * scale))
        return scale, ox, oy, nf

    if face is None:
        # No face: cover-crop the centre, which is the safe default
        scale = max(out_w / W, out_h / H)
        fx = fy = None
    else:
        x, y, fw, fh = face
        scale = (face_frac * out_h) / fh
        # Never below cover: a tightly framed headshot wants a smaller scale
        # than the frame needs, and letterboxing it leaves the subject floating
        # in a box with its original background still attached.
        scale = max(scale, max(out_w / W, out_h / H))
        scale = min(scale, 6.0)
        fx, fy = (x + fw / 2) * scale, (y + fh / 2) * scale

    new_w, new_h = max(1, int(round(W * scale))), max(1, int(round(H * scale)))

    if face is None:
        ox = (new_w - out_w) // 2
        oy = int((new_h - out_h) * 0.35)          # a little headroom
    else:
        ox = int(round(fx - out_w / 2))
        oy = int(round(fy - out_h * face_y))

    new_face = None
    if face is not None:
        x, y, fw, fh = face
        new_face = (int(x * scale) - ox, int(y * scale) - oy,
                    int(fw * scale), int(fh * scale))
    return scale, ox, oy, new_face


def apply_plan(bgr, scale, ox, oy, out_w, out_h, extend=False):
    """Resize and crop one frame using a precomputed plan."""
    H, W = bgr.shape[:2]
    new_w, new_h = max(1, int(round(W * scale))), max(1, int(round(H * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    resized = cv2.resize(bgr, (new_w, new_h), interpolation=interp)

    canvas = np.zeros((out_h, out_w, 3), np.uint8)
    valid = np.zeros((out_h, out_w), np.uint8)

    sx0, sy0 = max(0, ox), max(0, oy)
    sx1, sy1 = min(new_w, ox + out_w), min(new_h, oy + out_h)
    if sx1 <= sx0 or sy1 <= sy0:
        raise RuntimeError("crop fell outside the image")
    dx0, dy0 = sx0 - ox, sy0 - oy
    canvas[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)] = resized[sy0:sy1, sx0:sx1]
    valid[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)] = 1

    if extend:
        # Stretch the outermost column outward. Replicating a column rather than
        # filling with a flat colour carries any vertical gradient in the
        # backdrop straight through, so the join is invisible.
        x_lo, x_hi = dx0, dx0 + (sx1 - sx0) - 1
        if x_lo > 0:
            canvas[:, :x_lo] = canvas[:, x_lo:x_lo + 1]
        if x_hi < out_w - 1:
            canvas[:, x_hi + 1:] = canvas[:, x_hi:x_hi + 1]
        y_lo, y_hi = dy0, dy0 + (sy1 - sy0) - 1
        if y_lo > 0:
            canvas[:y_lo, :] = canvas[y_lo:y_lo + 1, :]
        if y_hi < out_h - 1:
            canvas[y_hi + 1:, :] = canvas[y_hi:y_hi + 1, :]

        # A replicated column repeats whatever detail sat at that x — a shadow
        # edge, say — as a visible band. Blur the extension and ramp it in from
        # the seam so the transition cannot be picked out.
        if x_lo > 0 or x_hi < out_w - 1:
            blurred = cv2.GaussianBlur(canvas, (0, 0), sigmaX=max(6, out_w / 26), sigmaY=2)
            ramp = np.zeros((out_w,), np.float32)
            feather = max(8, int(out_w * 0.05))
            if x_lo > 0:
                ramp[:x_lo] = 1.0
                lo = max(0, x_lo - feather)
                ramp[lo:x_lo] = np.linspace(0, 1, x_lo - lo)[::-1] * 0 + \
                                np.linspace(1, 0, x_lo - lo)[::-1]
            if x_hi < out_w - 1:
                ramp[x_hi + 1:] = 1.0
                hi = min(out_w, x_hi + 1 + feather)
                ramp[x_hi + 1:hi] = np.linspace(0, 1, hi - (x_hi + 1))
            a = ramp[None, :, None]
            canvas = (canvas.astype(np.float32) * (1 - a) +
                      blurred.astype(np.float32) * a).astype(np.uint8)

        valid[:] = 1        # the extension is real background, not padding

    return canvas, valid


def segment(bgr, face, valid, iters=5):
    """GrabCut matte, seeded from the face box. Returns 0..1 float mask."""
    h, w = bgr.shape[:2]
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)

    # Probable subject: a torso-shaped column under the head
    if face is not None:
        fx, fy, fw, fh = face
        cx = fx + fw // 2
        col_w = int(fw * 3.4)
        x0, x1 = max(0, cx - col_w // 2), min(w, cx + col_w // 2)
        y0 = max(0, fy - int(fh * 0.85))
        mask[y0:h, x0:x1] = cv2.GC_PR_FGD
        # the face itself is certain
        mask[max(0, fy + int(fh * 0.12)):fy + int(fh * 0.88),
             max(0, fx + int(fw * 0.15)):fx + int(fw * 0.85)] = cv2.GC_FGD
    else:
        # No face: assume a centred subject and be conservative — a loose seed
        # here lets GrabCut swallow large parts of a busy background.
        mask[int(h * 0.14):, int(w * 0.30):int(w * 0.70)] = cv2.GC_PR_FGD
        mask[:, :int(w * 0.14)] = cv2.GC_BGD
        mask[:, int(w * 0.86):] = cv2.GC_BGD
        mask[:int(h * 0.06), :] = cv2.GC_BGD

    # Outer frame is certainly background
    b = max(2, int(min(h, w) * 0.02))
    mask[:b, :] = cv2.GC_BGD
    mask[:, :b] = cv2.GC_BGD
    mask[:, -b:] = cv2.GC_BGD
    # Padding introduced by the crop is background too
    mask[valid == 0] = cv2.GC_BGD

    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(bgr, mask, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    except cv2.error as e:
        print(f"    grabCut failed ({e.err.strip() if hasattr(e,'err') else e});"
              " keeping original background", file=sys.stderr)
        return None

    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    # Keep the blob that actually holds the subject, not merely the biggest
    n, labels, stats, _ = cv2.connectedComponentsWithStats((fg > 0).astype(np.uint8), 8)
    if n > 1:
        if face is not None:
            px = int(np.clip(face[0] + face[2] / 2, 0, w - 1))
            py = int(np.clip(face[1] + face[3] / 2, 0, h - 1))
        else:
            px, py = w // 2, int(h * 0.55)
        want = labels[py, px]
        if want == 0:                       # seed landed on background
            want = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        fg = np.where(labels == want, 255, 0).astype(np.uint8)

    if fg.max() == 0:
        return None

    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    soft = cv2.GaussianBlur(fg, (0, 0), sigmaX=max(1.2, min(h, w) / 420))
    return (soft.astype(np.float32) / 255.0)[..., None]


def process(src, dst, out_w, out_h, face_frac, face_y, keep_bg, quality,
            debug_mask=False, animate=True, max_frames=120, fit=False):
    try:
        frames, durations, animated = load_frames(src)
    except Exception as e:
        print(f"  SKIP {os.path.basename(src)} — unreadable ({e})", file=sys.stderr)
        return False
    if not frames:
        print(f"  SKIP {os.path.basename(src)} — no frames", file=sys.stderr)
        return False

    want_gif = dst.lower().endswith(".gif")
    keep_anim = animated and animate and want_gif
    if animated and not keep_anim:
        frames, durations = frames[:1], durations[:1]
    if keep_anim and len(frames) > max_frames:
        print(f"    {len(frames)} frames, keeping first {max_frames}", file=sys.stderr)
        frames, durations = frames[:max_frames], durations[:max_frames]

    # Geometry and matte are computed once from the reference frame and reused
    # for every frame — per-frame segmentation would flicker badly.
    ref = frames[0]
    face = detect_face(ref)
    scale, ox, oy, new_face = plan(ref.shape, face, out_w, out_h, face_frac, face_y, fit)
    if scale > 1.6:
        sh, sw = ref.shape[:2]
        print(f"    source is {sw}x{sh}; filling {out_w}x{out_h} needs {scale:.1f}x "
              f"upscaling and will look soft. Use a larger original, or --width "
              f"{int(out_w / scale * 1.6 // 10 * 10)}.", file=sys.stderr)

    ref_placed, valid = apply_plan(ref, scale, ox, oy, out_w, out_h, fit)
    cx = None if new_face is None else new_face[0] + new_face[2] / 2
    cy = None if new_face is None else new_face[1] + new_face[3] / 2
    bg = gradient(out_w, out_h, cx, cy)

    alpha = None
    if not keep_bg:
        alpha = segment(ref_placed, new_face, valid)
        if alpha is not None and debug_mask:
            mpath = os.path.splitext(dst)[0] + ".mask.png"
            cv2.imwrite(mpath, (alpha[..., 0] * 255).astype(np.uint8))
            print(f"    matte -> {os.path.basename(mpath)}")

    out_frames = []
    for fr in frames:
        placed, v = apply_plan(fr, scale, ox, oy, out_w, out_h, fit)
        if alpha is None:
            comp = placed.copy()
            comp[v == 0] = bg[v == 0]
        else:
            comp = (placed.astype(np.float32) * alpha +
                    bg.astype(np.float32) * (1 - alpha)).astype(np.uint8)
        img = Image.fromarray(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
        if not keep_anim:
            img = img.filter(ImageFilter.UnsharpMask(radius=1.1, percent=42, threshold=3))
        out_frames.append(img)

    os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
    if keep_anim:
        out_frames[0].save(dst, save_all=True, append_images=out_frames[1:],
                           duration=durations, loop=0, optimize=True,
                           disposal=2)
    elif dst.lower().endswith((".png", ".gif")):
        out_frames[0].save(dst, optimize=True)
    else:
        out_frames[0].save(dst, quality=quality, optimize=True, progressive=True)

    if keep_anim:
        kb = os.path.getsize(dst) / 1024
        if kb > 500:
            print(f"    {kb:.0f} KB — heavy for a web avatar; try "
                  f"--width 600 or --max-frames 24", file=sys.stderr)

    note = "centre crop (no face found)" if face is None else "face-centred"
    if not keep_bg:
        note += ", background replaced" if alpha is not None else ", background kept (matte failed)"
    if keep_anim:
        note += f", {len(out_frames)} frames"
    elif animated:
        note += ", first frame only"
    print(f"  {os.path.basename(dst):<30} {out_w}x{out_h}  {note}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="image file, or a directory for batch mode")
    ap.add_argument("--out", help="output file (single input)")
    ap.add_argument("--out-dir", help="output directory (batch)")
    ap.add_argument("--ratio", type=parse_ratio, default="4:3",
                    metavar="W:H", help="aspect ratio, width:height (default 4:3)")
    ap.add_argument("--width", type=int, default=1200, help="output width px (default 1200)")
    ap.add_argument("--face-frac", type=float, default=0.30,
                    help="face height as a fraction of image height (default 0.30)")
    ap.add_argument("--face-y", type=float, default=0.40,
                    help="vertical position of the face centre, 0-1 (default 0.40)")
    ap.add_argument("--fit", action="store_true",
                    help="show the whole photo and extend its background sideways to "
                         "reach the ratio, instead of cropping to fill")
    ap.add_argument("--keep-bg", action="store_true",
                    help="crop and position only; do not replace the background")
    ap.add_argument("--quality", type=int, default=88, help="JPEG quality (default 88)")
    ap.add_argument("--debug-mask", action="store_true",
                    help="also write the segmentation matte next to the output")
    ap.add_argument("--no-animate", action="store_true",
                    help="animated GIF input: keep only the first frame")
    ap.add_argument("--max-frames", type=int, default=120,
                    help="cap on GIF frames kept (default 120)")
    args = ap.parse_args()

    rw, rh = args.ratio if isinstance(args.ratio, tuple) else parse_ratio(args.ratio)
    out_w = args.width
    out_h = int(round(out_w * rh / rw))

    if os.path.isdir(args.input):
        if not args.out_dir:
            ap.error("--out-dir is required when the input is a directory")
        files = sorted(f for f in glob.glob(os.path.join(args.input, "*"))
                       if f.lower().endswith(EXTS))
        if not files:
            print(f"No images in {args.input}", file=sys.stderr)
            return 1
        ok = 0
        for f in files:
            stem, ext = os.path.splitext(os.path.basename(f))
            # animated sources stay GIF so the animation survives
            out_ext = ".gif" if ext.lower() == ".gif" else ".jpg"
            dst = os.path.join(args.out_dir, stem + out_ext)
            ok += process(f, dst, out_w, out_h, args.face_frac, args.face_y,
                          args.keep_bg, args.quality, args.debug_mask,
                          not args.no_animate, args.max_frames, args.fit)
        print(f"{ok}/{len(files)} converted")
        return 0 if ok else 1

    if not args.out:
        ap.error("--out is required for a single image")
    return 0 if process(args.input, args.out, out_w, out_h, args.face_frac,
                        args.face_y, args.keep_bg, args.quality,
                        args.debug_mask, not args.no_animate,
                        args.max_frames, args.fit) else 1


if __name__ == "__main__":
    sys.exit(main())
