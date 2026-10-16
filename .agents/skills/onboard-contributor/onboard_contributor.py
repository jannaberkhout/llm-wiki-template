#!/usr/bin/env python3
"""Mechanical steps for the onboard-contributor skill. See SKILL.md.

Unlike the lint helper, this script DOES write files -- the steps here are
pure templating with zero judgment (create folders, substitute a name into
JSON/template files, append a log row), and the touched files are either
untracked local config (../inbox/.obsidian/ -- ../inbox/ has no git at all)
or trivial per-person templates.

Run via uv (see SKILL.md step 0 for installing uv first):

    uv run .agents/skills/onboard-contributor/onboard_contributor.py \\
        --naam "Jan de Vries" --rol contributor [--dry-run]

--dry-run prints every planned write without touching disk -- use it to
preview, or when testing this script itself (a real run overwrites the
machine-local .obsidian/*.json, which is meant to happen at most once per
person per machine).

Still the agent's job: asking for/confirming Input (naam/rol), the
step-0 uv-install check, and relaying the printed welkomstbericht +
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


def normalize_naam(raw):
    naam = raw.strip().lower()
    naam = re.sub(r"\s+", "-", naam)
    naam = re.sub(r"[^a-z0-9\-]", "", naam)
    return naam


def fail(msg):
    print(f"FOUT: {msg}", file=sys.stderr)
    sys.exit(1)


def write_file(path, content, dry_run, label=None):
    label = label or path
    if dry_run:
        print(f"  [dry-run] zou schrijven: {label}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  geschreven: {label}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--naam", required=True, help="ruwe naam, wordt genormaliseerd naar lowercase-met-koppeltekens")
    p.add_argument("--rol", choices=["contributor", "curator"], default="contributor")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if not os.path.isdir(WIKI):
        fail(f"run dit script vanuit de repo root (geen {WIKI}/ hier gevonden)")

    naam_raw = args.naam
    naam = normalize_naam(naam_raw)
    if naam != naam_raw.strip().lower():
        print(f"Naam genormaliseerd: '{naam_raw}' -> '{naam}' (bevestig dit met de contributor voordat je doorgaat)\n")

    dry_run = args.dry_run

    # --- step 1: local inbox folders (per machine, not per name) ---
    inbox_existed = os.path.isdir(RAW)
    print("== Stap 1: lokale inbox-map ==")
    if inbox_existed:
        print(f"  {RAW}/ bestaat al -- sla aanmaken over")
    for sub in ("raw", "processed", "staging", "templates"):
        d = os.path.join(RAW, sub)
        if dry_run:
            print(f"  [dry-run] zou aanmaken: {d}/")
        else:
            os.makedirs(d, exist_ok=True)
    if not inbox_existed and not dry_run:
        print(f"  aangemaakt: {RAW}/{{raw,processed,staging,templates}}/")

    obsidian_templates = os.path.join(SCHEMA, "obsidian-templates")

    inbox_note_path = os.path.join(RAW, "templates", "inbox-note.md")
    if not os.path.isfile(inbox_note_path):
        src = os.path.join(obsidian_templates, "inbox-note.md")
        if not os.path.isfile(src):
            fail(f"{src} niet gevonden")
        write_file(inbox_note_path, open(src, encoding="utf-8").read(), dry_run)

    # --- step 2: obsidian settings (always overwritten, local-only, machine-local) ---
    print("\n== Stap 2: Obsidian-instellingen (lokaal, niet gecommit) ==")
    for name in ("app.json", "templates.json", "hotkeys.json"):
        src = os.path.join(obsidian_templates, name)
        if not os.path.isfile(src):
            fail(f"{src} niet gevonden")
        write_file(os.path.join(RAW, ".obsidian", name), open(src, encoding="utf-8").read(), dry_run)

    # --- step 3: personal clipper template ---
    print("\n== Stap 3: persoonlijke clipper-template ==")
    base_path = os.path.join(SCHEMA, "clipper-templates", "_base.json")
    if not os.path.isfile(base_path):
        fail(f"{base_path} niet gevonden")
    base_content = open(base_path, encoding="utf-8").read()
    clipper_content = base_content.replace("CONTRIBUTOR_NAME", naam)
    clipper_path = os.path.join(SCHEMA, "clipper-templates", f"wiki-clipper-{naam}.json")
    write_file(clipper_path, clipper_content, dry_run)

    # --- step 4: log entry ---
    print("\n== Stap 4: log-entry ==")
    log_path = os.path.join(WIKI, "log.md")
    beschrijving = "lokale inbox bestond al, Obsidian ingesteld, clipper template gegenereerd" if inbox_existed \
        else "lokale inbox aangemaakt, Obsidian ingesteld, clipper template gegenereerd"
    datum = datetime.date.today().isoformat()
    if dry_run:
        print(f"  [dry-run] zou log-rij invoegen in {log_path}: {datum} | onboard-contributor | {naam} | {beschrijving}")
    else:
        content = open(log_path, encoding="utf-8").read()
        sep_match = re.search(r"^\|---\|.*\|\n", content, re.MULTILINE)
        if not sep_match:
            fail(f"kon de tabel-scheidingsregel niet vinden in {log_path} -- voeg de rij handmatig toe")
        insert_at = sep_match.end()
        row = f"| {datum} | onboard-contributor | {naam} | {beschrijving} |\n"
        new_content = content[:insert_at] + row + content[insert_at:]
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print(f"  rij ingevoegd in {log_path} ({datum})")

    # --- welcome message (step 5) ---
    print("\n== Stap 5: welkomstbericht (relay dit aan de contributor) ==")
    print(f"""
