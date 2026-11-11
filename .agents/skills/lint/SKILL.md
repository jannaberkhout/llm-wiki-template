---
name: lint
description: Run a health check on the wiki and produce a prioritised report of structural and semantic issues
---

# Skill: lint

Run a health check on the wiki and produce a prioritised report of structural and semantic issues. Meant to run monthly and be discussed briefly with the team.

## When to use

- Monthly, as part of the lint + retro rhythm
- Before promoting a large batch of pages to main
- On request, when the curator suspects drift or inconsistency

## Output

A structured report with findings by severity. Save it as `wiki/lint/YYYY-MM-DD-lint-report.md` and add a row to `wiki/log.md`. Do not fix findings automatically: only report, so the curator decides what happens.

---

## Checks

Run all checks below in order. Collect all findings before writing the report.

**The structural checks (S1-S6) are automated.** Run `uv run .agents/skills/lint/check_structure.py` from the repo root and use the output directly. Do not re-derive S1-S6 by reading files by hand: that costs tokens for no gain. Apart from stdlib Python 3, the script has no dependencies. If the output looks wrong, fix the script instead of falling back to manual checking.

**Content types:** the terms project, project folder and decision in this skill are the types from the default template. This team's actual types are in `schema/structure.json`; read "project" as a `layout: folder` type with `in_index: true` and "decision" as the individual documents (`layout: file`). The script already does this automatically.

Only the semantic checks (M1-M3) require you to read page content, because they call for judgment the script cannot give. Limit your reading there too: only read the pages within the project or section you are checking, not the whole wiki at once.

---

### Structural checks

#### S1 — Broken wikilinks

Scan every `.md` file under `wiki/` for `[[...]]` patterns. For each link, check whether a file with that name exists anywhere under `wiki/`. Flag every link whose target cannot be found.

Severity: **blocker** — broken links confuse agents and readers.

#### S2 — Orphan pages

List all `.md` files under `wiki/` (except `index.md`, `log.md` and `README.md`). For each file, check whether at least one other page or `wiki/index.md` links to it. Flag every file without incoming links.

Severity: **warning** — orphan pages are impossible to find and probably forgotten.

#### S3 — Schema violations

For every `.md` file under the folders of the types with `validate: true` in `schema/structure.json` (by default `wiki/projects/` and `wiki/decisions/`; excluding `README.md`), check whether the following frontmatter fields are present and non-empty:

- All pages: `title`, `status`, `tags`, `date-created`, `contributed-by`
- Extra required fields per type: the fields with `required: true` under `fields` in `structure.json` (by default for decisions: `project`, `decision`, `date`)

Flag every page with missing or empty required fields.

Severity: **warning** — incomplete metadata breaks index updates and agent routing.

#### S4 — Index consistency

Compare the subfolders of `wiki/projects/` with the projects table in `wiki/index.md`. Flag:
- A project folder with `index.md` that is not in the index table
- A row in the index table without a corresponding project folder

Severity: **warning** — the index is the team's dashboard; drift makes it unreliable.

#### S5 — Status mismatch

For every project page, compare the `status` field in the frontmatter with the status column in `wiki/index.md`. Flag every deviation.

Severity: **warning** — the index should always show the current page status.

#### S6 — Unresolved conflicts

Find all `.md` files under `wiki/` with `status: conflict` in the frontmatter. Show them as pages the curator must resolve.

Severity: **blocker** — conflict pages must never reach main unresolved.

---

### Semantic checks

Run these after all structural checks. Read the relevant pages carefully before passing judgment.

#### M1 — Contradictions within a project case

For every subfolder under `wiki/projects/`, read all pages. Check whether claims contradict each other, for example: the status in the table under History clashes with the `status` in the frontmatter, or two entries draw opposite conclusions about the same question.

Flag concrete contradictions with a quote from each clashing passage.

Severity: **warning** — contradictions mislead the team and agents.

#### M2 — Contradictions between pages

Read all pages under `wiki/projects/` and `wiki/decisions/`. Look for pairs of pages that make directly contradictory claims about the same concept, the same agreement or the same project status. Example: a decision says a project has been stopped, while the project page shows `active`.

Limit the scope: only flag clear, specific contradictions, not differences in emphasis or perspective. When in doubt: do not flag.

Severity: **advisory** — drift between pages comes with a growing wiki; only flag clear cases.

#### M3 — Outdated claims

Look for claims that are probably outdated given other content in the wiki, for example a page that calls something "still to be worked out" or "in development" while another page shows it is finished or abandoned.

Flag the specific claim and the page that contradicts it.

Severity: **advisory** — outdated claims erode trust in the wiki over time.

---

## Report format

Save as `wiki/lint/YYYY-MM-DD-lint-report.md`:

```markdown
---
title: Lint report YYYY-MM-DD
generated-by: <model>, YYYY-MM-DD
tags: [lint]
---

# Lint report YYYY-MM-DD

## Summary

| Severity | Count |
|---|---|
| Blocker | n |
| Warning | n |
| Advisory | n |

## Blockers

### [S6] Unresolved conflict pages
- `wiki/projects/llm-wiki/index.md` — status: conflict

## Warnings

### [S2] Orphan pages
- `wiki/projects/llm-wiki/research/note.md` — no incoming links

### [S3] Schema violations
- `wiki/decisions/2026-07-29-llm-wiki-start-pilot.md` — field `date` empty

### [S4] Index inconsistency
- `wiki/projects/new-project/index.md` — not in wiki/index.md

## Advisories

### [M3] Outdated claims
- `wiki/projects/llm-wiki/index.md` — "pilot still to be worked out" while the decision of 2026-07-29 records the start

## No findings

S1 (broken links): none
M1 (internal contradictions): none
M2 (contradictions between pages): none
```

---

## After the report

Add a row directly below the header row in `wiki/log.md`:
```
| YYYY-MM-DD | lint | — | <n> blockers, <n> warnings, <n> advisories — see wiki/lint/YYYY-MM-DD-lint-report.md |
```

Do not commit or push automatically. Tell the curator:

```
Lint report saved in wiki/lint/YYYY-MM-DD-lint-report.md.
Review the report and commit when you are ready, or say "commit the lint report".
```

## Edge cases

- **Empty wiki:** if there are fewer than 5 pages, skip the semantic checks (M1–M3) and note "too little content for semantic analysis" in the report.
- **Uncertain contradiction:** when in doubt on M1–M3, do not flag. False positives damage trust in the lint report faster than missed findings.
- **Large wiki (50+ pages):** limit M2 and M3 to pages updated in the last 90 days so the check stays manageable. Note that limitation in the report.
