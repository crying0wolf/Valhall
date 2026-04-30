# Notat – hvordan implementasjonen svarer på oppgaven

Dette notatet er skrevet ut fra den faktiske koden i prosjektet. Noen kriterier er løst direkte med klasser og objekter, mens andre er løst gjennom **komposisjon** og **data-drevet logikk** i stedet for mange subklasser.

---

## 1 – Classes and Instances

### Classes and Instances
Jeg bruker klasser som `Pokemon`, `Player`, `Encounter`, `Button` og `SaveManager` som maler for objektene i spillet. Når spillet starter eller en kamp opprettes, lages det konkrete instanser av disse klassene. Hver Pokémon-instans har sin egen tilstand, for eksempel `level`, `xp`, `stats`, `needs` og om den er `hospitalized`.

Det betyr at to Pokémon kan være like i art og nivå, men fortsatt være to forskjellige objekter i minnet.

### Object Construction
Objektene lages gjennom konstruktører som `Pokemon(species, level)` og `Player(starter)`. Jeg sender inn bare det som varierer, mens resten bygges internt i klassen. For eksempel oppretter `Pokemon` selv både `Needs()` og `Stats(...)` basert på data i `data.py`.

Dette gjør konstruksjonen tryggere, fordi objektet alltid får en gyldig starttilstand.

### System Structure
Systemet er delt opp etter ansvar:

- `main.py` styrer spillflyten ved hjelp av `GameState`
- `world.py` håndterer encounters, fangst og kamp
- `player.py` holder spillerens Pokémon, inventory og badges
- `pokemon.py` inneholder logikken for stats, behov, XP og evolusjon
- `ui.py` tegner knapper, tekst og health bars
- `save_manager.py` tar seg av lagring og lasting

Dette gir tydelig ansvarsdeling og gjør koden lettere å vedlikeholde.

### Refactoring
Et viktig designvalg er at logikken ikke ligger i selve UI-koden. Når spilleren trykker på en knapp, kalles metoder som `feed()`, `walk()`, `tick()` eller `start_catch_attempt()` i de riktige objektene. I tillegg er lagring flyttet ut i `SaveManager`, og tegning av knapper er flyttet til `ui.py`.

Dette er en refaktorering som reduserer duplisering og kobling mellom deler av systemet.

### Object Interaction
Objektene samarbeider gjennom tydelige kall. Et typisk flyt-mønster er:

`UI/input -> main.py -> Player / World / Pokemon -> oppdatert state -> UI tegner på nytt`

For eksempel går mating via input i `main.py`, som deretter kaller `selected_farm_pokemon.feed()`. Selve endringen av behov skjer inne i `Pokemon`-objektet, ikke i UI.

---

## 2 – Inheritance Design

### Inheritance Design
I denne implementasjonen brukes arv **lite og bevisst**. Det tydeligste eksempelet er `PokeballButton(Button)` i `ui.py`. Her brukes arv fordi begge er knapper med felles grunnstruktur, men forskjellig utseende.

For Pokémon-typene har jeg **ikke** laget egne subklasser som `FirePokemon` eller `WaterPokemon`. I stedet er type representert som data (`Pokemon.type`) og oppslag i type-tabeller i `data.py`.

### Base vs Subclass Structure
`Button` fungerer som superklasse med felles felter og funksjoner som `rect`, tekst og `is_clicked()`. `PokeballButton` arver dette og spesialiserer bare hvordan knappen tegnes.

Det gir et ryddig skille mellom felles ansvar og spesialisert oppførsel.

### Behavior Specialization
Spesialiseringen skjer ved at `PokeballButton` overstyrer `draw()`-metoden. Dermed kan programmet bruke begge som knapper, men få ulik oppførsel ved kjøring.

For Pokémon skjer ulik oppførsel mest gjennom type-data og stats, ikke gjennom mange underklasser.

### Constructor Chaining
I `PokeballButton` brukes `super().__init__(...)`. Det sikrer at alt som `Button` trenger blir riktig initialisert før subklassen legger til sitt eget.

Uten dette kunne objektet blitt stående i en ugyldig eller ufullstendig tilstand.

---

## 3 – Composition

### Composition
Komposisjon er en sentral del av designet mitt. En `Pokemon` **har** en `Needs` og en `Stats`, i stedet for å arve dette. `Player` **har** en liste med Pokémon og et inventory, og `World` **har** en aktiv `Encounter`.

Dette gjør at hver del har sitt eget ansvar.

### Composition vs Inheritance
For type-systemet valgte jeg komposisjon og data fremfor arv. En Pokémon har et felt `type`, og kampberegningene bruker `get_type_multiplier()` fra `data.py`. Dette er mer fleksibelt enn å lage en egen klasse for hver type.

Det gjør også systemet lettere å utvide med nye arter.

