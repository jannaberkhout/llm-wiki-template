---
name: setup-structuur
description: Pas de mappenstructuur van de wiki aan op het team: kies contenttypes (bijvoorbeeld klanten, gesprekken, kandidaten in plaats van projecten en besluiten), genereer mappen, templates en dashboard, en werk AGENTS.md en README.md bij. Gebruik bij het opzetten van een nieuwe teamwiki of als het team zijn indeling wil wijzigen.
---

# setup-structuur

De wiki is opgebouwd uit **contenttypes**. Elk type is een map onder `wiki/` met een eigen template. Welke types er zijn staat in `schema/structuur.json`. De template levert drie startertypes (`projecten`, `besluiten`, `werkwijze`), maar een team dat niet projectmatig werkt past die aan: een sales team heeft bijvoorbeeld `klanten` en `gesprekken`, een detacheerder `klanten`, `kandidaten` en `gesprekken`.

Deze skill voert het gesprek, past `structuur.json` aan en laat het script `setup_structuur.py` de bestanden aanmaken. Het script verwijdert nooit iets.

## Wanneer

- Bij het opzetten van de wiki (voordat er inhoud in staat) — dan is alles vrij aan te passen.
- Later, als het team een type wil toevoegen, hernoemen of schrappen. Is er al inhoud, werk dan voorzichtig (zie "Bestaande wiki").

Alleen de curator draait deze skill.

## Stappen

### 1. Begrijp hoe het team werkt

Stel de vragen één voor één, in gewone taal, en pas door op de antwoorden. Niet alles in één keer.

1. **Waar gaat het werk om?** Wat zijn de dingen waar het team documentatie over bijhoudt? (projecten, klanten, kandidaten, opdrachten, producten, gesprekken, besluiten, ...)
2. **Welke daarvan zijn een dossier, en welke losse documenten?**
   - *Dossier*: een ding dat een eigen map krijgt met een `index.md` en eventueel bijlagen, en dat in de loop van de tijd verandert (een klant, een kandidaat, een project).
   - *Bestand*: een losse pagina met een datum die niet verandert (een gesprek, een besluit, een notitie).
3. **Per type:** hoe heet het in het Nederlands (enkelvoud en meervoud)? Welke statussen doorloopt het? Welke extra gegevens horen op elke pagina (bijvoorbeeld bij een gesprek: welke klant, welke datum, soort gesprek)? Welke kopjes moet een pagina hebben?
4. **Welke dossiers horen op het dashboard** (`wiki/index.md`)? Meestal het hoofdtype (klanten, projecten).
5. **Is er een werkwijze-map nodig?** (Meestal ja: afspraken en processen.)

### 2. Let op persoonsgegevens

Bij types over mensen (kandidaten, klantcontacten) geldt: namen van bijdragers staan alleen in de frontmatter, en de wiki heeft een brede kring van lezers. Vraag de curator hoe om te gaan met persoonsgegevens van derden (AVG: bewaartermijn, wie mag lezen, rol of initialen in plaats van volledige naam). Leg het antwoord vast in de `omschrijving` van het type, zodat ingest-note het volgt. Gaat het om gevoelige gegevens die de wiki niet aankan, zeg dat dan en stel voor dat type buiten de wiki te houden.

### 3. Toon het voorstel en wacht op akkoord

Laat een tabel zien en wacht op bevestiging voordat je schrijft:

```
Voorstel voor de structuur van <TEAMNAAM>:

| Map | Soort | Op dashboard | Extra velden | Statussen |
|---|---|---|---|---|
| wiki/klanten/ | dossier | ja | branche, accountmanager | prospect · actief · inactief |
| wiki/gesprekken/ | bestand | nee | klant (verplicht), datum (verplicht), soort | — |
| wiki/werkwijze/ | bestand | nee | — | — |
```

### 4. Pas `schema/structuur.json` aan

Bewerk het bestand. Velden per type:

