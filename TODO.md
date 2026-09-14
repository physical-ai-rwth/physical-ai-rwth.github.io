# PAI Site — What to change before going live

Current as of the latest build. Three tiers: **Must fix** (wrong, or placeholder content
a visitor would see), **Could do** (real improvements, not blocking), **Ignore** (noise,
or working as intended).

---

## 1. Must fix

### 1.1 Delete the fabricated publications

`_bibliography/papers.bib` contains **three invented papers** written to exercise the
pipeline. They carry fake identifiers — `10.1109/LRA.2025.000000` and
`arXiv:0000.00000` — and a co-author who does not exist ("Jane Doe").

On an academic site these read as real publications. Delete all three, paste your actual
BibTeX, and regenerate:

```bash
python3 tools/bib2yml.py
```

Until that is done, leaving Publications hidden from the nav (as it is now) is the safer
state, though the page is still reachable at `/publications/` and the entries still show
on member pages.

### 1.2 Replace the placeholder hero video

The homepage embeds a **third-party YouTube video** about NEURA's robot gym
(`aWLz0HYobd8`), chosen only because it matches your NEURA Gym access. Two reasons to swap
it before you publicise the site:

- It is someone else's content sitting on your official lab page.
- YouTube contacts Google servers on every visit. The embed uses `youtube-nocookie.com`
  (privacy-enhanced mode), but self-hosting avoids the GDPR question entirely — the same
  reasoning behind self-hosting the fonts.

| Option | How |
|---|---|
| Self-host (preferred) | Drop the file at `assets/video/hero.mp4`. It takes priority automatically — no config edit, and the "third-party footage" disclaimer disappears by itself. |
| Different YouTube clip | Change `hero_video.youtube_id` in `_config.yml`. |
| No video | Set `youtube_id: ""` and add no file — the ambient gradient stands on its own. |

### 1.3 Every image is a placeholder

| What | Where | Currently |
|---|---|---|
| Team portraits | `_members/*.md` → `image:` | gray silhouette SVG |
| Machine photos | `neura-gym.md`, `gpu-cluster.md` | generic robot-arm SVG |
| Research cards | `_research/*.md` → `image:` | generated abstract art |

**For people and machines there is a tool** — see *Making portraits* below. It crops to
4:3 with the subject centred on a gray gradient, so a set of photos looks consistent.

Also set **`image_alt:`** — the image revealed on hover. Make it visibly different (in
action, a different angle, or an animated GIF). Without it the card just zooms.

Research cards now carry **generated abstract backgrounds**, one motif per topic, made by
`tools/make_topic_bg.py`. They are placeholders in the sense that real lab photography
would be better, but they are distinct and on-brand rather than filler. Regenerate or
restyle with that script; replace `image:` in a topic file to use a photo instead.

### 1.4 Fill in the team

`_members/` has five entries: Prof. Schulz, you, one "Open Position" placeholder, and the
two machines. Add people as they join — see *Adding a team member* below.

Two things to verify:

- **Prof. Schulz's bio** is my inference from the job description, which says only that he
  heads the chair. Confirm or replace.
- **The machines list** covers only what the JD confirms (NEURA Gym, ~120 GPUs). Add your
  actual robot platforms with real model names and specs.

### 1.5 Finish the CVs and profile links

The tabular CVs are now filled from the institute pages
(`lfb.rwth-aachen.de/en/institute/team/{schulz,wu}/`), so the appointments and degrees
are real. Two gaps remain:

- **Neither doctorate is listed.** Both of you hold a Dr.-Ing., but neither institute page
  states the year, so no row was invented. Add one to `cv:` in each file.
- **Profile URLs are still placeholders** — `links:` in both files contains `[ID]` and
  `[handle]`. Replace or delete; they are entirely optional.
- `assets/cv/*.pdf` are generated placeholders stamped PLACEHOLDER. Replace, or delete
  them and drop `cv_pdf:` to rely on the tabular CV alone.

### 1.6 Review the HiWi and Thesis position pages

`_positions/phd.md` is taken verbatim from your JD. **`hiwi.md` and `thesis.md` are my
drafts** — plausible but unverified. Read them before publishing.

Two specifics: the `apply_subject:` values `PhysicalAI_HiWi_{LastName}` and
`PhysicalAI_Thesis_{LastName}` are my extrapolation from the PhD convention in the JD, and
neither position has a job description PDF. Drop one in `assets/jd/` and uncomment `pdf:`
in that file to make the download button appear.

### 1.7 Set `url` and `baseurl` before deploying

