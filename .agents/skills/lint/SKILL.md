---
name: lint
description: Run a health check on the wiki and produce a prioritised report of structural and semantic issues
---

# Skill: lint

Draai een gezondheidscheck op de wiki en maak een geprioriteerd rapport van structurele en semantische problemen. Bedoeld om maandelijks te draaien en kort in het team te bespreken.

## Wanneer gebruiken

- Maandelijks, als onderdeel van het ritme van lint + retro
- Voordat je een grote batch pagina's naar main promoveert
- Op verzoek, als de curator drift of inconsistentie vermoedt

## Uitvoer

Een gestructureerd rapport met bevindingen per ernst. Sla het op als `wiki/lint/YYYY-MM-DD-lint-report.md` en voeg een regel toe aan `wiki/log.md`. Los bevindingen niet automatisch op: rapporteer alleen, zodat de curator beslist wat er gebeurt.

---

## Controles

Draai alle onderstaande controles op volgorde. Verzamel alle bevindingen voordat je het rapport schrijft.

**De structurele controles (S1-S6) zijn geautomatiseerd.** Draai `uv run .agents/skills/lint/check_structure.py` vanuit de repo-root en gebruik de uitvoer direct. Leid S1-S6 niet opnieuw af door bestanden met de hand te lezen: dat kost tokens zonder winst. Het script heeft naast stdlib-Python 3 geen dependencies. Ziet de uitvoer er verkeerd uit, repareer dan het script in plaats van terug te vallen op handmatig controleren.

**Contenttypes:** de begrippen project, projectmap en besluit in deze skill zijn de types uit de standaardtemplate. De werkelijke types van dit team staan in `schema/structuur.json`; lees "project" als een dossiertype met `in_index: true` en "besluit" als de losse documenten (`layout: bestand`). Het script doet dit al vanzelf.

Alleen de semantische controles (M1-M3) vragen dat je de inhoud van pagina's leest, omdat ze oordeelsvorming vragen die het script niet kan geven. Beperk ook daar je leeswerk: lees alleen de pagina's binnen het project of de sectie die je controleert, niet de hele wiki tegelijk.

---

### Structurele controles

#### S1 — Gebroken wikilinks

Scan elk `.md`-bestand onder `wiki/` op `[[...]]`-patronen. Controleer per link of er ergens onder `wiki/` een bestand met die naam bestaat. Markeer elke link waarvan het doel niet te vinden is.

Ernst: **blocker** — gebroken links verwarren agents en lezers.

#### S2 — Weespagina's

Maak een lijst van alle `.md`-bestanden onder `wiki/` (behalve `index.md`, `log.md` en `README.md`). Controleer per bestand of er minstens één andere pagina of `wiki/index.md` naar linkt. Markeer elk bestand zonder inkomende links.

Ernst: **warning** — weespagina's zijn onvindbaar en waarschijnlijk vergeten.

#### S3 — Schemaschendingen

Controleer voor elk `.md`-bestand onder de mappen van de types met `validate: true` in `schema/structuur.json` (standaard `wiki/projecten/` en `wiki/besluiten/`; behalve `README.md`) of de volgende frontmattervelden aanwezig en niet leeg zijn:

- Alle pagina's: `title`, `status`, `tags`, `date-created`, `contributed-by`
- Extra verplichte velden per type: de velden met `required: true` bij `fields` in `structuur.json` (standaard bij besluiten: `project`, `besluit`, `datum`)

Markeer elke pagina met ontbrekende of lege verplichte velden.

Ernst: **warning** — onvolledige metadata breekt indexupdates en agent-routing.

#### S4 — Indexconsistentie

Vergelijk de submappen van `wiki/projecten/` met de projectentabel in `wiki/index.md`. Markeer:
- Een projectmap met `index.md` die niet in de indextabel staat
- Een rij in de indextabel zonder bijbehorende projectmap

Ernst: **warning** — de index is het dashboard van het team; drift maakt hem onbetrouwbaar.

#### S5 — Statusmismatch

Vergelijk voor elke projectpagina het veld `status` in de frontmatter met de statuskolom in `wiki/index.md`. Markeer elke afwijking.

Ernst: **warning** — de index hoort altijd de huidige paginastatus te tonen.

#### S6 — Onopgeloste conflicten

Zoek alle `.md`-bestanden onder `wiki/` met `status: conflict` in de frontmatter. Toon ze als pagina's die de curator moet oplossen.