**Je onboarding is klaar, {naam}!**

Het volgende is automatisch voor je aangemaakt:
- `../inbox/` naast deze repo (`raw/`, `processed/`, `staging/`) — een gewone map, geen git. Nieuwe notities en bijlagen gaan naar `raw/`
- Obsidian-instellingen ingesteld (app.json, templates.json, hotkeys.json)
- Persoonlijke clipper-template: `wiki-clipper-{naam}.json` (stempelt elke clip met `contributor: {naam}`)

**De git-CLI instellen (nodig voor de share skill, die er automatisch een merge request mee aanmaakt)**

Check of `glab` (GitLab) of `gh` (GitHub) al geïnstalleerd is:

```bash
glab --version   # of: gh --version
```

Zo niet, installeer het (bijv. `brew install glab` op mac, `scoop install glab` op windows) en log daarna zelf in, in je eigen terminal (niet via Claude Code):

```bash
glab auth login --hostname <GIT-HOST>   # of: gh auth login
```

Plak een token nooit in een bericht aan Claude Code — dat token blijft dan voorgoed in de sessie-transcript staan.

**Obsidian instellen (als je dat nog niet hebt gedaan)**

Download en installeer Obsidian via https://obsidian.md/download.

Open daarna beide mappen als vault — je hebt ze allebei nodig:

1. Open Obsidian → **Open folder as vault** → selecteer de `../inbox/`-map naast deze repo
   - Nieuwe notities en bijlagen gaan automatisch naar `raw/`
   - Het `inbox-note` template staat klaar via **Ctrl+T**
2. Voeg ook de wikirepo toe: **Open another vault → Open folder as vault** → selecteer de geklonede wiki-map
   - Dit is de gecureerde wiki — hier lees je wat er al gepubliceerd is

