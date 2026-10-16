---
name: onboard-contributor
description: Onboard a new contributor: create inbox, generate clipper template, and produce a welcome message
---

# Skill: onboard-contributor

Onboard een nieuwe bijdrager. Maakt de lokale inboxmap aan (`../inbox/` — raw/processed/staging, nooit git), genereert een persoonlijke Obsidian Web Clipper-template en print een kant-en-klaar welkomstbericht.

## Wanneer gebruiken

Draai deze skill als een nieuw teamlid ruw materiaal gaat bijdragen aan de wiki.

## Invoer

Vraag de bijdrager als niet opgegeven:

1. **Naam** — voornaam in lowercase, zonder spaties (bijv. `jan`, `fatima`).
2. **Rol** — `contributor` (draait skills, voegt notities toe; bewerkt wikibestanden en skills niet direct) of `curator` (mag skills en wiki direct bewerken en keurt merge requests goed). Standaard: `contributor`.

Normaliseer namen met spaties of hoofdletters naar lowercase-met-koppeltekens (bijv. `Jan de Vries` → `jan-de-vries`). Bevestig dit bij de gebruiker voordat je doorgaat.

## Benodigde tools

| Tool | Waarvoor |
|---|---|
| Git | Claude Code gebruikt het voor de wikirepo |
| uv | Python-omgeving voor de helperscripts van de skills |
| `glab` of `gh` | De share skill gebruikt dit om merge requests aan te maken |
| Obsidian | Notities schrijven en conceptpagina's beoordelen |
| Obsidian Web Clipper | Webpagina's opslaan in de inbox |

Bijdragers gebruiken git niet zelf: de skills regelen alle git-operaties op de wikirepo (het enige repo in dit systeem; `../inbox/` is een gewone map zonder git). Voor `glab`/`gh` logt de bijdrager eenmalig zelf in. Een token mag nooit in de chat met Claude Code terechtkomen.

## Stappen

### 0. Zorg dat uv geïnstalleerd is

De helperscripts van deze skills draaien via [uv](https://docs.astral.sh/uv/). Dat regelt zelf een Python-installatie, dus de bijdrager heeft geen systeem-Python nodig. Controleer of het al aanwezig is:

```bash
uv --version
```

Zo niet, installeer het:

```bash
# mac / linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Daarna is geen aparte installatiestap voor Python nodig: `uv run <script>.py` zet bij eerste gebruik de juiste Python-versie (gepind via `.python-version` en `pyproject.toml`) en een `.venv` klaar.

### 1. Zorg dat de git-CLI geïnstalleerd en geauthenticeerd is

De share skill maakt automatisch een merge request aan. Zonder een ingelogde CLI faalt die stap. Controleer `glab --version` (GitLab) of `gh --version` (GitHub) en installeer zo nodig:

```bash
# mac
brew install glab    # of: brew install gh

# windows (scoop)
scoop install glab   # of: scoop install gh
```

Inloggen doet de bijdrager zelf, in een eigen terminal en niet via Claude Code. Een token is een geheim; plakt iemand het in de chat, dan staat het voorgoed in het sessietranscript.

```bash
glab auth login --hostname <GIT-HOST>
# of
gh auth login
```

Controleer samen dat het gelukt is met `glab auth status` of `gh auth status`.

### 2. Draai het onboardingscript

De overige stappen (inboxmap, Obsidian-instellingen, clipper-template, logregel, welkomstbericht) zijn pure templating zonder oordeelsvorming. Draai in plaats van ze met de hand te doen:

```bash
uv run .agents/skills/onboard-contributor/onboard_contributor.py \
  --naam <naam> --rol <contributor|curator>
```

Het script:
- normaliseert de naam (bevestig dit bij de bijdrager als het afwijkt van de ruwe invoer)
- maakt `../inbox/raw/`, `../inbox/processed/`, `../inbox/staging/` en `../inbox/templates/` aan naast deze repo (of meldt dat ze al bestaan): puur lokaal, geen git
- kopieert `schema/obsidian-templates/inbox-note.md` naar `../inbox/templates/inbox-note.md` (alleen als die nog niet bestaat)
- kopieert `schema/obsidian-templates/{app,templates,hotkeys}.json` naar `../inbox/.obsidian/` (lokaal, niet gecommit; wordt altijd overschreven)
- genereert `schema/clipper-templates/wiki-clipper-<naam>.json` uit `_base.json` (stempelt elke clip met `contributor: <naam>` in de frontmatter)
- voegt een rij toe aan `wiki/log.md` (direct onder de scheidingsregel, met de datum van vandaag)
- print het complete welkomstbericht (geef dit letterlijk door aan de bijdrager) en een samenvatting van wat is aangemaakt

Gebruik `--dry-run` om te previewen zonder te schrijven. Een echte run overschrijft de machinelokale `.obsidian`-config, wat maar voor één persoon per keer geldt.

Bij `--rol curator` print het script een aparte waarschuwing dat de "wat je wél/niet doet"-sectie in het welkomstbericht voor bijdragers is geschreven. Pas die sectie handmatig aan voor een curator (die mag `wiki/` en `.agents/skills/` wél direct bewerken en MR's goedkeuren).

## Randgevallen

- **Naam bestaat al:** het script detecteert dit zelf (slaat het aanmaken van de inboxmappen over als ze al bestaan, genereert de clipper-template opnieuw en logt "inbox bestond al"). Elke bijdrager onboardt op de eigen machine, dus `../inbox/` is niet per naam: het bestaan ervan betekent alleen dat déze machine al eerder is ingericht.
- **Naam met spaties of hoofdletters:** normaliseer naar lowercase-met-koppeltekens en bevestig dit bij de gebruiker voordat je doorgaat.
- **Eerste clone:** is de repo nog niet gekloond op de machine van de bijdrager, gebruik dan `git clone <REPO-URL>`. Dit is eenmalig; `../inbox/` heeft geen git en wordt door het onboardingscript zelf aangemaakt.
