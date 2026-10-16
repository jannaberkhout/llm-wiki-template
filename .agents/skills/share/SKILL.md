---
name: share
description: Promote reviewed draft pages from staging to the wiki repo and push for curator review
---

# Skill: share

Promoveer beoordeelde conceptpagina's uit `../inbox/staging/` naar de wikirepo en push ze naar een gedateerde ingest-branch voor beoordeling door de curator. Dit is de expliciete deelbeslissing: niets bereikt de wikirepo voordat deze skill draait. `../inbox/` heeft geen git. De enige git-operaties in deze skill zitten op deze repo.

## Wanneer gebruiken

Draai deze skill als de bijdrager de stagingpagina's in Obsidian heeft beoordeeld en alles of een deel met het team wil delen.

## Invoer

- **Bijdrager** — naam van de bijdrager, voor de branchnaam en het log. Vraag dit als het niet uit de context af te leiden is.

## Stappen

### 0. Synchroniseer de wiki met main

Zorg dat de wiki up-to-date is, zodat je niet over wijzigingen van de curator heen schrijft.

```bash
git fetch origin
git merge origin/main
```

Bij merge-conflicten: los ze op voordat je verdergaat.

### 1. Ontdek stagingbestanden

Maak een lijst van alle bestanden in `../inbox/staging/`:

```
De volgende conceptpagina's staan klaar om te delen:

  - staging/projecten/llm-wiki/index.md  →  wiki/projecten/llm-wiki/index.md
  - staging/besluiten/2026-07-29-llm-wiki-start-pilot.md  →  wiki/besluiten/...
  - staging/werkwijze/overlegstructuur.md  →  wiki/werkwijze/overlegstructuur.md

Wil je alle pagina's delen, of alleen specifieke?
(antwoord: "alle" of geef de bestandsnamen op)
```

Wacht op het antwoord van de bijdrager voordat je verdergaat.

### 2. Kopieer goedgekeurde pagina's naar de wikirepo

Voor elke goedgekeurde stagingpagina:

1. Kopieer van `../inbox/staging/<pad>` naar `wiki/<pad>` in de wikirepo.
2. Bestaat er al een wikipagina op dat pad, merge de nieuwe inhoud dan erin en overschrijf niet. Voeg nieuwe secties toe en werk het veld `date-updated` bij.
3. Verwijder het bestand uit `../inbox/staging/`.

Wijzig geen stagingbestanden die niet zijn goedgekeurd.

### 3. Werk wiki/index.md bij

Voor elke gedeelde projectpagina met een nieuwe of gewijzigde `status`:
- Werk de rij in de projectentabel bij (laatste besluit, status), of voeg een rij toe voor een nieuw project.

Voor elk gedeeld besluitdocument zonder bijgewerkte projectpagina in dezelfde batch:
- Lees de frontmatter (`project:`, `besluit:`) en pas dezelfde doorwerking toe als `ingest-note` had gedaan: werk de wikiprojectpagina bij (status, verloop, besluiten) en de indexrij. Zo valt een besluitdocument dat buiten de gewone ingestflow binnenkomt nooit stilzwijgend weg.

### 4. Voeg toe aan wiki/log.md

Voeg een rij toe direct onder de koprij in `wiki/log.md`:

```
| YYYY-MM-DD | share | <bijdrager> | <stagingbestanden> → <wikipagina's> |
```

### 5. Zoek conflictpagina's

Zoek in alle bestanden onder `wiki/` naar `status: conflict` in de frontmatter. Neem pagina's mee die in stap 2 zijn toegevoegd.

Zijn er conflictpagina's, toon ze dan als waarschuwing in de samenvatting:

```
⚠️  Conflictpagina's gevonden — curator actie vereist:
  - wiki/projecten/llm-wiki/index.md
```

### 6. Commit, push en merge request aanmaken

Geen aparte bevestigingsvraag hier: de goedkeuring in stap 1 (welke pagina's delen) is de bevestiging. Ga direct door.

```bash
git fetch origin
if git rev-parse --verify origin/ingest/YYYY-MM-DD-<bijdrager> 2>/dev/null; then
  git checkout ingest/YYYY-MM-DD-<bijdrager>
  git merge origin/ingest/YYYY-MM-DD-<bijdrager>
else
  git checkout -b ingest/YYYY-MM-DD-<bijdrager>
fi
git add wiki/
git commit -m "share: <korte omschrijving van wat er gedeeld is>"
git push origin ingest/YYYY-MM-DD-<bijdrager>
```

Maak daarna een merge request (of pull request) aan met de CLI van jullie git-platform. Pas dit commando aan op het platform van de repo en bewaar de URL die het teruggeeft:

```bash
# GitLab
glab mr create \
  --title "share: <korte omschrijving van wat er gedeeld is>" \
  --source-branch ingest/YYYY-MM-DD-<bijdrager> \
  --target-branch main \
  --label "needs-review"

# GitHub
gh pr create \
  --title "share: <korte omschrijving van wat er gedeeld is>" \
  --head ingest/YYYY-MM-DD-<bijdrager> \
  --base main \
  --label "needs-review"
```

### 7. Ruim staging op

Alleen uitvoeren als het aanmaken van de MR/PR in stap 6 is geslaagd en een URL heeft opgeleverd. Mislukt de push of de MR, sla deze stap dan over: staging blijft ongewijzigd, zodat de bijdrager stap 6 opnieuw kan draaien.

Ruim alleen de sporen van het delen op, in `../inbox/staging/`:

```bash
find ../inbox/staging -name .DS_Store -delete
find ../inbox/staging -mindepth 1 -type d -empty -delete
```

- Verwijder geen bestanden die niet gedeeld zijn: concepten die de bijdrager in stap 1 niet heeft goedgekeurd blijven staan, ook als ze in dezelfde map liggen.
- Verwijder de map `../inbox/staging/` zelf niet.
- `find ... -empty -delete` verwijdert eerst de diepste lege mappen en daarna ook de ouders die leeg zijn geworden.

### 8. Bevestig aan de bijdrager

```
Gedeeld. De merge request is aangemaakt voor de curator:

<URL>
```

Zijn er conflictpagina's gevonden, herinner de curator er dan aan die op te lossen vóór het mergen.

## Randgevallen

- **Geen stagingbestanden gevonden:** meld dit aan de bijdrager en stop. Er is niets te delen.
- **Merge-conflict met een bestaande wikipagina:** schrijf beide versies in de pagina onder een `> **Conflict:**`-blok, zet `status: conflict` in de frontmatter en markeer het in de samenvatting voor de curator.
- **De CLI (`glab`/`gh`) geeft een authenticatiefout:** de sessie van de bijdrager is verlopen of nooit ingesteld. Laat de bijdrager zelf inloggen in een eigen terminal (nooit een token in de chat plakken) en probeer stap 6 opnieuw.
