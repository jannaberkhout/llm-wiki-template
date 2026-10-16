---
name: ingest-note
description: Process raw notes from inbox into staging drafts
---

# Skill: ingest-note

Verwerk ruwe notities uit `../inbox/raw/` tot conceptpagina's in `../inbox/staging/`. Niets bereikt de wikirepo totdat de bijdrager expliciet de share skill draait. `../inbox/` is een gewone lokale map, geen git-repo. Behalve de wiki-sync in stap 0 wordt er in deze skill niets gefetcht, gemerged, gecommit of gepusht.

## Wanneer gebruiken

Draai deze skill als de bijdrager nieuwe inboxitems naar staging wil brengen, of als een specifieke ruwe notitie in de staginglaag moet komen.

## Invoer

- Het pad naar de lokale inbox: `../inbox/raw/`
- Optioneel: een specifiek bestand
- **Naam van de bijdrager** — voor `contributed-by` in de frontmatter van de nieuwe pagina's. Web Clipper-notities leveren dit al aan via het `contributor:`-veld in hun frontmatter (ingevuld door de persoonlijke clipper-template). Voor handmatige notities: vraag het als het niet uit de context (eerdere sessie in dit gesprek) is af te leiden.
- **anonimiseren** — optioneel. Standaard: nee. Alleen toepassen als de bijdrager dit expliciet aangeeft.

## Invoertypes

Bestanden in de inbox komen uit drie bronnen. Herken ze aan extensie en frontmatter:

**Obsidian Web Clipper** (primaire bron voor webcontent)
Gegenereerd door de clipper-template. Herkenbaar aan `tags: [clippings]` en een `source:`-URL. Bevat ook `context: webclipping`, `author:`, `published:`, `created:`. Behandel ze als research, tenzij de inhoud duidelijk een project of besluit beschrijft.

**Handmatige notities** (vergaderverslagen, ideeën, besluiten)
Direct geschreven in Obsidian of een andere editor. Kunnen `context:`, `type:` en `share:` bevatten.

**Binaire documenten** (`.docx`, `.pdf`, `.pptx`, `.xlsx`)
Lokaal in de inbox gezet, nooit gecommit. Stap 2 zet ze om naar markdown voordat ze verder worden verwerkt.

## Bestandsnaam-sanitatie

Elke bestandsnaam die deze skill aanmaakt of verplaatst (in `processed/`, `staging/`, of afgeleid van een titel/slug) mag geen tekens bevatten die op Windows niet zijn toegestaan: `< > : " / \ | ? *`, en mag niet eindigen op een punt of spatie. Een bestand met zo'n teken breekt `git clone` op Windows.

Pas dit toe:
- Bij het afleiden van een slug uit een titel (stap 4): vervang illegale tekens door niets of een koppelteken, en comprimeer opeenvolgende koppeltekens.
- Bij het verplaatsen van het originele bestand naar `processed/` (stap 5): bevat de bestandsnaam uit de inbox (bijv. een Web Clipper-titel) illegale tekens, saniteer de naam dan bij het verplaatsen. De titel in de frontmatter of tekst blijft ongewijzigd, alleen de bestandsnaam wordt aangepast.

## Stappen

### 0. Synchroniseer de wiki met main

Zorg dat je de laatste versie van de wiki hebt. Merge eventuele curator-wijzigingen in voordat je staging aanmaakt.

```bash
git fetch origin
git merge origin/main
```

Bij merge-conflicten: los ze op voordat je verdergaat. `../inbox/` heeft geen git en dus geen sync-stap nodig.

### 1. Ontdek inboxbestanden

Maak een lijst van alle bestanden in `../inbox/raw/`, inclusief binaire formaten (`.docx`, `.doc`, `.pdf`, `.pptx`, `.ppt`, `.xlsx`, `.xls`). Sla bestanden over die al in `../inbox/processed/` staan.

### 2. Zet binaire bestanden om naar markdown

