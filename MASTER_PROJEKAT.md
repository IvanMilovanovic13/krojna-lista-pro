# MASTER PROJEKAT - Krojna Lista PRO
**Poslednje ažuriranje:** 16. mart 2026 (sesija 9)

---

## O PROJEKTU

**Naziv app:** Krojna Lista PRO
**Cilj:** Web aplikacija za jednostavno projektovanje kuhinje/nameštaja i dobijanje profesionalne krojne liste.
**Tech stack:** Python + NiceGUI + Matplotlib + ReportLab + Pandas

**Scope odluka (12.03.2026):**
- `krojna_lista_pro` je iskljucivo aplikacija za kuhinju
- TV / ormari / hodnik / kupatilo / kancelarija izlaze iz scope-a ove app
- za te scenarije koristi se posebna aplikacija `krojna_studio`

---

## TRENUTNA STRUKTURA KODA (REALNO STANJE — 42 fajla, mart 2026)

```text
krojna_lista_pro/
│
├── app.py                        ← entry point, GLOBAL_UI_STYLE, ui.page('/')
├── state_logic.py                ← AppState singleton, kitchen/room mutacije, save/load JSON
├── layout_engine.py              ← pack/insert algoritmi, zone Y pozicije
├── cutlist.py                    ← krojna lista, MANUFACTURING_PROFILES
├── visualization.py              ← matplotlib 2D rendering engine
├── render_3d.py                  ← NiceGUI WebGL 3D scene
├── module_templates.json         ← katalog 30+ modula
├── module_templates.py           ← loader JSON kataloga
├── i18n.py                       ← SVI srpski stringovi (~412 linija)
├── svg_icons.py                  ← SVG ikone za ~30 template tipova
├── room_setup_wizard.py          ← wizard korak 4 (prostorija, otvori)
├── room_openings_editor.py       ← editor otvora/instalacija
├── smoke_scenarios.py            ← automatski smoke testovi
├── test_wall_upper.py            ← testovi wall_upper zone
│
├── ui_panels.py                  ← glavna orkestracija (~406 lin)
├── ui_main_content.py            ← tab router/dispatcher
├── ui_navigation.py              ← switch_tab() + room validacija
├── ui_toolbar.py                 ← toolbar layout
├── ui_panels_helpers.py          ← delegation helperi
│
├── ui_sidebar.py                 ← sidebar shell (ADD/EDIT tab)
├── ui_sidebar_panel.py           ← composer: sidebar + palette + params
├── ui_sidebar_actions.py         ← "Dodaj na zid" primary action state
│
├── ui_catalog_panel.py           ← render_palette(), render_variants()
├── ui_catalog_config.py          ← PALETTE_TABS, _FRONT_COLOR_PRESETS (16 boja)
│
├── ui_params_panel.py            ← add-mode: dimenzije, fioke, dubina (~563 lin)
├── ui_edit_panel.py              ← edit-mode: izmena modula, swap, delete (~661 lin)
├── ui_module_properties.py       ← desni properties panel (~293 lin)
│
├── ui_canvas_2d.py               ← render_nacrt() matplotlib canvas
├── ui_canvas_toolbar.py          ← toolbar iznad canvasa
├── ui_image_utils.py             ← fig_to_data_uri_exact()
│
├── ui_elements_tab.py            ← Elements tab: 2D/3D mode switch
├── ui_cutlist_tab.py             ← Krojna lista tab (~221 lin)
├── ui_settings_tab.py            ← Podešavanja (~281 lin)
├── ui_nova_tab.py                ← Nova kuhinja / save / load (~103 lin)
├── ui_help_tab.py                ← Pomoć markdown (11 lin)
├── ui_wizard_tab.py              ← Wizard koraci 1-4 (~232 lin)
│
├── ui_add_above_dialogs.py       ← dijaloži za wall_upper/tall_top (~218 lin)
├── ui_assembly.py                ← uputstvo za montažu po zonama (~297 lin)
├── ui_pdf_export.py              ← build_pdf_bytes() ReportLab (~305 lin)
├── ui_project_io.py              ← toolbar save/load akcije (~86 lin)
├── ui_room_helpers.py            ← ensure_room_walls(), ROOM_OPENING_TYPES (~49 lin)
└── ui_color_picker.py            ← color picker sa presetovima (~80 lin)
```

Napomena: ranije informacije o `main.py` i starom `sidebar.py` više ne važe za aktivan flow.

---

## STATUS FAZA (AŽURIRANO — 11.03.2026)

### Završeno
- Faza 0: bugfix osnove prikaza
- Faza 3A: paleta elemenata (Donji/Gornji/Visoki/Ugradni)
- Faza 3B: 2D prikaz + 3D preview elemenata
- Faza 3C: selekcija, edit, brisanje, swap, quick edit
- Faza 4A: krojna lista osnova + PDF + 2D/3D preview u izveštaju
- Zone Depth Standards (STANDARD/CUSTOM/INDEPENDENT)
- Podešavanja (materijali, dimenzije, granice, grid, itd.)
- Save/Load JSON projekta
- Excel export krojne liste
- i18n centralizacija (gotovo 100%)
- KL black/white stil
- Room setup wizard (multi-wall A/B/C, otvori, instalacije)
- Modularizacija ui_panels.py (17+ novih modula)
- smoke_scenarios.py auto testovi

### Urađeno u sesiji 3 (11.03.2026)
- **n_shelves wiring** — `ui_edit_panel.py`: `_collect_drawer_params` sada čuva broj polica pri Apply
- **Ormari u katalogu** — `ui_catalog_config.py`: dodat tab "Ormari" (key: `garderoba`) sa svim ormar grupama
  - Krilna i klizna, Američki plakar, Unutrašnje sekcije, Ugaoni ormari
- **SVG ikone za ormare** — `svg_icons.py`: dodate posebne ikone za `INT_SHELVES`, `INT_DRAWERS`, `INT_HANG`
- **Krojna lista — 5 bugova popravljeno** (detalji u sekciji Audit ispod)
- **Krojna lista — dimenzije sve tačne** — provjera XLSX exporta ručno i po formulama (86 redova, 25+ modula)
- **PDF engine ujedinjen** — `ui_panels.py`: jedna putanja kroz `cutlist.generate_cutlist_pdf()`, uklonjen paralelni tok
- **PDF error logging** — `ui_cutlist_tab.py`: dodat `_LOG.exception(...)` na pad PDF exporta
- **Room setup — 3 jasna koraka** — `room_setup_wizard.py`: dugmad `1) Zid / 2) Dimenzije / 3) Otvori`, napredne opcije sklonjene u ekspanziju
- **Reset projekta dugme** — `ui_toolbar.py` + `ui_panels.py` + `i18n.py`: dugme sa potvrdom za brisanje cijelog projekta

### Urađeno u sesiji 5 (12.03.2026)
- **WALL_CORNER min. širina** — `state_logic.py`: ugaoni min. sirina sada je zone-aware:
  - `BASE_CORNER` → min. 800mm (ostalo)
  - `WALL_CORNER` → min. 450mm (novo, ranije je greškom bilo 800mm)
- **Dijagonalni corner ikone** — `ui_catalog_panel.py`: SVG bypass za `BASE_CORNER_DIAGONAL` i `WALL_CORNER_DIAGONAL`
  - ranije su obje verzije (L-oblik i dijagonalna) prikazivale identičnu ikonu
  - sada `DIAGONAL` u TID-u forsira SVG prikaz koji vizuelno prikazuje dijagonalni front

### Urađeno u sesiji 7 (16.03.2026)
- **Strateška odluka: jedan zid → produkcija** — L-kuhinja se razvija u odvojenom beta projektu, potom integriše
- **L-kuhinja sakrivena iz UI-ja** — `ui_wizard_tab.py` L199-200: `l_oblik_desni` i `l_oblik_levi` postavljeni na `aktivan=False` (prikazuju se kao "Uskoro" kartice); engine kod ostaje netaknut
- **Ugaoni tab u katalogu** automatski nestaje (već bio uslovljen `kitchen_layout == 'l_oblik'`)
- **Audit produkcijske spremnosti** — detaljna analiza tačnosti i krojna liste; rezultati u sekciji "Audit — Produkcijska Spremnost" ispod
- **Prioritetna lista za 100% tačnost** — 6 konkretnih zadataka dokumentovano i uvršteno u agendu

### Urađeno u sesiji 6 (15.03.2026)
- **Kompletan audit koda za L-kuhinju** — pregled svih 42 fajla, potvrđeni pozitivni nalozi:
  - anchor auto-placement ugaonih elemenata (state_logic.py L590-597, L664-665) ✅
  - wall switch dugmad u toolbar-u (Zid A/B/C) ✅
  - sokla i radna ploča splitovane po zidovima u cutlist.py ✅
  - 3D L-krilo za ugaone elemente ✅
- **Pronađen kritični bug** — `layout_engine.py` ne primenjuje corner offset za Wall B:
  - Wall B elementi počinju od x=0
  - Wall A elementi (dubina 560mm) fizički zauzimaju x=0..560mm na Wall B
  - Rezultat: 560×560mm kolizija u uglu vidljiva u 3D prikazu
- **Zadaci za sesiju 6** → vidi sekciju `P2A-4` u agendi

### Delimično završeno / u toku
- **Krojna lista hardware** — klinovi za police i ručke još uvek nedostaju (vidi P0 agendu)
- 2D/3D paritet svih edge-case scenarija (automatizovan smoke prolazi)
- Room setup/wizard UX (3 koraka implementirano)

### Nije započeto (strateške faze)
- L-kuhinja (razvija se u odvojenom beta projektu, integriše se naknadno)
- U/galija/ostrvo layout
- SaaS/auth/cloud/billing/deploy
- Sheet optimizer / CNC nesting
- Undo/redo

---

## 7 KORAKA REFAKTORA - STATUS

1. 3D levo/desno mapiranje + korisnički front pogled: **ZAVRŠENO**
2. SR latinica kroz centralni i18n sloj: **ZAVRŠENO**
3. KL black/white globalno (bez plavih akcenata): **ZAVRŠENO**
4. Stabilan error handling (bez tihog `pass`): **ZAVRŠENO**
5. Razbijanje `ui_panels.py` na module: **ZAVRŠENO**
6. 2D↔3D paritet + smoke scenariji: **ZAVRŠENO**
7. `ui.run` izdvojen iz importabilnog dela: **ZAVRŠENO**

---

## ŠTA JE VEĆ MODULARIZOVANO

Svi UI moduli su već izdvojeni. Kompletan spisak u sekciji "Trenutna struktura koda" iznad.

---

## AUDIT — KROJNA LISTA (11.03.2026)

### Metod provjere
1. **Audit koda** — ručno praćenje svake `if/elif` grane u `cutlist.py` za svaki template ID (string pattern matching zamke)
2. **XLSX provjera** — skriptu koja čita eksport `krojna_lista_20260311.xlsx`, grupira komade po modulima i poredi sa formulama
3. **Formule koje se provjeravaju:**
   - `Stranica: CUT = d × h`
   - `Dno/Plafon: CUT = (w − 2×18) × (d − 18)`
   - `FIN = CUT − n_kantova × 2mm`

### Bugovi pronađeni i popravljeni

| # | Šta je bilo pogrešno | Uzrok | Fix |
|---|---|---|---|
| 1 | `BASE_DOOR_DRAWER` — vrata nisu generisana u fronts | `"DOOR_DRAWER"` sadrži `"DRAWER"` → padao u pogrešnu granu | Dodat poseban `elif "DOOR_DRAWER" in tid:` PRIJE `elif "DRAWER" in tid:` |
| 2 | `BASE_DOOR_DRAWER` — nedostajao klizač za fioku u hardware | Isti uzrok kao #1 | Dodat hardware blok za DOOR_DRAWER |
| 3 | `TALL_WARDROBE_AMERICAN` — nula frontova | TID nije bio ni u `_DOOR_TIDS` ni u `"1DOOR"/"2DOOR"` patternima | Dodat `elif "WARDROBE_AMERICAN" in tid:` — generiše klizne panele |
| 4 | `TALL_WARDROBE_CORNER / CORNER_SLIDING` — nula frontova | Isti problem | Proširena detekcija vrata: dodao `"WARDROBE" in tid and "CORNER" in tid` |
| 5 | `TALL_WARDROBE_2DOOR_SLIDING` — pogrešno dobijao srednju vertikalu | `if "2DOOR" in tid:` hvata i klizna ormara | Fix: `if "2DOOR" in tid and "SLIDING" not in tid:` |

