#!/usr/bin/env python3
"""Structural lint checks (S1-S6) for the team wiki. See SKILL.md for the
full check definitions and severities. Run from the repo root:

    uv run .agents/skills/lint/check_structure.py

Prints a compact findings list grouped by check code. No external
dependencies (stdlib only) so it runs anywhere Python 3 is available.

This script does NOT do the semantic checks (M1-M3) in SKILL.md -- those
need judgment and content reading, and stay the agent's job. This script
exists purely to keep the mechanical structural checks out of the agent's
context window.
"""
import json
import os
import re
import sys

WIKI = "wiki"
CONFIG = os.path.join("schema", "structure.json")

# Content types come from schema/structure.json. If that file is missing, fall
# back to the default template (projects + decisions).
_DEFAULT_TYPES = [
    {"key": "projects", "layout": "folder", "validate": True, "fields": [], "in_index": True},
    {"key": "decisions", "layout": "file", "validate": True, "in_index": False,
     "fields": [{"name": n, "required": True} for n in ("project", "decision", "date")]},
]


def load_types():
    try:
        with open(CONFIG, encoding="utf-8") as fh:
            return json.load(fh)["types"]
    except FileNotFoundError:
        return _DEFAULT_TYPES


TYPES = load_types()


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def frontmatter(content):
    """Return (fm_text, body) or (None, content) if no frontmatter block."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not m:
        return None, content
    return m.group(1), m.group(2)


def fm_field(fm_text, key):
    """Best-effort extraction of a scalar or inline-list frontmatter field.
    Returns the raw string value (unstripped of brackets/quotes) or None if
    absent. Does not handle multi-line YAML lists (e.g. `sources:` blocks)."""
    if fm_text is None:
        return None
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm_text, re.MULTILINE)
    if m is None:
        return None
    return m.group(1).strip()


def fm_list(fm_text, key):
    """Parse an inline `key: [a, b]` list into a Python list of strings.
    Returns [] if the field is absent or empty."""
    raw = fm_field(fm_text, key)
    if not raw:
        return []
    m = re.match(r"^\[(.*)\]$", raw)
    if not m:
        # multi-line list (- item) or a bare scalar; treat scalar as single item
        return [raw] if raw else []
    inner = m.group(1).strip()
    if not inner:
        return []
    return [x.strip().strip("\"'") for x in inner.split(",")]


def all_md_files():
    out = []
    for root, _, fnames in os.walk(WIKI):
        for fn in fnames:
            if fn.endswith(".md"):
                out.append(os.path.normpath(os.path.join(root, fn)))
    return sorted(out)


def is_readme(path):
    return os.path.basename(path) == "README.md"


def is_root_index(path):
    return os.path.normpath(path) == os.path.normpath(os.path.join(WIKI, "index.md"))


def is_log(path):
    return os.path.normpath(path) == os.path.normpath(os.path.join(WIKI, "log.md"))


def check_s1_s2(files):
    """Broken wikilinks (S1) and orphan pages (S2)."""
    name_map = {}
    for f in files:
        content = read(f)
        fm_text, _ = frontmatter(content)
        base = os.path.splitext(os.path.basename(f))[0].lower()
        name_map.setdefault(base, []).append(f)
        for alias in fm_list(fm_text, "aliases"):
            name_map.setdefault(alias.lower(), []).append(f)

    md_link_re = re.compile(r"\[[^\]]*\]\(([^)]+\.md)[^)]*\)")
    wiki_link_re = re.compile(r"\[\[([^\]|]+?)(?:\\?\|[^\]]*)?\]\]")

    broken = []  # (source_file, raw_target)
    incoming = {f: set() for f in files}
    # lint reports are meta-content: a mention inside one doesn't count as a
    # real navigational link for orphan purposes.
    referrer_files = [f for f in files if not f.startswith(os.path.join(WIKI, "lint") + os.sep)]

    for f in referrer_files:
        content = read(f)
        d = os.path.dirname(f)
        for m in md_link_re.finditer(content):
            target = m.group(1)
            resolved = os.path.normpath(os.path.join(d, target))
            if resolved in incoming:
                incoming[resolved].add(f)
        for m in wiki_link_re.finditer(content):
            raw = m.group(1)
            name = raw.split("#")[0].strip()
            base = os.path.basename(name).lower()
            candidates = name_map.get(base, [])
            if not candidates:
                broken.append((f, raw))
            else:
                for c in candidates:
                    incoming[c].add(f)

    orphans = []
    for f in files:
        if is_readme(f) or is_log(f) or is_root_index(f):
            continue
        srcs = incoming[f] - {f}
        if not srcs:
            orphans.append(f)

    return broken, orphans


REQUIRED_BASE = ["title", "status", "tags", "date-created", "contributed-by"]


def required_fields(t):
    return REQUIRED_BASE + [f["name"] for f in t.get("fields", []) if f.get("required")]


def check_s3(files):
    """Schema violations: required frontmatter fields present and non-empty,
    for every type in structure.json with validate=true (excluding README.md)."""
    by_key = {t["key"]: t for t in TYPES if t.get("validate")}
    violations = []  # (file, missing_fields)
    for f in files:
        if is_readme(f):
            continue
        parts = f.split(os.sep)
        if len(parts) < 3 or parts[0] != WIKI or parts[1] not in by_key:
            continue
        required = required_fields(by_key[parts[1]])
        content = read(f)
        fm_text, _ = frontmatter(content)
        missing = []
        for field in required:
            val = fm_field(fm_text, field)
            if val is None or val in ("", "[]", "~"):
                missing.append(field)
        if missing:
            violations.append((f, missing))
    return violations


def check_s4_s5(files):
    """Index consistency (S4) and status mismatch (S5) for every folder-layout type
    with in_index=true against wiki/index.md. Expected row format:

        | [Title](<folder>/<slug>/index.md) | ...extra columns... | status |
    """
    index_path = os.path.join(WIKI, "index.md")
    index_content = read(index_path)
    findings_s4, findings_s5 = [], []

    for t in TYPES:
        if t.get("layout") != "folder" or not t.get("in_index"):
            continue
        key = t["key"]
        index_files = [
            f for f in files
            if f.startswith(os.path.join(WIKI, key) + os.sep)
            and os.path.basename(f) == "index.md"
            and os.path.dirname(f) != os.path.join(WIKI, key)
        ]
        slugs_in_index = set(re.findall(rf"{re.escape(key)}/([\w\-]+)/index\.md", index_content))
        slugs_actual = {os.path.basename(os.path.dirname(f)) for f in index_files}
        for missing in sorted(slugs_actual - slugs_in_index):
            findings_s4.append(f"{key}/{missing} not found in wiki/index.md table")
        for extra in sorted(slugs_in_index - slugs_actual):
            findings_s4.append(f"index.md refers to {key}/{extra} but that folder/index.md does not exist")

        for f in index_files:
            slug = os.path.basename(os.path.dirname(f))
            row_m = re.search(rf"\[.*?\]\({re.escape(key)}/{re.escape(slug)}/index\.md\)([^\n]*)\n", index_content)
            if row_m:
                cells = [c.strip() for c in row_m.group(1).strip().strip("|").split("|")]
                index_status = cells[-1] if cells else None
                fm_text, _ = frontmatter(read(f))
                fm_status = fm_field(fm_text, "status")
                if fm_status and index_status and fm_status != index_status:
                    findings_s5.append(f"{f}: frontmatter status={fm_status!r} vs index.md status={index_status!r}")

    return findings_s4, findings_s5


def check_s6(files):
    conflicts = []
    for f in files:
        if is_readme(f):
            continue
        fm_text, _ = frontmatter(read(f))
        if fm_field(fm_text, "status") == "conflict":
            conflicts.append(f)
    return conflicts


def main():
    if not os.path.isdir(WIKI):
        print(f"error: run from repo root (no {WIKI}/ found here)", file=sys.stderr)
        sys.exit(1)

    files = all_md_files()

    broken, orphans = check_s1_s2(files)
    s3_violations = check_s3(files)
    s4_findings, s5_findings = check_s4_s5(files)
    s6_conflicts = check_s6(files)

    print(f"Scanned {len(files)} .md files under {WIKI}/\n")

    print("== S1 Broken wikilinks (blocker) ==")
    if broken:
        for f, target in broken:
            print(f"  {f} -> [[{target}]]")
    else:
        print("  none")

    print("\n== S2 Orphan pages (warning) ==")
    if orphans:
        for f in orphans:
            print(f"  {f}")
    else:
        print("  none")

    print("\n== S3 Schema violations (warning) ==")
    if s3_violations:
        for f, missing in s3_violations:
            print(f"  {f} -- missing: {', '.join(missing)}")
    else:
        print("  none")

    print("\n== S4 Index inconsistency (warning) ==")
    if s4_findings:
        for line in s4_findings:
            print(f"  {line}")
    else:
        print("  none")

    print("\n== S5 Status mismatch (warning) ==")
    if s5_findings:
        for line in s5_findings:
            print(f"  {line}")
    else:
        print("  none")

    print("\n== S6 Unresolved conflicts (blocker) ==")
    if s6_conflicts:
        for f in s6_conflicts:
            print(f"  {f}")
    else:
        print("  none")


if __name__ == "__main__":
    main()
