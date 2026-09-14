#!/usr/bin/env python3
"""
Generate a branded placeholder CV PDF for a team member.

These exist so the "Download CV" button can be seen and styled before real CVs
arrive. Every page is stamped PLACEHOLDER so it cannot be mistaken for a real
document if the site goes live before they are replaced.

Usage:
    python3 tools/make_cv_placeholder.py --slug yuli-wu \
        --name "Dr.-Ing. Yuli Wu" --role "Group Leader — Physical AI Lab"

Requires rsvg-convert (brew install librsvg).
"""

import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "cv")

BLUE = "#00549F"
INK = "#111110"
MUTED = "#74746F"
RULE = "#DDDDD8"
GHOST = "#E9E9E4"

# PAI compact mark, viewBox 0 0 900 400
LOGO = (
    '<g transform="translate({x},{y}) scale({s})" fill="{c}">'
    '<path d="M 50 50 L 310 50 C 400.49 49.71 450.18 90.77 450 150 C 449.82 210.23 400.5 '
    '249.65 310 250 L 160 250 L 160 350 L 50 350 Z M 160 130 L 160 170 L 310 170 C 330.19 '
    '169.93 340 160.35 340 150 C 340 140.41 330.24 129.89 310 130 Z"/>'
    '<path d="M 310 350 L 625 50 L 735 50 L 735 350 L 635 350 L 635 300 L 520 300 L 470 350 '
    'Z M 580 230 L 635 230 L 635 170 Z"/>'
    '<path d="M 766 50 L 866 50 L 866 350 L 766 350 Z"/>'
    "</g>"
)

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "Helvetica, Arial, sans-serif"
MONO = "'Courier New', Courier, monospace"


def esc(t):
    """XML-escape text so an & or < in a name cannot break the document."""
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def skeleton(y, widths, gap=13, h=7):
    """Gray bars standing in for unwritten content."""
    out = []
    for i, w in enumerate(widths):
        out.append(
            f'<rect x="56" y="{y + i * gap}" width="{w}" height="{h}" rx="3" fill="{GHOST}"/>'
        )
    return "".join(out), y + len(widths) * gap


def build_svg(name, role, email, institute):
    W, H = 595, 842
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        LOGO.format(x=56, y=52, s=110 / 900, c=BLUE),
    ]

    # Placeholder stamp, top right
    parts.append(
        f'<rect x="{W-56-118}" y="52" width="118" height="22" rx="3" '
        f'fill="none" stroke="{BLUE}" stroke-width="1" opacity="0.5"/>'
        f'<text x="{W-56-59}" y="67" text-anchor="middle" font-family="{MONO}" '
        f'font-size="9" letter-spacing="1.6" fill="{BLUE}" opacity="0.75">PLACEHOLDER</text>'
    )

    y = 150
    parts.append(
        f'<text x="56" y="{y}" font-family="{SERIF}" font-size="27" font-weight="bold" '
        f'fill="{INK}">{esc(name)}</text>'
    )
    y += 22
    parts.append(
        f'<text x="56" y="{y}" font-family="{SANS}" font-size="11.5" fill="{MUTED}">{esc(role)}</text>'
    )
    y += 16
    parts.append(
        f'<text x="56" y="{y}" font-family="{SANS}" font-size="10" fill="{MUTED}">{esc(institute)}</text>'
    )
    if email:
        y += 14
        parts.append(
            f'<text x="56" y="{y}" font-family="{MONO}" font-size="9.5" fill="{BLUE}">{esc(email)}</text>'
        )

    y += 24
    parts.append(f'<line x1="56" y1="{y}" x2="{W-56}" y2="{y}" stroke="{RULE}" stroke-width="1"/>')
    y += 34

    sections = [
        ("Education", [330, 250, 300]),
        ("Appointments", [300, 340, 260]),
        ("Selected Publications", [380, 350, 320, 300]),
        ("Teaching & Supervision", [300, 270]),
        ("Awards", [250, 220]),
    ]
    for title, widths in sections:
        parts.append(
            f'<text x="56" y="{y}" font-family="{MONO}" font-size="9" letter-spacing="1.5" '
            f'fill="{BLUE}">{esc(title.upper())}</text>'
        )
        y += 16
        bars, y = skeleton(y, widths)
        parts.append(bars)
        y += 22

    parts.append(
        f'<line x1="56" y1="{H-86}" x2="{W-56}" y2="{H-86}" stroke="{RULE}" stroke-width="1"/>'
        f'<text x="56" y="{H-66}" font-family="{SANS}" font-size="9" fill="{MUTED}">'
        f'This is a placeholder document, not a curriculum vitae.</text>'
        f'<text x="56" y="{H-53}" font-family="{SANS}" font-size="9" fill="{MUTED}">'
        f'Replace it with the real PDF at assets/cv/ before publishing the site.</text>'
        f'<text x="{W-56}" y="{H-53}" text-anchor="end" font-family="{MONO}" font-size="8.5" '
        f'fill="{MUTED}">Physical AI Lab · RWTH Aachen</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--role", default="")
    ap.add_argument("--email", default="")
    ap.add_argument("--institute",
                    default="Chair of Imaging and Computer Vision, RWTH Aachen University")
    args = ap.parse_args()

    if not shutil.which("rsvg-convert"):
        print("rsvg-convert not found — install with: brew install librsvg", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    svg = build_svg(args.name, args.role, args.email, args.institute)
    tmp = os.path.join(OUT_DIR, f".{args.slug}.svg")
    pdf = os.path.join(OUT_DIR, f"{args.slug}.pdf")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(svg)
    try:
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, tmp], check=True)
    finally:
        os.remove(tmp)

    print(f"  {os.path.relpath(pdf, ROOT)}  ({os.path.getsize(pdf):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