**Bug #1 POTVRĐEN direktno iz XLSX-a:** modul `#6 [D] Donji (vrata + fioka) — 1000×720` imao samo "Front fioke 1" — **nigdje vrata front.**

### Dimenzije korpusa — sve tačne
Provjera svih 86 redova / 25+ modula u Korpus sheetu XLSX exporta:

| Komad | Formula | Status |
|---|---|---|
| Leva/Desna strana | `d × h` | ✅ |
| Dno / Plafon | `(w−36) × (d−18)` | ✅ |
| Srednja vertikala | `d × h` (samo hinged 2DOOR) | ✅ |
| Police | `(w−36) × (d−18)` | ✅ |
| FIN dimenzije | `CUT − n_kantova × 2mm` | ✅ |

### Preostala ograničenja krojna liste (nije 100% "fabrički standard")
- Okovi pokrivaju samo dio spektra (šarke, klizači, lift-up, MZS front) — nema kompletne liste potrošnog materijala
- Nema profila po proizvođaču (Blum/Hettich/GTV), pravila bušenja i razmaka
- Nema validacija konflikata i "manufacturing warnings"

---

## OCJENA PROJEKTA (ažurirano 11.03.2026)

| Kategorija | Ocjena | Komentar |
|-----------|--------|---------|
| Arhitektura koda | 85/100 | 42 modula, i18n, error handling, smoke testovi |
| Funkcionalnost | 82/100 | Kompletan workflow wizard→dizajn→krojna lista→PDF/Excel; ormar tab dodat |
| Krojna lista tačnost | 78/100 | 5 bugova popravljeno, dimenzije tačne; okovi/potrošni materijal nepotpuni |
| Tehnički 2D prikaz | 65/100 | Informacije su tu, ali vizuelno bučno |
| 3D prikaz | 30/100 | Funkcionalan ali daleko od standarda |
| UX/Tok rada | 73/100 | Room setup sad 3 jasna koraka, Reset dugme dodato |
| Vizuelni dizajn UI | 68/100 | B&W sistem konzistentan, sidebar gust |
| Katalog elemenata | 75/100 | Dodata i Ormari kategorija sa svim grupama |
| **UKUPNO** | **75/100** | Jak **beta/MVP** — spreman za prve testne korisnike |

### Vizualizacija — trenutno vs. postizivo

| Prikaz | Sad | Postizivo |
|--------|-----|-----------|
| Tehnički 2D | ~62% | ~80% (uglavnom čišćenje slojeva) |
| Katalog 2D | ~55% | ~65% (ravna 2D vs. 3D referenca) |
| 3D | ~22% | ~45% (WebGL bez custom shadera ima ograničenja) |

### Šta drži projekat ispod 80/100
1. **3D prikaz** — kutije bez senke, nije prodajni argument
2. **Samo jedan-zid layout aktivno radi** — L/U/galija/ostrvo su "Uskoro" (60% tržišta kuhinja)
3. **Krojna lista** — okovi i potrošni materijal nisu kompletni za fabričku upotrebu
4. **Vizualizacija** nije na nivou konkurencije (IKEA planner, KD Max)

---

## AGENDA ZA REALIZACIJU — PO PRIORITETIMA

### P0 — Hitno (blokiraju prvu upotrebu u produkciji)

| # | Zadatak | Status | Fajlovi |
|---|---|---|---|
| P0-1 | ~~Ujednačiti tok prostora za laike (3 koraka: Zid/Dimenzije/Otvori)~~ | ✅ URAĐENO | `room_setup_wizard.py` |
| P0-2 | ~~Stabilizovati PDF eksport (jedan engine + detaljan log)~~ | ✅ URAĐENO | `ui_panels.py`, `ui_cutlist_tab.py` |
| P0-3 | ~~Krojna lista — 5 kritičnih bugova~~ | ✅ URAĐENO | `cutlist.py` |
| P0-4 | ~~L-kuhinja sakrijena iz UI-ja~~ (corner offset rešava se u beta projektu) | ✅ URAĐENO | `ui_wizard_tab.py` L199-200 |
| P0-5 | ~~Fix template ID — `smoke_scenarios.py` L930: `"BASE_3DRAWER"` → `"BASE_DRAWERS_3"`~~ | ✅ URAĐENO (sesija 7) | `smoke_scenarios.py` |
| P0-6 | ~~Shelf pins (klinovi za police)~~ — već postojali (L2082-2089), potvrđeni testom | ✅ POTVRĐENO (sesija 7) | `cutlist.py` |
| P0-7 | ~~Ručke/Pulls~~ — `handle` ključ u sve 3 brande + generisanje po broju frontova; 36/36 smoke OK | ✅ URAĐENO (sesija 7) | `cutlist.py` |
| P0-8 | ~~Validacija `door_height`~~ — clamp: ako `door_height > h - 80mm` → fallback na 72% proporciju | ✅ URAĐENO (sesija 7) | `cutlist.py` |
| P0-9 | **QA matrica** — ručni end-to-end klik-smoke svih tabova pred release | ⬜ TODO | — |

### P1 — Sledeće (kvalitet i tačnost)

| # | Zadatak | Status | Fajlovi |
|---|---|---|---|
| P1-1 | **Wardrobe hardware** — klizne šine za `TALL_WARDROBE_2DOOR_SLIDING`, `TALL_WARDROBE_CORNER_SLIDING`, `TALL_WARDROBE_AMERICAN`; sipka za vešanje za `TALL_WARDROBE_INT_HANG`; ručke po kliznom krilu | ✅ URAĐENO | `cutlist.py` |
| P1-2 | **Prošireni okovi** — `hinge_plate` ključ (BLUM=ploča, HETTICH="" integrisano, GTV=ploča); `handle_screw` ključ; project-level: montažne ploče šarki + vijci za ručke (2/ručka); bušenje nota na šarke redove | ✅ URAĐENO | `cutlist.py` |
| P1-3 | **Validacije konflikata** — `BASE_COOKING_UNIT` i freestanding validacije već postoje (w < 600); dodato `BASE_HOB` w < 450mm upozorenje | ✅ URAĐENO | `cutlist.py` |
| P1-4 | ~~**3D minimalna poboljšanja**~~ — frontalni ugao: "front" view promenjen na 20° 3/4 ugao (kamera desno, vidi se dubina korpusa); ispravka buga `_lock_scene_to_horizontal_orbit` (nedostajalo `cam_x/y/z`); dinamički polar_angle; radna ploča i senčanje već implementirani | ✅ URAĐENO (sesija 9) | `render_3d.py` |
| P1-5 | **Tehnički 2D čišćenje** — grid skrvan u tehničkom modu (`show_grid and not technical`); kote na y=-40 (ispod dna) i y=wall_h+45 (iznad vrha) — već implementirano | ✅ URAĐENO | `visualization.py` |
| P1-6 | **Smoke test pokrivenost** — dodati 3 nova testa: wardrobe hardware counts, freestanding validacije, standardni hardware counts (sarke/rucke/klizaci) | ✅ URAĐENO | `smoke_scenarios.py` |

### P2 — Strateški (dugoročno)

| # | Zadatak | Status |
|---|---|---|
| P2-1 | L-kuhinja integracija iz beta projekta | ⬜ TODO |
| P2-2 | U/galija/ostrvo layout | ⬜ TODO |
| P2-3 | Undo/redo | ⬜ TODO |
| P2-4 | Sheet optimizer / CNC nesting | ⬜ TODO |
| P2-5 | SaaS/auth/cloud/billing/deploy | ⬜ TODO |

---

## AUDIT — PRODUKCIJSKA SPREMNOST (18.03.2026 — sesija 9, ažurirano)

> **Cilj:** Dovesti tačnost krojna liste i hardware BOM-a na 100% pre naplaćivanja.

### Status po kategorijama (AŽURIRANO)

| Kategorija | Pre sesija 7-9 | Sada | Cilj | Preostali blokeri |
|---|---|---|---|---|
| Dimenzije korpusa | 92% | **97%** | 100% | Corner back panel formula **verifikovana ispravna** (2×GROOVE je tačno za oba bočna panela kraka); sitne edge-case tolerancije |
| Frontovi | 88% | **98%** | 100% | `door_height` clamp ✅ urađen (P0-8); edge-case DOOR_DRAWER za nestandard visine |
| Drawer box | 85% | **97%** | 100% | `door_height` clamp ✅ urađen (P0-8) |
| **Hardware** | **60%** | **97%** | 100% | Klinovi ✅, Ručke ✅, Wardrobe ✅, Hinge plates ✅, Handle screws ✅, BASE_HOB handles ✅ (sesija 9) |
| Manufacturing upozorenja | 70% | **88%** | 90% | 31 tip validacije implementirano; dodato MODULE_OUT_OF_BOUNDS (sesija 9) |
| Test pokrivenost | 65% | **90%** | 95% | 39/39 testova prolazi; wardrobe ✅, freestanding ✅, hardware counts ✅ |

### Rešeni nalazi (sesije 7-9)

| # | Problem | Status |
|---|---|---|
| 1 | Shelf pins (klinovi) nedostaju | ✅ POTVRĐENO da postoje (L2193-2200, `4 × N_polica`) |
| 2 | Ručke / pulls nedostaju | ✅ URAĐENO (P0-7, sesija 7) |
| 3 | Wardrobe specijalni okovi nedostaju | ✅ URAĐENO (P1-1, sesija 8) |
| 4 | Template ID lažni pozitiv (`BASE_3DRAWER`) | ✅ URAĐENO (P0-5, sesija 7) |
| 5 | `door_height` validacija | ✅ URAĐENO (P0-8, sesija 7) |
| 6 | Corner back panel groove | ✅ VERIFIKOVANO ISPRAVNO — `w-d - 2×GROOVE` je tačno (oba bočna panela kraka imaju žleb) |
| 7 | BASE_HOB bez ručke | ✅ URAĐENO (sesija 9) — uklonjen pogrešan `not _is_hob_m` uslov |
| 8 | Modul van zida bez upozorenja | ✅ URAĐENO (sesija 9) — dodat `MODULE_OUT_OF_BOUNDS` check |
| 9 | Hinge plates + handle screws nedostaju | ✅ URAĐENO (P1-2, sesija 8) |
| 10 | `_lock_scene_to_horizontal_orbit` bez `cam_x/y/z` | ✅ URAĐENO (P1-4, sesija 9) — bio preskakao TypeError |

---

## TEST CHECKLIST (AKTIVNA)

- Pokretanje app bez runtime greške tabova
- Elementi tab: dodaj/edit/delete/swap
- 3D prikaz elemenata
- Save/Load JSON
- PDF export (ujedinjen engine)
- Excel export
- Room setup wizard (3 koraka)
- Reset projekta (toolbar dugme + potvrda)
- Ormari tab (sve 4 grupe vidljive u katalogu)
- Krojna lista: BASE_DOOR_DRAWER — vrata + fioka front oba prisutna
- Krojna lista: TALL_WARDROBE_AMERICAN — klizni paneli generisani
- Krojna lista: TALL_WARDROBE_2DOOR_SLIDING — bez srednje vertikale

### Poslednja verifikacija (11.03.2026)
- `smoke_scenarios.py`: `TEMPLATE_PREVIEWS_OK=52`, `TEMPLATE_PREVIEWS_ERR=0`, `LAYOUT_AUDIT_OK=True`, `GRID_MODES_OK=True`
- `python -m py_compile` na svim izmenjenim fajlovima: OK
- XLSX export audit: 86 redova Korpus sheet — sve dimenzije tačne
- Frontovi sheet: bug #1 potvrđen i popravljen (BASE_DOOR_DRAWER vrata)

