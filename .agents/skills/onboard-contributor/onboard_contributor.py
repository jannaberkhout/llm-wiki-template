#!/usr/bin/env python3
"""Mechanical steps for the onboard-contributor skill. See SKILL.md.

Unlike the lint helper, this script DOES write files -- the steps here are
pure templating with zero judgment (create folders, substitute a name into
JSON/template files, append a log row), and the touched files are either
untracked local config (../inbox/.obsidian/ -- ../inbox/ has no git at all)
or trivial per-person templates.

Run via uv (see SKILL.md step 0 for installing uv first):

    uv run .agents/skills/onboard-contributor/onboard_contributor.py \\
        --name "Jan de Vries" --role contributor [--dry-run]

--dry-run prints every planned write without touching disk -- use it to
preview, or when testing this script itself (a real run overwrites the
machine-local .obsidian/*.json, which is meant to happen at most once per
person per machine).

Still the agent's job: asking for/confirming Input (name/role), the
step-0 uv-install check, and relaying the printed welcome message +
summary to the contributor.
"""
import argparse
import datetime
import os
import re
import sys

RAW = os.path.join("..", "inbox")
WIKI = "wiki"
SCHEMA = "schema"


def normalize_name(raw):
    name = raw.strip().lower()
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-z0-9\-]", "", name)
    return name


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def write_file(path, content, dry_run, label=None):
    label = label or path
    if dry_run:
        print(f"  [dry-run] would write: {label}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  written: {label}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", required=True, help="raw name, normalized to lowercase-with-hyphens")
    p.add_argument("--role", choices=["contributor", "curator"], default="contributor")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not os.path.isdir(WIKI):
        fail(f"run this script from the repo root (no {WIKI}/ found here)")

    name_raw = args.name
    name = normalize_name(name_raw)
    if name != name_raw.strip().lower():
        print(f"Name normalized: '{name_raw}' -> '{name}' (confirm this with the contributor before continuing)\n")

    dry_run = args.dry_run

    # --- step 1: local inbox folders (per machine, not per name) ---
    inbox_existed = os.path.isdir(RAW)
    print("== Step 1: local inbox folder ==")
    if inbox_existed:
        print(f"  {RAW}/ already exists -- skipping creation")
    for sub in ("raw", "processed", "staging", "templates"):
        d = os.path.join(RAW, sub)
        if dry_run:
            print(f"  [dry-run] would create: {d}/")
        else:
            os.makedirs(d, exist_ok=True)
    if not inbox_existed and not dry_run:
        print(f"  created: {RAW}/{{raw,processed,staging,templates}}/")

    obsidian_templates = os.path.join(SCHEMA, "obsidian-templates")

    inbox_note_path = os.path.join(RAW, "templates", "inbox-note.md")
    if not os.path.isfile(inbox_note_path):
        src = os.path.join(obsidian_templates, "inbox-note.md")
        if not os.path.isfile(src):
            fail(f"{src} not found")
        write_file(inbox_note_path, open(src, encoding="utf-8").read(), dry_run)

    # --- step 2: obsidian settings (always overwritten, local-only, machine-local) ---
    print("\n== Step 2: Obsidian settings (local, not committed) ==")
    for name in ("app.json", "templates.json", "hotkeys.json"):
        src = os.path.join(obsidian_templates, name)
        if not os.path.isfile(src):
            fail(f"{src} not found")
        write_file(os.path.join(RAW, ".obsidian", name), open(src, encoding="utf-8").read(), dry_run)

    # --- step 3: personal clipper template ---
    print("\n== Step 3: personal clipper template ==")
    base_path = os.path.join(SCHEMA, "clipper-templates", "_base.json")
    if not os.path.isfile(base_path):
        fail(f"{base_path} not found")
    base_content = open(base_path, encoding="utf-8").read()
    clipper_content = base_content.replace("CONTRIBUTOR_NAME", name)
    clipper_path = os.path.join(SCHEMA, "clipper-templates", f"wiki-clipper-{name}.json")
    write_file(clipper_path, clipper_content, dry_run)

    # --- step 4: log entry ---
    print("\n== Step 4: log entry ==")
    log_path = os.path.join(WIKI, "log.md")
    description = "local inbox already existed, Obsidian configured, clipper template generated" if inbox_existed \
        else "local inbox created, Obsidian configured, clipper template generated"
    date_str = datetime.date.today().isoformat()
    if dry_run:
        print(f"  [dry-run] would insert log row in {log_path}: {date_str} | onboard-contributor | {name} | {description}")
    else:
        content = open(log_path, encoding="utf-8").read()
        sep_match = re.search(r"^\|---\|.*\|\n", content, re.MULTILINE)
        if not sep_match:
            fail(f"could not find the table separator row in {log_path} -- add the row manually")
        insert_at = sep_match.end()
        row = f"| {date_str} | onboard-contributor | {name} | {description} |\n"
        new_content = content[:insert_at] + row + content[insert_at:]
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print(f"  row inserted in {log_path} ({date_str})")

    # --- welcome message (step 5) ---
    print("\n== Step 5: welcome message (relay this to the contributor) ==")
    print(f"""
**Your onboarding is complete, {name}!**

The following was created for you automatically:
- `../inbox/` next to this repo (`raw/`, `processed/`, `staging/`) — a plain folder, no git. New notes and attachments go to `raw/`
- Obsidian settings configured (app.json, templates.json, hotkeys.json)
- Personal clipper template: `wiki-clipper-{name}.json` (stamps every clip with `contributor: {name}`)

**Set up the git CLI (needed for the share skill, which uses it to create a merge request automatically)**

Check whether `glab` (GitLab) or `gh` (GitHub) is already installed:

```bash
glab --version   # or: gh --version
```

If not, install it (e.g. `brew install glab` on mac, `scoop install glab` on windows) and then log in yourself, in your own terminal (not via Claude Code):

```bash
glab auth login --hostname <GIT-HOST>   # or: gh auth login
```

Never paste a token in a message to Claude Code — the token would then stay in the session transcript forever.

**Set up Obsidian (if you haven't already)**

Download and install Obsidian from https://obsidian.md/download.

Then open both folders as vaults — you need both:

1. Open Obsidian → **Open folder as vault** → select the `../inbox/` folder next to this repo
   - New notes and attachments automatically go to `raw/`
   - The `inbox-note` template is available via **Ctrl+T**
2. Also add the wiki repo: **Open another vault → Open folder as vault** → select the cloned wiki folder
   - This is the curated wiki — here you read what has already been published

**Set up the Obsidian Web Clipper (for saving web pages)**

Install the extension from https://obsidian.md/clipper (Chrome, Firefox, Safari or Edge).

After installing, go through these steps in the extension settings:

1. **Add vault:** Settings → Vaults → add the `../inbox/` vault
2. **Import template:** Settings → Templates → Import → select `schema/clipper-templates/wiki-clipper-{name}.json` from the wiki repo
3. **Set default vault:** make sure new clips are written to the `../inbox/` vault (not to the wiki repo)

---

**How the system works**

The system has two layers:

- **../inbox/** — your personal workspace, purely local on this machine. Here you put raw notes, clips and scribbles, and review drafts before you share them. Nobody else reads this directly, and it is never in git.
- **The wiki repo** — the shared, curated wiki. Only curated and approved content lives here. This is what the team reads and consults.

**The documentation flow**

```
../inbox/raw/          →  ../inbox/staging/      →  wiki/
  (your raw input)         (draft after ingest)      (published)

  [you write]              [ingest-note skill]       [share skill + MR]
```

1. Create a note in `../inbox/raw/` in Obsidian (naming convention: `YYYY-MM-DD-topic.md`)
2. Run the **ingest-note skill** in Claude Code — Claude reads your notes, structures them as wiki pages and puts drafts ready in `../inbox/staging/`
3. Review the drafts in Obsidian and adjust where needed
4. Run the **share skill** — the drafts are pushed as a branch to the wiki repo
5. The curator reviews the MR and merges to main

**Available skills**

| Skill | What it does |
|---|---|
| `ingest-note` | Processes raw notes from your inbox into structured drafts in staging |
| `share` | Pushes approved staging drafts as a branch to the wiki repo |
| `lint` | Runs a health check on the wiki and produces a prioritized report |
| `onboard-contributor` | Onboards a new contributor (local inbox, Obsidian settings, clipper template) |
| `answer-from-wiki` | Answers questions based on the wiki |
| `update-wiki` | Syncs the wiki with main and shows what is new since your last sync |

**Claude as a knowledge assistant**

You can ask Claude Code at any time to search the wiki and write new notes for you. For example:

- *"Summarize what the wiki says about [topic]"*
- *"Write a new note about [topic] and put it in my inbox"* — Claude then writes a .md file to `../inbox/raw/`

**What you do and don't do as a contributor**

Do:
- Add files to `../inbox/raw/`
- Run all skills via Claude Code
- Review staging in Obsidian
- Ask Claude to look up wiki content or write notes

Don't:
- Edit wiki files (`wiki/`) or skill files (`.agents/skills/`) directly
- Approve MRs — that is the curator's job

Questions? Ask the curator.
""")

    if args.role == "curator":
        print("NOTE: role=curator -- the \"what you do and don't do\" section above is written for contributors. "
              "Curators may edit wiki/ and .agents/skills/ directly and approve MRs -- adjust the last "
              "section manually for a curator onboarding (this is not handled in the skill/template itself).")

    # --- summary (step 6) ---
    print("\n== Step 6: summary ==")
    print(f"Onboarding {name} {'checked (dry-run, nothing written)' if dry_run else 'completed'}.\n")
    print("Created:" if not inbox_existed else "Created/checked:")
    print("  - ../inbox/{raw,processed,staging}/" + ("  (already existed)" if inbox_existed else ""))
    print("  - ../inbox/.obsidian/app.json  (raw/ as default location — not committed)")
    print("  - ../inbox/.obsidian/templates.json  (templates folder — not committed)")
    print("  - ../inbox/.obsidian/hotkeys.json  (Ctrl+T for Insert template — not committed)")
    print(f"  - schema/clipper-templates/wiki-clipper-{name}.json")
    print(f"\nLog updated: {log_path}" + (" (dry-run: not actually written)" if dry_run else ""))


if __name__ == "__main__":
    main()
