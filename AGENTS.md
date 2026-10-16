# AGENTS.md — Team Wiki

Dit bestand is de leidende instructieset voor elke agent die in deze repository werkt. Lees het voordat je iets doet. Herschrijf het niet zonder goedkeuring van de curator.

> **Template:** dit is de basis voor een teamwiki. Zoek na het kopiëren op `<TEAMNAAM>` en `<REPO-URL>` en vul die in.

## Wat is deze repository

De gecureerde wiki van <TEAMNAAM>: gesynthetiseerde, teamgerichte kennis, afgeleid van ruw materiaal dat een bijdrager eerst lokaal op de eigen machine verzamelt. Ruw materiaal komt nooit in git. Het staat in een gewone lokale map `../inbox/` naast deze repo. De wiki heeft een bredere kring van lezers dan die lokale map en is daarom op paginaniveau geanonimiseerd.

## Lokale inbox + wiki-indeling

```
../inbox/                          (alleen lokaal — nooit gecommit; elke bijdrager heeft een eigen map op de eigen machine)
  raw/                             ruw materiaal dat nog verwerkt moet worden
  processed/                       na ingest hierheen verplaatst (archief van de originelen)
  staging/                         door de agent gegenereerde concepten die op goedkeuring wachten

./                                 (deze repo — git, bredere kring)
  wiki/index.md                    dashboard van alle dossiers — altijd actueel houden
  wiki/log.md                      append-only logboek
  wiki/projecten/<slug>/           één submap per project
                                    index.md    de projectpagina
                                    research/   onderzoeksnotities en rapporten
                                    bijlagen/   overige documenten
  wiki/besluiten/                  besluiten per project
  wiki/werkwijze/                  hoe het team werkt: processen, rollen, afspraken, principes
  wiki/lint/                       maandelijkse lintrapporten
  wiki/archive/                    vervangen documenten, bewaard als naslag
  schema/                          paginatemplates en conventies
  .agents/skills/                  beschikbare skills; sommige met een *.py-helper (zie hieronder)
  pyproject.toml, .python-version  uv-omgeving voor die helpers (alleen stdlib, geen dependencies)
```

`../inbox/` is een gewone map, geen git-repository. Er is niets om te fetchen, mergen of pushen. Dat is bewust: ruw materiaal en conceptpagina's zijn persoonlijk en blijven op de machine van de bijdrager. De enige git-operaties in dit systeem zitten op deze repo, bij de laatste `share`-stap.

**Helperscripts van skills**
Enkele skills hebben een stdlib-only Python-script naast hun `SKILL.md` (`lint/check_structure.py`, `setup-structuur/setup_structuur.py`, `onboard-contributor/onboard_contributor.py`) dat het mechanische deel van de skill doet: controles, bestanden aanmaken. Draai ze met `uv run .agents/skills/<skill>/<script>.py ...` (zie de `SKILL.md` voor de exacte argumenten). `uv` zet bij eerste gebruik Python en een `.venv` klaar. De `SKILL.md` zegt welke delen nog bij de agent liggen: oordeelsvorming, bevestiging door een mens, git-commits.

## Contentflow

```
../inbox/raw/  →  ingest-note skill  →  ../inbox/staging/  →  share skill  →  wiki/
  (ruwe input)      (altijd, lokaal)      (bijdrager beoordeelt   (expliciete       (team ziet
                                           hier, lokaal)           goedkeuring)       dit)
```

De wiki ontvangt alleen content die een bijdrager expliciet heeft goedgekeurd. Staging is de persoonlijke reviewruimte: een lokale map, onzichtbaar voor het team en nooit in git.

## Regels — altijd volgen

**Ruw materiaal lezen**
- Lees uit `../inbox/raw/` en wijzig daar nooit iets.
- Verplaats een bestand na een geslaagde ingest met `mv` naar `../inbox/processed/`. Verwijder nooit ruwe bestanden.
- Vergadernotities (`type: meeting` in de frontmatter) vragen om `share: approved` vóór ingest. Ontbreekt dat, of staat er `share: pending`, sla het bestand dan over en noteer dat in het log.
- Alle andere inboxbestanden worden standaard verwerkt: wie iets in `raw/` zet, deelt het daarmee.

**Wikipagina's schrijven**
- Namen van bijdragers staan alleen in de frontmatter (`contributed-by:`), nooit in de paginatekst. Dit is niet optioneel.
- Bronnen staan in de frontmatter (`sources:`) als paden relatief aan `../inbox/`, bijvoorbeeld `raw/2026-07-29-onderwerp.md`.
- Gebruik de templates in `schema/` voor nieuwe pagina's. Verzin geen frontmattervelden.
- Herschrijf bestaande paginateksten niet in zijn geheel. Voeg liever secties toe of werk specifieke velden bij.

**Logboek**
- Voeg na elke ingest- of curatie-actie een rij toe aan de tabel in `wiki/log.md`, direct onder de koprij (nieuwste bovenaan). Formaat: `| YYYY-MM-DD | <skill> | <bijdrager of —> | <beschrijving> |`
- Verwijder of herschrijf nooit logregels.

**Index**
- Werk `wiki/index.md` bij zodra een dossier is aangemaakt of de `status` van een dossier verandert. Een dossier is een item van een type met `layout: dossier` en `in_index: true` in `schema/structuur.json` (in de standaardtemplate: een project).

**Mappenstructuur**
- De mappen onder `wiki/` (de contenttypes) staan in `schema/structuur.json`. Dat bestand is de bron van waarheid; lees het om te weten waar een soort pagina hoort en welk template erbij hoort. Verzin geen eigen mappen.
- Woorden als "project" en "besluit" in deze instructies en in de skills zijn de begrippen uit de standaardtemplate. Heeft het team andere types gekozen, lees ze dan als de types uit `structuur.json`.
- Wijzig de structuur alleen via de `setup-structuur` skill, met goedkeuring van de curator.

**Conflicten**
- Laat nooit stilzwijgend inhoud vallen. Spreken twee bronnen elkaar tegen, schrijf dan beide in de pagina onder een duidelijk `> **Conflict:**`-blok en zet `status: conflict` in de frontmatter.

## Vragen over de wiki beantwoorden

Als een gebruiker een vraag stelt die uit de wiki te beantwoorden is (over dossiers, besluiten of andere kennis in `wiki/`), laad dan eerst de `answer-from-wiki` skill. Antwoord niet uit je hoofd: zoek altijd in de wiki.

## Beschikbare skills

- `.agents/skills/setup-structuur/` — pas de mappenstructuur van de wiki aan op het team (contenttypes, templates, index); eenmalig bij het opzetten, daarna alleen door de curator
- `.agents/skills/ingest-note/` — verwerk inboxbestanden tot conceptpagina's in staging (lokaal, `../inbox/`)
- `.agents/skills/share/` — promoveer beoordeelde stagingpagina's naar de wikirepo en push voor beoordeling door de curator
- `.agents/skills/lint/` — maandelijkse gezondheidscheck: structureel (gebroken links, weespagina's, schema, index) en semantisch (tegenspraken, verouderde claims)
- `.agents/skills/onboard-contributor/` — onboard een nieuwe bijdrager: inboxmap aanmaken en een persoonlijke clipper-template genereren
- `.agents/skills/answer-from-wiki/` — beantwoord vragen op basis van de wiki
- `.agents/skills/update-wiki/` — synchroniseer de wiki met main en toon wat er nieuw is