### Object Ownership & Lifecycle
Hver `Pokemon` oppretter og eier sine egne komponenter (`Needs` og `Stats`). De deles ikke mellom flere Pokémon, noe som hindrer utilsiktede sideeffekter. `Player` eier `pokemon_farm`, mens `World` oppretter nye `Encounter`-objekter når spilleren går på tur eller starter kamp.

### Composing Collections
Jeg bruker en `list` for `pokemon_farm` fordi rekkefølge og iterasjon er viktig. Jeg bruker en `dict` for inventory fordi det passer godt til oppslag som `"potion" -> antall`.

---

## 4 – Polymorfisme

### Polymorfisme
Polymorfisme finnes i løsningen, men den er delvis klassisk og delvis data-drevet.

- **Klassisk polymorfisme:** `Button` og `PokeballButton` deler samme grunnform, men `draw()` oppfører seg forskjellig.
- **Data-drevet polymorfisme:** alle Pokémon bruker samme metoder som `feed()`, `tick()`, `take_damage()` og `gain_xp()`, men resultatet varierer ut fra Pokémonens type, stats og nivå.

### Shared Interface
Alle Pokémon-objekter kan behandles gjennom det samme grensesnittet. Det gjør at resten av systemet slipper å vite hvilken art Pokémonen er for å kunne bruke den.

### Method Overriding
Den tydeligste overstyringen i prosjektet er `PokeballButton.draw()`, som overstyrer `Button.draw()`. Python velger riktig metode ved kjøring ut fra hvilken objekttype det faktisk er.

---

## 5 – Abstract Base Class (ABC)

### ABC
Jeg bruker **ikke en eksplisitt ABC** i denne versjonen av prosjektet. Det betyr at dette punktet ikke er løst med `abc.ABC` og `@abstractmethod`, men heller gjennom vanlige klasser med et felles grensesnitt.

Hvis jeg skulle utviklet systemet videre, kunne jeg laget en abstrakt klasse for objekter som må støtte for eksempel `tick()`, `to_dict()` eller kampfunksjoner. Da ville kontrakten vært enda tydeligere.

---

## 6 – Encapsulation & Access Control

### Encapsulation og State Protection
Jeg beskytter tilstanden ved å la objektene styre sine egne endringer gjennom metoder som `feed()`, `pet()`, `walk()`, `sleep()`, `take_damage()` og `use_item()`. Det gjør at resten av programmet ikke trenger å endre interne verdier direkte.

Et konkret eksempel er behovssystemet:

- `Needs.decay()` senker behovene over tid
- Deretter kalles `_clamp()`
- `_clamp()` bruker `max(0, min(100, value))`

Det betyr at behov som `hunger`, `energy`, `happiness` og `social` alltid holdes mellom **0 og 100**.

> **Eksempel jeg kan si muntlig:** Feed-behovet går ikke i minus fordi alle behov blir clampet til intervallet `0–100` i `Needs._clamp()`. I tillegg bruker `feed()` `min(100, ...)`, så verdien kan heller ikke gå over maks.

På samme måte hindrer `take_damage()` at HP går under 0, og `Player.use_item()` hindrer at inventory blir negativt.

### Information Hiding
Lagring og lasting er kapslet inn gjennom `to_dict()` og `from_dict()`. Resten av systemet trenger derfor ikke å vite detaljene om hvordan en Pokémon eller en spiller gjøres om til JSON.

---

## ✅ Save-funksjon (JSON)

Jeg har lagt inn lagring og lasting av spilltilstand med JSON:

- `SaveManager.save()` skriver data til fil
- `Player.to_dict()` lagrer spillerens navn, farm, inventory, penger og badges
- `Pokemon.to_dict()` lagrer art, level, XP, stats, needs og sykehusstatus
- `Player.from_dict()` og `Pokemon.from_dict()` bygger nye objekter fra JSON-data når spillet lastes inn

Dette er en god løsning fordi jeg lagrer **bare nødvendig data**, ikke hele Python-objekter direkte. Det gjør lagringen robust og enkel å videreutvikle.

---

## Kort oppsummering til muntlig

Det viktigste å fremheve er at løsningen bruker objektorientering på en ryddig måte:

1. **Klasser og objekter** modellerer spiller, Pokémon og verden.
2. **Komposisjon** er hoveddesignet (`Pokemon` har `Needs` og `Stats`).
3. **Arv og polymorfisme** brukes der det passer, særlig i UI.
4. **Kapsling** beskytter tilstanden mot ugyldige verdier.
5. **JSON-lagring** viser at objektene kan serialiseres og gjenoppbygges på en kontrollert måte.

Hvis jeg får spørsmål om arv eller ABC, kan jeg også forklare at jeg bevisst har valgt **komposisjon og data-drevet logikk** flere steder, fordi det passet bedre til denne implementasjonen.
