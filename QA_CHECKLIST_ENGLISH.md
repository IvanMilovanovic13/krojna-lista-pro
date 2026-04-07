# QA Checklist - English and Final UI Polish

Ovaj checklist sluzi za zavrsni prolaz kroz aplikaciju kada je aktivan `English`.
Ideja je da se proverava sistematski, bez preskakanja ekrana i bez nasumicnog lova na greske.

## Cilj

- da nijedan glavni user-facing tekst ne ostane na srpskom kada je izabran `English`
- da poruke gresaka i upozorenja budu razumljive i profesionalne
- da se tekst u poljima, tabovima i dugmadima vidi ceo
- da PDF, Excel i CSV eksport budu dosledni aktivnom jeziku
- da 2D i 3D izgled deluju komercijalno i citljivo

## Kako se radi prolaz

1. Pokreni aplikaciju.
2. Odmah prebaci jezik na `English`.
3. Prodi sve glavne tabove redom.
4. Za svaki ekran proveri:
   - da li postoji srpski tekst
   - da li je engleski prirodan i profesionalan
   - da li se labela ili tekst sece
   - da li upozorenje ili greska izlazi na engleskom
5. Na kraju proveri PDF, Excel i CSV eksport.

## Prioritet 1 - Glavni korisnicki tok

### 1. Toolbar i navigacija

Proveri:
- `Start`
- `Elements`
- `Cut List`
- `Settings`
- `Help`
- `Save`
- `Load`
- `Reset`
- `Language`

Pass kriterijum:
- nema srpskih ostataka
- dugmad nisu prevelika
- tekst nije isecen

Glavni fajlovi:
- [ui_toolbar.py](C:/Users/Korisnik/krojna_lista_pro/ui_toolbar.py)
- [ui_panels.py](C:/Users/Korisnik/krojna_lista_pro/ui_panels.py)

### 2. Wizard / room setup

Proveri:
- izbor tipa projekta
- izbor merenja `Standard / PRO`
- zidovi `Wall A / B / C`
- room setup korake
- openings / fixtures editor
- 3D room pregled

Posebno proveri:
- helper poruke
- status koraka
- nazive layout-a
- warning i error poruke

Glavni fajlovi:
- [ui_wizard_tab.py](C:/Users/Korisnik/krojna_lista_pro/ui_wizard_tab.py)
- [room_setup_wizard.py](C:/Users/Korisnik/krojna_lista_pro/room_setup_wizard.py)
- [room_floorplan_editor.py](C:/Users/Korisnik/krojna_lista_pro/room_floorplan_editor.py)
- [room_openings_editor.py](C:/Users/Korisnik/krojna_lista_pro/room_openings_editor.py)
- [ui_room_helpers.py](C:/Users/Korisnik/krojna_lista_pro/ui_room_helpers.py)

### 3. Elements

Proveri:
- levi katalog
- grupe modula
- nazive kartica
- `Add to wall`
- wall switch `A / B / C`
- `Technical / Catalog`
- `Grid`
- edit panel za element na zidu
- params panel
- sve warning poruke pri dodavanju ili izmeni

Posebno proveri:
- da nema srpskih naziva kao `Donji`, `Gornji`, `Zavrsna bocna ploca`, `Iverica`
- da se tekst u formama ne sece
- da se `Name`, `Width`, `Height`, `Depth`, `Handle`, `Grain direction` vide ceo

Glavni fajlovi:
- [ui_catalog_config.py](C:/Users/Korisnik/krojna_lista_pro/ui_catalog_config.py)
- [ui_catalog_panel.py](C:/Users/Korisnik/krojna_lista_pro/ui_catalog_panel.py)
- [ui_sidebar.py](C:/Users/Korisnik/krojna_lista_pro/ui_sidebar.py)
- [ui_sidebar_panel.py](C:/Users/Korisnik/krojna_lista_pro/ui_sidebar_panel.py)
- [ui_canvas_toolbar.py](C:/Users/Korisnik/krojna_lista_pro/ui_canvas_toolbar.py)
- [ui_canvas_2d.py](C:/Users/Korisnik/krojna_lista_pro/ui_canvas_2d.py)
- [ui_params_panel.py](C:/Users/Korisnik/krojna_lista_pro/ui_params_panel.py)
- [ui_edit_panel.py](C:/Users/Korisnik/krojna_lista_pro/ui_edit_panel.py)
- [ui_module_properties.py](C:/Users/Korisnik/krojna_lista_pro/ui_module_properties.py)

### 4. Settings

Proveri:
- sve labele inputa
- helper tekst ispod polja
- materijale
- dubine i standarde zona
- sve dijaloge i obavestenja

