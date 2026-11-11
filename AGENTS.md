# AGENTS.md — Team Wiki

This file is the leading instruction set for every agent working in this repository. Read it before you do anything. Do not rewrite it without the curator's approval.

> **Template:** this is the basis for a team wiki. After copying, search for `<TEAM-NAME>` and `<REPO-URL>` and fill them in.

## What this repository is

The curated wiki of <TEAM-NAME>: synthesized, team-oriented knowledge, derived from raw material that a contributor first collects locally on their own machine. Raw material never goes into git. It lives in a plain local folder `../inbox/` next to this repo. The wiki has a wider readership than that local folder and is therefore anonymized at page level.

## Local inbox + wiki layout

```
../inbox/                          (local only — never committed; each contributor has their own folder on their own machine)
  raw/                             raw material that still has to be processed
  processed/                       moved here after ingest (archive of the originals)
  staging/                         agent-generated drafts awaiting approval

./                                 (this repo — git, wider readership)
  wiki/index.md                    dashboard of all cases — always keep current
  wiki/log.md                      append-only log
  wiki/projects/<slug>/            one subfolder per project
                                    index.md    the project page
                                    research/   research notes and reports
                                    attachments/ other documents
  wiki/decisions/                  decisions per project
  wiki/ways-of-working/            how the team works: processes, roles, agreements, principles
  wiki/lint/                       monthly lint reports
  wiki/archive/                    superseded documents, kept for reference
  schema/                          page templates and conventions
  .agents/skills/                  available skills; some with a *.py helper (see below)
  pyproject.toml, .python-version  uv environment for those helpers (stdlib only, no dependencies)
```

`../inbox/` is a plain folder, not a git repository. There is nothing to fetch, merge or push. This is deliberate: raw material and draft pages are personal and stay on the contributor's machine. The only git operations in this system are on this repo, at the final `share` step.

**Skill helper scripts**
Some skills have a stdlib-only Python script next to their `SKILL.md` (`lint/check_structure.py`, `setup-structure/setup_structure.py`, `onboard-contributor/onboard_contributor.py`) that does the mechanical part of the skill: checks, creating files. Run them with `uv run .agents/skills/<skill>/<script>.py ...` (see the `SKILL.md` for the exact arguments). On first use `uv` sets up Python and a `.venv`. The `SKILL.md` says which parts remain with the agent: judgment, human confirmation, git commits.

## Content flow

```
../inbox/raw/  →  ingest-note skill  →  ../inbox/staging/  →  share skill  →  wiki/
  (raw input)       (always, local)       (contributor reviews    (explicit        (team sees
                                           here, local)            approval)        this)
```

The wiki only receives content that a contributor has explicitly approved. Staging is the personal review space: a local folder, invisible to the team and never in git.

## Rules — always follow

**Reading raw material**
- Read from `../inbox/raw/` and never change anything there.
- After a successful ingest, move a file with `mv` to `../inbox/processed/`. Never delete raw files.
- Meeting notes (`type: meeting` in the frontmatter) require `share: approved` before ingest. If that is missing, or `share: pending` is set, skip the file and note it in the log.
- All other inbox files are processed by default: whoever puts something in `raw/` shares it by doing so.

**Writing wiki pages**
- Contributor names appear only in the frontmatter (`contributed-by:`), never in the page text. This is not optional.
- Sources appear in the frontmatter (`sources:`) as paths relative to `../inbox/`, for example `raw/2026-07-29-topic.md`.
- Use the templates in `schema/` for new pages. Do not invent frontmatter fields.
- Do not rewrite existing page texts in their entirety. Prefer adding sections or updating specific fields.

**Log**
- After every ingest or curation action, add a row to the table in `wiki/log.md`, directly below the header row (newest at the top). Format: `| YYYY-MM-DD | <skill> | <contributor or —> | <description> |`
- Never delete or rewrite log lines.

**Index**
- Update `wiki/index.md` as soon as a case is created or the `status` of a case changes. A case is an item of a type with `layout: folder` and `in_index: true` in `schema/structure.json` (in the default template: a project).

**Folder structure**
- The folders under `wiki/` (the content types) are listed in `schema/structure.json`. That file is the source of truth; read it to know where a kind of page belongs and which template goes with it. Do not invent your own folders.
- Words like "project" and "decision" in these instructions and in the skills are the concepts from the default template. If the team has chosen other types, read them as the types from `structure.json`.
- Change the structure only via the `setup-structure` skill, with the curator's approval.

**Conflicts**
- Never silently drop content. If two sources contradict each other, write both in the page under a clear `> **Conflict:**` block and set `status: conflict` in the frontmatter.

## Answering questions about the wiki

When a user asks a question that can be answered from the wiki (about cases, decisions or other knowledge in `wiki/`), load the `answer-from-wiki` skill first. Do not answer from memory: always search the wiki.

## Available skills

- `.agents/skills/setup-structure/` — adapt the wiki's folder structure to the team (content types, templates, index); once at setup, afterwards only by the curator
- `.agents/skills/ingest-note/` — process inbox files into draft pages in staging (local, `../inbox/`)
- `.agents/skills/share/` — promote reviewed staging pages to the wiki repo and push for review by the curator
- `.agents/skills/lint/` — monthly health check: structural (broken links, orphan pages, schema, index) and semantic (contradictions, outdated claims)
- `.agents/skills/onboard-contributor/` — onboard a new contributor: create the inbox folder and generate a personal clipper template
- `.agents/skills/answer-from-wiki/` — answer questions based on the wiki
- `.agents/skills/update-wiki/` — sync the wiki with main and show what is new
