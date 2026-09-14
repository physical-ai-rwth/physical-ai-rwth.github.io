# Bibliography

`papers.bib` is the **source of truth** for publications. After editing it, run:

```bash
python3 tools/bib2yml.py
```

That regenerates `_data/publications.yml`, which the site actually reads.
**Do not edit that YAML by hand** — it is overwritten on every run.

## Why a script instead of jekyll-scholar

GitHub Pages builds from a branch and does **not** execute custom Jekyll plugins, so
`jekyll-scholar` cannot run there. Resolving the `.bib` to plain data beforehand keeps
BibTeX as the source of truth while staying plugin-free.

Commit both `papers.bib` and the generated `publications.yml`.

## Listing a person's papers automatically

The converter turns each BibTeX author into an id: `Wu, Yuli` and `Yuli Wu` both become
`yuli-wu`. Put that id in the member's file:

```yaml
# _members/yuli-wu.md
author_id: "yuli-wu"
```

Their page then lists every matching paper, newest first, with their own name in bold.
Nothing else to maintain — add a paper to the `.bib`, rerun the script, and it appears on
every co-author's page and on `/publications/`.

Running the script prints the ids it found:

```
author ids found (use these as `author_id:` in _members/*.md):
  yuli-wu                      3
  volkmar-schulz               2
```

### Name variants

Initials and other forms the converter cannot guess go in `_data/author_aliases.yml`:

```yaml
aliases:
  yuli-wu:
    - "Y. Wu"
    - "Wu, Y."
```

## What the converter handles

- Accents and escapes — `M{\"u}ller` → Müller, `\&` → &, `\ss` → ß
- Nested braces, and `{Van der Berg}` kept as one surname
- Inline maths in titles — `$\alpha$` → α, `$L_2$` → L₂, `$10^6$` → 10⁶
- arXiv `eprint` + `archivePrefix` → a link; bare `doi` → a doi.org link
- Venue from `booktitle` / `journal` / `publisher` / `school`
- Duplicate keys are skipped with a warning

## Checking it is current

```bash
python3 tools/bib2yml.py --check
```

Exits non-zero if the YAML no longer matches the `.bib` — useful in CI or a pre-commit
hook so a stale list can't be committed.
