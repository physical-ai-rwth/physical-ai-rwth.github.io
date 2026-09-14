# tools/

| Script | Purpose |
|---|---|
| `bib2yml.py` | `_bibliography/*.bib` → `_data/publications.yml` |
| `make_portrait.py` | Any photo → studio-style 4:3 team portrait |
| `make_cv_placeholder.py` | Branded placeholder CV PDF |
| `make_topic_bg.py` | Abstract 4:3 background art for the research cards |

---

## make_portrait.py

Crops a photo to a fixed ratio with the subject centred, and replaces the background
with a soft gray gradient — the look used on Apple's leadership page.

```bash
# one photo
python3 tools/make_portrait.py photo.jpg --out assets/images/team/jane-doe.jpg

# a whole folder
python3 tools/make_portrait.py raw-photos/ --out-dir assets/images/team/
```

Output defaults to **1200×900 (4:3)** — horizontal 4, vertical 3 — which is what the
team cards and member portraits expect, so nothing gets re-cropped by CSS.

### Options

| Flag | Default | Notes |
|---|---|---|
| `--ratio W:H` | `4:3` | Width:height. Use `3:4` for a portrait-orientation crop. |
| `--width` | `1200` | Output width in px; height follows the ratio. |
| `--face-frac` | `0.30` | Head height as a fraction of image height. Raise for a tighter crop. |
| `--face-y` | `0.40` | Where the face centre sits vertically, 0–1. |
| `--fit` | off | Show the whole photo and extend its background sideways to reach the ratio, instead of cropping to fill. |
| `--keep-bg` | off | Crop and position only; leave the background alone. |
| `--debug-mask` | off | Also writes the cut-out matte next to the output. |
| `--quality` | `88` | JPEG quality. |
| `--no-animate` | off | Animated GIF input: keep only the first frame. |
| `--max-frames` | `120` | Cap on GIF frames kept. |

### How it works

1. Finds the face with OpenCV Haar cascades (frontal, then profile).
2. Scales and crops so every portrait has the head at the same size and height —
   this is what makes a row of them look consistent.
3. Separates subject from background with GrabCut, seeded from the face box.
4. Feathers the matte and composites onto the gradient.

If no face is found it falls back to a centre crop and says so.

### Animated GIFs

GIF input is supported, and animation is preserved when the output is also `.gif`:

```bash
python3 tools/make_portrait.py wave.gif --out assets/images/team/jane-doe.gif
```

The crop and the cut-out are computed **once from the first frame** and reused for every
frame. Segmenting each frame separately would make the background boil and flicker; a
shared matte stays perfectly still.

The tradeoff: **a fixed matte cannot follow a moving subject.** If the person moves much
between frames, background leaks in around them or parts get clipped. For a GIF with real
motion, `--keep-bg` usually looks better.

GIFs get heavy fast — a 1200×900 12-frame GIF is around 750 KB. The script warns past
500 KB. For an avatar, `--width 600` and `--max-frames 24` keep it reasonable.

In batch mode, `.gif` sources stay `.gif` so animation survives; everything else becomes
`.jpg`.

Animation also works nicely for the hover image: point `image:` at a still and
`image_alt:` at the GIF, and the card animates only on hover.

### When the source is the wrong shape

A square or portrait-orientation photo cannot fill a 4:3 frame without losing the top of
the head. `--fit` avoids that: it matches the height, centres the photo, and extends the
backdrop outward by replicating the edge columns — then blurs and feathers the extension
so the seam cannot be picked out. Replicating a column rather than filling with a flat
colour carries any vertical gradient in the backdrop straight through.

Useful for studio headshots, which are usually framed square or tall.

### Honest limits

**GrabCut is a general segmenter, not a matting model.** Fine hair detail can be lost,
and a busy or low-contrast background can leave fragments attached to the subject.
Always look at the result.

Two ways to deal with a bad cut-out:

- `--keep-bg` — skip segmentation entirely. Always safe, and the right choice when the
  photo already has a clean studio backdrop.
- `--debug-mask` — inspect the matte to see what it actually selected.

For a difficult photo, cutting the subject out by hand and saving a transparent PNG will
beat anything automatic.

Because the pipeline scales around the detected face, a photo where the face is very
small will be upscaled (capped at 4×) and may look soft. Start from the largest original
you have.


---

## make_topic_bg.py

Generates the abstract background behind each research card — one generative motif per
topic, so the set reads as a family while staying distinguishable.

```bash
python3 tools/make_topic_bg.py                       # all seven
python3 tools/make_topic_bg.py --only world-models   # just one
```

Output: `assets/images/research/<slug>.jpg`, 1200×900 (4:3).

| Topic | Motif |
|---|---|
| `vision-language-action` | streamlines through a flow field |
| `world-models` | a grid deformed by a lens |
| `active-perception` | sight lines sweeping from a viewpoint |
| `structured-memory` | stacked strata |
| `cognitive-alignment` | two ring systems overlapping |
| `imitation-rl` | a branching search tree |
| `medical-robotics` | measured grid with registration marks |

The art sits under a dark gradient veil on the site, so it is tuned for **contrast under
that veil** rather than on its own. Judged in isolation the files look strong; that is
deliberate. If you restyle them, check the result on the page, not in an image viewer.

Adding a topic means adding a motif function and an entry to `TOPICS` in the script — or
just pointing that topic's `image:` at a photograph instead.