### Verifikacija (06.03.2026)
- `APP_IMPORT_OK` (import `app.py` bez runtime greške)
- `smoke_scenarios.py`: `TEMPLATE_PREVIEWS_ERR=0`, `LAYOUT_AUDIT_OK=True`
- `test_wall_upper.py`: sve provere prošle
- `ui_edit_panel.py` i `ui_params_panel.py`: uklonjeni preostali obojeni (orange/yellow/purple) panel stilovi
- `room_openings_editor.py` i `room_setup_wizard.py`: dodatni i18n prolaz kroz ključne UI poruke/label-e
- `ui_edit_panel.py`: preostale hardkodovane edit labele (X/Visina/Gap/Naziv) prebačene na i18n
- Save/Load roundtrip: `save_project_json()` → `load_project_json()` = `OK`
- `ui_cutlist_tab.py`: prebačene hardkodovane preview labele (`2D`/`3D`) na i18n
- `ui_panels.py`: uklonjen `traceback.print_exc()`; uveden kontrolisan `_LOG.exception(...)`
- `ui_canvas_2d.py`: uklonjen duplikat image helpera, koristi `ui_image_utils.fig_to_data_uri_exact`
- `smoke_scenarios.py`: dodat `GRID_MODES` smoke scenario (`grid_mm`: 1/5/10)
- dodat `ui_panels_helpers.py`: izdvojeni sidebar/color-picker wrapper-i iz `ui_panels.py`
- `ui_wizard_tab.py`: uklonjen mojibake (UTF-8), tekstovi centralizovani kroz `i18n.py`
- `i18n.py`: dodate wizard konstante za tipove nameštaja, raspored i učitavanje projekta
- Verifikacija: `python -m py_compile ...` + `python smoke_scenarios.py` + `python test_wall_upper.py` = `OK`
- Napomena: puni ručni klik-smoke svih tabova i dalje ostaje preporučen pre finalnog release-a.

---

## DETALJAN PREGLED APLIKACIJE (12.03.2026 - sesija 4)

Ovaj blok je radni pregled stvarnog stanja koda, sa fokusom na scenario:

`laik napravi dizajn -> odnese krojnu listu u servis plocastog materijala -> servis isece/kantuje -> korisnik kuci sklapa`

Zakljucak pregleda:
- Aplikacija je vec dobra `projektantska beta` za single-wall kuhinju i osnovne ormare.
- Aplikacija jos nije `samodovoljan proizvodni paket za laika`.
- Najveca rupa nije samo u dimenzijama ploca, nego u kompletnosti izlaza:
  - sta tacno servis treba da isece
  - sta treba da kantuje
  - sta korisnik mora da kupi
  - sta i kako korisnik sklapa
  - koje dizajne treba blokirati jer nisu bezbedni za laicku montazu

### 1. Realan tok aplikacije iz koda

1. `ui_wizard_tab.py`
   - aktivan tok je prakticno kitchen-only
   - wizard vodi kroz tip, nacin merenja, raspored, pa room setup
   - L layout se nudi u wizardu, ali puna layout logika jos nije aktivna u proizvodnom smislu

2. `state_logic.py`
   - drzi globalni state projekta, room podatke, kitchen parametre, module i defaults po zoni
   - vec postoji room model sa zidovima `A/B/C`, otvorima i fixtures
   - to znaci da je UI priprema za multi-wall prisutna, ali jezgro rasporeda jos nije zatvoreno

3. `module_templates.json` + `module_templates.py`
   - template JSON je jedini izvor istine za katalog
   - katalog obuhvata donje, gornje, visoke, ugradne i wardrobe elemente
   - visual i defaults sloj su odvojeni od poslovne logike, sto je dobro za dalje sirenje

4. `ui_catalog_config.py` + `ui_catalog_panel.py`
   - paleta je organizovana po grupama i podgrupama
   - preview u katalogu ide 3D/2D render -> fallback na SVG/foto ikonu
   - to znaci da korisnik vidi elemente dosta verno onome sto kasnije dobija na zidu

5. `ui_params_panel.py` + `ui_edit_panel.py` + `ui_module_properties.py`
   - korisnik pri dodavanju i izmeni menja dimenzije, dubinu, smer goda, broj polica, fioka i pojedine wardrobe parametre
   - to je kljucno jer cutlist ne zavisi samo od template-a nego i od `params`

6. `layout_engine.py`
   - trenutno stabilno pakuje i kontrolise preklapanja prvenstveno za one-wall tok
   - postoje helperi za wall_key i odvojene zidove, ali to jos nije pun multi-wall placement engine

7. `visualization.py`
   - 2D prikaz je informativni tehnicki crtez i glavni izvor vizuelne logike za elemente
   - tip elementa se dominantno prepoznaje preko `template_id` string-pattern pravila
   - 2D detalji su dosta bogati: vrata, fioke, staklo, sink, hob, rerna, lift-up, handles

8. `render_3d.py`
   - 3D scena je funkcionalna i oslanja se na slicnu klasifikaciju template-a kao 2D
   - kamera, svetlo i horizontal orbit lock su unapredjeni
   - i dalje je to pregled/radni preview, ne prodajni realizam

9. `cutlist.py`
   - ovo je kljucni proizvodni engine
   - iz jednog kitchen state-a generise:
     - `carcass`
     - `backs`
     - `fronts`
     - `drawer_boxes`
     - `worktop`
     - `plinth`
     - `hardware`
   - poseduje `PartCode`, `Pozicija`, `SklopKorak`, CUT/FIN logiku, edge flags `L1/L2/K1/K2`, grain za frontove, warning mehanizam, PDF i Excel export

10. `ui_cutlist_tab.py` + `ui_assembly.py`
    - korisnik u UI vec dobija:
      - pregled kuhinje
      - sumarni pregled
      - sekcije krojne liste
      - detalje po elementu
      - preview 2D/3D
      - osnovno uputstvo za montazu
    - to je vec vise od "gola tabela", ali jos nije zatvoren "idi u servis i sklopi sam" paket

### 2. Realna mapa elemenata kroz app

### 2A. Katalog i crtanje
- Donji:
  - `BASE_NARROW`, `BASE_1DOOR`, `BASE_2DOOR`, `BASE_OPEN`
  - `BASE_DRAWERS_3`, `BASE_DOOR_DRAWER`
  - `BASE_CORNER`
  - `SINK_BASE`, `BASE_TRASH`, `BASE_HOB`
  - `FILLER_PANEL`, `END_PANEL`
- Gornji:
  - `WALL_NARROW`, `WALL_1DOOR`, `WALL_2DOOR`, `WALL_GLASS`, `WALL_LIFTUP`
  - `WALL_OPEN`, `WALL_CORNER`
  - `WALL_UPPER_1DOOR`, `WALL_UPPER_2DOOR`, `WALL_UPPER_OPEN`
- Visoki:
  - `TALL_PANTRY`, `TALL_GLASS`, `TALL_DOORS`, `TALL_OPEN`
  - `TALL_FRIDGE`, `TALL_FRIDGE_FREEZER`
  - `TALL_TOP_DOORS`, `TALL_TOP_OPEN`
- Ugradni:
  - `BASE_COOKING_UNIT`, `TALL_OVEN`, `TALL_OVEN_MICRO`
  - `BASE_DISHWASHER`, `WALL_MICRO`, `WALL_HOOD`
- Ormari:
  - `TALL_WARDROBE_2DOOR`, `TALL_WARDROBE_DRAWERS`, `TALL_WARDROBE_2DOOR_SLIDING`
  - `TALL_WARDROBE_AMERICAN`
  - `TALL_WARDROBE_INT_SHELVES`, `TALL_WARDROBE_INT_DRAWERS`, `TALL_WARDROBE_INT_HANG`
  - `TALL_WARDROBE_CORNER`, `TALL_WARDROBE_CORNER_SLIDING`

### 2B. Kako se tip elementa prepoznaje
- 2D i 3D rendering se u velikoj meri oslanjaju na `template_id` string logiku:
  - `DRAWER`, `SINK`, `HOB`, `OVEN`, `FRIDGE`, `GLASS`, `LIFTUP`, `OPEN`, `CORNER`, `PANTRY`
- `cutlist.py` koristi slican princip:
  - skupovi poznatih TID-ova + substring provere
- Ovo radi dovoljno dobro za brz razvoj, ali nosi rizik:
  - novi template moze vizuelno da postoji u katalogu
  - a da proizvodna logika bude samo delimicno pogodjena substring pravilom

### 2C. Trenutni proizvodni izlaz po tipovima
- Dobra pokrivenost:
  - standardni donji/gornji/visoki sa vratima
  - otvoreni elementi
  - stakleni gornji
  - fiokari
  - vrata + fioka
  - sink base
  - machine slot za MZS
  - cooking unit / oven / oven+micro
  - pantry/open tall
  - osnovni wardrobe front scenariji
- Osetljiva pokrivenost:
  - paneli (`FILLER_PANEL`, `END_PANEL`)
  - TV / hallway / bathroom / office varijante ako se budu aktivirale
  - wardrobe unutrasnje sekcije i corner/sliding kombinacije
  - appliance slotovi
  - svaki novi template koji se nasloni samo na substring logiku bez eksplicitne proizvodne grane

### 3. Sta aplikacija danas dobro radi za proizvodnju

- Drzi dimenzije modula, dubine i visine po zoni centralno.
- 2D/3D preview prolazi smoke scenario za template preview.
- Cutlist ima razdvojene sekcije po proizvodnim grupama.
- Excel export vec ima pregled + sekcije + okove.
- `PartCode`, `Pozicija`, `SklopKorak` postoje.
- CUT i FIN mere su odvojene.
- Kant ivice imaju i tekstualni opis i machine-friendly zastavice.
- Za frontove postoji smer goda.
- Za neke rizicne slucajeve postoje manufacturing warnings.
- Postoje osnovna montazna uputstva po zoni/tipu.

### 4. Sta nedostaje da bi laik mogao bez stolarskog znanja

Ovo je najvazniji deo pregleda.

Profesionalna krojna lista za laika nije samo lista rezova. Mora da bude kompletan paket:

1. `sta servis sece`
2. `sta servis kantuje`
3. `sta servis eventualno busi/zuje/obradi`
4. `sta korisnik kupuje gotovo`
5. `sta korisnik sklapa redom`
6. `kako korisnik proverava da nista ne fali`

Trenutne rupe:
- Nema kompletne shopping liste za laika.
- Nema kompletne liste potrosnog materijala.
- Nema busece mape po delu.
- Nema CNC/operacija tabele po delu.
- Nema jasne servis-instrukcije "obavezno uraditi i kantovanje".
- Nema blokirajucih validacija za dizajne koji su teski ili neprakticni za kucnu montazu.
- Nema pune revizione i projektne identifikacije za izlaz.
- Nema zatvoren "check before go to workshop" paket.

### 5. Posebni rizici po scenariju "laik nosi u servis"

1. Ako servis dobije samo tabelu komada, bez eksplicitne instrukcije za kant i obradu:
   - korisnik ce dobiti isecele ploce koje nisu spremne za sklapanje

2. Ako korisnik nema listu za kupovinu okova:
   - kuci ce imati sav materijal, ali nece imati sarke, klizace, tiplove, nogice, vezni materijal

3. Ako komadi nisu dovoljno jasno imenovani:
   - korisnik nece znati sta je koja ploca kada se vrati iz servisa

4. Ako nema montaznog reda po elementu:
   - krojna lista mu ne pomaze dovoljno, jer je problem sklapanje a ne secenje

5. Ako UI dozvoli dizajn koji trazi stolarsko iskustvo:
   - korisnik moze naruciti nesto sto realno nece znati da sastavi

### 6. Detaljna agenda za sledeci sistematski rad

Napomena:
- Ovo nije vise agenda samo za "tehnicki razvoj".
- Ovo je agenda za pretvaranje app iz `beta projektantskog alata` u `proizvodni alat za laika`.

### P0A - Zatvaranje "laik workflow" paketa

Status: `GLAVNI KOSTUR ZAVRSEN 12.03.2026`

Cilj:
- da korisnik moze da ode u servis plocastog materijala sa jednim PDF/Excel paketom i vrati se sa svim sto treba za sklapanje

Zadaci:
1. Uvesti `radni nalog / project header`
   - projekat
   - datum
   - verzija
   - prostorija
   - zid
   - korisnicko ime / kupac
   - napomena za servis

2. Uvesti `servis paket`
   - tabela za secenje
   - tabela za kantovanje
   - tabela za obradu
   - napomena "ovo se ne sece, ovo se kupuje gotovo"

3. Uvesti `shopping list` za laika
   - okovi
   - potrosni materijal
   - alat za montazu
   - materijal za zidnu montazu

4. Uvesti `checklist before workshop`
   - proveri materijal
   - proveri kant
   - proveri broj komada
   - proveri da li su svi frontovi i ledja prisutni
   - proveri da li okovi nisu deo secenja

