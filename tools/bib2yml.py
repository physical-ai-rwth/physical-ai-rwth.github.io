#!/usr/bin/env python3
"""
Convert _bibliography/*.bib into _data/publications.yml.

Why a script instead of jekyll-scholar: GitHub Pages builds from a branch and
does not execute custom Jekyll plugins, so the .bib must be resolved to plain
data before the site is built. The .bib stays the source of truth; the YAML is
a generated artifact.

Usage:
    python3 tools/bib2yml.py            # convert
    python3 tools/bib2yml.py --check    # exit 1 if the YAML is out of date
"""

import argparse
import glob
import os
import re
import sys
import unicodedata

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB_DIR = os.path.join(ROOT, "_bibliography")
OUT = os.path.join(ROOT, "_data", "publications.yml")
ALIASES = os.path.join(ROOT, "_data", "author_aliases.yml")

# Venue field by entry type, in priority order
VENUE_FIELDS = ["booktitle", "journal", "journaltitle", "publisher", "school", "howpublished"]

LATEX = {
    r"\&": "&", r"\%": "%", r"\_": "_", r"\#": "#", r"\$": "$",
    "---": "\u2014", "--": "\u2013", "~": " ",
    r"\ ": " ", "``": "\u201c", "''": "\u201d", "`": "\u2018", "'": "\u2019",
}
ACCENTS = {
    ('"', "o"): "ö", ('"', "a"): "ä", ('"', "u"): "ü", ('"', "O"): "Ö",
    ('"', "A"): "Ä", ('"', "U"): "Ü", ('"', "e"): "ë", ('"', "i"): "ï",
    ("'", "e"): "é", ("'", "a"): "á", ("'", "o"): "ó", ("'", "i"): "í",
    ("'", "u"): "ú", ("'", "c"): "ć", ("'", "s"): "ś", ("'", "n"): "ń",
    ("`", "e"): "è", ("`", "a"): "à", ("`", "o"): "ò", ("`", "u"): "ù",
    ("^", "e"): "ê", ("^", "a"): "â", ("^", "o"): "ô", ("^", "i"): "î",
    ("~", "n"): "ñ", ("~", "a"): "ã", ("~", "o"): "õ",
    ("c", "c"): "ç", ("c", "s"): "ş", ("v", "s"): "š", ("v", "c"): "č",
    ("v", "z"): "ž", ("H", "o"): "ő", ("u", "a"): "ă", (".", "z"): "ż",
    ("=", "o"): "ō", ("=", "a"): "ā", ("=", "u"): "ū",
}


GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
MATH = {r"\times": "×", r"\to": "→", r"\rightarrow": "→", r"\leftarrow": "←",
        r"\leq": "≤", r"\geq": "≥", r"\neq": "≠", r"\approx": "≈",
        r"\pm": "±", r"\cdot": "·", r"\infty": "∞", r"\ell": "ℓ",
        r"\circ": "°", r"\%": "%"}


def demath(s):
    """Render simple inline math ($\\alpha$, $L_2$) as plain Unicode."""
    def one(m):
        inner = m.group(1)
        # longest first, so \Omega is not shadowed by a shorter match
        for name in sorted(GREEK, key=len, reverse=True):
            inner = inner.replace("\\" + name, GREEK[name])
        for k, v in MATH.items():
            inner = inner.replace(k, v)
        # subscripts/superscripts: L_2 -> L₂, x^2 -> x²
        subs = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
        sups = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
        inner = re.sub(r"_\{?([0-9+\-=()]+)\}?", lambda g: g.group(1).translate(subs), inner)
        inner = re.sub(r"\^\{?([0-9+\-=()n]+)\}?", lambda g: g.group(1).translate(sups), inner)
        inner = inner.replace("\\", "").replace("{", "").replace("}", "")
        return inner
    return re.sub(r"\$([^$]*)\$", one, s)


def clean(s):
    """Turn a raw BibTeX field value into display text."""
    if not s:
        return ""
    s = s.strip()
    s = demath(s)
    # \"{o} / \"o / \c{c}  ->  accented character
    s = re.sub(r'\\([\'"`^~=.HuvcC])\{?\\?([a-zA-Z])\}?',
               lambda m: ACCENTS.get((m.group(1), m.group(2)), m.group(2)), s)
    s = re.sub(r"\\ss\{?\}?", "ß", s)
    s = re.sub(r"\\[oO]\{?\}?", "ø", s)
    s = re.sub(r"\\aa\{?\}?", "å", s)
    # \emph{x}, \textbf{x}, \mbox{x} -> x
    s = re.sub(r"\\(?:emph|textit|textbf|textrm|mbox|text|url)\{([^{}]*)\}", r"\1", s)
    for k, v in LATEX.items():
        s = s.replace(k, v)
    s = s.replace("{", "").replace("}", "")   # brace-protection for casing
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def slug(name):
    """'Wu, Yuli' and 'Yuli Wu' both -> 'yuli-wu'."""
    name = clean(name)
    if "," in name:
        family, _, given = name.partition(",")
        name = f"{given.strip()} {family.strip()}"
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[\s_]+", "-", name)


