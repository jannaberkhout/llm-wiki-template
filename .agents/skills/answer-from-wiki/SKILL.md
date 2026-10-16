---
name: answer-from-wiki
description: Synthesize answers from the team wiki knowledge base
---
# Answer From Wiki

Gebruik deze skill om een vraag van een gebruiker te beantwoorden met de wiki.

## Werkwijze

### 0. Synchroniseer de wikirepo met `main`

Doe dit voordat je zoekt.

```bash
git fetch origin
git merge origin/main
```

Bij merge-conflicten: los ze op voordat je verdergaat.

### 0.5. Vraag om verduidelijking bij onduidelijke vragen

ALS de vraag meerdere interpretaties toelaat, **moet je eerst doorvragen** en niet meteen antwoorden.

**Wanneer doorvragen** — bij onduidelijkheid in:

1. **Term of begrip**: het woord kan meerdere dingen betekenen in de wiki.
   - *Voorbeeld*: "Hoeveel notities staan er in de wiki?" → Wat versta je onder "notities"? Pagina's in `wiki/projecten/`, besluiten in `wiki/besluiten/`, of alle markdown-bestanden?
2. **Bereik**: niet duidelijk of de vraag over één project, een deel of de hele wiki gaat.
   - *Voorbeeld*: "Wat is de status?" → Heb je een specifiek project in gedachten, of bedoel je de hele wiki?
3. **Tijdspunt**: de vraag kan een specifiek moment bedoelen of nu.
   - *Voorbeeld*: "Welke besluiten zijn er genomen?" → Alleen de laatste, of de hele geschiedenis?
4. **Context**: de vraag is te breed voor een zinvol antwoord.
   - *Voorbeeld*: "Vertel me over project X" → Wil je de samenvatting, de besluiten, de research of alles?

**Hoe doorvragen**
- Maximaal 1-2 vragen.
- Benoem kort welke interpretaties mogelijk zijn, zodat de gebruiker kan kiezen.
- Je hoeft geen opties voor te leggen. "Bedoel je X, Y of Z?" is goed.
- Is de vraag al specifiek genoeg: antwoord direct.

## Zoeken en antwoorden

Na eventuele verduidelijking (of direct als de vraag specifiek is):

1. Lees `schema/structuur.json` om te weten welke soorten pagina's de wiki heeft en in welke map ze staan. Zoek daarna in `wiki/`.
2. Gebruik `../inbox/processed/` en `../inbox/raw/` als aanvullend bewijs wanneer nodig.
3. Geef de voorkeur aan synthese boven ruwe fragmenten.
4. Benoem onzekerheid als notities onvolledig zijn of elkaar tegenspreken.
5. Verwijs naar de relevante gecureerde pagina's.
6. Levert het antwoord een duurzame synthese op, bied dan aan om een wikipagina aan te maken of bij te werken.

## Antwoordstijl

- Begin met het antwoord.
- Citeer het sterkste lokale bewijs.
- Houd letterlijke citaten kort.
- Maak onderscheid tussen wat de wiki zegt en wat je zelf afleidt.
