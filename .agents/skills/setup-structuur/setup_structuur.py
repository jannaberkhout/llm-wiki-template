#!/usr/bin/env python3
"""Pas de mappenstructuur van de wiki toe volgens schema/structuur.json.

    uv run .agents/skills/setup-structuur/setup_structuur.py check
    uv run .agents/skills/setup-structuur/setup_structuur.py apply [--dry-run]

`check` valideert structuur.json en toont wat er van `apply` te verwachten is.
`apply` maakt per type de map + README aan, genereert ontbrekende templates,
ververst de mappenlijsten in AGENTS.md en README.md en maakt een lege
wiki/index.md aan als die nog geen rijen bevat. Een type met `"hernoemd_van"`
wordt met `git mv` (of os.rename) hernoemd. Er wordt nooit iets verwijderd;
bestaande mappen die niet meer in de config staan worden alleen gemeld.

Alleen stdlib. Draai vanuit de repo-root.
"""
import json
import os
import re
import subprocess
import sys

CONFIG = os.path.join("schema", "structuur.json")
WIKI = "wiki"
RESERVED = {"lint", "archive"}          # vaste mappen, geen contenttype
GENERATED = "<!-- gegenereerd door setup-structuur: bewerk gerust, haal deze regel weg om overschrijven te voorkomen -->"
BASE_FIELDS = ["title", "aliases", "tags", "status", "contributed-by",
               "generated-by", "date-created", "date-updated", "sources"]
BASE_REQUIRED = ["title", "status", "tags", "date-created", "contributed-by"]
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def load():
    with open(CONFIG, encoding="utf-8") as fh:
        return json.load(fh)["types"]


def validate(types):
    errs, seen = [], set()
    if not types:
        errs.append("geen enkel type gedefinieerd")
    for t in types:
        k = t.get("key", "")
        if not KEY_RE.match(k):
            errs.append(f"key {k!r}: alleen kleine letters, cijfers en koppeltekens")
        if k in RESERVED or k in ("index", "log"):
            errs.append(f"key {k!r} is gereserveerd")
        if k in seen:
            errs.append(f"key {k!r} komt dubbel voor")
        seen.add(k)
        if t.get("layout") not in ("dossier", "bestand"):
            errs.append(f"{k}: layout moet 'dossier' of 'bestand' zijn")
        for f in ("label", "label_plural", "omschrijving", "naamconventie"):
            if not t.get(f):
                errs.append(f"{k}: veld '{f}' ontbreekt")
        if t.get("in_index") and t.get("layout") != "dossier":
            errs.append(f"{k}: in_index kan alleen bij layout 'dossier'")
        tpl = t.get("template")
        if tpl and (os.sep in tpl or not tpl.endswith(".md")):
            errs.append(f"{k}: template moet een bestandsnaam .md in schema/ zijn")
    return errs