def display_name(name):
    """Normalise to 'Given Family' for display."""
    name = clean(name)
    if "," in name:
        family, _, given = name.partition(",")
        return f"{given.strip()} {family.strip()}".strip()
    return name


def split_authors(field):
    # BibTeX separates authors with a top-level ' and '
    parts, depth, buf = [], 0, ""
    tokens = re.split(r"(\{|\})", field)
    flat = ""
    for t in tokens:
        if t == "{":
            depth += 1
        elif t == "}":
            depth -= 1
        flat += t
    # simple split is safe once braces are balanced in practice
    for chunk in re.split(r"\s+and\s+", field):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


def parse_bib(text):
    """Minimal BibTeX parser: handles nested braces and quoted values."""
    entries = []
    i, n = 0, len(text)
    while i < n:
        at = text.find("@", i)
        if at == -1:
            break
        m = re.match(r"@(\w+)\s*\{", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            i = at + 1
            continue

        start = at + m.end()          # just past the opening brace
        depth, j = 1, start
        while j < n and depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        body = text[start:j - 1]
        raw = text[at:j]

        key, _, rest = body.partition(",")
        fields = {}
        # split top-level commas
        depth, cur, items = 0, "", []
        in_q = False
        for ch in rest:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == '"' and depth == 0:
                in_q = not in_q
            if ch == "," and depth == 0 and not in_q:
                items.append(cur)
                cur = ""
            else:
                cur += ch
        items.append(cur)

        for item in items:
            if "=" not in item:
                continue
            k, _, v = item.partition("=")
            k = k.strip().lower()
            v = v.strip().rstrip(",").strip()
            if v.startswith("{") and v.endswith("}"):
                v = v[1:-1]
            elif v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            if k:
                fields[k] = v

        fields["_type"] = etype
        fields["_key"] = key.strip()
        fields["_raw"] = raw.strip()
        entries.append(fields)
        i = j
    return entries


def to_record(e, alias_map):
    authors_raw = split_authors(e.get("author", "")) if e.get("author") else []
    names = [display_name(a) for a in authors_raw]
    ids = []
    for a in authors_raw:
        s = slug(a)
        ids.append(alias_map.get(s, s))

    venue = ""
    for f in VENUE_FIELDS:
        if e.get(f):
            venue = clean(e[f])
            break

    url = e.get("url") or e.get("doi") or ""
    if url and url.startswith("10."):
        url = "https://doi.org/" + url
    if not url and e.get("eprint") and "arxiv" in (e.get("archiveprefix", "") or "").lower():
        url = "https://arxiv.org/abs/" + clean(e["eprint"])

    year = clean(e.get("year", "")) or "n.d."
    try:
        year_sort = int(re.sub(r"\D", "", year) or 0)
    except ValueError:
        year_sort = 0

    rec = {
        "key": e["_key"],
        "type": e["_type"],
        "year": year,
        "year_sort": year_sort,
        "title": clean(e.get("title", "Untitled")),
        "authors": names,
        "author_ids": ids,
        "venue": venue,
        "url": url,
        "bibtex": e["_raw"],
    }
    for opt in ("note", "volume", "number", "pages"):
        if e.get(opt):
            rec[opt] = clean(e[opt])

    # `keywords = {vla, world-models}` lets a research page pull its own papers
    kw = e.get("keywords") or e.get("keyword") or ""
    rec["keywords"] = [k.strip().lower() for k in re.split(r"[;,]", clean(kw)) if k.strip()]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if publications.yml is stale")
    args = ap.parse_args()

    alias_map = {}
    if os.path.exists(ALIASES):
        with open(ALIASES) as fh:
            loaded = yaml.safe_load(fh) or {}
        for canonical, variants in (loaded.get("aliases") or {}).items():
            for v in variants or []:
                alias_map[slug(v)] = canonical

    files = sorted(glob.glob(os.path.join(BIB_DIR, "*.bib")))
    if not files:
        print(f"No .bib files in {os.path.relpath(BIB_DIR, ROOT)}/", file=sys.stderr)

    records, seen = [], set()
    for path in files:
        with open(path, encoding="utf-8") as fh:
            for e in parse_bib(fh.read()):
                if e["_key"] in seen:
                    print(f"  duplicate key skipped: {e['_key']}", file=sys.stderr)
                    continue
                seen.add(e["_key"])
                records.append(to_record(e, alias_map))

    records.sort(key=lambda r: (-r["year_sort"], r["title"].lower()))

    header = (
        "# GENERATED FILE — do not edit by hand.\n"
        "# Source: _bibliography/*.bib\n"
        "# Regenerate with:  python3 tools/bib2yml.py\n"
    )
    body = yaml.safe_dump(records, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100)
    out = header + body

    if args.check:
        current = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if current != out:
            print("publications.yml is out of date — run: python3 tools/bib2yml.py",
                  file=sys.stderr)
            return 1
        print("publications.yml is up to date")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(out)

    by_author = {}
    for r in records:
        for a in r["author_ids"]:
            by_author[a] = by_author.get(a, 0) + 1

    print(f"{len(records)} publication(s) -> {os.path.relpath(OUT, ROOT)}")
    if by_author:
        print("author ids found (use these as `author_id:` in _members/*.md):")
        for a, c in sorted(by_author.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {a:<28} {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