5. Posebno uraditi audit `mesovitih` i `panel` modula u 2D i katalog preview-u
   - `BASE_COOKING_UNIT`: samo fioka je front boja, uredjaj ostaje appliance izgled
   - `END_PANEL`: mora izgledati kao zavrsna bocna ploca, ne kao uredjaj
   - `FILLER_PANEL`: mora izgledati kao uski popunjavac, ne kao ormaric
   - proveriti i ostale integrisane appliance module da nema istog 2D problema
   - `TALL_OVEN` i `TALL_OVEN_MICRO`: servisni/front panel mora biti jasno odvojen od appliance zone
   - `BASE_DISHWASHER`, `TALL_FRIDGE`, `TALL_FRIDGE_FREEZER`: katalog treba da koristi preview koji najbolje objasnjava front vs uredjaj
   - `WALL_MICRO` i `WALL_HOOD`: katalog treba da koristi preview koji jasno razlikuje nišu/napu od obicnog gornjeg ormara

6. Posvetiti vecu paznju ikonama i realizmu samih elemenata
   - ikonice treba da budu sto realnije i odmah razumljive laiku
   - elementi u 2D i 3D treba da izgledaju sto blize stvarnom kuhinjskom elementu
   - prioritet je da korisnik na prvi pogled razume razliku izmedju fronta, korpusa, panela i uredjaja
   - vizuelni realizam nije samo estetika nego deo tacnosti proizvoda
7. Uvesti sistematski smoke za celu aktivnu kitchen paletu
   - svaki aktivni `template_id` iz kataloga mora da prodje 2D i 3D preview
   - posebna `2D priority` pravila za module gde 2D bolje objasnjava odnos front/uredjaj/panel
   - time se buduce izmene vizuelnog sloja proveravaju automatski, ne samo rucno

Fajlovi:
- `cutlist.py`
- `ui_cutlist_tab.py`
- `ui_pdf_export.py`
- `ui_assembly.py`
- po potrebi `i18n.py`

Status 12.03.2026:
- uradjen `project header` u PDF/Excel/UI
- uradjen `servis paket`:
  - secenje
  - kantovanje
  - obrada / napomene
- uradjen `shopping list`:
  - okovi i mehanizmi za kupovinu
  - sitni materijal za montazu
  - alat koji treba kod kuce
  - materijal za zidnu montazu
- uradjena lista `kupuje se gotovo`
  - uredjaji
  - sudopera / slavina / sifon
- uradjen `vodic za korisnika`
  - sta nosi u servis
  - sta kupuje posebno
  - kojim redom radi kod kuce
- uradjene dve `checklist` tabele:
  - pre servisa
  - pre kucnog sklapanja
- tekstovi u UI/PDF/Excel su pojednostavljeni za laika

Otvoreno u P0A:
- eventualno dodatni alat / potrosni materijal po scenariju
- finalni zaseban checklist dokument na kraju cele agende
- sitne UX dorade po stvarnom korisnickom testu

### P0B - Cutlist engine hardening po tipu elementa

Status: `PRAKTICNO ZATVORENO 12.03.2026 - kitchen-only template audit`

Radni audit dokument:
- `P0B_TEMPLATE_AUDIT.md`

Cilj:
- nijedan template iz kataloga ne sme imati "vizuelno postoji, proizvodno nejasno"

Napomena 12.03.2026:
- kitchen-only audit je zatvoren kroz `P0B_TEMPLATE_AUDIT.md`
- nema otvorenih `PARTIAL/FAIL` kitchen-only template-a u matrici
- `P0A` glavni kostur je zavrsen
- sledeca aktivna tehnicka faza je `P0C` - blokirajuce validacije za los dizajn

Zadaci:
1. Napraviti matricu `template_id -> render -> cutlist -> hardware -> assembly`
2. Za svaki aktivan template eksplicitno oznaciti:
   - ima korpus
   - ima ledja
   - ima front
   - ima sanduk fioke
   - ima radnu plocu / veznu letvu / dodatni element
   - ima shopping-list stavke
3. Posebno proveriti:
   - panele
   - wardrobe unutrasnje sekcije
   - corner/sliding wardrobe
   - appliance slotove
   - jasno razdvajanje `samostojeci` vs `ugradni` uredjaj
     - `samostojeci` = bez korpusa, bez fronta
     - `ugradni` = sa korpusom i, gde sistem to trazi, sa frontom/frontovima uredjaja
   - ovo obavezno vazi za:
     - frizider
     - masina za sudove
     - sporet / rerna + ploca
4. Gde je substring logika krhka, zameniti je jasnim klasifikacionim slojem

Fajlovi:
- `module_templates.json`
- `module_templates.py`
- `visualization.py`
- `render_3d.py`
- `cutlist.py`

### P0C - Proizvodne validacije koje blokiraju los dizajn

Status: `U TOKU 12.03.2026`

Cilj:
- aplikacija mora da spreci korisnika da napravi nesto sto ne moze lako da isece/sastavi

Zadaci:
1. Uvesti `warning` vs `blocking error`
2. Blokirati ili oznaciti:
   - preuske / preplitke module
   - previsoke ili preteske frontove
   - nerealne fioke
   - problematican lift-up
   - konflikt sa otvorima/instalacijama
   - elemente koji traze zid B/C ako placement engine nije spreman
3. Dodati "home assembly risk" validacije
   - previse veliki komadi za laika
   - previsok ormar bez anti-tip upozorenja
   - nestabilan raspored bez bocnog oslonca

Fajlovi:
- `cutlist.py`
- `layout_engine.py`
- `state_logic.py`
- `room_constraints.py`

Status 12.03.2026:
- uveden prvi talas `blocking error` pravila u `state_logic.py`
- sada se odmah blokiraju tipicni losi slucajevi:
  - preplitak donji element
  - predubok / premalen gornji element
  - prevelik lift-up
  - preplitak fiokar
  - premala sirina za MZS / frizider / rernu+plocu / sudoperu
  - previsok visoki element za laicki workflow
  - prevelik jednokrilni front
- uveden drugi talas `blocking/support` pravila:
  - `wall_upper` ne moze bez gornjeg elementa ispod
  - `tall_top` ne moze bez visokog elementa ispod
- uveden treci talas `appliance/depth` pravila:
  - previše plitki visoki korpusi se blokiraju
  - integrisane visoke appliance kolone traze min 560 mm dubine
  - samostojeci frizider trazi min 600 mm dubine
  - samostojeci donji uredjaji traze min 580 mm dubine
  - `WALL_HOOD` i `WALL_MICRO` traze min 600 mm sirine i min 300 mm dubine
  - ugaoni moduli ispod 800 mm sirine se blokiraju
- dodat warning fallback u `cutlist.py` za stare/rucno ucitane rizicne projekte
- warning fallback je prosiren i na appliance/corner/depth slucajeve
- smoke scenario za blocking validacije je prosiren na tall appliance, corner, hood i freestanding fridge slucajeve
- UI now koristi jasnije poruke za odbijene elemente (`Blokirano: ...`) u add/edit/canvas tokovima
- dodat front validation sloj:
  - fioka ispod 80 mm se blokira
  - `vrata + fioka` mora imati razumnu podelu visine
- dodat smoke za `update_module_local`, ne samo za add tok
- uveden `full support span` validation sloj:
  - `wall_upper` mora da lezi na elementu ispod po celoj sirini
  - `tall_top` mora da lezi na visokom elementu ispod po celoj sirini
  - stari projekti dobijaju warning fallback za ove slucajeve
- `layout_audit` je uskladjen sa istim pravilom punog oslonca
- dodat smoke koji proverava da audit hvata los `wall_upper` support scenario
- `room constraints` sada su pokriveni kroz ceo tok:
  - `add` i dalje izbegava hard prepreke kada moze
  - `update` sada takodje blokira vrata/prozore
  - soft instalacije se cuvaju u modulu i izlaze kao warning u cutlist-u
  - dodat smoke za vrata + instalacije + update tok
- dodat smoke za `warning generation`, tako da se proverava da `cutlist` stvarno izbacuje kljucne warning kodove

Procena statusa:
- `P0C` je sada `PRAKTICNO ZATVOREN`
- ostaju samo eventualna fina dopunska pravila ako ih otkrijemo kroz QA/checklist fazu

Otvoreno u P0C:
- dopunska finija pravila otvarati samo ako ih otkrijemo kroz QA ili realne korisnicke scenarije

### P1A - Potpuni okovi i potrosni materijal

Status: `ODMAH posle P0`

Cilj:
- korisnik mora da dobije punu listu kupovine, ne samo osnovne sarke i klizace

Zadaci:
1. Razdvojiti:
   - okove po elementu
   - potrosni materijal po projektu
   - zidne tiplove i montazni materijal
2. Dodati:
   - confirmat, tipl, sraf, shelf pin, nogice, nosace, spojnice
   - anti-tip set za visoke elemente
   - spoj radne ploce
   - silikon / zaptivni materijal gde ima smisla
3. Dodati realisticne profile:
   - Blum
   - Hettich
   - GTV
4. Dodati sifre i jedinicu mere

Fajlovi:
- `cutlist.py`
- `ui_cutlist_tab.py`

Status 12.03.2026:
- uveden prvi pravi `P1A` projektni sloj u `cutlist.py`
- pored elementskih okova sada se dodaju i projektne stavke:
  - `Spojnica susednih korpusa`
  - `Klipsa za soklu`
  - `Vijak / ugaonik za radnu plocu`
  - `Zaptivna lajsna / silikon uz zid`
- prosiren hardware katalog profila (`BLUM`, `HETTICH`, `GTV`) i na te projektne stavke
- dodat smoke koji proverava da ove stavke izlaze i u `hardware` i u `shopping_list`
- uveden drugi `P1A` talas:
  - genericki `Anti-tip set` za sve visoke korpuse koji ga ranije nisu imali
  - `Prikljucni set uredjaja` za MZS, rernu/plocu, tall appliance kolone i samostojece uredjaje
  - dodat ventilacioni distancer za `WALL_MICRO`
- dodat smoke za appliance/tall hardware pokrivenost
- uvedeno poslovno pravilo za cutlist:
  - sam uredjaj se vise NE pojavljuje u `hardware` / `shopping_list`
  - na listi ostaje samo ono sto pripada elementu oko uredjaja
  - ugradni uredjaji ostaju kroz korpus/front i pratece montažne okove
  - samostojeci uredjaji ne dobijaju korpus, front ni kupovni appliance red u krojnoj listi
- dodat smoke koji proverava da appliance proizvodi vise nisu prisutni u listi

- `BASE_COOKING_UNIT` je dodatno zatvoren kao pravi element:
  - donja fioka vise nije samo front, nego pravi sklop
  - cutlist sada generise `front fioke` + `sanduk fioke`
  - hardware sada ukljucuje `Klizac za fioku` i `Nosac fronta fioke`
  - assembly vise ne govori o laznoj fioci, nego o stvarnoj donjoj fioci
- dodat smoke `COOKING_UNIT_DRAWER_OK` koji proverava da `BASE_COOKING_UNIT` stvarno ima:
  - front fioke
  - sanduk fioke
  - klizace
  - nosac fronta fioke
- dodat treci `P1A` talas za realnu kupovinu sklapanja:
  - `Vijak za sarku`
  - `Vijak za klizac`
  - `Vijak / ekser za ledja`
  - `Vijak za zidni nosac / sinu`
- shopping lista je jasnije razdvojena na:
  - `Okovi i mehanizmi po elementu`
  - `Sitni materijal po elementu`
  - `Projektni potrosni materijal`
  - `Montaza na zid`
- UI shopping tabela sada prikazuje i `Tip / Sifra`
- dodat smoke `FASTENER_GROUPING_OK` za:
  - prisustvo realnih fastenera u hardware/shopping sloju
  - proveru grupisanja shopping liste

Otvoreno u P1A:
- dodatno zatvoriti realisticne profile i sifre za sitni materijal
- dopuniti jos appliance pratece setove i zidni montazni materijal
- po potrebi odvojiti `okov po elementu` i `potrosni po projektu` jos jasnije u UI

### P1A-1 - Dokumentacija zazora i otvaranja

Status: `URADJENO 12.03.2026`

Dokument:
- `DOOR_CLEARANCES_AND_GAPS.md`

Zakljucak iz dokumenta:
- zazori za zatvoren polozaj frontova jesu uracunati
- puna provera sudara pri otvaranju jos nije kompletno uvedena
- dodatna pravila su potrebna posebno:
  - uz bocni zid
  - kod ugaonih elemenata
  - u `L kuhinji`