Zet elk binair bestand uit stap 1 met pandoc om naar markdown voordat je verdergaat:

```bash
pandoc "<input>" -t markdown -o "<input-zonder-extensie>.md"
```

Per formaat:
- **docx** — goede kwaliteit; tabellen, koppen en lijsten komen goed over
- **pdf** (tekstgebaseerd) — redelijk; kan lichte opschoning nodig hebben
- **pptx** — alleen tekst; dia's worden secties
- **xlsx** — alleen tabellen, geen formules

Na een geslaagde conversie:
- Voeg minimale frontmatter toe aan de gegenereerde `.md` als die ontbreekt:
  ```yaml
  ---
  date: YYYY-MM-DD
  context: converted-document
  original-file: <originele bestandsnaam met extensie>
  ---
  ```
- Verplaats het binaire origineel naar `../inbox/processed/` (blijft lokaal).
- Verwerk de `.md` verder als een gewoon inboxbestand.

Faalt pandoc (bijv. een gescande pdf zonder tekstlaag), sla het bestand dan over en meld het in de samenvatting als `SKIPPED (conversie mislukt — <reden>)`.

### 3. Lees en interpreteer het bestand

Bepaal wat het bestand is. Lees eerst `schema/structuur.json`: dat bevat de contenttypes van dit team (map, omschrijving, template, verplichte velden). De types hieronder (project, besluit, werkwijze) zijn de standaardtemplate; heeft het team andere types, gebruik dan die. Past het bestand bij geen enkel type, vraag de bijdrager dan waar het heen moet.

**Project** — gaat over een bestaand of nieuw project in `wiki/projecten/`.

**Besluit** — frontmatter bevat `type: besluit`, of de inhoud beschrijft duidelijk een besluit (go, no-go, parkeren, stoppen).

**Werkwijze** — beschrijft hoe het team werkt: proces, rollen, afspraken, principes of handleidingen. Komt in `wiki/werkwijze/`.

**Research of algemeen inzicht** — onderzoeksnotitie, rapport of achtergrond die bij een project hoort. Komt in `wiki/projecten/<slug>/research/`. Hoort het bij geen enkel project, vraag de bijdrager dan waar het heen moet.

### 4. Maak conceptpagina's in staging

Maak conceptpagina's in `../inbox/staging/` die de uiteindelijke wikimapstructuur spiegelen. Bijvoorbeeld:

```
../inbox/staging/projecten/llm-wiki/index.md              →  wiki/projecten/llm-wiki/index.md
../inbox/staging/projecten/llm-wiki/research/2026-07-28-markt.md  →  wiki/projecten/llm-wiki/research/...
../inbox/staging/besluiten/2026-07-29-llm-wiki-start-pilot.md     →  wiki/besluiten/...
../inbox/staging/werkwijze/overlegstructuur.md                     →  wiki/werkwijze/overlegstructuur.md
```

Gebruik het template dat bij het type hoort: het veld `template` van het type in `schema/structuur.json` (standaard `schema/project-template.md` en `schema/besluit-template.md`). Vul ook de velden uit `fields` in. Houdt de `omschrijving` van het type rekening met bijzondere regels, bijvoorbeeld voor persoonsgegevens, dan volg je die.

Zet `status: draft` op alle pagina's. Schrijf in deze stap NIET naar `wiki/`.

**Bij besluiten: werk ook de gevolgen door** (alleen als het team een besluit-type heeft dat naar een dossier verwijst; bij andere types: werk het bijbehorende dossier en de index bij op dezelfde manier, met de statusovergangen die het team heeft vastgelegd)

Het besluitdocument alleen is niet genoeg. Pas na het schrijven van `../inbox/staging/besluiten/<bestandsnaam>.md` het besluit ook toe op het project en de index in staging:

1. **Bepaal slug en besluit** uit de frontmatter (`project:`, `besluit:`) of leid ze af uit de tekst.
2. **Zoek de projectpagina in staging** op `../inbox/staging/projecten/<slug>/index.md`. Ontbreekt die, kopieer dan `wiki/projecten/<slug>/index.md` eerst naar staging. Bestaat ook die niet, maak dan een minimale stub op basis van `schema/project-template.md`.
3. **Werk de projectpagina in staging bij:**
   - `status` volgens het besluit: `go` → `actief`; `parkeren` → `gepauzeerd`; `stoppen` → `gestopt`; `no-go` en `aanpassen` → laat `status` ongewijzigd
   - `date-updated` → vandaag
   - voeg een rij toe aan de tabel onder Verloop
   - voeg een link naar het besluitdocument toe onder Besluiten
4. **Werk de index in staging bij** op `../inbox/staging/index.md` (kopieer van `wiki/index.md` als die ontbreekt): de rij van het project (laatste besluit, status), of een nieuwe rij als het project er nog niet in staat.

Bij nieuwe projecten: voeg ook een rij toe aan `../inbox/staging/index.md`.

**Anonimisering (alleen als de bijdrager dit heeft aangevraagd):**

Heeft de bijdrager `anonimiseren` opgegeven:
- Scan de tekst op herkende namen (gebruik `contributed-by`-waarden als startpunt, plus namen in de bronbestanden).
- Vervang gevonden namen door een generieke rolbeschrijving (bijv. "Jan de Vries" → "de projectleider"). Is de rol niet af te leiden, gebruik dan "een teamlid".
- Voeg toe aan de frontmatter: `anonymiseer-status: geanonimiseerd`
- Noteer in de samenvatting (stap 6) welke namen zijn vervangen.

Is `anonimiseren` niet opgegeven: laat de tekst ongewijzigd en voeg geen anonymiseer-status toe.

### 5. Archiveer de originele bron

Verplaats het originele inboxbestand (de ongewijzigde `.md`-notitie, of het in stap 2 al verplaatste binaire origineel) naar `../inbox/processed/` (maak de map aan als die ontbreekt), zodat `raw/` alleen nog bestanden bevat die nog verwerkt moeten worden. Verwijder nooit ruwe bestanden. `processed/` is alleen lokaal. De conceptpagina's uit stap 4 blijven ook lokaal in `../inbox/staging/`, totdat de bijdrager `share` draait.

Pas de bestandsnaam-sanitatie toe op de bestandsnaam vóór het verplaatsen.

```bash
mkdir -p ../inbox/processed/
mv "../inbox/raw/$(basename "$file")" "../inbox/processed/"
```

### 6. Toon een samenvatting

Geef de bijdrager een overzicht:

```
Ingest voltooid. De volgende conceptpagina's staan klaar in staging:

- staging/projecten/llm-wiki/index.md  →  wiki/projecten/llm-wiki/index.md  [geanonimiseerd: Jan de Vries → "de projectleider"]
- staging/besluiten/2026-07-29-llm-wiki-start-pilot.md  →  wiki/besluiten/...
- ...

Overgeslagen: <lijst met reden>

Bekijk ze in Obsidian via de inbox-vault (../inbox/).
Als je klaar bent om te delen, zeg: "run de share skill".
```

Vermeld alleen anonimiseringsinformatie als de bijdrager dit heeft gevraagd: welke namen zijn vervangen en door welke rol.

## Randgevallen

- **Onduidelijk bij welk project een notitie hoort:** maak stagingpagina's voor beide projecten en zet bovenaan elke pagina een opmerking dat de bijdrager dit voor het delen moet beslissen.
- **Geen duidelijk project:** maak een stagingpagina in `../inbox/staging/onbekend/` en meld dit in de samenvatting.
- **Dubbele inhoud:** herhaalt de notitie grotendeels een bestaande staging- of wikipagina, voeg dan een korte opmerking toe aan de bestaande stagingpagina in plaats van een nieuwe te maken.
- **Stagingbestand bestaat al:** voeg de nieuwe inhoud toe aan de bestaande stagingpagina in plaats van die te overschrijven.