**Obsidian Web Clipper instellen (voor het opslaan van webpagina's)**

Installeer de extensie via https://obsidian.md/clipper (Chrome, Firefox, Safari of Edge).

Na installatie, doorloop deze stappen in de extensie-instellingen:

1. **Vault toevoegen:** Settings → Vaults → voeg de `../inbox/`-vault toe
2. **Template importeren:** Settings → Templates → Import → selecteer `schema/clipper-templates/wiki-clipper-{naam}.json` uit de wikirepo
3. **Standaard vault instellen:** zorg dat nieuwe clips naar de `../inbox/`-vault worden geschreven (niet naar de wikirepo)

---

**Hoe het systeem werkt**

Het systeem bestaat uit twee lagen:

- **../inbox/** — jouw persoonlijke werkruimte, puur lokaal op deze machine. Hier zet je ruwe notities, clips en aantekeningen, en review je concepten voor je ze deelt. Niemand anders leest dit rechtstreeks, en het is nooit in git.
- **De wikirepo** — de gedeelde, gecureerde wiki. Alleen gecureerde en goedgekeurde content staat hier. Dit is wat het team leest en raadpleegt.

**De flow van documentatie**

```
../inbox/raw/          →  ../inbox/staging/      →  wiki/
  (jouw ruwe input)        (concept na ingest)       (gepubliceerd)

  [jij schrijft]           [ingest-note skill]       [share skill + MR]
```

1. Maak een notitie aan in `../inbox/raw/` in Obsidian (naamconventie: `YYYY-MM-DD-onderwerp.md`)
2. Draai de **ingest-note skill** in Claude Code — Claude leest je notities, structureert ze als wiki-pagina's en zet concepten klaar in `../inbox/staging/`
3. Bekijk de concepten in Obsidian en pas aan waar nodig
4. Draai de **share skill** — de concepten worden als branch naar de wikirepo gepusht
5. De curator beoordeelt de MR en merget naar main

**Beschikbare skills**

| Skill | Wat het doet |
|---|---|
| `ingest-note` | Verwerkt ruwe notities uit je inbox naar gestructureerde concepten in staging |
| `share` | Pusht goedgekeurde staging-concepten als branch naar de wikirepo |
| `lint` | Draait een gezondheidscheck op de wiki en produceert een geprioriteerd rapport |
| `onboard-contributor` | Onboardt een nieuwe contributor (lokale inbox, Obsidian-instellingen, clipper-template) |
| `answer-from-wiki` | Beantwoordt vragen op basis van de wiki |
| `update-wiki` | Sync de wiki met main en toon wat er nieuw is sinds je laatste sync |

**Claude als kennisassistent**

Je kunt Claude Code op elk moment vragen om de wiki te doorzoeken en nieuwe notities voor je te schrijven. Bijvoorbeeld:

- *"Vat samen wat er in de wiki staat over [onderwerp]"*
- *"Schrijf een nieuwe notitie over [onderwerp] en zet die in mijn inbox"* — Claude schrijft dan een .md-bestand naar `../inbox/raw/`

**Wat je als contributor wél en niet doet**

Wél:
- Bestanden toevoegen aan `../inbox/raw/`
- Alle skills draaien via Claude Code
- Staging reviewen in Obsidian
- Claude vragen om wiki-inhoud op te zoeken of notities te schrijven

Niet:
- Wiki-bestanden (`wiki/`) of skill-bestanden (`.agents/skills/`) direct bewerken
- MRs goedkeuren — dat doet de curator

Vragen? Spreek de curator aan.
""")

    if args.rol == "curator":
        print("LET OP: rol=curator -- de \"wat je wél/niet doet\"-sectie hierboven is geschreven voor contributors. "
              "Curators mogen wiki/ en .agents/skills/ wél direct bewerken en MRs goedkeuren -- pas de laatste "
              "sectie handmatig aan voor een curator-onboarding (dit is niet in de skill/template zelf opgelost).")

    # --- summary (step 6) ---
    print("\n== Stap 6: samenvatting ==")
    print(f"Onboarding {naam} {'gecontroleerd (dry-run, niets geschreven)' if dry_run else 'voltooid'}.\n")
    print("Aangemaakt:" if not inbox_existed else "Aangemaakt/gecontroleerd:")
    print("  - ../inbox/{raw,processed,staging}/" + ("  (bestond al)" if inbox_existed else ""))
    print("  - ../inbox/.obsidian/app.json  (raw/ als standaardlocatie — niet gecommit)")
    print("  - ../inbox/.obsidian/templates.json  (templates folder — niet gecommit)")
    print("  - ../inbox/.obsidian/hotkeys.json  (Ctrl+T voor Insert template — niet gecommit)")
    print(f"  - schema/clipper-templates/wiki-clipper-{naam}.json")
    print(f"\nLog bijgewerkt: {log_path}" + (" (dry-run: niet echt geschreven)" if dry_run else ""))


if __name__ == "__main__":
    main()
