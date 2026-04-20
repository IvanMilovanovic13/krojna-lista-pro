# Mapa Projekta - Krojna Pista PRO

## 1) Start i orkestracija
- `app.py` - pokretanje aplikacije.
- `ui_panels.py` - glavni orkestrator UI-a (toolbar, sidebar, canvas, tabovi).
- `ui_main_content.py` - render glavnog sadr?aja po aktivnom tabu.
- `ui_navigation.py` - pravila prelaska izme?u tabova.

## 2) Stanje i poslovna logika
- `state_logic.py` - globalni state, reset, save/load, CRUD modula.
- `auth_models.py` - minimalni session/access skeleton za buduci login i billing.
- `project_store.py` - lokalni SQLite temelj za buduce `users/projects` modele.
- `layout_engine.py` - raspored i pakovanje elemenata po zidovima/zona.
- `room_constraints.py` - ograni?enja zbog otvora/instalacija.

## 3) Wizard i prostorija
- `ui_wizard_tab.py` - po?etni koraci projekta.
- `room_setup_wizard.py` - unos dimenzija zidova i priprema prostora.
- `room_openings_editor.py` - editor otvora.
- `room_floorplan_editor.py` - editor osnove prostora.
- `ui_room_helpers.py` - pomo?ne room funkcije i tipovi.

## 4) Elementi (dodavanje/izmena)
- `ui_catalog_config.py` - grupe/tabs i raspored elemenata u paleti.
- `ui_catalog_panel.py` - render varijanti i izbor elementa.
- `ui_params_panel.py` - parametri pri dodavanju elementa.
- `ui_edit_panel.py` - parametri pri izmeni postoje?eg elementa.
- `ui_module_properties.py` - napredni panel svojstava elementa.
- `ui_add_above_dialogs.py` - dodavanje gornjih iznad postoje?ih.

## 5) Prikaz (2D/3D)
- `visualization.py` - 2D crtanje elemenata i tehni?ki prikaz.
- `ui_canvas_2d.py` - interakcija u 2D (klik/drag/select).
- `render_3d.py` - 3D scena i elementi.
- `ui_canvas_toolbar.py` - kontrole prikaza (mre?a, mod, zoom i sl.).
- `svg_icons.py` - SVG ikonice elemenata.

## 6) Krojna lista i eksport
- `cutlist.py` - prora?un krojne liste i export CSV/Excel podataka.
- `ui_cutlist_tab.py` - UI za prikaz i preuzimanje krojne liste.
- `ui_pdf_export.py` - PDF eksport.
- `ui_assembly.py` - uputstva za sklapanje.

## 7) Konfiguracija i podaci
- `module_templates.json` - definicije template elemenata.
- `module_templates.py` - u?itavanje/rezolucija template-a.
- `i18n.py` - svi tekstovi/label-e na UI-u.
- `requirements.txt` - zavisnosti.
- `.python-version` - preporucena Python verzija za lokalni rad/deploy.
- `SETUP_VENV.ps1` - automatsko pravljenje `venv` i instalacija paketa.
- `SETUP_OKRUZENJE.md` - kratko uputstvo za setup i pokretanje.
- `DEPLOY_RENDER_OD_LOKALA_DO_HOSTA.md` - korak-po-korak vodic za push na GitHub i deploy na Render host.
- `QA_STAGING_SMOKE_ACCEPTANCE.md` - staging smoke + acceptance checklista za hostovanu proveru.
- `MASTER_PROJEKAT.md` - projektna bele?nica.

## 8) Testiranje
- `smoke_scenarios.py` - brza regresiona provera.
- `test_wall_upper.py` - test specifi?ne logike gornjeg reda.

## 9) Referentni materijali i asseti
- Stari Word/image referentni artefakti vise nisu aktivni deo runtime projekta.
- `fonts/DejaVuSans*.ttf` - fontovi za render/PDF.

---
Detaljna tabela svih fajlova je u: `MAPA_PROJEKTA_FAJLOVI.xlsx`
