# Logo files

Two lockups, three colours each. Blue is **`#00549F`** — the exact brand blue from the
source artwork, and also the site accent in `_sass/_variables.scss`.

| | Blue | Black | White |
|---|---|---|---|
| **Full lockup** (mark + wordmark) | `pai_logo_full_blue.svg` | `pai_logo_full_black.svg` | `pai_logo_full_white.svg` |
| **Compact mark** (PAI only) | `pai_logo_blue.svg` | `pai_logo_black.svg` | `pai_logo_white.svg` |

## Where each is used

- **Header** — full lockup. Cross-fades white over the dark hero, blue once you scroll
  onto light content. Both colour files are required; supplying only one leaves the logo
  invisible against one background.
- **Hero and footer** — compact mark, white.
- **Under 640px** — the header falls back to the compact mark, since a wide lockup with
  text would crowd the menu button.
- **Black** — print, documents, single-colour contexts. Not used on the site.

The header detects the full lockup automatically and falls back to the compact mark if
those files are missing, so removing them degrades gracefully rather than breaking.

## Replacing these

SVG is preferred and takes priority if both an `.svg` and `.png` exist.

| | |
|---|---|
| **Background** | **Must be transparent.** The original `pai_logo_blue.png` had an opaque white background, which rendered as a solid white rectangle over the dark hero. The PDF export had the same problem — a white rect covering the full canvas. |
| **Text** | Convert to outlines. The source PDF used Helvetica Neue Condensed Bold; as live text it would fall back to a different font anywhere that isn't installed. |
| **PNG fallback** | Renders at 32px tall, so export ≥128px tall (192px safer). Width is `auto`. |

## Current files

| File | Used for |
|---|---|
| `pai_logo_blue.svg` | Compact mark on light backgrounds — **in use** |
| `pai_logo_white.svg` | Compact mark on dark backgrounds (hero, footer) — **in use** |
| `pai_logo_black.svg` | Print, documents, single-colour contexts |
| `pai_logo_blue.png` | Superseded by the SVG; kept for slides, Word, email signatures |
| `pai_logo_white.png` | Superseded by the SVG |

The compact mark is used everywhere except the header, and on narrow screens
(under 640px) the header falls back to it too, since a wide lockup would crowd
the menu button.

### About the SVGs

**Compact mark** — rebuilt from `pai_logo_raw.svg`. The original had the **"I" as an embedded base64
PNG** rather than a path — it was a fully solid 100×300 rectangle, so it became a
plain four-point path. All three files now contain exactly three paths (P, A, I)
sharing one colour set on the root `<svg fill>`, so the letters can never drift
apart in colour.

569 bytes each, down from 2388. Verified pixel-aligned against the original raster.

**Full lockup** — converted from `pai_logo_full_black.pdf` with `pdftocairo -svg`.
Removed an opaque white background rect, stripped per-element colour so everything
inherits one value from the root `<svg>`, and dropped the fixed width/height so CSS
controls the size. The wordmark's glyphs were already outlined by the conversion, so
it carries no font dependency. Verified pixel-aligned against the source PDF.

Note the wordmark is drawn twice — filled glyphs plus a 3px stroke outline over them,
which is what gives it its weight. That stroke inherits the root colour too, so it
never separates from the fill.

The source masters live outside the repo, in `~/Desktop/design/`.

## PDF versions

Vector PDFs for print, LaTeX, Word and Keynote are **not kept in the repo** — they are
generated from the SVGs here whenever needed:

```bash
mkdir -p ~/Desktop/design/pdf
for f in assets/images/logo/*.svg; do
  rsvg-convert -f pdf -o ~/Desktop/design/pdf/"$(basename "$f" .svg)".pdf "$f"
done
```

That produces all six — two lockups × three colours — fully vector with transparent
backgrounds, carrying the same cleaned geometry and exact `#00549F` as the web SVGs.

Requires `rsvg-convert` (`brew install librsvg`).

**The white versions look blank** on a white background. That is correct — white artwork
on transparency, meant for dark backgrounds.