Both are empty in `_config.yml`. Fine locally and for a user/org site; **a project site
will break** — every stylesheet, font and image 404s.

```yaml
# Project site at https://<user>.github.io/pai-site
url: "https://<user>.github.io"
baseurl: "/pai-site"

# User/org site or custom domain
url: "https://physical-ai-lab.github.io"
baseurl: ""
```

Every internal path uses `relative_url`, so this is the only change needed.

---

## 2. Could do

**Content**
- **A seventh research card sits alone** on the last row of the 3-column grid. Deleting one
  file from `_research/` gives a clean 3×2.
- **Tag publications by topic.** Add `keywords = {vla, world-models}` to entries in
  `papers.bib`; each research page pulls matching papers automatically via its
  `pub_keywords:`. Or list exact BibTeX keys in `pub_keys:`. Either is optional — with
  neither, no publications section renders.
- **News / highlights** — the homepage "The lab" section is static.
- **German translation**, if the chair expects one.

**Site plumbing**
- **`404.html`** — GitHub Pages serves its generic page otherwise.
- **`jekyll-sitemap`** — add to `plugins:` in `_config.yml`.
- **`CNAME`** — only for a custom domain.
- **Stale-check in CI** — `python3 tools/bib2yml.py --check` exits non-zero when the
  generated YAML no longer matches the `.bib`. Useful as a pre-commit or CI step.

---

## 3. Ignore

### 3.1 Sass `@import` deprecation warnings
Dart Sass 3.0 is unreleased. `@import` works. Pure noise on every build.

### 3.2 `--livereload` doesn't work
`eventmachine`'s native extension is ABI-incompatible with Ruby 3.1.2 and will not rebuild
(`gem pristine` does not help). It is only used by livereload. `bundle exec jekyll serve`
works fine — refresh manually. Already removed from `.claude/launch.json`.

### 3.3 The Gemfile uses plain `jekyll`, not `github-pages`
Deliberate. The `github-pages` gem pins 100+ dependencies and never finished installing.
GitHub Pages builds with **its own** gem environment on push, so deployment is unaffected.

### 3.4 `vollkorn-4-105/`, `tools/`, `raw-photos/` in the project root
Font masters, scripts and photo staging. All excluded from the build; none ship.

### 3.5 The white logo PDFs look blank
White artwork on transparency, meant for dark backgrounds. Working as intended.

### 3.6 `_data/publications.yml` looks machine-written
It is. Generated from the `.bib` — see *Publications* below.

---

## Gotchas

**`jekyll serve` does not watch `_config.yml`.** Edit the config and the running server
keeps serving stale values — this has bitten twice. Restart after any config change.

**Editing the `.bib` alone changes nothing.** Run `python3 tools/bib2yml.py` after every
edit, or the site keeps serving the previous list.

**Browsers cache `main.js` and the favicon hard.** After a JS or icon change, hard-reload
with `Cmd+Shift+R`.

**Port 4000 in use?** `lsof -nP -iTCP:4000 -sTCP:LISTEN` for the PID, or
`bundle exec jekyll serve --port 4001`.

```bash
bundle exec jekyll serve     # http://localhost:4000
bundle exec jekyll build     # output to _site/
```

**Testing on a phone:** `bundle exec jekyll serve --host 0.0.0.0`, then open
`http://<your-lan-ip>:4000` from a device on the same network.

**Deploying:** push to `main`, then Settings → Pages → Deploy from branch → `main` → `/`.
Set `url`/`baseurl` first (1.7).

---

## Research directions

Each direction is a file in `_research/`, published at `/research/<slug>/`, and listed
automatically on the home page and `/research/`.

```yaml
---
num: "08"
title: "New Direction"
summary: "One sentence — used on the cards."
image: "/assets/images/research/new-direction.jpg"    # 4:3
order: 8
topics: ["Tag One", "Tag Two"]
pub_keys: ["wu2026generalist"]     # optional: exact BibTeX keys
pub_keywords: ["vla"]              # optional: match entry `keywords`
---

Markdown body — the prose on that page.
```

Publications are **optional and additive**: `pub_keys` and `pub_keywords` are unioned,
deduplicated and sorted newest first. With neither, the section does not render.

Card art comes from `tools/make_topic_bg.py`, which has one generative motif per topic.

---

## Making portraits

Every image frame on the site is **4:3** (horizontal 4, vertical 3). The tool matches it:

```bash
# one photo
python3 tools/make_portrait.py photo.jpg --out assets/images/team/jane-doe.jpg

# a folder — drop originals in raw-photos/ first
python3 tools/make_portrait.py raw-photos/ --out-dir assets/images/team/
```

It finds the face, scales and crops so every portrait has the head at the same size and
height, then cuts the subject out and composites onto a gray gradient. Output is
1200×900.

**Animated GIFs keep their animation** when the output is also `.gif`. The crop and
cut-out are computed once from the first frame and reused, so the background never
flickers — but that fixed matte cannot follow a moving subject, so for a GIF with much
motion use `--keep-bg`. A nice pairing: a still for `image:`, a GIF for `image_alt:`, so
the card animates only on hover.

**The cut-out is approximate.** GrabCut is a general segmenter, not a matting model, so
hair detail can be lost and busy backgrounds can leave fragments. Check every result.
`--keep-bg` skips segmentation entirely (always safe, and right when the photo already
has a clean backdrop); `--debug-mask` writes the matte so you can see what it selected.

Full options in `tools/README.md`.

---

## Adding a team member

Create a file in `_members/`. The filename becomes the URL, so `_members/jane-doe.md`
publishes at `/team/jane-doe/`.

```yaml
---
name: "Jane Doe, M.Sc."        # card and page heading
short_name: "Jane Doe"          # short form, used where space is tight
order: 4                        # position in the grid
type: member                    # leader | head | member | associate | robot
display_types: [member]         # which filter tabs it appears under
role: "Doctoral Researcher"
affiliation: "Physical AI Lab, RWTH Aachen University"
bio: "One or two sentences — card hover text and the page lede."
research: [World Models, Sim-to-Real]
email: "jane.doe@lfb.rwth-aachen.de"
image: "/assets/images/team/jane-doe.jpg"           # 4:3
image_alt: "/assets/images/team/jane-doe-alt.gif"   # revealed on hover; GIF fine
author_id: "jane-doe"                               # pulls their papers from the .bib
show_publications: true                             # false hides the papers section
cv_pdf: "/assets/cv/jane-doe.pdf"                   # optional; hidden if file missing
cv:                                                 # optional short CV, one flat list
  - period: "2025 – present"
    title: "Doctoral Researcher"
    org: "Physical AI Lab, RWTH Aachen University"
links:                                              # all optional
  - key: scholar
    url: "https://scholar.google.com/citations?user=..."
  - key: linkedin
    url: "https://www.linkedin.com/in/..."
---

Markdown body — becomes the prose on the individual page.
```

The card, filter tab, individual page, CV table and publication list all follow
automatically. An entry with `type: associate` makes the Associates tab appear on its own.

Recognised `links` keys: `scholar`, `linkedin`, `github`, `orcid`, `arxiv`, `x`,
`bluesky`, `mastodon`, `researchgate`, `semanticscholar`, `dblp`, `website`. For anything
else give your own `label:`.

Robots use `type: robot`, and take `description:` plus a `specs:` list of label/value
pairs instead of `bio:`.

---

## Publications

`_bibliography/papers.bib` is the **source of truth**. After editing it:

```bash
python3 tools/bib2yml.py          # regenerates _data/publications.yml
python3 tools/bib2yml.py --check  # exits 1 if that file is stale
```

`_data/publications.yml` is **generated** — never edit it by hand. Commit both files.

**Why not jekyll-scholar:** GitHub Pages builds from a branch and does not execute custom
Jekyll plugins, so it cannot run there. Converting ahead of time keeps BibTeX as the source
while staying plugin-free.

### Per-person lists are automatic

The converter normalises each author to an id — `Wu, Yuli` and `Yuli Wu` both become
`yuli-wu` — and prints what it found:

```
author ids found (use these as `author_id:` in _members/*.md):
  yuli-wu                      3
  volkmar-schulz               2
```

Put an id in a member's `author_id:` and their page lists every matching paper, newest
first, with their own name in bold. Add a paper once and it appears on every co-author's
page and on `/publications/`.

Initials and other variants the converter cannot guess go in `_data/author_aliases.yml`.

### Publication lists are currently switched off

Per-member publication sections are disabled site-wide. The machinery is untouched — the
matching, the highlighting, the BibTeX toggle all still work; the sections simply do not
render. This is a single default in `_config.yml`:

```yaml
defaults:
  - scope:
      type: members
    values:
      layout: member
      show_publications: false     # <- delete this line to re-enable for everyone
```

Three ways to bring them back:

| Want | Do |
|---|---|
| Everyone | Delete the `show_publications: false` line above |
| One person only | Add `show_publications: true` to that member's front matter — it overrides the default |
| Everyone except one | Delete the default, then add `show_publications: false` to the exception |