def run_git_mv(src, dst):
    try:
        subprocess.run(["git", "mv", src, dst], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        os.rename(src, dst)


def is_generated(path):
    if not os.path.exists(path):
        return True
    with open(path, encoding="utf-8") as fh:
        return GENERATED in fh.read()


def readme_text(t):
    lines = [GENERATED, "", f"# {t['label_plural']}", "", t["omschrijving"], ""]
    lines.append(f"Naamconventie: `{t['naamconventie']}`")
    if t["layout"] == "dossier":
        lines += ["", f"Elke {t['label'].lower()} heeft een eigen submap met een `index.md`."]
        if t.get("submappen"):
            lines.append("Aanvullende bestanden komen in dezelfde submap, bijvoorbeeld in: "
                         + ", ".join(f"`{s}/`" for s in t["submappen"]) + ".")
    if t.get("template"):
        lines += ["", f"Gebruik `schema/{t['template']}` voor nieuwe pagina's."]
    lines += ["", "De agent maakt pagina's en submappen aan op basis van goedgekeurde notities uit de lokale inbox.",
              "Maak hier zelf geen mappen aan: dat verstoort de index.", ""]
    return "\n".join(lines)


def template_text(t):
    path = (f"wiki/{t['key']}/<slug>/index.md" if t["layout"] == "dossier"
            else f"wiki/{t['key']}/{t['naamconventie']}")
    extra = t.get("fields", [])
    fm = ["---"]
    for f in BASE_FIELDS:
        if f == "tags":
            fm.append(f"tags: [{t['key']}]")
        elif f == "status":
            fm.append("status: draft")
        elif f in ("aliases", "contributed-by", "sources"):
            fm.append(f"{f}: []")
        else:
            fm.append(f"{f}: ")
        if f == "status":
            for e in extra:
                fm.append(f"{e['name']}: ")
    fm.append("---")
    out = [GENERATED, "", f"# {t['label']}template", "",
           f"Gebruik dit template voor nieuwe pagina's in `{path}`.",
           f"Naamconventie: `{t['naamconventie']}`", "", "---", "",
           "```yaml", *fm, "```", ""]
    if t.get("status_values"):
        out += ["**`status`** — één van: " + " · ".join(f"`{s}`" for s in t["status_values"]) + ".", ""]
    for e in extra:
        out.append(f"**`{e['name']}`** — {e.get('hint', '')}" + (" (verplicht)" if e.get("required") else ""))
        out.append("")
    out += ["---", ""]
    for s in t.get("sections") or ["Samenvatting", "Details", "Open vragen", "Gerelateerd"]:
        out += [f"## {s}", ""]
    return "\n".join(out)


def tree_lines(types):
    out = []
    for t in types:
        pad = f"  wiki/{t['key']}/"
        desc = t.get("kort") or t["omschrijving"]
        out.append(f"{pad:<35}{desc}")
        if t["layout"] == "dossier":
            subs = "  ".join(["index.md"] + [f"{s}/" for s in t.get("submappen", [])])
            out.append(f"{'':<35}  ({t['naamconventie']}; {subs})")
    return out


def readme_rows(types):
    return [f"| `wiki/{t['key']}/` | {t['omschrijving']} |" for t in types]


def replace_region(path, start_re, end_re, new_lines, dry):
    """Vervang de regels tussen de ankers (ankers blijven staan)."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    s = next((i for i, l in enumerate(lines) if re.search(start_re, l)), None)
    e = next((i for i, l in enumerate(lines) if s is not None and i > s and re.search(end_re, l)), None)
    if s is None or e is None:
        return f"{path}: ankers niet gevonden ({start_re!r} .. {end_re!r}); pas de lijst met de hand aan"
    new = lines[:s + 1] + new_lines + lines[e:]
    if new != lines and not dry:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(new))
    return None


def index_text(types):
    out = ["---", "title: Overzicht", "status: stub", "generated-by: ", "date-updated: ", "---", "",
           "# Overzicht", "", "_Bijgewerkt door agent. Voeg dossiers toe via de lokale inbox._", "", "---", ""]
    for t in (x for x in types if x.get("in_index")):
        cols = [t["label"]] + t.get("index_columns", []) + ["Status"]
        out += [f"## {t['label_plural']}", "", "| " + " | ".join(cols) + " |",
                "|" + "---|" * len(cols), ""]
    if not any(x.get("in_index") for x in types):
        out += ["_Geen type met `in_index` in schema/structuur.json._", ""]
    return "\n".join(out)


def index_has_rows():
    p = os.path.join(WIKI, "index.md")
    if not os.path.exists(p):
        return False
    with open(p, encoding="utf-8") as fh:
        text = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.DOTALL)
        return bool(re.search(r"^\|\s*\[.+\]\(.+\.md\)", text, re.MULTILINE))


def write(path, text, dry, log):
    log.append(("(dry) " if dry else "") + f"schrijf {path}")
    if not dry:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


def apply(types, dry):
    log, warn = [], []
    for t in types:                                  # 1. hernoemen
        old = t.get("hernoemd_van")
        if old:
            src, dst = os.path.join(WIKI, old), os.path.join(WIKI, t["key"])
            if os.path.isdir(src) and not os.path.exists(dst):
                log.append(("(dry) " if dry else "") + f"hernoem {src} -> {dst}")
                if not dry:
                    run_git_mv(src, dst)
            elif os.path.isdir(src):
                warn.append(f"{src} en {dst} bestaan allebei; voeg met de hand samen")
    for t in types:                                  # 2. map + README + template
        d = os.path.join(WIKI, t["key"])
        if not os.path.isdir(d):
            log.append(("(dry) " if dry else "") + f"maak {d}/")
            if not dry:
                os.makedirs(d)
        readme = os.path.join(d, "README.md")
        if is_generated(readme):
            write(readme, readme_text(t), dry, log)
        else:
            warn.append(f"{readme} is met de hand bewerkt; niet overschreven")
        if t.get("template"):
            tp = os.path.join("schema", t["template"])
            if not os.path.exists(tp) or is_generated(tp):
                write(tp, template_text(t), dry, log)
    # AGENTS.md: lijst staat tussen log.md en lint/; README.md: tussen index.md-rij en log.md-rij
    for args in (("AGENTS.md", r"^\s*wiki/log\.md\b", r"^\s*wiki/lint/", tree_lines(types)),
                 ("README.md", r"^\| `wiki/index\.md` \|", r"^\| `wiki/log\.md` \|", readme_rows(types))):
        m = replace_region(*args, dry)
        if m:
            warn.append(m)
        else:
            log.append(("(dry) " if dry else "") + f"ververs mappenlijst in {args[0]}")
    ip = os.path.join(WIKI, "index.md")             # 4. index
    if not index_has_rows():
        write(ip, index_text(types), dry, log)
    else:
        warn.append("wiki/index.md bevat al rijen en is niet herschreven; controleer de koppen met de hand")
    keys = {t["key"] for t in types} | RESERVED     # 5. wezen
    for name in sorted(os.listdir(WIKI)):
        if os.path.isdir(os.path.join(WIKI, name)) and name not in keys:
            warn.append(f"wiki/{name}/ staat niet in structuur.json (niet verwijderd)")
    return log, warn


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("check", "apply"):
        print(__doc__)
        sys.exit(2)
    if not os.path.isdir(WIKI) or not os.path.exists(CONFIG):
        print("fout: draai vanuit de repo-root (wiki/ en schema/structuur.json verwacht)", file=sys.stderr)
        sys.exit(1)
    types = load()
    errs = validate(types)
    if errs:
        print("structuur.json is ongeldig:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    dry = sys.argv[1] == "check" or "--dry-run" in sys.argv
    log, warn = apply(types, dry)
    print(f"{len(types)} types: " + ", ".join(t["key"] for t in types) + "\n")
    for l in log:
        print(" ", l)
    for w in warn:
        print("  LET OP:", w)
    if dry:
        print("\n(niets geschreven; draai `apply` om door te voeren)")


if __name__ == "__main__":
    main()
