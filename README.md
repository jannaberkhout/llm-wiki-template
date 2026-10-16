# <TEAMNAAM> Wiki

De gedeelde kennisbase van <TEAMNAAM>. Pagina's hier zijn gecureerd en geanonimiseerd: namen staan alleen in metadata, nooit in de pagina-inhoud zelf.

## Deze template gebruiken

1. Kopieer deze map naar een nieuwe repo en geef die de naam van je team.
2. Zoek in de hele repo op `<TEAMNAAM>` en `<REPO-URL>` en vul ze in.
3. Draai de **setup-structuur skill**. Die vraagt hoe jullie team werkt (projecten? klanten en gesprekken? kandidaten?) en past de mappen, templates, het dashboard en de instructies daarop aan. Handmatig kan ook: pas `schema/structuur.json` aan en draai `uv run .agents/skills/setup-structuur/setup_structuur.py apply`.
4. Pas de statussen en besluitwaarden in de gegenereerde templates in `schema/` aan op jullie eigen begrippen.
5. Wijs een curator aan en draai de **onboard-contributor skill** voor jezelf.
6. Verwijder dit hoofdstuk uit de README.

## Nieuw? Begin hier

**Stap 1 — Toegang**

Vraag toegang aan tot de repo (<REPO-URL>) bij de curator.

**Stap 2 — Onboarding**

Draai de **onboard-contributor skill** met jouw naam. Die maakt twee dingen aan:

1. Jouw lokale inbox-map naast deze repo (`../inbox/` met `raw/`, `processed/`, `staging/`). Puur lokaal, nooit gecommit.
2. Een op maat gemaakt Obsidian Web Clipper-template (`wiki-clipper-<naam>.json`).

**Stap 3 — Gereedschap**

- **Obsidian** — open de `../inbox/`-map als vault
- **Obsidian Web Clipper** — installeer de browserextensie en importeer jouw `.json`-template

## Hoe werkt het bijdragen?

```
jouw inbox     →  ingest skill  →  jouw staging   →  share skill  →  wiki
(../inbox/raw/,                    (../inbox/staging/,                (hier)
 lokaal)                            jij beoordeelt,
                                     lokaal)
```

`../inbox/` is een gewone map, geen git-repo. Alles daar blijft op jouw eigen machine.

**Eigen notities** — maak een `.md`-bestand aan in `../inbox/raw/` met de naamconventie `YYYY-MM-DD-onderwerp.md`. Minimale frontmatter:

```yaml
---
date: 2026-07-29
context: notitie / research / besluit / vergadering
---
```

**Webpagina's** — gebruik de Web Clipper. Die slaat de pagina op in `../inbox/raw/` met de juiste frontmatter.

**Vergadernotities** — zet `type: meeting` en `share: approved` in de frontmatter. Zonder die goedkeuring slaat de ingest ze over.

## Van inbox naar wiki

1. Leg bestanden neer in `../inbox/raw/` (of via de Web Clipper)
2. Draai de **ingest-note skill**: de agent maakt conceptpagina's in `../inbox/staging/`
3. Bekijk de concepten in Obsidian
4. Draai de **share skill**: goedgekeurde pagina's gaan naar een branch in deze repo
5. De curator beoordeelt het merge request en merget naar main

Niets bereikt de wiki zonder jouw expliciete keuze in stap 4 en de goedkeuring van de curator in stap 5.

## Wat staat waar?

| Map | Inhoud |
|---|---|
| `wiki/index.md` | Dashboard: alle dossiers met status |
| `wiki/projecten/` | Eén submap per project |
| `wiki/besluiten/` | Besluiten per project |
| `wiki/werkwijze/` | Hoe het team werkt: processen, rollen, afspraken, principes |
| `wiki/log.md` | Logboek van alle agent-acties |
| `wiki/lint/` | Maandelijkse kwaliteitsrapporten |
| `wiki/archive/` | Vervangen documenten, bewaard als naslag |
| `schema/` | Templates voor nieuwe pagina's |
| `.agents/skills/` | Skills voor agents |

## Rollen en rechten

| Actie | Contributor | Curator |
|---|---|---|
| Notities toevoegen aan inbox | Ja | — |
| Ingest-note skill draaien | Ja | — |
| Share skill draaien | Ja | — |
| Wiki-bestanden direct bewerken | Nee | Ja |
| Skills bewerken (`.agents/skills/`) | Nee | Ja |
| MRs mergen naar main | Nee | Ja |
| Lint skill draaien | Nee | Ja |

Wiki-bestanden worden uitsluitend via skills bijgewerkt, nooit handmatig door contributors.

## Vragen of correcties?

Maak een issue aan in deze repo of spreek de curator aan.