Status update 12.03.2026:
- uveden prvi stvarni `door opening collision` talas:
  - blokira se eksplicitno losa strana otvaranja jednokrilnih vrata uz levi/desni zid
  - dodat `SIDE_WALL_DOOR` warning fallback za stare projekte
  - dodat `CORNER_OPENING_CLEARANCE` warning za ugaoni modul i suseda bez servisnog razmaka
  - smoke pokriva i blocking i warning sloj za ova pravila

### P1B - Obrade i servis instrukcije

Status: `PRAKTICNO ZATVORENO 13.03.2026`

Cilj:
- servis mora tacno da zna da li radi samo secenje ili i kantovanje/obradu

Status 13.03.2026:
- servis paket sada ima prosirenu tabelu `Obrade` sa kolonama:
  - `Tip obrade`
  - `Izvodi`
  - `Osnov izvođenja`
  - `Obrada / napomena`
- generator eksplicitno izdvaja obrade za:
  - `SINK_BASE`
  - `BASE_COOKING_UNIT`
  - `BASE_DISHWASHER`
  - `WALL_HOOD`
  - `WALL_MICRO`
  - `TALL_FRIDGE` / `TALL_FRIDGE_FREEZER`
- dodata posebna sekcija `Instrukcije za servis`
- UI cutlist tab prikazuje i `Obrade` i `Instrukcije za servis`
- PDF export prikazuje i `Obrade` i `Instrukcije za servis`
- Excel export ima i sheet `Servis uputstvo`
- `Izvodi` je standardizovan na jasan tok:
  - `Servis`
  - `Kuća / lice mesta`
- `Osnov izvođenja` jasno razdvaja:
  - `Po meri iz projekta`
  - `Po šablonu proizvođača`
- smoke pokriva servis paket kroz `SERVICE_PROCESSING_OK=True`
- prakticno je zatvoren i ostaje samo:
  - precizna busacka mapa za sarke / klizace kada se uvede drilling sloj
  - pripadnost `zidu` i `segmentu` kasnije u L kuhinji

Zadaci:
1. Dodati posebnu sekciju `Obrade`
   - utor za ledja
   - rupe za sarke
   - pozicija klizaca
   - rupe za police
   - otvor za sudoperu
   - otvor za plocu
   - prolaz za kabl / sifon
2. Dodati sekciju `Instrukcije za servis`
3. Oznaciti sta je:
   - obavezna obrada
   - opciona usluga
   - kucna obrada
4. Sledeci finiÅ¡ u P1B:
   - dopuniti rupe za sarke / klizace kada bude uvedena precizna busacka mapa
   - dodati jasnije razlikovanje `Servis` vs `Kuca` vs `Po sablonu proizvodjaca`
   - za L kuhinju kasnije obavezno dodati pripadnost `zidu` i `segmentu`

Fajlovi:
- `cutlist.py`
- `ui_pdf_export.py`
- `ui_assembly.py`

### P1C - Vizuelno mapiranje komada za montazu

Status: `PRAKTICNO ZATVORENO 13.03.2026`

Cilj:
- korisnik mora da moze da spari komad iz tabele sa komadom u elementu

Zadaci:
1. Uvesti oznake delova direktno na crtez elementa
   - npr. `C01`, `C02`, `F01`
2. U PDF po elementu dodati:
   - eksplodirani mini prikaz ili makar oznaceni prikaz front/korpus delova
3. U tabelama koristiti ljudski razumljive nazive
   - ne samo "Leva strana"
   - nego i kojoj zoni/modulu pripada

Fajlovi:
- `visualization.py`
- `ui_cutlist_tab.py`
- `ui_pdf_export.py`

Status 13.03.2026:
- uradjena prva `mapa delova za sklapanje` po elementu u UI cutlist tabu
- uradjena ista `mapa delova za sklapanje` i u PDF po elementu
- per-element 2D preview sada koristi skraćene oznake iz stvarnog `PartCode`
  - npr. `M01-F02 -> F02`
- preview je direktno vezan za tabelu i assembly korake
- prikaz po elementu sada prevodi cesce tehnicke nazive u citljivije nazive za laika
  - korisnik sada po elementu vidi:
    - `PartCode`
    - `Deo`
    - `Gde ide`
    - `Korak`
    - `Kom.`

Otvoreno u P1C:
- jos jaca veza preview <-> tabela <-> assembly koraci po potrebi za kompleksne module
- eventualni eksplodirani mini prikaz kasnije, ako se pokaze da je potreban kroz QA

### P1D - 2D/3D i cutlist paritet

Status: `PRAKTICNO ZATVORENO 13.03.2026`

Cilj:
- ono sto korisnik vidi mora biti isto sto ide u proizvodnju

Zadaci:
1. Proveriti da svaki front/render detalj ima pandan u cutlist logici
2. Proveriti da posebni tipovi:
   - glass
   - lift-up
   - sink
   - cooking unit
   - wardrobe sliding
   - wardrobe american
   - wall_upper / tall_top
   isto izgledaju i isto se racunaju
3. Smanjiti oslanjanje na implicitne substring pogodke
4. Ikonice koje predstavljaju elemente u katalogu moraju biti realni primer modula
   - ne genericka ikonica
   - nego vizuel koji odgovara stvarnom elementu
   - primer: `ugradna rerna + ploca + fioka` mora izgledati kao taj element, a ne kao apstraktan simbol
   - isto pravilo vazi za frižider, MZS, sudoperu, narrow, corner, lift-up i ostale kuhinjske module

Fajlovi:
- `visualization.py`
- `render_3d.py`
- `cutlist.py`
- `ui_catalog_panel.py`
- `svg_icons.py`

Status 13.03.2026:
- dodat reprezentativni `render -> cutlist` parity smoke
- smoke sada proverava da reprezentativni kitchen moduli imaju dosledan odnos:
  - preview postoji
  - cutlist sekcije postoje ili ne postoje tamo gde treba
- parity smoke je prosiren na siri skup aktivnih kitchen modula:
  - `BASE_2DOOR`, `BASE_OPEN`, `BASE_DRAWERS_3`, `BASE_NARROW`, `BASE_CORNER`
  - `WALL_2DOOR`, `WALL_GLASS`, `WALL_LIFTUP`, `WALL_OPEN`, `WALL_CORNER`, `WALL_NARROW`
  - `TALL_PANTRY`, `TALL_DOORS`, `TALL_GLASS`, `TALL_OPEN`, `TALL_OVEN`, `TALL_OVEN_MICRO`
  - `WALL_UPPER_2DOOR`, `WALL_UPPER_OPEN`, `TALL_TOP_OPEN`
- dodat je i strozi quantity smoke za parametarski osetljive module:
  - proverava ocekivani broj frontova
  - proverava broj stvarnih sanduka fioka preko `Dno sanduka`
  - pokriveni primeri: `BASE_DRAWERS_3`, `BASE_DOOR_DRAWER`, `BASE_2DOOR`, `WALL_2DOOR`, `TALL_FRIDGE_FREEZER`, `TALL_OVEN_MICRO`, `BASE_COOKING_UNIT`, `BASE_DISHWASHER`
- dodat je i smoke za specijalne front tipove:
  - staklena vrata
  - lift-up front
  - integrisani friÅ¾ider i friÅ¾ider + zamrzivaÄ
  - MZS front
  - front fioke ispod rerne
  - donji servisni front za appliance kolone
- zatvoreni konkretni parity propusti:
  - standardni fiokar sada dobija i `drawer_boxes` kada nema rucno zadate visine fioka
  - `BASE_DOOR_DRAWER` sada dobija i sanduk fioke
  - `TALL_TOP_DOORS` sada dobija frontove
- `RENDER_CUTLIST_PARITY_OK=True`
- `FRONT_DRAWER_QUANTITIES_OK=True`
- `SPECIAL_FRONT_TYPES_OK=True`
- katalog sada forsira 2D preview za specijalne module gde je to razumljivije laiku:
  - `SINK_BASE`, `BASE_HOB`, `BASE_COOKING_UNIT`, `BASE_DISHWASHER`
  - `BASE_NARROW`, `BASE_CORNER`, `WALL_GLASS`, `WALL_LIFTUP`
  - `WALL_HOOD`, `WALL_MICRO`, `WALL_NARROW`, `WALL_CORNER`
  - `TALL_OVEN`, `TALL_OVEN_MICRO`, `TALL_FRIDGE`, `TALL_FRIDGE_FREEZER`
- dodat smoke `PARTCODE_PREVIEW_OK=True` za render sa stvarnim part oznakama

Otvoreno u P1D:
- dalja fina vizuelna uskladjenja otvarati samo ako ih prijavi QA ili realni korisnicki test

### P2A - Multi-wall kao stvarno funkcionalan model

Status: `STRATESKI, ali ne pre P0C/P1`

Razlog:
- za scenario laika je opasnije da dobije nepotpun proizvodni paket nego da nema odmah L/U/galija

Zadaci:
1. Zid A/B/C kao stvarna placement logika
2. L/U/galija sa realnim corner pravilima
3. Radna ploca po segmentima, ne jedan komad
4. Sokla po segmentima
5. Corner, continuity i workshop output po zidu

#### P2A-1 - Usavrsiti L kuhinju kao prvi pravi multi-wall milestone

Status: `DJELIMIČNO OTVORENO — corner offset bug pronađen u sesiji 6 (15.03.2026) → vidi P2A-4`

Status update 13.03.2026:
- `l_oblik` vise nije samo priprema u wizardu:
  - aktivni zid u dizajnu sada moze da se prebacuje kroz UI (`Zid A / B / C`)
  - add/edit/canvas/3D tok sada rade po `active_wall`, ne samo po glavnom zidu
- state i layout sloj sada sinhronizuju duzinu i visinu aktivnog zida iz `room.walls`
- osnovni multi-wall smoke je dodat:
  - `MULTIWALL_L_BASIC_OK=True`
  - proverava dodavanje modula na zid A i zid B bez rucnog varanja modela

Prakticno zatvoreno u ovom koraku:
- stvarno odvojeno postavljanje elemenata po zidu A/B
- prvi upotrebljivi L workflow za dodavanje i editovanje po aktivnom zidu
- 2D prikaz sada ima mini `L plan` inset koji pokazuje prelom A+B i aktivni krak
- 3D prikaz sada pokazuje i drugi krak `L` kuhinje uz bočni zid, ne samo aktivni linearni niz
- radna ploca i sokla sada se generisu po segmentima zida
- cutlist / servis paket / UI / glavni PDF izlaz sada nose oznaku pripadnosti zidu
- dodat smoke:
  - `MULTIWALL_CUTLIST_OK=True`
  - proverava segmentaciju radne ploce, sokle i servis paketa po zidu A/B

Otvoreno posle P2A-1:
- **corner offset bug** (sesija 6) — Wall B elementi počinju od x=0 umjesto od x=560mm → `P2A-4`
- dublja koliziona upozorenja za ugao i susedne fronte
- dalje sirenje na `U`, `galija` i ostrvo

Status update 13.03.2026 - sledeci korak posle P2A-1:
- uvedena su prva eksplicitna ugaona pravila u layout/state sloju:
  - `BASE_CORNER` i `WALL_CORNER` sada moraju biti na unutrasnjoj ivici kraka
  - zid `A` = ugaoni modul mora biti poslednji desno
  - zid `B/C` = ugaoni modul mora biti prvi levo
- layout audit i blocking validacije sada hvataju pogresno postavljen ugaoni modul
- manufacturing warning sloj daje dodatno upozorenje ako ugaoni modul nije naslonjen na ugao
- dodat smoke:
  - `CORNER_RULES_OK=True`

Zasto prvo L kuhinja:
- to je najcesci sledeci realni kuhinjski scenario posle jednog zida
- dovoljno je slozena da natera engine da resi ugao, continuity i zid B
- mnogo je manji rizik nego da se odmah otvara U/galija/ostrvo

Cilj:
- da `l_oblik` u wizardu ne bude samo priprema, nego potpuno upotrebljiv kuhinjski workflow

Sta mora da radi da bi L kuhinja bila smatrana zavrsenom:
1. Zid A i zid B moraju imati stvarno odvojeno postavljanje elemenata
2. Corner logika mora biti eksplicitna:
   - `BASE_CORNER`
   - `WALL_CORNER`
   - pravilo koji susedni elementi smeju da nalegnu na ugaoni modul