Posebno proveri:
- `Chipboard`
- `Bottom edge of upper cabinet`
- info poruke sa mm vrednostima
- da select i input ne seku tekst

Glavni fajlovi:
- [ui_settings_tab.py](C:/Users/Korisnik/krojna_lista_pro/ui_settings_tab.py)
- [i18n.py](C:/Users/Korisnik/krojna_lista_pro/i18n.py)

### 5. Cut List

Proveri:
- naslov i sekcije
- kolone tabela
- checklist sekcije
- by-unit prikaz
- assembly instructions
- warning i empty-state poruke

Posebno proveri:
- sirove vrednosti kolona
- friendly nazive delova
- da ne ostanu pojedini srpski nazivi u tabelama

Glavni fajlovi:
- [ui_cutlist_tab.py](C:/Users/Korisnik/krojna_lista_pro/ui_cutlist_tab.py)
- [ui_assembly.py](C:/Users/Korisnik/krojna_lista_pro/ui_assembly.py)
- [cutlist.py](C:/Users/Korisnik/krojna_lista_pro/cutlist.py)

## Prioritet 2 - Export

### 6. PDF

Proveri:
- naslov dokumenta
- project header
- summary
- by-unit sekcije
- shopping / ready-made / checklist
- assembly instructions

Posebno proveri:
- da nema mešanja srpskog i engleskog
- da redovi ne pucaju ruzno
- da je english prirodan, ne bukvalno preveden

Glavni fajlovi:
- [ui_pdf_export.py](C:/Users/Korisnik/krojna_lista_pro/ui_pdf_export.py)
- [cutlist.py](C:/Users/Korisnik/krojna_lista_pro/cutlist.py)

### 7. Excel i CSV

Proveri:
- sheet nazive
- nazive kolona
- summary sheet
- service packet
- wardrobe CSV

Glavni fajlovi:
- [cutlist.py](C:/Users/Korisnik/krojna_lista_pro/cutlist.py)

## Prioritet 3 - Vizuelni polish

### 8. 2D prikaz

Proveri:
- `Technical` i `Catalog`
- da je grid logican: `1`, `5`, `10`
- da je zid dovoljno velik i citljiv
- da se kote vide bez secenja
- da `WALL` i `free` oznake izgledaju uredno

Glavni fajlovi:
- [visualization.py](C:/Users/Korisnik/krojna_lista_pro/visualization.py)
- [ui_canvas_toolbar.py](C:/Users/Korisnik/krojna_lista_pro/ui_canvas_toolbar.py)

### 9. 3D prikaz

Proveri:
- proporcije elemenata
- radnu plocu
- sudoperu i otvor
- boju rucki prema svetlini fronta
- debljinu rucki
- visoke elemente i appliance frontove

Glavni fajlovi:
- [render_3d.py](C:/Users/Korisnik/krojna_lista_pro/render_3d.py)

## Prioritet 4 - Greske i upozorenja

### 10. Namerno izazovi greske

Obavezno testiraj:
- dodavanje elementa kada nema mesta
- preklapanje elemenata
- pogresnu sirinu / visinu / dubinu
- konflikt sa uglom
- los upload / load projekta
- eksport bez validnih podataka

Pass kriterijum:
- poruka je na engleskom
- poruka je kratka i jasna
- nema mesavine jezika

Glavni fajlovi:
- [ui_panels_helpers.py](C:/Users/Korisnik/krojna_lista_pro/ui_panels_helpers.py)
- [state_logic.py](C:/Users/Korisnik/krojna_lista_pro/state_logic.py)
- [layout_engine.py](C:/Users/Korisnik/krojna_lista_pro/layout_engine.py)

## Brza matrica za prijavu buga

Za svaki problem zabelezi:

- ekran
- aktivni jezik
- sta pise pogresno
- screenshot
- koraci za reprodukciju
- ocekivano ponasanje
- stvarno ponasanje

Primer:

- Ekran: `Elements > Edit panel`
- Jezik: `English`
- Problem: `Dubina (mm)` ostala na srpskom
- Ocekivano: `Depth (mm)`
- Screenshot: `Screenshot_XX.png`

## Zavrsna komanda za proveru posle svake serije izmena

```powershell
python run_all_tests.py --quick
python run_all_tests.py
```

## Napomena

Ako hoces maksimalno efikasan zavrsni QA, najbolji metod je screenshot-driven prolaz:

1. ti slikas ekran gde jos vidis problem
2. ja ga ispravim ciljano
3. odmah pustim testove
4. predemo na sledeci ekran