A member also needs `author_id:` set and at least one matching paper in the bibliography,
or nothing renders regardless.

Note the standalone `/publications/` page is **not** affected by this — it lists the whole
bibliography and is controlled separately (it is hidden from the nav, see below).

### What the converter handles

Accents (`M{\"u}ller` → Müller), nested braces, `{Van der Berg}` as one surname, inline
maths (`$\alpha$` → α, `$L_2$` → L₂), arXiv `eprint` and bare `doi` turned into links,
and duplicate keys skipped with a warning.

It is a pragmatic parser, not a full BibTeX implementation — it does **not** expand
`@string` macros or `crossref`. Check the output if your `.bib` uses those.

Full detail in `_bibliography/README.md`.

### Re-enabling the nav link

The page builds and stays reachable at `/publications/`; it is only hidden from the nav.
Uncomment the two `Publications` lines under `navigation:` in `_config.yml`.

An empty bibliography shows a "coming soon" note rather than a broken page.

---

## Reference

### Where things live
| Want to change | File |
|---|---|
| People and machines | `_members/*.md` — one file each, becomes `/team/<slug>/` |
| Publications | `_bibliography/papers.bib`, then run `python3 tools/bib2yml.py` |
| Author name variants | `_data/author_aliases.yml` |
| Short tabular CV | `cv:` in `_members/*.md` |
| CV PDF (optional) | `assets/cv/`, referenced by `cv_pdf:` |
| Profile links | `links:` in `_members/*.md` |
| Research directions | `_research/*.md` — one file each, becomes `/research/<slug>/` |
| Hero video, nav, contact, institute | `_config.yml` |
| Colours, fonts, type scale, corner radii | `_sass/_variables.scss` |
| Homepage sections | `index.html` |
| Openings | `_positions/*.md` — one file each, becomes `/join/<slug>/` |
| Job description PDFs | `assets/jd/`, referenced by `pdf:` in `_positions/*.md` |
| Logo usage and specs | `assets/images/logo/README.md` |
| Scripts | `tools/README.md` |

### Generated files — do not hand-edit
| File | Regenerate with |
|---|---|
| `_data/publications.yml` | `python3 tools/bib2yml.py` |

### Brand
Blue is **`#00549F`**, taken from the source logo artwork and used as the site accent.

Logos come in two lockups (full and compact mark), three colours each, as SVG in
`assets/images/logo/`. The header uses the full lockup and falls back to the compact mark
under 640px.

Source masters live **outside the repo** in `~/Desktop/design/`. Vector PDFs of all six
web logos can be regenerated any time from the SVGs — see `assets/images/logo/README.md`.

### Typography
- **Vollkorn** — headings and display
- **Roboto** — longer running text
- **Roboto Mono** — tags, badges, labels, nav, buttons, numeric data

Driven by `$font-serif` / `$font-sans` / `$font-mono` in `_sass/_variables.scss`. The type
scale (`$fs-micro` 11px → `$fs-body` 16px) lives in the same file; nothing renders below
11px. All fonts are self-hosted — no Google Fonts CDN call, deliberately.

### Shape
Corner radii come from `$r-sm` 5px (chips, tags), `$r-md` 9px (buttons) and `$r-lg` 16px
(cards, panels, portraits). Every image frame is 4:3.

### Content source
All research and recruitment copy derives from the PhD job description, a copy of which is
served at `assets/jd/PhD_JD_PAI_03-09-r2.pdf`. Your working original lives outside the repo
in `~/Desktop/jobs/akademie/`. **If you revise it, copy the new PDF into `assets/jd/`** and
update `pdf:` in `_positions/phd.md`, plus `index.html`, `_research/*.md` and
`_positions/phd.md` if the substance changed.


---

## Openings

Each opening is a file in `_positions/`, published at `/join/<slug>/` and listed
automatically on `/join/`.

```yaml
---
title: "PostDoc"
kicker: "Postdoctoral"
order: 4
summary: "One sentence — shown on the card."
facts:                                   # the "At a glance" table
  - label: "Type"
    value: "Full-time"
pdf: "/assets/jd/PostDoc_JD.pdf"         # optional; button hidden if file missing
apply_subject: "PhysicalAI_PostDoc_{LastName}"
---

Markdown body — the detail on that page.
```

Job description PDFs live in `assets/jd/`. The download button renders only when the file
actually exists, so a stale `pdf:` path fails silently rather than publishing a dead link.