Ernst: **blocker** — conflictpagina's mogen nooit onopgelost op main komen.

---

### Semantische controles

Draai deze na alle structurele controles. Lees de relevante pagina's zorgvuldig voordat je een oordeel velt.

#### M1 — Tegenspraken binnen een projectdossier

Lees voor elke submap onder `wiki/projecten/` alle pagina's. Controleer of claims elkaar tegenspreken, bijvoorbeeld: de status in de tabel onder Verloop botst met de `status` in de frontmatter, of twee vermeldingen trekken tegengestelde conclusies over dezelfde vraag.

Markeer concrete tegenspraken met een citaat uit elke botsende passage.

Ernst: **warning** — tegenspraken misleiden het team en agents.

#### M2 — Tegenspraken tussen pagina's

Lees alle pagina's onder `wiki/projecten/` en `wiki/besluiten/`. Zoek paren pagina's die directe tegenstrijdige claims doen over hetzelfde begrip, dezelfde afspraak of dezelfde projectstatus. Voorbeeld: een besluit zegt dat een project is gestopt, terwijl de projectpagina `actief` toont.

Beperk het bereik: markeer alleen duidelijke, specifieke tegenspraken, geen verschillen in nadruk of perspectief. Bij twijfel: niet markeren.

Ernst: **advisory** — drift tussen pagina's hoort bij een groeiende wiki; markeer alleen duidelijke gevallen.

#### M3 — Verouderde claims

Zoek claims die waarschijnlijk achterhaald zijn gezien andere inhoud in de wiki, bijvoorbeeld een pagina die iets "nog uit te werken" of "in ontwikkeling" noemt terwijl een andere pagina laat zien dat het af of verlaten is.

Markeer de specifieke claim en de pagina die haar tegenspreekt.

Ernst: **advisory** — verouderde claims verlagen na verloop van tijd het vertrouwen in de wiki.

---

## Rapportformaat

Sla op als `wiki/lint/YYYY-MM-DD-lint-report.md`:

```markdown
---
title: Lint rapport YYYY-MM-DD
generated-by: <model>, YYYY-MM-DD
tags: [lint]
---

# Lint rapport YYYY-MM-DD

## Samenvatting

| Ernst | Aantal |
|---|---|
| Blocker | n |
| Warning | n |
| Advisory | n |

## Blockers

### [S6] Onopgeloste conflictpagina's
- `wiki/projecten/llm-wiki/index.md` — status: conflict

## Warnings

### [S2] Weespagina's
- `wiki/projecten/llm-wiki/research/notitie.md` — geen inkomende links

### [S3] Schemaschendingen
- `wiki/besluiten/2026-07-29-llm-wiki-start-pilot.md` — veld `datum` leeg

### [S4] Indexinconsistentie
- `wiki/projecten/nieuw-project/index.md` — staat niet in wiki/index.md

## Advisories

### [M3] Verouderde claims
- `wiki/projecten/llm-wiki/index.md` — "pilot nog uit te werken" terwijl het besluit van 2026-07-29 de start vastlegt

## Geen bevindingen

S1 (gebroken links): geen
M1 (interne tegenspraken): geen
M2 (tegenspraken tussen pagina's): geen
```

---

## Na het rapport

Voeg een rij toe direct onder de koprij in `wiki/log.md`:
```
| YYYY-MM-DD | lint | — | <n> blockers, <n> warnings, <n> advisories — zie wiki/lint/YYYY-MM-DD-lint-report.md |
```

Commit of push niet automatisch. Zeg tegen de curator:

```
Lint rapport opgeslagen in wiki/lint/YYYY-MM-DD-lint-report.md.
Bekijk het rapport en commit wanneer je klaar bent, of zeg "commit de lint report".
```

## Randgevallen

- **Lege wiki:** bestaan er minder dan 5 pagina's, sla de semantische controles (M1–M3) dan over en noteer "te weinig content voor semantische analyse" in het rapport.
- **Onzekere tegenspraak:** bij twijfel bij M1–M3 niet markeren. Valse positieven schaden het vertrouwen in het lintrapport sneller dan gemiste bevindingen.
- **Grote wiki (50+ pagina's):** beperk M2 en M3 tot pagina's die de afgelopen 90 dagen zijn bijgewerkt, zodat de controle hanteerbaar blijft. Noteer die beperking in het rapport.
