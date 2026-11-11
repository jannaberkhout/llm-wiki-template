---
name: update-wiki
description: Sync the wiki with main and show what's new since the last sync — use when a contributor just wants to update/sync the wiki, without running any other skill
---

# Skill: update-wiki

Sync this repo with `main` and report what has changed. Nothing is written: this is a read-only sync, useful when a contributor wants to catch up before browsing in Obsidian, or wants to know what is new.

## When to use

Run this skill when a contributor asks to "update the wiki" or sync it, or wants to know what is new, without asking for another skill. The other skills already sync themselves as step 0. This skill is for when syncing is the only thing asked.

## Input

None.

## Steps

### 0. Remember the current state

Before fetching, remember the current HEAD and read the current contents of `wiki/log.md`.

```bash
git rev-parse HEAD
```

### 1. Sync with main

```bash
git fetch origin
git merge origin/main
```

On merge conflicts: resolve them before continuing.

### 2. Determine whether anything changed

Compare the HEAD from before step 1 with the current HEAD.

- **Unchanged:** report "The wiki is already up to date. No new changes." and stop.
- **Changed:** continue to step 3.

### 3. Show a summary of what is new

Compare the contents of `wiki/log.md` from before and after the merge. Show the rows that are new at the top of the table. Those are exactly the actions other contributors or the curator have taken since the last sync.

```
The wiki has been updated. New since your last sync:

| 2026-09-05 | share | someone-else | ... |
| 2026-09-04 | share | somebody | ... |
```

**Fallback (rare):** if `wiki/log.md` itself did not change while HEAD did (e.g. a curator fix without a log row), use `git log --oneline <old-HEAD>..HEAD` and show the commit subjects as the summary.

## Edge cases

- **Merge conflicts:** resolve them as in the other skills and mention in the summary which files had a conflict and how you resolved it.
- **`wiki/log.md` itself has a conflict:** resolve that first and then use the fallback (`git log --oneline`) for the summary, instead of comparing table rows on a file that just had a conflict.
- **Not in the repo root:** report this and stop. This skill expects you to work in the root of the wiki repo.
