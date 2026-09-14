# CVs

Members have **two** CV surfaces, and both are optional:

| | Field | Where it shows |
|---|---|---|
| Short tabular CV | `cv:` in `_members/*.md` | Rendered on the page itself |
| Full CV PDF | `cv_pdf:` in `_members/*.md` | "Download" button in the sidebar |

The tabular CV is the primary form — most visitors read it without downloading
anything. The PDF is a supplement for people who want the full record.

## Short tabular CV

Put it straight in the member's front matter. Each block is a section; each entry is
a row with the period on the left and the details on the right.

One flat list, newest first — no section grouping.

```yaml
cv:
  - period: "2024 – present"
    title: "Group Leader, Physical AI Lab"
    org: "Chair of Imaging and Computer Vision, RWTH Aachen University"
  - period: "2018 – 2022"
    title: "Dr.-Ing., Electrical Engineering"
    org: "RWTH Aachen University"
    note: "Thesis: Learned Models for Contact-Rich Manipulation"
```

`title` is required; `org` and `note` are optional and omitted cleanly if absent.
Rows render in the order written.

Omit `cv:` entirely and no CV section appears.

The period column is 142pt wide, which comfortably fits forms like `2024 – present`.
On phones the table stacks to one column automatically.

## Full CV PDF

```yaml
cv_pdf: "/assets/cv/jane-doe.pdf"
```

The button only renders if the file actually exists, so a wrong or stale path fails
silently rather than publishing a dead download link. If the button is missing, check
the filename matches the path exactly.

## Placeholders

`yuli-wu.pdf` and `volkmar-schulz.pdf` are **generated placeholders**, not real CVs — a
single branded page stamped PLACEHOLDER, with a footer saying so. Replace them with the
real PDFs, or delete them and drop `cv_pdf:` to rely on the tabular CV alone.

To make one for a new member:

```bash
python3 tools/make_cv_placeholder.py --slug jane-doe \
    --name "Jane Doe, M.Sc." \
    --role "Doctoral Researcher" \
    --email "jane.doe@lfb.rwth-aachen.de"
```

Requires `rsvg-convert` (`brew install librsvg`).

---

# Profile links

Optional, and shown as small chips under the CV download. Known keys fill in the
label for you:

```yaml
links:
  - key: scholar
    url: "https://scholar.google.com/citations?user=..."
  - key: linkedin
    url: "https://www.linkedin.com/in/..."
```

Recognised keys: `scholar`, `linkedin`, `github`, `orcid`, `arxiv`, `x`, `bluesky`,
`mastodon`, `researchgate`, `semanticscholar`, `dblp`, `website`.

For anything else, give your own label:

```yaml
  - label: "Personal site"
    url: "https://example.org"
```

Delete any line you do not want — omit `links:` entirely and no section appears.

---

# Publications

A member's papers are pulled automatically from the bibliography when `author_id:` is
set. To suppress the section for someone who has papers but should not list them:

```yaml
show_publications: false
```
