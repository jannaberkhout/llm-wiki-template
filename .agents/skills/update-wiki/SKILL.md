---
name: update-wiki
description: Sync the wiki with main and show what's new since the last sync — use when a contributor just wants to update/sync the wiki, without running any other skill
---

# Skill: update-wiki

Synchroniseer deze repo met `main` en meld wat er veranderd is. Er wordt niets geschreven: dit is een read-only sync, handig als een bijdrager wil bijlezen voordat hij in Obsidian gaat browsen, of wil weten wat er nieuw is.

## Wanneer gebruiken

Draai deze skill als een bijdrager vraagt om "de wiki bij te werken" of te synchroniseren, of wil weten wat er nieuw is, zonder een andere skill te vragen. De andere skills synchroniseren zelf al als stap 0. Deze skill is voor het geval synchroniseren het enige is dat gevraagd wordt.

## Invoer

Geen.

## Stappen

### 0. Onthoud de huidige staat

Onthoud vóór het fetchen de huidige HEAD en lees de huidige inhoud van `wiki/log.md`.

```bash
git rev-parse HEAD
```

### 1. Synchroniseer met main

```bash
git fetch origin
git merge origin/main
```

Bij merge-conflicten: los ze op voordat je verdergaat.

### 2. Bepaal of er iets veranderd is

Vergelijk de HEAD van vóór stap 1 met de huidige HEAD.

- **Ongewijzigd:** meld "De wiki is al up-to-date. Geen nieuwe wijzigingen." en stop.
- **Gewijzigd:** ga door naar stap 3.

### 3. Toon een samenvatting van wat er nieuw is

Vergelijk de inhoud van `wiki/log.md` van vóór en na de merge. Toon de rijen die nieuw bovenaan de tabel staan. Dat zijn precies de acties die andere bijdragers of de curator sinds de laatste sync hebben gedaan.

```
De wiki is bijgewerkt. Nieuw sinds je laatste sync:

| 2026-09-05 | share | anders | ... |
| 2026-09-04 | share | iemand | ... |
```

**Terugval (zeldzaam):** is `wiki/log.md` zelf niet gewijzigd terwijl de HEAD wel veranderde (bijv. een fix van de curator zonder logregel), gebruik dan `git log --oneline <oude-HEAD>..HEAD` en toon de commit-onderwerpen als samenvatting.

## Randgevallen

- **Merge-conflicten:** los ze op zoals bij de andere skills en vermeld in de samenvatting welke bestanden een conflict hadden en hoe je het hebt opgelost.
- **`wiki/log.md` zelf heeft een conflict:** los dat eerst op en gebruik daarna de terugval (`git log --oneline`) voor de samenvatting, in plaats van tabelrijen te vergelijken op een net-geconflicteerd bestand.
- **Niet in de repo-root:** meld dit en stop. Deze skill verwacht dat je in de root van de wikirepo werkt.
