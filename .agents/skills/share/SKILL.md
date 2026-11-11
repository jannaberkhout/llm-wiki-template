---
name: share
description: Promote reviewed draft pages from staging to the wiki repo and push for curator review
---

# Skill: share

Promote reviewed draft pages from `../inbox/staging/` to the wiki repo and push them to a dated ingest branch for curator review. This is the explicit sharing decision: nothing reaches the wiki repo before this skill runs. `../inbox/` has no git. The only git operations in this skill are on this repo.

## When to use

Run this skill when the contributor has reviewed the staging pages in Obsidian and wants to share all or some of them with the team.

## Input

- **Contributor** — the contributor's name, for the branch name and the log. Ask for it if it cannot be inferred from context.

## Steps

### 0. Sync the wiki with main

Make sure the wiki is up to date so you don't overwrite curator changes.

```bash
git fetch origin
git merge origin/main
```

On merge conflicts: resolve them before continuing.

### 1. Discover staging files

List all files in `../inbox/staging/`:

```
The following draft pages are ready to share:

  - staging/projects/llm-wiki/index.md  →  wiki/projects/llm-wiki/index.md
  - staging/decisions/2026-07-29-llm-wiki-start-pilot.md  →  wiki/decisions/...
  - staging/ways-of-working/meeting-structure.md  →  wiki/ways-of-working/meeting-structure.md

Do you want to share all pages, or only specific ones?
(answer: "all" or give the file names)
```

Wait for the contributor's answer before continuing.

### 2. Copy approved pages to the wiki repo

For each approved staging page:

1. Copy from `../inbox/staging/<path>` to `wiki/<path>` in the wiki repo.
2. If a wiki page already exists at that path, merge the new content into it and do not overwrite. Add new sections and update the `date-updated` field.
3. Remove the file from `../inbox/staging/`.

Do not change staging files that have not been approved.

### 3. Update wiki/index.md

For each shared project page with a new or changed `status`:
- Update the row in the projects table (latest decision, status), or add a row for a new project.

For each shared decision document without an updated project page in the same batch:
- Read the frontmatter (`project:`, `decision:`) and apply the same follow-through `ingest-note` would have: update the wiki project page (status, history, decisions) and the index row. This way a decision document that arrives outside the normal ingest flow is never silently dropped.

### 4. Add to wiki/log.md

Add a row directly below the header row in `wiki/log.md`:

```
| YYYY-MM-DD | share | <contributor> | <staging files> → <wiki pages> |
```

### 5. Look for conflict pages

Search all files under `wiki/` for `status: conflict` in the frontmatter. Include pages added in step 2.

If there are conflict pages, show them as a warning in the summary:

```
⚠️  Conflict pages found — curator action required:
  - wiki/projects/llm-wiki/index.md
```

### 6. Commit, push and create a merge request

No separate confirmation question here: the approval in step 1 (which pages to share) is the confirmation. Continue directly.

```bash
git fetch origin
if git rev-parse --verify origin/ingest/YYYY-MM-DD-<contributor> 2>/dev/null; then
  git checkout ingest/YYYY-MM-DD-<contributor>
  git merge origin/ingest/YYYY-MM-DD-<contributor>
else
  git checkout -b ingest/YYYY-MM-DD-<contributor>
fi
git add wiki/
git commit -m "share: <short description of what was shared>"
git push origin ingest/YYYY-MM-DD-<contributor>
```

Then create a merge request (or pull request) with the CLI of your git platform. Adjust this command to the repo's platform and keep the URL it returns:

```bash
# GitLab
glab mr create \
  --title "share: <short description of what was shared>" \
  --source-branch ingest/YYYY-MM-DD-<contributor> \
  --target-branch main \
  --label "needs-review"

# GitHub
gh pr create \
  --title "share: <short description of what was shared>" \
  --head ingest/YYYY-MM-DD-<contributor> \
  --base main \
  --label "needs-review"
```

### 7. Clean up staging

Only run this if creating the MR/PR in step 6 succeeded and returned a URL. If the push or the MR fails, skip this step: staging stays unchanged, so the contributor can run step 6 again.

Only clean up the traces of sharing, in `../inbox/staging/`:

```bash
find ../inbox/staging -name .DS_Store -delete
find ../inbox/staging -mindepth 1 -type d -empty -delete
```

- Do not delete files that were not shared: drafts the contributor did not approve in step 1 stay, even if they are in the same folder.
- Do not delete the `../inbox/staging/` folder itself.
- `find ... -empty -delete` first removes the deepest empty folders and then also the parents that have become empty.

### 8. Confirm to the contributor

```
Shared. The merge request has been created for the curator:

<URL>
```

If conflict pages were found, remind the curator to resolve them before merging.

## Edge cases

- **No staging files found:** tell the contributor and stop. There is nothing to share.
- **Merge conflict with an existing wiki page:** write both versions in the page under a `> **Conflict:**` block, set `status: conflict` in the frontmatter and flag it in the summary for the curator.
- **The CLI (`glab`/`gh`) returns an authentication error:** the contributor's session has expired or was never set up. Have the contributor log in themselves in their own terminal (never paste a token in the chat) and retry step 6.