3. Auto-placement mora da zna kada je korisnik presao sa zida A na zid B
4. 2D prikaz mora jasno da pokazuje prelom L kuhinje i kontinuitet modula
5. 3D prikaz mora da prikaze pravi ugao, ne samo linearni niz sa drugim `wall_key`
6. Radna ploca mora da se racuna po segmentima:
   - segment zid A
   - segment zid B
   - spoj / nastavak u uglu
7. Sokla mora da se racuna po segmentima, ne kao jedan linearni komad
8. Cutlist i servis paket moraju da nose jasnu informaciju kom zidu pripada deo
9. Upozorenja moraju da hvataju tipicne L probleme:
   - konflikt dubina u uglu
   - kolizija frontova / rucki
   - nedovoljna servisna tolerancija uz zid
   - pogresan raspored ugaonog modula i suseda
10. QA mora da postoji kroz najmanje 3 scenarija:
   - L kuhinja sa donjim ugaonim elementom
   - L kuhinja sa gornjim ugaonim elementom
   - L kuhinja sa visokom kolonom na jednom kraku

Otvorena tehnicka mesta za L kuhinju:
- `ui_wizard_tab.py`
  - `l_oblik` mora da vodi u stvarni room/layout tok, ne samo u pripremu prostora
- `state_logic.py`
  - dodavanje i editovanje modula mora da bude svesno zida A/B i prelaza ugla
- `layout_engine.py`
  - placement, free-space i audit moraju da rade po dva kraka sa pravilima ugla
- `visualization.py`
  - 2D mora da crta realan L raspored i continuity po zidu
- `render_3d.py`
  - 3D kamera i scene moraju da prate pravi ugaoni raspored
- `cutlist.py`
  - radna ploca, sokla i servis paket moraju da budu segmentni po zidu

Definition of done za L kuhinju:
- korisnik moze da napravi L kuhinju bez rucnog varanja `wall_key`
- svi elementi se pravilno crtaju u 2D i 3D
- ugaoni moduli imaju smislen proizvodni izlaz
- radna ploca i sokla izlaze po segmentima
- PDF/Excel jasno pokazuju koji deo pripada zidu A, a koji zidu B
- smoke/QA scenariji prolaze bez overlap i continuity gresaka

Fajlovi:
- `layout_engine.py`
- `state_logic.py`
- `visualization.py`
- `render_3d.py`
- `cutlist.py`

#### P2A-4 - L-kuhinja corner offset (ugaoni razmak između zidova)

Status: `AKTIVNO — sesija 6 (15.03.2026)`

---

##### OPIS PROBLEMA

Wall B elementi počinju na x=0 u `layout_engine.py`, ali Wall A elementi
(dubina=560mm) fizički zauzimaju prostor x=0..560mm na Wall B.
Rezultat: kolizija 560×560mm u uglu — vidljivo u 3D kao tamna zona preklapanja.

**Fizika ugla:**
```
Wall A (zadnji zid):
  ├── korpusi dubine 560mm → protežu se 560mm u prostoriju
  └── ugao je 90°

Wall B (bočni zid):
  ├── počinje od ugla (x=0)
  ├── korpusi dubine 560mm → protežu se 560mm ka unutra
  └── ali x=0..560mm je već zauzeto dubinom Wall A!

Kolizija = 560 × 560mm kvadrat u uglu (oba korpusa zauzimaju isti prostor)
```

**Ispravno ponašanje:**
```
Wall B regularni elementi počinju od: x = corner_offset_mm
  gdje corner_offset_mm = dubina Wall A baze = 560mm (ili d_corner modula)
  + opcionalni estetski razmak 0-20mm (fuga između dva korpusa)
```

**Izuzeci od pravila:**
```
Wall B ugaoni element (BASE_CORNER / WALL_CORNER) = počinje od x=0
  → jer je on SAM ugaoni element koji rješava ugao
  → njegova dubina (d_mm) jednaka je ili manja od corner_offset_mm
```

---

##### TAKSATIVNI ZADACI

---

###### ZADATAK 1 — `layout_engine.py` — novi helper `_l_corner_left_mm()`

**Fajl:** `layout_engine.py`
**Gdje dodati:** Iza funkcije `_corner_anchor_side()` (oko linije 120)

**Šta radi:**
- Vraća dodatni lijevi x-offset koji Wall B mora poštovati zbog ugla
- Za Wall A, non-L-kitchen i za Corner module vraća 0
- Za Wall B regular elemente vraća dubinu Wall A baze

**Pseudo-kod:**
```python
def _l_corner_left_mm(kitchen: Dict, wall_key: str, template_id: str = "") -> int:
    """
    Vraća x-offset od kojeg Wall B regularni elementi smiju početi.
    Razlog: Wall A baza (dubina 560mm) fizički zauzima ugaoni prostor.
    Ugaoni moduli (CORNER u TID-u) su izuzeti — oni su ugaoni element.
    """
    # Nije L-kuhinja → nema offset-a
    if str(kitchen.get("kitchen_layout", "")) != "l_oblik":
        return 0

    wk = str(wall_key or "A").upper()

    # Wall A nema corner offset (on je referentni zid)
    if wk == "A":
        return 0

    # Ugaoni moduli su izuzeti (oni počinju od x=0 / anchor pozicije)
    if "CORNER" in str(template_id or "").upper():
        return 0

    # Anchor za Wall B
    anchor = _corner_anchor_side(wk, kitchen)
    if anchor != "left":
        return 0  # Offset je na desnoj strani — obrađuje se posebno

    # Postoji li ugaoni modul na Wall B?
    corner_mod = next(
        (m for m in (kitchen.get("modules", []) or [])
         if "CORNER" in str(m.get("template_id", "")).upper()
         and str(m.get("wall_key", "A")).upper() == wk),
        None,
    )
    if corner_mod:
        # Ugaoni modul postoji → offset = njegova dubina (d_mm)
        return int(corner_mod.get("d_mm", 560))

    # Nema ugaonog modula → offset = dubina Wall A baze iz zone_defaults
    zd = kitchen.get("zone_defaults", {}) or {}
    return int((zd.get("base") or {}).get("d_mm", 560) or 560)
```

**Provjera:**
- `_l_corner_left_mm(k, "A")` → 0
- `_l_corner_left_mm(k, "B")` → 560 (ako nema corner modula)
- `_l_corner_left_mm(k, "B", "BASE_CORNER")` → 0

---

###### ZADATAK 2 — `layout_engine.py` — `find_first_free_x()` — primijeni offset

**Fajl:** `layout_engine.py`
**Funkcija:** `find_first_free_x()` (oko linije 308)
**Gdje:** U sekciji za zone "base" i "wall" (regularne zone, ne tall_top/wall_upper)

**Trenutni kod (problem):**
```python
x = max(int(left), int(start_x)) if start_x is not None else int(left)
while x + w <= wall_len - right:
    if fits(x):
        return int(x)
    x += step
```

**Izmjena:**
```python
# L-kuhinja corner offset — Wall B elementi ne smiju početi u ugaonoj zoni
_corner_off = _l_corner_left_mm(kitchen, wall_key)
_effective_left = max(int(left), _corner_off)

x = max(_effective_left, int(start_x)) if start_x is not None else _effective_left
while x + w <= wall_len - right:
    if fits(x):
        return int(x)
    x += step
```

**Napomena:** `fits(x)` mora ostati nepromijenjen — provjera overlap-a je ispravna

---

###### ZADATAK 3 — `layout_engine.py` — `_compact_zone_skip_tall()` — ne sabijaj ispod offset-a

**Fajl:** `layout_engine.py`
**Funkcija:** `_compact_zone_skip_tall()` (kompaktovanje baze/walla)

**Problem:** Kada se sabijaju elementi, compact algoritam može potisnuti elem na x < corner_offset

**Izmjena:** Pri kompaktovanju, lijeva granica za Wall B = `max(left_clear, _l_corner_left_mm(kitchen, wall_key))`

```python
# Na početku _compact_zone_skip_tall():
_corner_off = _l_corner_left_mm(kitchen, wall_key)
_compact_left = max(int(left_clear), _corner_off)
# ... koristiti _compact_left kao početnu x poziciju umjesto left_clear
```

---

###### ZADATAK 4 — `layout_engine.py` — `layout_audit()` — detekcija corner offset kolizije

**Fajl:** `layout_engine.py`
**Funkcija:** `layout_audit()` (oko linije 660)

**Gdje dodati:** U sekciji provjere po wall_key, nakon provjere corner anchor pozicije

**Šta dodati:**
```python
# Provjera corner offset za regularni element na Wall B
for _rm in [m for m in _zone_mods if not _is_corner_module(m)]:
    _off = _l_corner_left_mm(kitchen, wk)
    if _off > 0:
        _rx0, _ = _span_x(_rm)
        if _rx0 < _off:
            return (False,
                f"Element id={_rm.get('id')} na Wall B počinje na x={_rx0}mm, "
                f"ali mora biti min. x={_off}mm zbog dubine ugla (Wall A dubina={_off}mm).")
```

---

###### ZADATAK 5 — `state_logic.py` — `_validate_blocking_design_rules()` — blokira pre-offset placement

**Fajl:** `state_logic.py`
**Funkcija:** `_validate_blocking_design_rules()` (oko linije 325)

**Gdje dodati:** U sekciji CORNER validacija, kao dodatna provjera za non-corner elemente

**Šta dodati:**
```python
# Wall B corner offset provjera — regularni elementi ne smiju početi u ugaonoj zoni
if str(wall_key or "A").upper() != "A" and "CORNER" not in str(template_id or "").upper():
    from layout_engine import _l_corner_left_mm
    _off = _l_corner_left_mm(kitchen, wall_key)
    if _off > 0 and int(x_mm) < _off:
        _fail(
            f"Na zidu B (bočni zid) elementi moraju početi min. {_off}mm od ugla. "
            f"Razlog: dubina elemenata na zidu A ({_off}mm) zauzima ugaoni prostor. "
            f"Element je automatski pomjeren na ispravnu poziciju."
        )
```

**Napomena:** Ova validacija se u pravilu NE AKTIVIRA jer `add_module_instance_local()`
koristi `_l_corner_left_mm` iz `find_first_free_x()`. Ovo je sigurnosna mreža za
ručno postavljanje (drag, JSON učitavanje starih projekata).

---

###### ZADATAK 6 — `cutlist.py` — worktop ugaoni spoj napomena + ispravni x0 Wall B

**Fajl:** `cutlist.py`
**Sekcija:** Radna ploča (oko linije 1628)

**Problem:** Wall B worktop segment računa `total_wt_w = max(xe) - min(xs)`.
Ako Wall B elementi (po fixi) počinju od x=560mm, `min(xs)=560` → dimenzija je ispravna.
Ali napomena mora eksplicitno reći korisnik gdje da napravi ugaoni zarez.

**Izmjena — dodati u napomenu:**
```python
# Za Wall B segment, izračunaj corner junction info
_corner_junction_note = ""
if _bwk != "A":
    from layout_engine import _l_corner_left_mm
    _coff = _l_corner_left_mm(kitchen, _bwk)
    if _coff > 0:
        _corner_junction_note = (
            f" NAPOMENA: Ugaoni spoj — notchovati za {_coff}mm dubinu Zid A. "
            f"Radna ploča Zid A prolazi ispod; Zid B se zarezuje u ugaonom spoju."
        )

# U rows_worktop.append() dodati na kraju napomene:
"Napomena": f"1 segment na zidu {_bwk}, dužina {total_wt_w}mm" + _corner_junction_note,
```

---

###### ZADATAK 7 — `visualization.py` — 2D prikaz Wall B — prikaži ugaonu blok zonu

**Fajl:** `visualization.py`
**Funkcija:** `_render()` — sekcija crtanja pozadine / granica

**Šta dodati:** Sivi poluprozirni pravougaonik od x=0 do x=corner_offset_mm
za Wall B u L-kuhinji, sa oznakom "Ugaona zona (Zid A dubina)"

```python
# Na početku _render(), nakon crtanja pozadine:
if kitchen.get("kitchen_layout") == "l_oblik" and wall_key != "A":
    from layout_engine import _l_corner_left_mm
    _coff = _l_corner_left_mm(kitchen, wall_key)
    if _coff > 0:
        # Siva zona koja pokazuje da je ovaj prostor fizički zauzet Zid A dubinom
        ax.add_patch(
            mpl.patches.Rectangle(
                (0, 0), _coff / 1000.0, total_h,
                linewidth=0, facecolor="#cccccc", alpha=0.35, zorder=1
            )
        )
        ax.text(
            _coff / 2000.0, total_h * 0.5,
            f"Ugaona\nzona\n{_coff}mm",
            ha="center", va="center",
            fontsize=5, color="#888888", rotation=90,
        )
```