| Veld | Betekenis |
|---|---|
| `key` | mapnaam onder `wiki/` (kleine letters, cijfers, koppeltekens) |
| `label`, `label_plural` | weergavenaam enkelvoud en meervoud |
| `omschrijving` | wat hoort hier; komt in de map-README en README.md |
| `kort` | optioneel: korte regel voor AGENTS.md |
| `layout` | `dossier` (map per item, met `index.md`) of `bestand` (losse pagina's) |
| `naamconventie` | bestandsnaam of padpatroon, bijvoorbeeld `<slug>/index.md` of `YYYY-MM-DD-<klant>-<onderwerp>.md` |
| `submappen` | alleen bij dossier: vaste submappen, bijvoorbeeld `["gesprekken", "bijlagen"]` |
| `template` | bestandsnaam in `schema/`, of `null` voor geen template |
| `status_values` | optioneel: lijst toegestane statussen (komt in het template) |
| `sections` | optioneel: kopjes van het template |
| `fields` | extra frontmattervelden: `{"name", "hint", "required"}` |
| `validate` | `true`: de lint-skill controleert de verplichte velden |
| `in_index` | alleen bij dossier: krijgt een tabel in `wiki/index.md` |
| `index_columns` | extra kolommen in die tabel, tussen titel en status |
| `hernoemd_van` | alleen bij hernoemen: de oude mapnaam; het script doet `git mv` |

Gebruik `hernoemd_van` om een bestaand type te hernoemen in plaats van het te verwijderen en opnieuw aan te maken.

### 5. Controleer en pas toe

```bash
uv run .agents/skills/setup-structuur/setup_structuur.py check    # niets schrijven, toont wat er gebeurt
uv run .agents/skills/setup-structuur/setup_structuur.py apply
```

`apply` doet:
- maakt `wiki/<key>/` en een `README.md` per type;
- genereert `schema/<template>` voor types waarvan het bestand nog niet bestaat;
- ververst de mappenlijsten in `AGENTS.md` en `README.md`;
- maakt `wiki/index.md` opnieuw aan als er nog geen rijen in staan.

Bestanden die met de hand zijn bewerkt worden niet overschreven. Gegenereerde bestanden herken je aan de eerste regel `<!-- gegenereerd door setup-structuur ... -->`; haal die regel weg zodra je zelf wijzigt.

### 6. Ruim de rest op (dit doet het script niet)

- Lees het resultaat van `check`/`apply` en los alle `LET OP`-regels op. Bij een hernoemd type blijft de oude `README.md` staan (die is met de hand bewerkt): schrijf hem om, of haal de handmatige versie weg en draai `apply` opnieuw.
- Mappen van types die zijn vervallen: laat het team beslissen of de inhoud naar `wiki/archive/` gaat. Verwijder zelf niets.
- Starterstemplates die niet meer passen (`schema/project-template.md`, `schema/besluit-template.md`): verwijder ze alleen als geen type ze nog gebruikt.
- Zoek in `AGENTS.md`, `README.md` en `.agents/skills/*/SKILL.md` naar voorbeelden die nog over projecten of besluiten gaan en pas ze aan als dat verwarring geeft. De skills lezen de types zelf uit `structuur.json`; de voorbeelden zijn alleen illustratie.
- Draai `uv run .agents/skills/lint/check_structure.py` en controleer dat er geen blockers staan.
- Voeg een rij toe aan `wiki/log.md`: `| YYYY-MM-DD | setup-structuur | — | <samenvatting van de gekozen types> |`
- Commit op een eigen branch en laat de wijziging door de curator mergen.

## Bestaande wiki

Staat er al inhoud in de wiki, voer dan alleen **toevoegingen en hernoemingen** door. Een type schrappen betekent: pagina's verplaatsen naar `wiki/archive/` (met `git mv`), links bijwerken en `lint` draaien. Doe dat niet in dezelfde stap als andere wijzigingen.
