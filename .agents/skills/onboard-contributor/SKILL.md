---
name: onboard-contributor
description: Onboard a new contributor: create inbox, generate clipper template, and produce a welcome message
---

# Skill: onboard-contributor

Onboard a new contributor. Creates the local inbox folder (`../inbox/` — raw/processed/staging, never git), generates a personal Obsidian Web Clipper template and prints a ready-made welcome message.

## When to use

Run this skill when a new team member is going to contribute raw material to the wiki.

## Input

Ask the contributor if not provided:

1. **Name** — first name in lowercase, without spaces (e.g. `jan`, `fatima`).
2. **Role** — `contributor` (runs skills, adds notes; does not edit wiki files and skills directly) or `curator` (may edit skills and the wiki directly and approves merge requests). Default: `contributor`.

Normalize names with spaces or capitals to lowercase-with-hyphens (e.g. `Jan de Vries` → `jan-de-vries`). Confirm this with the user before continuing.

## Required tools

| Tool | Used for |
|---|---|
| Git | Claude Code uses it for the wiki repo |
| uv | Python environment for the skills' helper scripts |
| `glab` or `gh` | The share skill uses this to create merge requests |
| Obsidian | Writing notes and reviewing draft pages |
| Obsidian Web Clipper | Saving web pages to the inbox |

Contributors do not use git themselves: the skills handle all git operations on the wiki repo (the only repo in this system; `../inbox/` is a plain folder without git). For `glab`/`gh` the contributor logs in once themselves. A token must never end up in the chat with Claude Code.

## Steps

### 0. Make sure uv is installed

The helper scripts of these skills run through [uv](https://docs.astral.sh/uv/). It takes care of a Python installation itself, so the contributor does not need a system Python. Check whether it is already present:

```bash
uv --version
```

If not, install it:

```bash
# mac / linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After that no separate Python installation step is needed: `uv run <script>.py` sets up the right Python version (pinned via `.python-version` and `pyproject.toml`) and a `.venv` on first use.

### 1. Make sure the git CLI is installed and authenticated

The share skill creates a merge request automatically. Without a logged-in CLI that step fails. Check `glab --version` (GitLab) or `gh --version` (GitHub) and install if needed:

```bash
# mac
brew install glab    # or: brew install gh

# windows (scoop)
scoop install glab   # or: scoop install gh
```

The contributor logs in themselves, in their own terminal and not via Claude Code. A token is a secret; if someone pastes it in the chat, it stays in the session transcript forever.

```bash
glab auth login --hostname <GIT-HOST>
# or
gh auth login
```

Check together that it worked with `glab auth status` or `gh auth status`.

### 2. Run the onboarding script

The remaining steps (inbox folder, Obsidian settings, clipper template, log row, welcome message) are pure templating without judgment. Run this instead of doing them by hand:

```bash
uv run .agents/skills/onboard-contributor/onboard_contributor.py \
  --name <name> --role <contributor|curator>
```

The script:
- normalizes the name (confirm this with the contributor if it differs from the raw input)
- creates `../inbox/raw/`, `../inbox/processed/`, `../inbox/staging/` and `../inbox/templates/` next to this repo (or reports that they already exist): purely local, no git
- copies `schema/obsidian-templates/inbox-note.md` to `../inbox/templates/inbox-note.md` (only if it does not exist yet)
- copies `schema/obsidian-templates/{app,templates,hotkeys}.json` to `../inbox/.obsidian/` (local, not committed; always overwritten)
- generates `schema/clipper-templates/wiki-clipper-<name>.json` from `_base.json` (stamps every clip with `contributor: <name>` in the frontmatter)
- adds a row to `wiki/log.md` (directly below the separator row, with today's date)
- prints the complete welcome message (pass this on verbatim to the contributor) and a summary of what was created

Use `--dry-run` to preview without writing. A real run overwrites the machine-local `.obsidian` config, which should only happen once per person.

With `--role curator` the script prints a separate warning that the "what you do / don't do" section in the welcome message is written for contributors. Adjust that section manually for a curator (who may edit `wiki/` and `.agents/skills/` directly and approve MRs).

## Edge cases

- **Name already exists:** the script detects this itself (skips creating the inbox folders if they already exist, regenerates the clipper template and logs "inbox already existed"). Every contributor onboards on their own machine, so `../inbox/` is not per name: its existence only means that this machine has been set up before.
- **Name with spaces or capitals:** normalize to lowercase-with-hyphens and confirm this with the user before continuing.
- **First clone:** if the repo has not been cloned on the contributor's machine yet, use `git clone <REPO-URL>`. This is a one-time step; `../inbox/` has no git and is created by the onboarding script itself.