---

###### ZADATAK 8 — `render_3d.py` — 3D Wall B startna pozicija

**Fajl:** `render_3d.py`
**Sekcija:** Rendering Wall B modula u 3D sceni

**Problem:** Wall B moduli renderiraju se od z=0 (od ugla), ali fizički bi trebali
početi od z=corner_offset_mm zbog dubine Wall A.

**Šta mijenjati:** Kod renderiranja modula po wall_key-u, za Wall B:
- Ugaoni moduli (CORNER) → ostaju na z=0 (ispravno, oni su ugaoni element)
- Regularni Wall B moduli → z_offset = corner_offset_mm

```python
# U funkciji koja renderira Wall B module, dodati:
from layout_engine import _l_corner_left_mm
_b_corner_offset = _l_corner_left_mm(kitchen, wk)

# Za svaki Wall B modul koji NIJE CORNER:
if "CORNER" not in str(m.get("template_id", "")).upper():
    z_position = module_x_mm + _b_corner_offset  # pomaknut od ugla
else:
    z_position = module_x_mm  # ugaoni modul ostaje na uglu
```

**Napomena:** Tačno ime varijable i koordinatni sistem treba prilagoditi
postojećem `render_3d.py` kodu (provjeri ime varijable za Wall B z-os).

---

###### ZADATAK 9 — `smoke_scenarios.py` — novi testovi za corner offset

**Fajl:** `smoke_scenarios.py`

**Test 1: `smoke_corner_offset_wall_b()`**
```python
def smoke_corner_offset_wall_b():
    """
    Provjera: Wall B regularni element ne može biti postavljen na x < corner_offset.
    Provjera: find_first_free_x() za Wall B vraća x >= corner_offset.
    """
    # Reset state, postavi L-kuhinju
    # Dodaj BASE_2DOOR na Wall B
    # Provjeri da je x_mm >= zone_defaults['base']['d_mm'] (560mm)
    # PASS ako x >= 560
```

**Test 2: `smoke_corner_offset_no_break_wall_a()`**
```python
def smoke_corner_offset_no_break_wall_a():
    """
    Provjera: Wall A elementi NISU pogođeni corner offset logikom.
    Wall A find_first_free_x() počinje od 0 (samo profile clearance).
    """
    # Dodaj BASE_2DOOR na Wall A
    # Provjeri da je x_mm == 0 (ili profile_clearance)
    # PASS
```

**Test 3: `smoke_corner_offset_cutlist_worktop()`**
```python
def smoke_corner_offset_cutlist_worktop():
    """
    Provjera: Wall B worktop napomena sadrži 'notchovati' ili 'ugaoni spoj'.
    """
    # Dodaj modele na Wall A i Wall B
    # Generiši cutlist
    # Provjeri rows_worktop za Wall B: napomena sadrži ključnu riječ
    # PASS
```

---

###### ZADATAK 10 — Verifikacija (Definition of Done)

**Kompajliranje:**
```bash
python -m py_compile layout_engine.py state_logic.py cutlist.py visualization.py render_3d.py smoke_scenarios.py
```

**Automatski testovi:**
```bash
python smoke_scenarios.py
# Očekivano:
# CORNER_OFFSET_WALL_B_OK=True
# CORNER_OFFSET_NO_BREAK_WALL_A_OK=True
# CORNER_OFFSET_CUTLIST_WORKTOP_OK=True
# Sve prethodne provjere ostaju True (nema regresije)
```

**Ručni test (vizuelna provjera):**
1. Pokrenuti aplikaciju: `python app.py`
2. Wizard → L-oblik desni ugao → Zid A: 3000mm, Zid B: 2400mm
3. Dodati BASE_2DOOR na Zid A (3 komada)
4. Prebaciti na Zid B
5. Dodati BASE_2DOOR — mora početi od x≥560mm, NE od x=0
6. Preklopiti na 3D prikaz — kolizija u uglu mora biti NESTALA
7. Otvoriti krojna listu — Wall B worktop napomena mora sadržati "notchovati"

**Definition of done:**
- [ ] `_l_corner_left_mm()` dodan i poziva se iz `find_first_free_x()`
- [ ] Wall B elementi u UI počinju od x=560mm (ne x=0)
- [ ] 3D prikaz: nema tamne kolizije u uglu
- [ ] 2D prikaz Wall B: siva zona označava ugaonu blokadu
- [ ] Cutlist napomena za Wall B worktop sadrži info o ugaonom spoju
- [ ] Wall A elementi NISU pogođeni (regresija=0)
- [ ] Smoke testovi: svi prolaze

---

**Fajlovi koje dira P2A-4:**
- `layout_engine.py` — ZADACI 1, 2, 3, 4 (glavni nosač fixa)
- `state_logic.py` — ZADATAK 5 (sigurnosna validacija)
- `cutlist.py` — ZADATAK 6 (napomena worktop)
- `visualization.py` — ZADATAK 7 (2D vizualni indikator)
- `render_3d.py` — ZADATAK 8 (3D pozicioniranje)
- `smoke_scenarios.py` — ZADATAK 9 (automatski testovi)

**Redosljed implementacije:** 1 → 2 → 3 → 9 (testovi) → 4 → 5 → 6 → 7 → 8 → 10

---

#### P2A-2 - Ciscenje ikon sistema elemenata i realniji katalog preview

Status: `OTVORENO - VISOK PRIORITET posle osnovnog L ugla`

Cilj:
- da ikonice elemenata vise ne zavise od 3 nepovezana sloja
- da katalog, preview i izvestaji gledaju isti vizuelni jezik
- da posebno `OPEN` elementi, police, ugaoni elementi i appliance moduli izgledaju realnije i citljivije

Realno stanje sada:
1. `module_templates.json`
   - `visual.icon` postoji kao legacy metadata / pomocni simbol
   - nije dobar izvor za realan izgled elementa
2. `svg_icons.py`
   - rucni fallback SVG sloj
   - stabilan, ali lako odstupi od stvarnog 2D/3D izgleda
3. `visualization.py`
   - pravi render preview sloj
   - ovo treba da postane glavni izvor izgleda za katalog i preview

Zeljena arhitektura:
- glavni izvor ikonice / preview-a = `visualization.py`
- fallback samo ako render padne = `svg_icons.py`
- `module_templates.json.visual.icon` ostaje samo kao metadata ili legacy

Sta mora da se uradi:
1. `ui_catalog_panel.py`
   - katalog po default-u mora da koristi `render_element_preview(...)`
   - SVG fallback sme da se koristi samo kad preview render ne uspe
   - prosiriti `_CATALOG_2D_PRIORITY_TIDS` za module gde je 2D verniji od 3D thumbnail-a
   - obavezno dodati:
     - `BASE_OPEN`
     - `WALL_OPEN`
     - `TALL_OPEN`
     - `TALL_TOP_OPEN`
     - `WALL_UPPER_OPEN`
2. `visualization.py`
   - glavni posao na realizmu ikonica / preview-a
   - proveriti i po potrebi doraditi:
     - `_detect_type(...)`
     - `_draw_module(...)`
     - `_render_element_2d(...)`
     - specijalne draw funkcije za:
       - `open`
       - `drawer`
       - `corner`
       - `glass`
       - `dishwasher`
       - `fridge`
       - `oven`
       - `liftup`
3. `svg_icons.py`
   - ostaviti samo kao fallback sloj
   - ne koristiti ga kao glavni vizuelni sistem
   - po potrebi zadrzati samo osnovne rezervne SVG ikone
4. `module_templates.json`
   - ne ulagati vreme u `visual.icon` kao glavni vizuelni sloj
   - koristiti ga samo kao metadata / legacy
5. `ui_cutlist_tab.py`
   - proveriti da i ovde preview koristi isti render sloj kao katalog
   - izbeci da cutlist i katalog koriste razlicitu logiku izgleda

Poseban fokus za realizam:
- `OPEN` elementi moraju da imaju:
  - jasne bocne stranice
  - gornju i donju plocu
  - police pravilnog razmaka
  - jaci kontrast izmedju korpusa i police
  - bez vrata i bez rucki
- `CORNER` elementi moraju da izgledaju kao stvarni ugaoni front / ugaoni korpus
- appliance elementi moraju odmah da se razlikuju od obicnog ormara
- 2D preview mora da bude glavni thumbnail kad je informativniji od 3D

Preporuceni redosled rada:
1. `ui_catalog_panel.py` - prebaciti katalog na preview-first logiku
2. `visualization.py` - srediti `OPEN` elemente i police
3. `visualization.py` - srediti `CORNER` i appliance preview
4. `svg_icons.py` - svesti na rezervni fallback sloj

Definition of done:
- katalog koristi jedan glavni preview sistem
- `OPEN` elementi u katalogu izgledaju kao pravi otvoreni ormari / police
- `CORNER` i appliance elementi su odmah prepoznatljivi
- SVG fallback se koristi samo kad preview render ne uspe
- katalog, cutlist preview i element preview vise ne odstupaju vizuelno jedan od drugog

Fajlovi:
- `ui_catalog_panel.py`
- `visualization.py`
- `svg_icons.py`
- `module_templates.json`
- `ui_cutlist_tab.py`

### P2B - Nesting / optimizer / CNC export

Status: `POSLE zatvaranja osnovnog proizvodnog paketa`

Zadaci:
- nesting-friendly CSV/XLSX
- cut optimization po materijalu
- eventualni CNC izlaz ili barem machine-ready operaciona tabela

### P3 - Produkcija, login, pretplata i hosting

Status: `POSLE zatvaranja P1/P2A-1, pre javnog pustanja`

Cilj:
- da aplikacija ne ostane samo lokalni alat
- da korisnik moze da se registruje / uloguje
- da plati pristup na odredjeno vreme
- da aplikacija radi na javnom domenu sa SSL i backup-om

Sta mora da postoji:
1. Login i korisnicki nalozi
   - registracija
   - login / logout
   - reset lozinke
   - osnovne role: `admin`, `paid_user`, `trial_user`
2. Naplata i pretplata
   - mesecna ili godisnja pretplata
   - probni period ako se odluci
   - automatska aktivacija / deaktivacija pristupa po statusu pretplate
   - evidencija transakcije i statusa pretplate
3. Produkcioni deployment
   - javni domen
   - HTTPS / SSL
   - produkcioni server
   - restart procesa
   - logovi i monitoring
   - backup baze i korisnickih podataka
4. Operativna administracija
   - admin pregled korisnika i pretplata
   - blokiranje / odblokiranje naloga
   - osnovni usage audit
5. Pravna i poslovna priprema
   - uslovi koriscenja
   - politika privatnosti
   - napomena sta aplikacija garantuje, a sta korisnik proverava na licu mesta

Preporuceni tehnicki model:
- `NiceGUI app` kao glavni web UI i aplikacioni server
- `Supabase Auth + Postgres` za login, korisnike i status pretplate
- `Stripe` za naplatu pretplate
- `Docker` + `Caddy` ili `Nginx` za produkcioni deployment
- hosting:
  - jednostavniji start: `Render` ili `Railway`
  - ozbiljniji i jeftiniji dugorocni model: `Hetzner VPS`

