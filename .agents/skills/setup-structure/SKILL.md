---
name: setup-structure
description: Adapt the wiki's folder structure to the team: choose content types (for example customers, conversations, candidates instead of projects and decisions), generate folders, templates and dashboard, and update AGENTS.md and README.md. Use when setting up a new team wiki or when the team wants to change its layout.
---

# setup-structure

The wiki is built from **content types**. Each type is a folder under `wiki/` with its own template. Which types exist is defined in `schema/structure.json`. The template ships three starter types (`projects`, `decisions`, `ways-of-working`), but a team that does not work project-based adapts them: a sales team might have `customers` and `conversations`, a staffing agency `customers`, `candidates` and `conversations`.

This skill holds the conversation, adjusts `structure.json` and lets the script `setup_structure.py` create the files. The script never deletes anything.

## When

- When setting up the wiki (before it has any content) — then everything can be changed freely.
- Later, when the team wants to add, rename or drop a type. If there is already content, work carefully (see "Existing wiki").

Only the curator runs this skill.

## Steps

### 0. Team name and repo URL (first run only)

If the repo still contains the placeholders `<TEAM-NAME>` and `<REPO-URL>` (check with `grep -rn "<TEAM-NAME>\|<REPO-URL>" --exclude-dir=.git --exclude-dir=.venv .`), ask the curator for:

1. the **team name** (as it should appear in titles and texts);
2. the **repo URL** (the clone URL, for example `https://github.com/org/team-wiki.git`; `git remote get-url origin` can suggest it).

Then run:

```bash
uv run .agents/skills/setup-structure/setup_structure.py identity --team "Team name" --repo-url "https://..." --dry-run   # shows which files change
uv run .agents/skills/setup-structure/setup_structure.py identity --team "Team name" --repo-url "https://..."
```

This replaces the placeholders in README, AGENTS.md, the other skills and the wiki pages, and records both values under `"team"` in `schema/structure.json`. It also points the git remote `origin` at the new URL (`git remote set-url`, or `git remote add` if there is no origin yet). That only changes local git config; nothing is pushed. Tell the curator what will happen to the remote and add `--no-remote` if they would rather keep it as it is. If the placeholders are already gone, skip this step.

### 1. Understand how the team works

Ask the questions one at a time, in plain language, and adapt to the answers. Not all at once.

1. **What does the work revolve around?** What are the things the team keeps documentation about? (projects, customers, candidates, assignments, products, conversations, decisions, ...)
2. **Which of those are a case, and which are individual documents?**
   - *Case*: a thing that gets its own folder with an `index.md` and possibly attachments, and that changes over time (a customer, a candidate, a project).
   - *File*: a single page with a date that does not change (a conversation, a decision, a note).
3. **Per type:** what is it called (singular and plural)? Which statuses does it go through? Which extra data belongs on every page (for a conversation, for example: which customer, which date, type of conversation)? Which headings must a page have?
4. **Which cases belong on the dashboard** (`wiki/index.md`)? Usually the main type (customers, projects).
5. **Is a ways-of-working folder needed?** (Usually yes: agreements and processes.)

### 2. Watch out for personal data

For types about people (candidates, customer contacts): names of contributors appear only in the frontmatter, and the wiki has a wide circle of readers. Ask the curator how to handle personal data of third parties (GDPR: retention period, who may read, role or initials instead of full name). Record the answer in the `description` of the type, so ingest-note follows it. If the data is too sensitive for the wiki to handle, say so and suggest keeping that type out of the wiki.

### 3. Show the proposal and wait for approval

Show a table and wait for confirmation before writing:

```
Proposal for the structure of <TEAM-NAME>:

| Folder | Kind | On dashboard | Extra fields | Statuses |
|---|---|---|---|---|
| wiki/customers/ | folder | yes | industry, account manager | prospect · active · inactive |
| wiki/conversations/ | file | no | customer (required), date (required), kind | — |
| wiki/ways-of-working/ | file | no | — | — |
```

### 4. Edit `schema/structure.json`

Edit the file. Fields per type:

| Field | Meaning |
|---|---|
| `key` | folder name under `wiki/` (lowercase letters, digits, hyphens) |
| `label`, `label_plural` | display name singular and plural |
| `description` | what belongs here; goes into the folder README and README.md |
| `short` | optional: short line for AGENTS.md |
| `layout` | `folder` (folder per item, with `index.md`) or `file` (individual pages) |
| `naming` | file name or path pattern, for example `<slug>/index.md` or `YYYY-MM-DD-<customer>-<topic>.md` |
| `subfolders` | folder layout only: fixed subfolders, for example `["conversations", "attachments"]` |
| `template` | file name in `schema/`, or `null` for no template |
| `status_values` | optional: list of allowed statuses (goes into the template) |
| `sections` | optional: headings of the template |
| `fields` | extra frontmatter fields: `{"name", "hint", "required"}` |
| `validate` | `true`: the lint skill checks the required fields |
| `in_index` | folder layout only: gets a table in `wiki/index.md` |
| `index_columns` | extra columns in that table, between title and status |
| `renamed_from` | only when renaming: the old folder name; the script does `git mv` |

Use `renamed_from` to rename an existing type instead of deleting it and creating it again.

### 5. Check and apply

```bash
uv run .agents/skills/setup-structure/setup_structure.py check    # writes nothing, shows what would happen
uv run .agents/skills/setup-structure/setup_structure.py apply
```

`apply` does the following:
- creates `wiki/<key>/` and a `README.md` per type;
- generates `schema/<template>` for types whose file does not exist yet;
- refreshes the folder lists in `AGENTS.md` and `README.md`;
- recreates `wiki/index.md` if it has no rows yet.

Hand-edited files are not overwritten. You recognise generated files by the first line `<!-- generated by setup-structure ... -->`; remove that line as soon as you make your own changes.

### 6. Clean up the rest (the script does not do this)

- Read the output of `check`/`apply` and resolve all `NOTE` lines. For a renamed type the old `README.md` stays in place (it was hand-edited): rewrite it, or remove the manual version and run `apply` again.
- Folders of types that have been dropped: let the team decide whether the content goes to `wiki/archive/`. Do not delete anything yourself.
- Starter templates that no longer fit (`schema/project-template.md`, `schema/decision-template.md`): delete them only if no type still uses them.
- Search `AGENTS.md`, `README.md` and `.agents/skills/*/SKILL.md` for examples that still talk about projects or decisions and adjust them if they cause confusion. The skills read the types themselves from `structure.json`; the examples are only illustration.
- Run `uv run .agents/skills/lint/check_structure.py` and check that there are no blockers.
- Add a row to `wiki/log.md`: `| YYYY-MM-DD | setup-structure | — | <summary of the chosen types> |`
- Commit on a separate branch and let the curator merge the change.

## Existing wiki

If the wiki already has content, only make **additions and renames**. Dropping a type means: moving pages to `wiki/archive/` (with `git mv`), updating links and running `lint`. Do not do that in the same step as other changes.
