# <TEAM-NAME> Wiki

The shared knowledge base of <TEAM-NAME>. Pages here are curated and anonymized: names appear only in metadata, never in the page content itself.

## Using this template

1. Copy this folder to a new repo and name it after your team.
2. Search the whole repo for `<TEAM-NAME>` and `<REPO-URL>` and fill them in.
3. Run the **setup-structure skill**. It asks how your team works (projects? clients and conversations? candidates?) and adapts the folders, templates, dashboard and instructions accordingly. Doing it by hand also works: edit `schema/structure.json` and run `uv run .agents/skills/setup-structure/setup_structure.py apply`.
4. Adapt the statuses and decision values in the generated templates in `schema/` to your own terms.
5. Appoint a curator and run the **onboard-contributor skill** for yourself.
6. Remove this section from the README.

## New? Start here

**Step 1 — Access**

Ask the curator for access to the repo (<REPO-URL>).

**Step 2 — Onboarding**

Run the **onboard-contributor skill** with your name. It creates two things:

1. Your local inbox folder next to this repo (`../inbox/` with `raw/`, `processed/`, `staging/`). Purely local, never committed.
2. A tailored Obsidian Web Clipper template (`wiki-clipper-<name>.json`).

**Step 3 — Tools**

- **Obsidian** — open the `../inbox/` folder as a vault
- **Obsidian Web Clipper** — install the browser extension and import your `.json` template

## How does contributing work?

```
your inbox     →  ingest skill  →  your staging   →  share skill  →  wiki
(../inbox/raw/,                    (../inbox/staging/,                (here)
 local)                             you review,
                                     local)
```

`../inbox/` is a plain folder, not a git repo. Everything there stays on your own machine.

**Your own notes** — create a `.md` file in `../inbox/raw/` using the naming convention `YYYY-MM-DD-topic.md`. Minimal frontmatter:

```yaml
---
date: 2026-07-29
context: note / research / decision / meeting
---
```

**Web pages** — use the Web Clipper. It saves the page in `../inbox/raw/` with the right frontmatter.

**Meeting notes** — set `type: meeting` and `share: approved` in the frontmatter. Without that approval, ingest skips them.

## From inbox to wiki

1. Put files in `../inbox/raw/` (or via the Web Clipper)
2. Run the **ingest-note skill**: the agent creates draft pages in `../inbox/staging/`
3. Review the drafts in Obsidian
4. Run the **share skill**: approved pages go to a branch in this repo
5. The curator reviews the merge request and merges to main

Nothing reaches the wiki without your explicit choice in step 4 and the curator's approval in step 5.

## What lives where?

| Folder | Contents |
|---|---|
| `wiki/index.md` | Dashboard: all cases with status |
| `wiki/projects/` | One subfolder per project |
| `wiki/decisions/` | Decisions per project |
| `wiki/ways-of-working/` | How the team works: processes, roles, agreements, principles |
| `wiki/log.md` | Log of all agent actions |
| `wiki/lint/` | Monthly quality reports |
| `wiki/archive/` | Superseded documents, kept for reference |
| `schema/` | Templates for new pages |
| `.agents/skills/` | Skills for agents |

## Roles and permissions

| Action | Contributor | Curator |
|---|---|---|
| Add notes to inbox | Yes | — |
| Run ingest-note skill | Yes | — |
| Run share skill | Yes | — |
| Edit wiki files directly | No | Yes |
| Edit skills (`.agents/skills/`) | No | Yes |
| Merge MRs to main | No | Yes |
| Run lint skill | No | Yes |

Wiki files are updated exclusively via skills, never manually by contributors.

## Questions or corrections?

Create an issue in this repo or contact the curator.