Tehnicke stavke za realizaciju:
1. Izdvojiti produkcioni config:
   - `APP_ENV`
   - `BASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
2. Napraviti tabelu / model pretplate po korisniku
3. Dodati route / page za:
   - login
   - registraciju
   - profil
   - billing
4. Dodati proveru pristupa:
   - free / trial
   - paid
   - expired
5. Napraviti produkcione fajlove:
   - `Dockerfile`
   - `.dockerignore`
   - `docker-compose.yml` ili ekvivalent
   - reverse proxy config
6. Dodati operativne procedure:
   - deploy
   - rollback
   - backup
   - rotate kljuceva

Definition of done:
- korisnik moze da otvori javni domen
- moze da napravi nalog i potvrdi pristup
- moze da plati pretplatu
- posle placanja dobija pristup aplikaciji
- kada pretplata istekne, pristup se ogranicava po pravilima
- aplikacija radi stabilno na produkcionom hostingu sa SSL
- postoji osnovni admin pregled korisnika i pretplata

### 7. Predlog redosleda rada od sledece sesije

1. `P0B` - matrica svih template-a i zatvaranje cutlist pokrivenosti
2. `P0A` - servis paket + shopping list + checklist za laika
3. `P0C` - blokirajuce validacije
4. `P1A` - potpuni okovi i potrosni materijal
5. `P1B` - obrade i instrukcije za servis
6. `P1C` - vizuelno mapiranje delova
7. `P1D` - paritet render/cutlist
8. `P2A-1` - usavrsiti L kuhinju kao prvi multi-wall milestone
9. `P2A` - siri multi-wall (U/galija posle L)
10. `P2B` - optimizer/CNC

### 8. Operativna napomena za sledeci rad

Od ove tacke nadalje razvoj ne treba voditi samo kao "dodavanje funkcija".
Treba ga voditi kao proveru da svaki aktivni template moze da prodje kroz svih 6 koraka:

1. izbor u katalogu
2. pravilno crtanje 2D
3. pravilno crtanje 3D
4. pravilan proizvodni obracun
5. potpuna shopping lista
6. izvodljiva kucna montaza

Ako padne ijedan od 6 koraka, template nije spreman za laicki workflow.

---

## NAPOMENA ZA NOVI CHAT

Ako se nastavlja razvoj, prvo otvoriti ovaj dokument + navesti tačnu stavku iz sekcije **AGENDA ZA REALIZACIJU**.

**Sledeći konkretan korak:** `P0-4` — Realan multi-wall model (L/U/galija aktivno u layout/placement logici)
ili
**P0-5** — QA matrica (ručni klik-smoke svih tabova)
Napomena 12.03.2026 - ispravka prioriteta:
- novi prvi korak je `P0B` - matrica svih aktivnih template-a i zatvaranje cutlist pokrivenosti
- odmah zatim ide `P0A` - servis paket + shopping list + checklist za laika

---

## SESIJA 4 — 12. mart 2026

### Sta je uradjeno

#### Per-element boja za OPEN elemente — ZAVRSENO

- Dodat per-element color picker u `ui_edit_panel.py` za sve OPEN tipove:
  - `BASE_OPEN`, `WALL_OPEN`, `TALL_OPEN`, `TALL_TOP_OPEN`, `WALL_UPPER_OPEN`
- Boja se cuva u `module['params']['front_color']`
- `render_3d.py` vec cita ovaj podatak (`_m_front_raw`) i koristi ga kao boju ploce
- Smoke testovi prosli bez gresaka

Izmenjeni fajlovi:
- `ui_edit_panel.py` (4 izmene: import, `_is_open` detekcija, UI widget, `_collect_drawer_params`)

#### L-kuhinja analiza — dokumentovano

Provereno stanje:

1. **Ugaoni elementi koji postoje:**
   - `BASE_CORNER` (slepi kut, donji, 900×720×560mm) — postoji u JSON i katalogu
   - `WALL_CORNER` (L-ormaric, gornji, 600×720×350mm) — postoji u JSON i katalogu

2. **Sto nedostaje:**
   - `BASE_CORNER_DIAGONAL` (dijagonalni donji ugaoni) — treba dodati
   - `WALL_CORNER_DIAGONAL` (dijagonalni gornji ugaoni) — treba dodati
   - L-profil u `cutlist.py`: ugaoni elementi dobijaju PRAVOUGAONI korpus, ne L-oblik — samo stub komentar

3. **Vrata / otvaranje:**
   - `CORNER_DOOR_SWING`, `CORNER_OPENING_CLEARANCE`, `CORNER_FRONT_COLLISION` postoje kao warninzi
   - Nisu blokirajuci, samo upozorenja

4. **Crvena vertikalna linija u 2D:**
   - NIJE bag — to je indikator maksimalne visine na kojoj moze da se postavi viseci element na toj X poziciji

#### Ugaoni tab — plan dogovorenScopirana nova funkcionalnost:

- Poseban tab **"Ugaoni"** u bočnoj paleti
- Vidljiv SAMO kada je `kitchen_layout` u `("l_oblik", "u_oblik")`
- Sadrzi 4 elementa:
  - Donji ugaoni: `BASE_CORNER` + `BASE_CORNER_DIAGONAL`
  - Gornji ugaoni: `WALL_CORNER` + `WALL_CORNER_DIAGONAL`
- `BASE_CORNER` i `WALL_CORNER` se uklanjaju iz donji/gornji tabova (nema duplikata)
- `get_palette_tabs()` dobija novi parametar `kitchen_layout`

Fajlovi koji se menjaju:
- `ui_catalog_config.py` — novi `UGAONI_TAB`, izmena `get_palette_tabs()`
- `ui_catalog_panel.py` — prosledjivanje `kitchen_layout` parametra
- `ui_sidebar_panel.py` — provera da li state stize
- `module_templates.json` — 2 nova template-a
- `svg_icons.py` — 2 nove SVG ikone

### Sta je otvoreno posle sesije 4

#### P2A-2 — Ugaoni tab i novi ugaoni template-i

Status: `U TOKU — poceto sesija 4, implementacija u toku`

Zadaci:
1. `ui_catalog_config.py`:
   - Dodati `UGAONI_TAB` dict sa 4 elementa
   - Ukloniti `BASE_CORNER` iz donji taba
   - Ukloniti `WALL_CORNER` iz gornji taba
   - Izmeniti `get_palette_tabs()` da prima `kitchen_layout` i uslovno vraca ugaoni tab
2. `ui_catalog_panel.py`:
   - Proslediti `state.kitchen.get("kitchen_layout")` pri pozivu `get_palette_tabs()`
3. `ui_sidebar_panel.py`:
   - Proveriti/dopuniti prosledjivanje state-a do `render_palette()`
4. `module_templates.json`:
   - Dodati `BASE_CORNER_DIAGONAL` (900×720×560mm, zone: base)
   - Dodati `WALL_CORNER_DIAGONAL` (600×720×350mm, zone: wall)
5. `svg_icons.py`:
   - Dodati SVG ikone za dijagonalne varijante
6. Buduci korak (ne ova sesija):
   - `cutlist.py`: pravi L-oblik korpusa za ugaone elemente (umesto pravougaonog stuba)

Fajlovi:
- `ui_catalog_config.py`
- `ui_catalog_panel.py`
- `ui_sidebar_panel.py`
- `module_templates.json`
- `svg_icons.py`

---

## SESIJA 5 — 12. mart 2026

### Sta je uradjeno

#### Ugaoni tab — bug fix i implementacija — ZAVRSENO

Sesija 4 je završila implementaciju ugaonog taba, ali se pokazalo da tab nije bio vidljiv
jer je `_palette_tabs_current()` čitao pogrešan ključ iz dict-a:
- Bug: `state.kitchen.get("kitchen_layout")` → uvijek vraćalo `None`
- Fix: `getattr(state, "kitchen_layout", state.kitchen.get("layout", ""))` (isti pattern kao u `render_3d.py` linija 1022)

Nakon fixa, ugaoni tab je vidljiv za L/U kuhinje kao što je planirano.

Izmenjeni fajlovi u sesiji 4+5 kombinovano:
- `ui_catalog_config.py` — UGAONI_TAB + get_palette_tabs(kitchen_layout=)
- `ui_panels.py` — _palette_tabs_current() fix
- `module_templates.json` — BASE_CORNER_DIAGONAL, WALL_CORNER_DIAGONAL
- `svg_icons.py` — SVG ikone za dijagonalne varijante (BEFORE postojecih CORNER grana)
- `ui_catalog_panel.py` — BASE_CORNER_DIAGONAL, WALL_CORNER_DIAGONAL u 2D priority listi

#### cutlist.py — L-oblik korpusa za ugaone elemente — ZAVRSENO

Prethodni stub: ugaoni element tretiran kao pravougaoni korpus sa jednim frontom i napomenom.

Novi model: pravi L-oblik koriscenjem geometrije oba kraka:

**CARCASS (FAZA B):**
- `Strana 1 (ugaona)` + `Strana 2 (ugaona)`: h × d (krajnje bocne ploce, 1× svaka)
- `Kutna vertikala` (2×): h × d (unutrasnji separator, jedan za svaki krak)
- `Dno — Krak 1`: (w-2t) × (d-t) (pokriva kvadratni ugao + produzenje Kraka 1)
- `Dno — Krak 2`: (d-2t) × (w-d-t) (produzenje drugog kraka van ugaonog kvadrata)
- Za WALL zone: isti `Plafon — Krak 1` + `Plafon — Krak 2` komadi

**BACKS (FAZA C):**
- Umesto 1× (w×h), sada 2× arm backs:
  - `Ledna ploca — Krak 1`: (w-d) × h (krak A produzenje)
  - `Ledna ploca — Krak 2`: (w-d) × h (krak B produzenje, simetricno)
  - Groove formula: `(w-d) - 2*GROOVE_DEPTH` umesto `w - 2*GROOVE_DEPTH`

**FRONTS (FAZA E):**
- Poboljsana napomena razlikuje `DIAGONAL` vs standardni ugaoni element

**Assembly step:**
- `strana ... ugaon` → korak 1 (spoljna bocna ploca, montuje se prva)
- `kutna vertikala` → korak 3 (unutrasnji separator)

Verifikovane dimenzije za BASE_CORNER (w=900, h=720, d=560, thk=18):
- Strana: 560×720 ✓
- Kutna vertikala (2×): 560×720 ✓
- Dno K1: 864×542 ✓ (inner_w=864, inner_d=542)
- Dno K2: 524×322 ✓ (d-2t=524, w-d-t=322)
- Ledna K1+K2: 324×712 ✓ (arm=340-2*8=324, h-8=712)
- WALL_CORNER dobija i Plafon K1+K2 ✓

Izmenjeni fajlovi:
- `cutlist.py` (5 izmena: _is_corner flag, FAZA B, FAZA C, FAZA E, _assembly_step_for)

#### Smoke testovi — svi prosli

```
smoke_scenarios.py: 0 failing tests
CORNER_RULES_OK=True
CORNER_DOOR_SWING_OK=True
CORNER_GUIDANCE_OK=True
L_LEFT_CORNER_OK=True
MULTIWALL_L_BASIC_OK=True
MULTIWALL_CUTLIST_OK=True
... (sve OK)
```

### Sta je otvoreno posle sesije 5

#### P2A-3 — Vizuelni L-oblik u 2D/3D za ugaone elemente

Trenutno stanje:
- Ugaoni element se u 2D crta kao pravougaonik (sirine w, dubine d)
- 3D prikaz je takodje samo box

Sledeci korak:
- `visualization.py`: crtati ugaoni element kao L-oblik u 2D (plan view)
- Ili bar jasno oznaciti u 2D da je to ugaoni element (posebna srafura / label)
- `render_3d.py`: L-oblik u 3D (nizeg prioriteta)

Napomena: ovo je P2 prioritet — ne blokira produkciju.
### Status update 14.03.2026 - P2A-2 i P2A-3

Uraden dodatni vizuelni i UX sloj posle sesije 5:
- `P2A-3`:
  - `visualization.py` - `L plan` inset vise ne crta ugaone module kao obicne pravougaonike; standardni i dijagonalni ugaoni imaju poseban plan-oblik
  - `render_3d.py` - ugaoni moduli dobijaju realniji return/front, povrat radne ploce i finiji prikaz za `WALL_CORNER` i dijagonalne varijante
  - `visualization.py` - single-element 3D preview razlikuje `BASE_CORNER` i `BASE_CORNER_DIAGONAL`
- `P2A-2`:
  - `ui_catalog_panel.py` - katalog sada zaista koristi preview renderer kao glavni sloj; `svg_icons.py` je fallback
  - `ui_catalog_panel.py` - `OPEN` elementi su prebaceni na 2D priority (`BASE/WALL/TALL/TALL_TOP/WALL_UPPER`)
  - `visualization.py` - `OPEN` moduli imaju realnije bocne stranice, gornju/donju plocu, ledja i police
  - `visualization.py` - doradjeni `glass`, `dishwasher`, `hood` i `microwave` 2D preview-i za katalog

Aktuelno stanje:
- `P2A-3` je znacajno priblizen zavrsetku za L ugao i ugaone elemente
- `P2A-2` je u toku, ali glavni arhitektonski presek je uradjen: preview renderer je primaran, SVG je fallback

Smoke status:
- `WALL_CORNER_AUTOPLACE_OK=True`
- `DIAGONAL_CORNER_PREVIEW_OK=True`
- `DIAGONAL_CORNER_PREVIEW_3D_OK=True`
- `MULTIWALL_L_BASIC_OK=True`
- `MULTIWALL_CUTLIST_OK=True`
