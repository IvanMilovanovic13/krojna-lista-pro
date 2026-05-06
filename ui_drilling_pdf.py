# -*- coding: utf-8 -*-
"""
Generisanje PDF-a za plan bušenja i sklapanja.

Struktura PDF-a:
  1. Edukativni uvod  — "Kako se čita plan bušenja"
  2. Tehničke tabele  — po elementu, po ploči, sa koordinatama rupa
"""
from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path
from typing import List, Any

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Edukativni tekstovi — svi jezici
# ---------------------------------------------------------------------------

_EDU: dict[str, dict[str, str]] = {
    "sr": {
        "doc_title":      "Plan bušenja za radionicu",
        "doc_sub":        "KrojnaListaPRO — Generisani radionički dokument",
        "edu_title":      "Kako se čita plan bušenja",
        "edu_intro":      (
            "Ovaj dokument pokazuje gde radionica treba da izbuši rupe na svakoj ploči."
        ),
        "edu_panels_hdr": "Svaki element ima svoje ploče:",
        "edu_panels": [
            "LS  =  leva stranica",
            "DS  =  desna stranica",
            "DNO  =  donja ploča",
            "VRH  =  gornja ploča / plafon",
            "LEDJA  =  zadnja ploča",
            "FRONT  =  vrata",
        ],
        "edu_cols_hdr":   "Kolone znače:",
        "edu_cols": [
            "X  =  udaljenost rupe od leve ivice ploče",
            "Y  =  udaljenost rupe od donje ivice ploče",
            "Ø  =  prečnik rupe",
            "Dubina  =  koliko duboko se buši",
        ],
        "edu_example_hdr": "Primer:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— rupa se buši 50 mm od leve ivice i 9 mm od donje ivice."
        ),
        "edu_dowel_hdr":   "Tipl fi8:",
        "edu_dowel": (
            "Rupa za drveni tipl prečnika 8 mm. "
            "Tipl služi da ploče legnu tačno i da ne pobegnu "
            "prilikom sklapanja."
        ),
        "edu_shelf_hdr":   "Nosač police fi5:",
        "edu_shelf": (
            "Rupa za nosač police prečnika 5 mm. "
            "Ako postoji mnogo rupa u razmaku od 32 mm, to znači da se "
            "polica može podešavati po visini."
        ),
        "edu_important_hdr": "Važno:",
        "edu_important": (
            "Tipl ne steže element.\n"
            "Tipl samo vodi ploče.\n"
            "Šraf ili konfirmat steže spoj."
        ),
        "edu_rule":        "Tipl vodi — šraf steže.",
        # tabele
        "tbl_element":    "Element",
        "tbl_zone":       "Zona",
        "tbl_panel":      "Ploča",
        "tbl_dims":       "Dim. (mm)",
        "tbl_holes":      "Rupe",
        "tbl_purpose":    "Tip",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "Ø (mm)",
        "tbl_depth":      "Dubina (mm)",
        "tbl_note":       "Napomena",
        "tbl_no_holes":   "— bez rupa —",
        "tbl_assembly":   "Uputstvo za sklapanje",
        "tbl_workshop":   "Napomene za radionicu",
        "tbl_no_modules": "Nema elemenata u projektu.",
        "purpose_hinge":  "Šarka fi35",
        "purpose_dowel":  "Tipl fi8",
        "purpose_shelf":  "Nosač police fi5",
        "purpose_slide":  "Klizač fioke",
        # --- Opšta pravila ---
        "gen_rules_title": "Opšta pravila",
        "gen_sys32_title": "Sistem 32 mm — nosači polica",
        "gen_sys32_text":  (
            "Rupe za nosače polica izrađene su po standardnom sistemu 32 mm "
            "(razmak 32 mm između svake rupe). U tabeli se prikazuje samo "
            "prva (najniža) Y pozicija — sve ostale rupe nastavljaju na svakih 32 mm od nje."
        ),
        "gen_mirror_note":    "⇇  Desna stranica je ogledalo leve stranice.",
        "gen_shelf_hdr":      "Nosači polica — sistem 32 mm",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Prva Y (mm)",
        "gen_shelf_count":    "Br. rupa",
        "gen_shelf_note":     "Ostale rupe: svakih 32 mm od prve Y pozicije.",
        # tekstualni blok za police (bez tabele)
        "shelf_blk_title":    "Rupe za police (sistem 32 mm)",
        "shelf_blk_intro":    "Rupe za nosače polica bušiti po standardu sistema 32 mm.",
        "shelf_blk_raster":   "Razmak između rupa: 32 mm",
        "shelf_blk_first_y":  "Početna visina prve rupe: Y =",
        "shelf_blk_x_pos":    "X pozicije:",
        "shelf_blk_outro":    "Rupe se buše celom visinom ploče u ovom rasteru.",
        "shelf_universal":    (
            "NAPOMENA: Rupe za police izrađuju se po standardnom sistemu 32 mm "
            "i ne prikazuju se pojedinačno u tabeli."
        ),
        # --- Važno za montažu (profesionalna sekcija) ---
        "imp_title":       "VAŽNO ZA MONTAŽU",
        "imp_items": [
            "Sve rupe su fabrički definisane — nije potrebno dodatno bušenje.",
            "Tipl služi za pozicioniranje ploča (ne steže spoj).",
            "Šraf / konfirmat steže element.",
            "Police se mogu postavljati na željenu visinu (sistem 32 mm).",
            "Voditi računa o orijentaciji ploča: X = udaljenost od leve ivice, Y = od donje ivice.",
        ],
        # --- Uputstvo za sklapanje (korisnik početnik) ---
        "asm_title":       "Uputstvo za sklapanje",
        "asm_intro":       "Korisnik ne treba da buši rupe — sve rupe su već pripremljene u radionici.",
        "asm_steps": [
            "Ubaciti drvene tiplove u predviđene rupe.",
            "Spojiti stranice sa dnom elementa (tiplovi su vođice).",
            "Dodati gornju ploču (plafon elementa).",
            "Poravnati sve ploče da lepo legnu.",
            "Stegnuti spojeve šrafovima ili konfirmatima.",
            "Postaviti leđa elementa.",
            "Ubaciti nosače polica na željenu visinu.",
            "Postaviti police.",
            "Montirati vrata (ako postoje).",
        ],
        "asm_rule_title":  "Zlatno pravilo",
        "asm_rule":        "Tipl vodi — šraf steže.",
        "asm_rule_tipl":   "Tipl služi da ploče legnu tačno.",
        "asm_rule_sraf":   "Šraf služi da učvrsti spoj.",
        "asm_note_title":  "Napomena",
        "asm_note":        "Sve pozicije rupa su već definisane. Nije potrebno dodatno merenje.",
        "asm_shelf_title": "Police",
        "asm_shelf": [
            "Rupe za police izrađene su po sistemu 32 mm.",
            "Polica se može postaviti na bilo koju željenu visinu.",
            "Za jednu policu koriste se 4 nosača (2 po stranici).",
        ],
    },
    "en": {
        "doc_title":      "Drilling Plan for Workshop",
        "doc_sub":        "KrojnaListaPRO — Generated Workshop Document",
        "edu_title":      "How to Read the Drilling Plan",
        "edu_intro":      (
            "This document shows where the workshop needs to drill holes in each panel."
        ),
        "edu_panels_hdr": "Each unit has its own panels:",
        "edu_panels": [
            "LS  =  left side panel",
            "DS  =  right side panel",
            "DNO  =  bottom panel",
            "VRH  =  top panel",
            "LEDJA  =  back panel",
            "FRONT  =  door / front",
        ],
        "edu_cols_hdr":   "Column meanings:",
        "edu_cols": [
            "X  =  distance of hole from left edge of panel",
            "Y  =  distance of hole from bottom edge of panel",
            "Ø  =  hole diameter",
            "Depth  =  drilling depth",
        ],
        "edu_example_hdr": "Example:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— the hole is drilled 50 mm from the left edge and 9 mm from the bottom edge."
        ),
        "edu_dowel_hdr":   "Dowel fi8:",
        "edu_dowel": (
            "Hole for a wooden dowel with 8 mm diameter. "
            "The dowel ensures panels align precisely and do not slip during assembly."
        ),
        "edu_shelf_hdr":   "Shelf pin fi5:",
        "edu_shelf": (
            "Hole for a shelf pin with 5 mm diameter. "
            "Multiple holes at 32 mm spacing mean the shelf can be adjusted in height."
        ),
        "edu_important_hdr": "Important:",
        "edu_important": (
            "The dowel does not clamp the joint.\n"
            "The dowel only guides the panels.\n"
            "A screw or confirmat clamps the joint."
        ),
        "edu_rule":        "Dowel guides — screw tightens.",
        "tbl_element":    "Element",
        "tbl_zone":       "Zone",
        "tbl_panel":      "Panel",
        "tbl_dims":       "Dim. (mm)",
        "tbl_holes":      "Holes",
        "tbl_purpose":    "Type",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "Ø (mm)",
        "tbl_depth":      "Depth (mm)",
        "tbl_note":       "Note",
        "tbl_no_holes":   "— no holes —",
        "tbl_assembly":   "Assembly instructions",
        "tbl_workshop":   "Workshop notes",
        "tbl_no_modules": "No elements in project.",
        "purpose_hinge":  "Hinge fi35",
        "purpose_dowel":  "Dowel fi8",
        "purpose_shelf":  "Shelf pin fi5",
        "purpose_slide":  "Drawer slide",
        # --- General rules ---
        "gen_rules_title": "General Rules",
        "gen_sys32_title": "32 mm System — Shelf Pins",
        "gen_sys32_text":  (
            "Shelf pin holes are made using the standard 32 mm system "
            "(32 mm spacing between holes). Only the first (lowest) Y position "
            "is shown in the table — all subsequent holes continue every 32 mm from there."
        ),
        "gen_mirror_note":    "⇇  Right side is a mirror of the left side.",
        "gen_shelf_hdr":      "Shelf Pins — 32 mm System",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "First Y (mm)",
        "gen_shelf_count":    "No. holes",
        "gen_shelf_note":     "Remaining holes: every 32 mm from first Y position.",
        # text block for shelf pins (no table)
        "shelf_blk_title":    "Shelf Holes (32 mm System)",
        "shelf_blk_intro":    "Drill shelf pin holes according to the standard 32 mm system.",
        "shelf_blk_raster":   "Hole spacing: 32 mm",
        "shelf_blk_first_y":  "First hole height: Y =",
        "shelf_blk_x_pos":    "X positions:",
        "shelf_blk_outro":    "Holes are drilled along the full panel height at this pitch.",
        "shelf_universal":    (
            "NOTE: Shelf pin holes are made using the standard 32 mm system "
            "and are not listed individually in the table."
        ),
        # --- Important for assembly (professional) ---
        "imp_title":       "IMPORTANT FOR ASSEMBLY",
        "imp_items": [
            "All holes are factory-defined — no additional drilling required.",
            "Dowel is for panel alignment only (does not clamp the joint).",
            "Screw / confirmat clamps the joint.",
            "Shelves can be placed at any desired height (32 mm system).",
            "Check panel orientation: X = distance from left edge, Y = from bottom edge.",
        ],
        # --- Assembly guide (beginner user) ---
        "asm_title":       "Assembly Guide",
        "asm_intro":       "You do not need to drill any holes — all holes are already prepared in the workshop.",
        "asm_steps": [
            "Insert wooden dowels into the prepared holes.",
            "Join the side panels to the bottom panel (dowels act as guides).",
            "Add the top panel (ceiling of the unit).",
            "Align all panels so they sit flush.",
            "Tighten the joints using screws or confirmats.",
            "Attach the back panel.",
            "Insert shelf pins at the desired height.",
            "Place the shelves.",
            "Hang the doors (if any).",
        ],
        "asm_rule_title":  "Golden Rule",
        "asm_rule":        "Dowel guides — screw tightens.",
        "asm_rule_tipl":   "The dowel ensures panels sit exactly right.",
        "asm_rule_sraf":   "The screw locks the joint firmly.",
        "asm_note_title":  "Note",
        "asm_note":        "All hole positions are already defined. No additional measuring required.",
        "asm_shelf_title": "Shelves",
        "asm_shelf": [
            "Shelf holes are made using the 32 mm system.",
            "A shelf can be placed at any desired height.",
            "One shelf requires 4 pins (2 per side).",
        ],
    },
    "de": {
        "doc_title":      "Bohrplan für die Werkstatt",
        "doc_sub":        "KrojnaListaPRO — Generiertes Werkstattdokument",
        "edu_title":      "So liest man den Bohrplan",
        "edu_intro":      (
            "Dieses Dokument zeigt, wo die Werkstatt Bohrungen in jede Platte setzen muss."
        ),
        "edu_panels_hdr": "Jedes Element hat seine eigenen Platten:",
        "edu_panels": [
            "LS  =  linke Seitenplatte",
            "DS  =  rechte Seitenplatte",
            "DNO  =  Boden",
            "VRH  =  Deckel",
            "LEDJA  =  Ruckwand",
            "FRONT  =  Tur / Front",
        ],
        "edu_cols_hdr":   "Spaltenbedeutungen:",
        "edu_cols": [
            "X  =  Abstand der Bohrung vom linken Rand",
            "Y  =  Abstand der Bohrung vom unteren Rand",
            "O  =  Bohrungsdurchmesser",
            "Tiefe  =  Bohrtiefe",
        ],
        "edu_example_hdr": "Beispiel:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— die Bohrung liegt 50 mm vom linken Rand und 9 mm vom unteren Rand."
        ),
        "edu_dowel_hdr":   "Dubel O8:",
        "edu_dowel": (
            "Bohrung fur einen Holzdubel mit 8 mm Durchmesser. "
            "Der Dubel sorgt fur genaue Ausrichtung und verhindert Verrutschen beim Zusammenbau."
        ),
        "edu_shelf_hdr":   "Regaltragerboh. O5:",
        "edu_shelf": (
            "Bohrung fur Regaltrager mit 5 mm Durchmesser. "
            "Viele Locher im 32-mm-Raster bedeuten: Einlegeboden hohenverstellbar."
        ),
        "edu_important_hdr": "Wichtig:",
        "edu_important": (
            "Der Dubel klemmt nicht.\n"
            "Der Dubel fuhrt nur die Platten.\n"
            "Schraube oder Konfirmat klemmt die Verbindung."
        ),
        "edu_rule":        "Dubel fuhrt — Schraube zieht.",
        "tbl_element":    "Element",
        "tbl_zone":       "Zone",
        "tbl_panel":      "Platte",
        "tbl_dims":       "Mase (mm)",
        "tbl_holes":      "Bohrungen",
        "tbl_purpose":    "Typ",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "O (mm)",
        "tbl_depth":      "Tiefe (mm)",
        "tbl_note":       "Hinweis",
        "tbl_no_holes":   "— keine Bohrungen —",
        "tbl_assembly":   "Montageanleitung",
        "tbl_workshop":   "Werkstatthinweise",
        "tbl_no_modules": "Keine Elemente im Projekt.",
        "purpose_hinge":  "Scharnier O35",
        "purpose_dowel":  "Dubel O8",
        "purpose_shelf":  "Regaltrager O5",
        "purpose_slide":  "Schubladenfuhrung",
        # --- Montageanleitung (Anfanger) ---
        "asm_title":       "Montageanleitung",
        "asm_intro":       "Sie mussen keine Locher bohren — alle Bohrungen wurden bereits in der Werkstatt vorbereitet.",
        "asm_steps": [
            "Holzdubel in die vorgesehenen Locher einsetzen.",
            "Seitenteile mit dem Boden verbinden (Dubel dienen als Fuhrung).",
            "Deckelplatte aufsetzen (obere Abschlussplatte).",
            "Alle Platten ausrichten und bundig ausrichten.",
            "Verbindungen mit Schrauben oder Konfirmat festziehen.",
            "Ruckwand einsetzen.",
            "Regaltrager auf die gewunschte Hohe einsetzen.",
            "Einlegebodem einlegen.",
            "Turen montieren (falls vorhanden).",
        ],
        "asm_rule_title":  "Die goldene Regel",
        "asm_rule":        "Dubel fuhrt — Schraube zieht.",
        "asm_rule_tipl":   "Der Dubel sorgt dafur, dass die Platten genau sitzen.",
        "asm_rule_sraf":   "Die Schraube sichert die Verbindung.",
        "asm_note_title":  "Hinweis",
        "asm_note":        "Alle Bohrungspositionen sind bereits festgelegt. Kein zusatzliches Messen erforderlich.",
        "asm_shelf_title": "Einlegebodem",
        "asm_shelf": [
            "Bohrungen fur Einlegebodem sind im 32-mm-Raster ausgefuhrt.",
            "Der Einlegeboden kann auf beliebige Hohe eingestellt werden.",
            "Fur einen Einlegeboden werden 4 Trager benotigt (2 je Seite).",
        ],
        # --- Allgemeine Regeln ---
        "gen_rules_title": "Allgemeine Regeln",
        "gen_sys32_title": "32-mm-System — Regaltrager",
        "gen_sys32_text":  (
            "Regaltrager-Bohrungen sind nach dem 32-mm-Standard ausgefuhrt "
            "(32 mm Abstand zwischen den Bohrungen). In der Tabelle wird nur die "
            "erste (unterste) Y-Position angezeigt — alle weiteren Bohrungen folgen alle 32 mm."
        ),
        "gen_mirror_note":    "⇇  Rechte Seitenplatte ist ein Spiegel der linken.",
        "gen_shelf_hdr":      "Regaltrager — 32-mm-System",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Erste Y (mm)",
        "gen_shelf_count":    "Anz. Bohr.",
        "gen_shelf_note":     "Weitere Bohrungen: alle 32 mm von der ersten Y-Position.",
        # Textblock fur Regaltrager
        "shelf_blk_title":    "Regalbohrungen (32-mm-System)",
        "shelf_blk_intro":    "Regaltrager-Bohrungen nach dem 32-mm-Standard setzen.",
        "shelf_blk_raster":   "Bohrungsabstand: 32 mm",
        "shelf_blk_first_y":  "Erste Bohrung ab Boden: Y =",
        "shelf_blk_x_pos":    "X-Positionen:",
        "shelf_blk_outro":    "Bohrungen werden in diesem Raster uber die gesamte Plattenhohe gesetzt.",
        "shelf_universal":    (
            "HINWEIS: Regaltrager-Bohrungen sind nach dem 32-mm-System gefertigt "
            "und werden nicht einzeln in der Tabelle aufgefuhrt."
        ),
        # --- Wichtig fur die Montage ---
        "imp_title":       "WICHTIG FUR DIE MONTAGE",
        "imp_items": [
            "Alle Bohrungen sind werkseitig definiert — kein zusatzliches Bohren.",
            "Dubel dient nur zur Ausrichtung (klemmt nicht).",
            "Schraube / Konfirmat klemmt das Element.",
            "Einlegebodem konnen auf beliebige Hohe eingestellt werden (32-mm-System).",
            "Plattenorientierung beachten: X = von links, Y = vom Boden.",
        ],
    },
    "es": {
        "doc_title":      "Plan de Taladrado para el Taller",
        "doc_sub":        "KrojnaListaPRO — Documento de Taller Generado",
        "edu_title":      "Como leer el plan de taladrado",
        "edu_intro":      (
            "Este documento indica donde el taller debe taladrar los agujeros en cada panel."
        ),
        "edu_panels_hdr": "Cada modulo tiene sus propios paneles:",
        "edu_panels": [
            "LS  =  panel lateral izquierdo",
            "DS  =  panel lateral derecho",
            "DNO  =  panel de fondo",
            "VRH  =  panel superior / techo",
            "LEDJA  =  panel trasero",
            "FRONT  =  puerta / frente",
        ],
        "edu_cols_hdr":   "Significado de las columnas:",
        "edu_cols": [
            "X  =  distancia del agujero al borde izquierdo del panel",
            "Y  =  distancia del agujero al borde inferior del panel",
            "O  =  diametro del agujero",
            "Profundidad  =  profundidad de taladrado",
        ],
        "edu_example_hdr": "Ejemplo:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— el agujero se taladra a 50 mm del borde izquierdo y 9 mm del borde inferior."
        ),
        "edu_dowel_hdr":   "Clavija fi8:",
        "edu_dowel": (
            "Agujero para clavija de madera de 8 mm de diametro. "
            "La clavija alinea los paneles con precision e impide el desplazamiento durante el montaje."
        ),
        "edu_shelf_hdr":   "Soporte de balda fi5:",
        "edu_shelf": (
            "Agujero para soporte de balda de 5 mm de diametro. "
            "Muchos agujeros a 32 mm de separacion indican que la balda es regulable en altura."
        ),
        "edu_important_hdr": "Importante:",
        "edu_important": (
            "La clavija no aprieta la union.\n"
            "La clavija solo guia los paneles.\n"
            "El tornillo o confirmat aprieta la union."
        ),
        "edu_rule":        "La clavija guia — el tornillo aprieta.",
        "tbl_element":    "Elemento",
        "tbl_zone":       "Zona",
        "tbl_panel":      "Panel",
        "tbl_dims":       "Dim. (mm)",
        "tbl_holes":      "Agujeros",
        "tbl_purpose":    "Tipo",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "O (mm)",
        "tbl_depth":      "Profundidad (mm)",
        "tbl_note":       "Nota",
        "tbl_no_holes":   "— sin agujeros —",
        "tbl_assembly":   "Instrucciones de montaje",
        "tbl_workshop":   "Notas para el taller",
        "tbl_no_modules": "No hay elementos en el proyecto.",
        "purpose_hinge":  "Bisagra fi35",
        "purpose_dowel":  "Clavija fi8",
        "purpose_shelf":  "Soporte balda fi5",
        "purpose_slide":  "Corredera cajon",
        # --- Guia de montaje (principiante) ---
        "asm_title":       "Guia de montaje",
        "asm_intro":       "No necesita taladrar ningun agujero — todos los agujeros ya estan preparados en el taller.",
        "asm_steps": [
            "Insertar las clavijas de madera en los agujeros preparados.",
            "Unir los laterales al panel de fondo (las clavijas actuan como guias).",
            "Anadir el panel superior (techo del modulo).",
            "Alinear todos los paneles para que encajen bien.",
            "Apretar las uniones con tornillos o confirmats.",
            "Colocar el panel trasero.",
            "Insertar los soportes de balda a la altura deseada.",
            "Colocar las baldas.",
            "Montar las puertas (si las hay).",
        ],
        "asm_rule_title":  "Regla de oro",
        "asm_rule":        "La clavija guia — el tornillo aprieta.",
        "asm_rule_tipl":   "La clavija garantiza que los paneles encajen con precision.",
        "asm_rule_sraf":   "El tornillo asegura la union firmemente.",
        "asm_note_title":  "Nota",
        "asm_note":        "Todas las posiciones de los agujeros ya estan definidas. No se necesita medicion adicional.",
        "asm_shelf_title": "Baldas",
        "asm_shelf": [
            "Los agujeros para baldas siguen el sistema de 32 mm.",
            "La balda puede colocarse a cualquier altura deseada.",
            "Para una balda se necesitan 4 soportes (2 por lado).",
        ],
        # --- Reglas generales ---
        "gen_rules_title": "Reglas generales",
        "gen_sys32_title": "Sistema 32 mm — soportes de balda",
        "gen_sys32_text":  (
            "Los agujeros para soportes de balda se realizan con el sistema estandar de 32 mm "
            "(32 mm entre agujeros). En la tabla solo se muestra la primera (mas baja) "
            "posicion Y — los restantes continuan cada 32 mm."
        ),
        "gen_mirror_note":    "⇇  El panel derecho es el espejo del izquierdo.",
        "gen_shelf_hdr":      "Soportes de balda — sistema 32 mm",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Primera Y (mm)",
        "gen_shelf_count":    "Num. agujeros",
        "gen_shelf_note":     "Agujeros restantes: cada 32 mm desde la primera posicion Y.",
        # bloque de texto para baldas
        "shelf_blk_title":    "Agujeros de baldas (sistema 32 mm)",
        "shelf_blk_intro":    "Taladrar agujeros para soportes de balda segun el sistema estandar de 32 mm.",
        "shelf_blk_raster":   "Espaciado entre agujeros: 32 mm",
        "shelf_blk_first_y":  "Altura del primer agujero: Y =",
        "shelf_blk_x_pos":    "Posiciones X:",
        "shelf_blk_outro":    "Los agujeros se taladran en toda la altura del panel con este paso.",
        "shelf_universal":    (
            "NOTA: Los agujeros para baldas se realizan con el sistema de 32 mm "
            "y no se listan individualmente en la tabla."
        ),
        # --- Importante para el montaje ---
        "imp_title":       "IMPORTANTE PARA EL MONTAJE",
        "imp_items": [
            "Todos los agujeros estan definidos de fabrica — no se requiere taladrado adicional.",
            "La clavija sirve solo para alinear los paneles (no aprieta).",
            "El tornillo / confirmat aprieta el elemento.",
            "Las baldas pueden colocarse a cualquier altura (sistema 32 mm).",
            "Verificar orientacion: X = borde izquierdo, Y = borde inferior.",
        ],
    },
    "fr": {
        "doc_title":      "Plan de percage pour l'atelier",
        "doc_sub":        "KrojnaListaPRO — Document d'atelier genere",
        "edu_title":      "Comment lire le plan de percage",
        "edu_intro":      (
            "Ce document indique ou l'atelier doit percer les trous dans chaque panneau."
        ),
        "edu_panels_hdr": "Chaque element a ses propres panneaux :",
        "edu_panels": [
            "LS  =  cote gauche",
            "DS  =  cote droit",
            "DNO  =  fond de caisson",
            "VRH  =  panneau superieur / plafond",
            "LEDJA  =  fond arriere",
            "FRONT  =  porte / facade",
        ],
        "edu_cols_hdr":   "Signification des colonnes :",
        "edu_cols": [
            "X  =  distance du trou au bord gauche du panneau",
            "Y  =  distance du trou au bord inferieur du panneau",
            "O  =  diametre du trou",
            "Profondeur  =  profondeur de percage",
        ],
        "edu_example_hdr": "Exemple :",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— le trou est perce a 50 mm du bord gauche et 9 mm du bord inferieur."
        ),
        "edu_dowel_hdr":   "Cheville fi8 :",
        "edu_dowel": (
            "Trou pour cheville en bois de 8 mm de diametre. "
            "La cheville assure l'alignement precis et empeche le glissement lors de l'assemblage."
        ),
        "edu_shelf_hdr":   "Tasseau d'etagere fi5 :",
        "edu_shelf": (
            "Trou pour tasseau d'etagere de 5 mm de diametre. "
            "De nombreux trous espaces de 32 mm signifient que l'etagere est reglable en hauteur."
        ),
        "edu_important_hdr": "Important :",
        "edu_important": (
            "La cheville ne serre pas l'assemblage.\n"
            "La cheville guide seulement les panneaux.\n"
            "La vis ou le confirmat serre l'assemblage."
        ),
        "edu_rule":        "La cheville guide — la vis serre.",
        "tbl_element":    "Element",
        "tbl_zone":       "Zone",
        "tbl_panel":      "Panneau",
        "tbl_dims":       "Dim. (mm)",
        "tbl_holes":      "Percages",
        "tbl_purpose":    "Type",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "O (mm)",
        "tbl_depth":      "Profondeur (mm)",
        "tbl_note":       "Note",
        "tbl_no_holes":   "— sans percages —",
        "tbl_assembly":   "Instructions de montage",
        "tbl_workshop":   "Notes pour l'atelier",
        "tbl_no_modules": "Aucun element dans le projet.",
        "purpose_hinge":  "Charniere fi35",
        "purpose_dowel":  "Cheville fi8",
        "purpose_shelf":  "Tasseau fi5",
        "purpose_slide":  "Coulisse tiroir",
        # --- Guide de montage (debutant) ---
        "asm_title":       "Guide de montage",
        "asm_intro":       "Vous n'avez pas besoin de percer — tous les trous sont deja prepares en atelier.",
        "asm_steps": [
            "Inserer les chevilles en bois dans les trous prevus.",
            "Assembler les cotes avec le fond du caisson (les chevilles servent de guide).",
            "Poser le panneau superieur (dessus / plafond du caisson).",
            "Aligner tous les panneaux pour qu'ils s'emboitent correctement.",
            "Serrer les assemblages avec des vis ou des confirmats.",
            "Fixer le fond arriere.",
            "Inserer les tasseaux d'etagere a la hauteur souhaitee.",
            "Poser les etageres.",
            "Monter les portes (si necessaire).",
        ],
        "asm_rule_title":  "Regle d'or",
        "asm_rule":        "La cheville guide — la vis serre.",
        "asm_rule_tipl":   "La cheville assure l'alignement precis des panneaux.",
        "asm_rule_sraf":   "La vis verrouille l'assemblage.",
        "asm_note_title":  "Note",
        "asm_note":        "Toutes les positions de percage sont deja definies. Aucune mesure supplementaire n'est requise.",
        "asm_shelf_title": "Etageres",
        "asm_shelf": [
            "Les trous pour etageres suivent le systeme a 32 mm.",
            "L'etagere peut etre placee a n'importe quelle hauteur souhaitee.",
            "Une etagere necessite 4 tasseaux (2 par cote).",
        ],
        # --- Regles generales ---
        "gen_rules_title": "Regles generales",
        "gen_sys32_title": "Systeme 32 mm — tasseaux d'etagere",
        "gen_sys32_text":  (
            "Les trous de tasseaux sont realises selon le systeme standard 32 mm "
            "(espacement 32 mm entre chaque trou). Seule la premiere (plus basse) "
            "position Y est indiquee dans le tableau — tous les trous suivants "
            "continuent tous les 32 mm."
        ),
        "gen_mirror_note":    "⇇  Le cote droit est le miroir du cote gauche.",
        "gen_shelf_hdr":      "Tasseaux d'etagere — systeme 32 mm",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Premiere Y (mm)",
        "gen_shelf_count":    "Nb trous",
        "gen_shelf_note":     "Trous suivants : tous les 32 mm depuis la premiere position Y.",
        # bloc de texte pour etageres
        "shelf_blk_title":    "Trous d'etageres (systeme 32 mm)",
        "shelf_blk_intro":    "Percer les trous de tasseaux selon le systeme standard 32 mm.",
        "shelf_blk_raster":   "Espacement entre trous : 32 mm",
        "shelf_blk_first_y":  "Hauteur du premier trou : Y =",
        "shelf_blk_x_pos":    "Positions X :",
        "shelf_blk_outro":    "Les trous sont perces sur toute la hauteur du panneau a ce pas.",
        "shelf_universal":    (
            "NOTE : Les trous de tasseaux sont realises selon le systeme 32 mm "
            "et ne sont pas listes individuellement dans le tableau."
        ),
        # --- Important pour le montage ---
        "imp_title":       "IMPORTANT POUR LE MONTAGE",
        "imp_items": [
            "Tous les trous sont definis en usine — aucun percage supplementaire.",
            "La cheville sert uniquement a l'alignement des panneaux (ne serre pas).",
            "La vis / le confirmat serre l'assemblage.",
            "Les etageres peuvent etre placees a la hauteur souhaitee (systeme 32 mm).",
            "Respecter l'orientation : X = bord gauche, Y = bord inferieur.",
        ],
    },
    "pt-br": {
        "doc_title":      "Plano de Furacao para a Marcenaria",
        "doc_sub":        "KrojnaListaPRO — Documento de Marcenaria Gerado",
        "edu_title":      "Como ler o plano de furacao",
        "edu_intro":      (
            "Este documento indica onde a marcenaria deve furar cada peca."
        ),
        "edu_panels_hdr": "Cada modulo tem suas proprias pecas:",
        "edu_panels": [
            "LS  =  lateral esquerda",
            "DS  =  lateral direita",
            "DNO  =  fundo",
            "VRH  =  topo",
            "LEDJA  =  fundo traseiro",
            "FRONT  =  porta / frente",
        ],
        "edu_cols_hdr":   "Significado das colunas:",
        "edu_cols": [
            "X  =  distancia do furo a borda esquerda da peca",
            "Y  =  distancia do furo a borda inferior da peca",
            "O  =  diametro do furo",
            "Profundidade  =  profundidade da furacao",
        ],
        "edu_example_hdr": "Exemplo:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— o furo e feito a 50 mm da borda esquerda e 9 mm da borda inferior."
        ),
        "edu_dowel_hdr":   "Cavilha fi8:",
        "edu_dowel": (
            "Furo para cavilha de madeira de 8 mm de diametro. "
            "A cavilha garante alinhamento preciso e evita deslocamento durante a montagem."
        ),
        "edu_shelf_hdr":   "Suporte de prateleira fi5:",
        "edu_shelf": (
            "Furo para suporte de prateleira de 5 mm de diametro. "
            "Muitos furos a cada 32 mm significam que a prateleira e regulavel em altura."
        ),
        "edu_important_hdr": "Importante:",
        "edu_important": (
            "A cavilha nao aperta a juncao.\n"
            "A cavilha apenas guia as pecas.\n"
            "O parafuso ou confirmat aperta a juncao."
        ),
        "edu_rule":        "A cavilha guia — o parafuso aperta.",
        "tbl_element":    "Modulo",
        "tbl_zone":       "Zona",
        "tbl_panel":      "Peca",
        "tbl_dims":       "Dim. (mm)",
        "tbl_holes":      "Furos",
        "tbl_purpose":    "Tipo",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "O (mm)",
        "tbl_depth":      "Prof. (mm)",
        "tbl_note":       "Nota",
        "tbl_no_holes":   "— sem furos —",
        "tbl_assembly":   "Instrucoes de montagem",
        "tbl_workshop":   "Notas para a marcenaria",
        "tbl_no_modules": "Nenhum elemento no projeto.",
        "purpose_hinge":  "Dobradura fi35",
        "purpose_dowel":  "Cavilha fi8",
        "purpose_shelf":  "Suporte prateleira fi5",
        "purpose_slide":  "Corredicao gaveta",
        # --- Guia de montagem (iniciante) ---
        "asm_title":       "Guia de montagem",
        "asm_intro":       "Voce nao precisa furar nada — todos os furos ja foram preparados na marcenaria.",
        "asm_steps": [
            "Inserir as cavilhas de madeira nos furos preparados.",
            "Unir as laterais ao fundo (as cavilhas servem de guia).",
            "Adicionar o painel superior (tampo do modulo).",
            "Alinhar todos os paineis para assentarem corretamente.",
            "Apertar as unioes com parafusos ou confirmats.",
            "Fixar o fundo traseiro.",
            "Inserir os suportes de prateleira na altura desejada.",
            "Colocar as prateleiras.",
            "Montar as portas (se houver).",
        ],
        "asm_rule_title":  "Regra de ouro",
        "asm_rule":        "A cavilha guia — o parafuso aperta.",
        "asm_rule_tipl":   "A cavilha garante que as pecas se encaixem corretamente.",
        "asm_rule_sraf":   "O parafuso trava a uniao com firmeza.",
        "asm_note_title":  "Nota",
        "asm_note":        "Todas as posicoes dos furos ja estao definidas. Nenhuma medicao adicional e necessaria.",
        "asm_shelf_title": "Prateleiras",
        "asm_shelf": [
            "Os furos para prateleiras seguem o sistema de 32 mm.",
            "A prateleira pode ser colocada em qualquer altura desejada.",
            "Uma prateleira requer 4 suportes (2 por lado).",
        ],
        # --- Regras gerais ---
        "gen_rules_title": "Regras gerais",
        "gen_sys32_title": "Sistema 32 mm — suportes de prateleira",
        "gen_sys32_text":  (
            "Os furos para suportes de prateleira sao feitos com o sistema padrao de 32 mm "
            "(32 mm entre furos). Na tabela e mostrada apenas a primeira (mais baixa) "
            "posicao Y — todos os furos seguintes continuam a cada 32 mm."
        ),
        "gen_mirror_note":    "⇇  O painel direito e espelho do painel esquerdo.",
        "gen_shelf_hdr":      "Suportes de prateleira — sistema 32 mm",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Primeira Y (mm)",
        "gen_shelf_count":    "Num. furos",
        "gen_shelf_note":     "Furos restantes: a cada 32 mm da primeira posicao Y.",
        # bloco de texto para prateleiras
        "shelf_blk_title":    "Furos de prateleira (sistema 32 mm)",
        "shelf_blk_intro":    "Furar suportes de prateleira conforme o sistema padrao de 32 mm.",
        "shelf_blk_raster":   "Espacamento entre furos: 32 mm",
        "shelf_blk_first_y":  "Altura do primeiro furo: Y =",
        "shelf_blk_x_pos":    "Posicoes X:",
        "shelf_blk_outro":    "Os furos sao feitos em toda a altura da peca neste passo.",
        "shelf_universal":    (
            "NOTA: Os furos de prateleira sao feitos com o sistema de 32 mm "
            "e nao sao listados individualmente na tabela."
        ),
        # --- Importante para a montagem ---
        "imp_title":       "IMPORTANTE PARA A MONTAGEM",
        "imp_items": [
            "Todos os furos sao definidos em fabrica — nenhuma furacao adicional.",
            "A cavilha serve apenas para alinhar as pecas (nao aperta).",
            "O parafuso / confirmat aperta o elemento.",
            "As prateleiras podem ser colocadas em qualquer altura (sistema 32 mm).",
            "Verificar orientacao: X = borda esquerda, Y = borda inferior.",
        ],
    },
    "ru": {
        "doc_title":      "Plan sverlovki dlja masterskoj",
        "doc_sub":        "KrojnaListaPRO — Sgenerirovannyi dokument masterskoj",
        "edu_title":      "Kak chitat plan sverlovki",
        "edu_intro":      (
            "Etot dokument pokazyvaet, gde masterska dolzhna sveryat otverstija v kazhdoj plite."
        ),
        "edu_panels_hdr": "Kazhdyj element imeet svoi plity:",
        "edu_panels": [
            "LS  =  levaja stjenka",
            "DS  =  pravaja stjenka",
            "DNO  =  dno",
            "VRH  =  kryshka",
            "LEDJA  =  zadnjaja stjenka",
            "FRONT  =  dver / fasad",
        ],
        "edu_cols_hdr":   "Znachenie stolbtsov:",
        "edu_cols": [
            "X  =  rasstojanije otverstija ot levogo kraja plity",
            "Y  =  rasstojanije otverstija ot nizhnego kraja plity",
            "O  =  diametr otverstija",
            "Glubina  =  glubina sverlenija",
        ],
        "edu_example_hdr": "Primer:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— otverstije sveryat v 50 mm ot levogo kraja i 9 mm ot nizhnego kraja."
        ),
        "edu_dowel_hdr":   "Shpon fi8:",
        "edu_dowel": (
            "Otverstije dlja derevjannogo shpona diametrom 8 mm. "
            "Shpon obespechivajet tochnoye sovmeshchenije plit pri sborke."
        ),
        "edu_shelf_hdr":   "Polkoderzhatель fi5:",
        "edu_shelf": (
            "Otverstije dlja polkoderzhatelja diametrom 5 mm. "
            "Mnogo otverstij cherez 32 mm oznachajet regulirujemuju polku."
        ),
        "edu_important_hdr": "Vazhno:",
        "edu_important": (
            "Shpon ne stjagivajet sojedinjenije.\n"
            "Shpon toljko napravljajet plity.\n"
            "Vint ili konfirmat stjagivajet sojedinjenije."
        ),
        "edu_rule":        "Shpon napravljajet — vint stjagivajet.",
        "tbl_element":    "Element",
        "tbl_zone":       "Zona",
        "tbl_panel":      "Plita",
        "tbl_dims":       "Razm. (mm)",
        "tbl_holes":      "Otverstija",
        "tbl_purpose":    "Tip",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "O (mm)",
        "tbl_depth":      "Glubina (mm)",
        "tbl_note":       "Primechanije",
        "tbl_no_holes":   "— bez otverstij —",
        "tbl_assembly":   "Instrukcija po sborke",
        "tbl_workshop":   "Zamechanija dlja masterskoj",
        "tbl_no_modules": "Net elementov v proekte.",
        "purpose_hinge":  "Petlja fi35",
        "purpose_dowel":  "Shpon fi8",
        "purpose_shelf":  "Polkoderzhatель fi5",
        "purpose_slide":  "Napr. yashchika",
        # --- Rukovodstvo po sborke (nachinayushchij) ---
        "asm_title":       "Rukovodstvo po sborke",
        "asm_intro":       "Vam ne nuzhno sveryat otverstija — vse otverstija uzhe podgotovleny v masterskoj.",
        "asm_steps": [
            "Vstavit derevjannyje shpony v podgotovlennyje otverstija.",
            "Sojedinit bokoviny s dnom (shpony sluzhath kak napravljajushchije).",
            "Dobavit verkhnuyu panel (kryshku elementa).",
            "Vyrovnjat vse paneli, chtoby oni horosho legli.",
            "Zatjanut sojedinenija s pomoshchyu vintov ili konfirmata.",
            "Ustanovit zadnyuyu stenku.",
            "Vstavit polkoderzhatelja na zhelajemuyu vysotu.",
            "Ustanovit polki.",
            "Prikrepit dveri (pri nalichii).",
        ],
        "asm_rule_title":  "Zolotoje pravilo",
        "asm_rule":        "Shpon napravljajet — vint stjagivajet.",
        "asm_rule_tipl":   "Shpon obespechivajet tochnoye sojedinjenije plit.",
        "asm_rule_sraf":   "Vint nadezhno fiksirujet sojedinjenije.",
        "asm_note_title":  "Primechanije",
        "asm_note":        "Vse pozicii otverstij uzhe opredeleny. Dopolnitelnych izmerenij ne trebuetsja.",
        "asm_shelf_title": "Polki",
        "asm_shelf": [
            "Otverstija dlja polok vypolneny po sisteme 32 mm.",
            "Polku mozhno ustanovit na lyubuyu zhelajemuyu vysotu.",
            "Dlya odnoj polki ispolzujutsja 4 derzhatelja (2 s kazhdoj storony).",
        ],
        # --- Obshhije pravila ---
        "gen_rules_title": "Obshhije pravila",
        "gen_sys32_title": "Sistema 32 mm — polkoderzhatelja",
        "gen_sys32_text":  (
            "Otverstija dlja polkoderzhatelej vypolneny po standartnoi sisteme 32 mm "
            "(rasstojanije 32 mm mezhdu otverstijami). V tablice pokazyvajetsja tolko "
            "pervaja (nizhnjaja) Y pozicija — ostalnyje otverstija kazhdyje 32 mm."
        ),
        "gen_mirror_note":    "⇇  Pravaja stjenka javljajetsja zerkalom levoj.",
        "gen_shelf_hdr":      "Polkoderzhatelja — sistema 32 mm",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "Pervaja Y (mm)",
        "gen_shelf_count":    "Kol-vo otv.",
        "gen_shelf_note":     "Ostalnyje otverstija: kazhdyje 32 mm ot pervoj Y pozicii.",
        # Tekstovyi blok dlja polok
        "shelf_blk_title":    "Otverstija dlja polok (sistema 32 mm)",
        "shelf_blk_intro":    "Sverlit otverstija dlja polkoderzhatelej po sisteme 32 mm.",
        "shelf_blk_raster":   "Rasstojanije mezhdu otverstijami: 32 mm",
        "shelf_blk_first_y":  "Vysota pervogo otverstija: Y =",
        "shelf_blk_x_pos":    "X pozicii:",
        "shelf_blk_outro":    "Otverstija sveryatsja po vsej vysote plity v etom rastere.",
        "shelf_universal":    (
            "PRIMECHANIJE: Otverstija dlja polok vypolneny po sisteme 32 mm "
            "i ne pokazyvajutsja poodinochno v tablice."
        ),
        # --- Vazhno dlja sborki ---
        "imp_title":       "VAZHNO DLJA SBORKI",
        "imp_items": [
            "Vse otverstija zavodski opredeleny — dopolnitelnoje sverljenije ne trebuetsja.",
            "Shpon sluzhit tolko dlja vyravnivanija plit (ne stjagivajet).",
            "Vint / konfirmat stjagivajet sojedinjenije.",
            "Polki mozhno stavit na lyubuyu vysotu (sistema 32 mm).",
            "Sledit za oriyentaciyej: X = ot levogo kraja, Y = ot nizhnego kraja.",
        ],
    },
    "zh-cn": {
        "doc_title":      "钻孔计划（车间用）",
        "doc_sub":        "KrojnaListaPRO — 生成的车间文件",
        "edu_title":      "如何阅读钻孔计划",
        "edu_intro":      "本文件显示车间需要在每块板上打孔的位置。",
        "edu_panels_hdr": "每个柜体包含以下板件：",
        "edu_panels": [
            "LS  =  左侧板",
            "DS  =  右侧板",
            "DNO  =  底板",
            "VRH  =  顶板",
            "LEDJA  =  背板",
            "FRONT  =  门板 / 正面",
        ],
        "edu_cols_hdr":   "列含义：",
        "edu_cols": [
            "X  =  孔距板件左边缘的距离",
            "Y  =  孔距板件下边缘的距离",
            "Ø  =  孔径",
            "深度  =  钻孔深度",
        ],
        "edu_example_hdr": "示例：",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— 孔位于距左边缘50mm、距下边缘9mm处。"
        ),
        "edu_dowel_hdr":   "木榫 Ø8：",
        "edu_dowel": (
            "用于直径8mm木榫的孔。"
            "木榫确保板件精确对齐，防止组装时移位。"
        ),
        "edu_shelf_hdr":   "层板销 Ø5：",
        "edu_shelf": (
            "用于直径5mm层板销的孔。"
            "多个32mm间距的孔表示层板高度可调节。"
        ),
        "edu_important_hdr": "重要：",
        "edu_important": (
            "木榫不夹紧接合处。\n"
            "木榫仅用于引导板件。\n"
            "螺丝或确认钉夹紧接合处。"
        ),
        "edu_rule":        "木榫引导 — 螺丝紧固。",
        "tbl_element":    "元素",
        "tbl_zone":       "区域",
        "tbl_panel":      "板件",
        "tbl_dims":       "尺寸 (mm)",
        "tbl_holes":      "钻孔",
        "tbl_purpose":    "类型",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "Ø (mm)",
        "tbl_depth":      "深度 (mm)",
        "tbl_note":       "备注",
        "tbl_no_holes":   "— 无钻孔 —",
        "tbl_assembly":   "组装说明",
        "tbl_workshop":   "车间备注",
        "tbl_no_modules": "项目中没有元素。",
        "purpose_hinge":  "铰链 Ø35",
        "purpose_dowel":  "木榫 Ø8",
        "purpose_shelf":  "层板销 Ø5",
        "purpose_slide":  "抽屉滑轨",
        # --- 组装指南 ---
        "asm_title":       "组装指南",
        "asm_intro":       "您无需自行打孔 — 所有孔位已在工厂预先制作完毕。",
        "asm_steps": [
            "将木榫插入预制孔中。",
            "将侧板与底板连接（木榫起导向作用）。",
            "安装顶板（柜体顶部）。",
            "对齐所有板件使其平整贴合。",
            "用螺丝或确认钉紧固接合处。",
            "安装背板。",
            "将层板销插入所需高度位置。",
            "放置层板。",
            "安装柜门（如有）。",
        ],
        "asm_rule_title":  "黄金法则",
        "asm_rule":        "木榫引导 — 螺丝紧固。",
        "asm_rule_tipl":   "木榫确保板件精确对齐。",
        "asm_rule_sraf":   "螺丝将接合处牢固锁定。",
        "asm_note_title":  "说明",
        "asm_note":        "所有孔位已预先确定。无需额外测量。",
        "asm_shelf_title": "层板",
        "asm_shelf": [
            "层板孔采用32mm系统制作。",
            "层板可安装在任意所需高度。",
            "一块层板需要4个支撑销（每侧2个）。",
        ],
        # --- 通用规则 ---
        "gen_rules_title": "通用规则",
        "gen_sys32_title": "32 mm 系统 — 层板销",
        "gen_sys32_text":  (
            "层板销孔按标准32 mm系统加工（孔间距32 mm）。"
            "表格中只显示第一个（最低的）Y位置——所有后续孔每隔32 mm排列。"
        ),
        "gen_mirror_note":    "⇇  右侧板是左侧板的镜像。",
        "gen_shelf_hdr":      "层板销 — 32 mm 系统",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "首个 Y (mm)",
        "gen_shelf_count":    "孔数",
        "gen_shelf_note":     "其余孔：从第一个Y位置起每隔32 mm一个。",
        # 层板文本块
        "shelf_blk_title":    "层板孔（32 mm 系统）",
        "shelf_blk_intro":    "按标准32 mm系统钻层板销孔。",
        "shelf_blk_raster":   "孔间距：32 mm",
        "shelf_blk_first_y":  "第一个孔距底部：Y =",
        "shelf_blk_x_pos":    "X 位置：",
        "shelf_blk_outro":    "按此间距在板件全高范围内钻孔。",
        "shelf_universal":    (
            "注意：层板销孔按32 mm系统加工，不在表格中单独列出。"
        ),
        # --- 组装注意事项 ---
        "imp_title":       "组装注意事项",
        "imp_items": [
            "所有孔位均已在工厂定义——无需额外钻孔。",
            "木榫仅用于板件对齐（不夹紧接合处）。",
            "螺丝或确认钉夹紧接合处。",
            "层板可安装在任意所需高度（32 mm系统）。",
            "注意板件方向：X = 距左边缘，Y = 距下边缘。",
        ],
    },
    "hi": {
        "doc_title":      "वर्कशॉप ड्रिलिंग प्लान",
        "doc_sub":        "KrojnaListaPRO — उत्पन्न वर्कशॉप दस्तावेज़",
        "edu_title":      "ड्रिलिंग प्लान कैसे पढ़ें",
        "edu_intro":      "यह दस्तावेज़ दिखाता है कि वर्कशॉप को प्रत्येक पैनल में छेद कहाँ करने हैं।",
        "edu_panels_hdr": "प्रत्येक यूनिट के अपने पैनल होते हैं:",
        "edu_panels": [
            "LS  =  बायाँ साइड पैनल",
            "DS  =  दायाँ साइड पैनल",
            "DNO  =  नीचे का पैनल",
            "VRH  =  ऊपर का पैनल",
            "LEDJA  =  पीछे का पैनल",
            "FRONT  =  दरवाज़ा / फ्रंट",
        ],
        "edu_cols_hdr":   "कॉलम का अर्थ:",
        "edu_cols": [
            "X  =  पैनल के बाएँ किनारे से छेद की दूरी",
            "Y  =  पैनल के निचले किनारे से छेद की दूरी",
            "Ø  =  छेद का व्यास",
            "गहराई  =  ड्रिलिंग की गहराई",
        ],
        "edu_example_hdr": "उदाहरण:",
        "edu_example": (
            "X = 50 mm,  Y = 9 mm\n"
            "— छेद बाएँ किनारे से 50mm और निचले किनारे से 9mm पर किया जाता है।"
        ),
        "edu_dowel_hdr":   "डॉवेल fi8:",
        "edu_dowel": (
            "8mm व्यास की लकड़ी की डॉवेल के लिए छेद। "
            "डॉवेल पैनलों को सटीक रूप से संरेखित करता है।"
        ),
        "edu_shelf_hdr":   "शेल्फ पिन fi5:",
        "edu_shelf": (
            "5mm व्यास के शेल्फ पिन के लिए छेद। "
            "32mm की दूरी पर कई छेद — शेल्फ की ऊँचाई समायोज्य है।"
        ),
        "edu_important_hdr": "महत्वपूर्ण:",
        "edu_important": (
            "डॉवेल जोड़ को नहीं कसता।\n"
            "डॉवेल केवल पैनलों को गाइड करता है।\n"
            "स्क्रू या कन्फर्मेट जोड़ को कसता है।"
        ),
        "edu_rule":        "डॉवेल गाइड करता है — स्क्रू कसता है।",
        "tbl_element":    "तत्व",
        "tbl_zone":       "ज़ोन",
        "tbl_panel":      "पैनल",
        "tbl_dims":       "आयाम (mm)",
        "tbl_holes":      "छेद",
        "tbl_purpose":    "प्रकार",
        "tbl_x":          "X (mm)",
        "tbl_y":          "Y (mm)",
        "tbl_dia":        "Ø (mm)",
        "tbl_depth":      "गहराई (mm)",
        "tbl_note":       "नोट",
        "tbl_no_holes":   "— कोई छेद नहीं —",
        "tbl_assembly":   "असेंबली निर्देश",
        "tbl_workshop":   "वर्कशॉप नोट्स",
        "tbl_no_modules": "प्रोजेक्ट में कोई तत्व नहीं।",
        "purpose_hinge":  "हिंज fi35",
        "purpose_dowel":  "डॉवेल fi8",
        "purpose_shelf":  "शेल्फ पिन fi5",
        "purpose_slide":  "ड्रॉअर स्लाइड",
        # --- असेंबली गाइड (शुरुआती) ---
        "asm_title":       "असेंबली गाइड",
        "asm_intro":       "आपको कोई छेद ड्रिल करने की जरूरत नहीं — सभी छेद पहले से वर्कशॉप में तैयार हैं।",
        "asm_steps": [
            "लकड़ी के डॉवेल को तैयार छेदों में डालें।",
            "बगल के पैनलों को नीचे के पैनल से जोड़ें (डॉवेल गाइड की तरह काम करते हैं)।",
            "ऊपरी पैनल (यूनिट की छत) लगाएं।",
            "सभी पैनलों को ठीक से संरेखित करें।",
            "स्क्रू या कन्फर्मेट से जोड़ों को कसें।",
            "पीछे का पैनल लगाएं।",
            "शेल्फ पिन को वांछित ऊंचाई पर डालें।",
            "शेल्फ रखें।",
            "दरवाजे लगाएं (यदि हों)।",
        ],
        "asm_rule_title":  "सुनहरा नियम",
        "asm_rule":        "डॉवेल गाइड करता है — स्क्रू कसता है।",
        "asm_rule_tipl":   "डॉवेल सुनिश्चित करता है कि पैनल सही जगह बैठें।",
        "asm_rule_sraf":   "स्क्रू जोड़ को मजबूती से बंद करता है।",
        "asm_note_title":  "नोट",
        "asm_note":        "सभी छेद की स्थिति पहले से निर्धारित है। किसी अतिरिक्त माप की आवश्यकता नहीं।",
        "asm_shelf_title": "शेल्फ",
        "asm_shelf": [
            "शेल्फ के लिए छेद 32 mm सिस्टम से बनाए गए हैं।",
            "शेल्फ को किसी भी वांछित ऊंचाई पर रखा जा सकता है।",
            "एक शेल्फ के लिए 4 पिन (प्रत्येक साइड 2) की जरूरत होती है।",
        ],
        # --- सामान्य नियम ---
        "gen_rules_title": "सामान्य नियम",
        "gen_sys32_title": "32 mm सिस्टम — शेल्फ पिन",
        "gen_sys32_text":  (
            "शेल्फ पिन के छेद मानक 32 mm सिस्टम के अनुसार बनाए जाते हैं "
            "(छेदों के बीच 32 mm)। तालिका में केवल पहली (सबसे नीची) Y स्थिति "
            "दिखाई जाती है — बाकी सभी छेद वहाँ से हर 32 mm पर होते हैं।"
        ),
        "gen_mirror_note":    "⇇  दायाँ पैनल बाएँ पैनल का दर्पण है।",
        "gen_shelf_hdr":      "शेल्फ पिन — 32 mm सिस्टम",
        "gen_shelf_x":        "X (mm)",
        "gen_shelf_y1":       "पहली Y (mm)",
        "gen_shelf_count":    "छेदों की संख्या",
        "gen_shelf_note":     "शेष छेद: पहली Y स्थिति से हर 32 mm पर।",
        # पुस्तक में शेल्फ के लिए टेक्स्ट ब्लॉक
        "shelf_blk_title":    "शेल्फ छेद (32 mm सिस्टम)",
        "shelf_blk_intro":    "शेल्फ पिन के छेद मानक 32 mm सिस्टम के अनुसार बनाएं।",
        "shelf_blk_raster":   "छेदों के बीच दूरी: 32 mm",
        "shelf_blk_first_y":  "पहले छेद की ऊंचाई: Y =",
        "shelf_blk_x_pos":    "X स्थितियाँ:",
        "shelf_blk_outro":    "छेद इस रैस्टर में पूरे पैनल की ऊंचाई पर बनाए जाते हैं।",
        "shelf_universal":    (
            "नोट: शेल्फ पिन के छेद 32 mm सिस्टम के अनुसार बनाए जाते हैं "
            "और तालिका में अलग-अलग नहीं दिखाए जाते।"
        ),
        # --- मोंटेज के लिए महत्वपूर्ण ---
        "imp_title":       "मोंटेज के लिए महत्वपूर्ण",
        "imp_items": [
            "सभी छेद फ़ैक्टरी में निर्धारित हैं — अतिरिक्त ड्रिलिंग आवश्यक नहीं।",
            "डॉवेल केवल पैनलों को संरेखित करने के लिए है (कसता नहीं)।",
            "स्क्रू / कन्फर्मेट जोड़ को कसता है।",
            "शेल्फ किसी भी ऊंचाई पर लगाई जा सकती है (32 mm सिस्टम)।",
            "पैनलों की दिशा ध्यान रखें: X = बाएँ किनारे से, Y = निचले किनारे से।",
        ],
    },
}

# fallback na srpski za nepoznate jezike
for _lc in ("de", "es", "fr", "pt-br", "ru", "zh-cn", "hi"):
    if _lc not in _EDU:
        _EDU[_lc] = _EDU["sr"]


def _e(key: str, lang: str) -> str:
    """Dohvata edukativni string za dati jezik."""
    d = _EDU.get(lang) or _EDU.get("sr") or {}
    return d.get(key, (_EDU.get("sr") or {}).get(key, key))


def _find_font_file(filename: str) -> str | None:
    here = Path(__file__).resolve().parent
    cwd = Path.cwd()
    for p in (
        here / "fonts" / filename,
        here / filename,
        cwd / "fonts" / filename,
        cwd / filename,
    ):
        if p.exists():
            return str(p)
    return None


def _register_fonts() -> tuple[str, str]:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        pdfmetrics.getFont("DejaVuSans")
        pdfmetrics.getFont("DejaVuSans-Bold")
        return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    reg = _find_font_file("DejaVuSans.ttf")
    bold = _find_font_file("DejaVuSans-Bold.ttf")
    try:
        if reg:
            pdfmetrics.registerFont(TTFont("DejaVuSans", reg))
        if bold:
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
        if reg and bold:
            return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


# ---------------------------------------------------------------------------
# Helper funkcije za kondenzaciju podataka
# ---------------------------------------------------------------------------

def _condense_holes(holes: list) -> tuple[list, list]:
    """
    Uklanja SVE shelf_pin rupe iz glavne tabele i vraća samo info za tekstualni blok.
    - Vraća: (ostale_rupe_bez_shelf_pin, shelf_info_lista)
    shelf_info = [{"x": x_mm, "y1": first_y, "count": n, "dia": d, "depth": dep}, ...]
    """
    shelf = [h for h in holes if h.purpose == "shelf_pin"]
    rest  = [h for h in holes if h.purpose != "shelf_pin"]
    if not shelf:
        return rest, []
    by_x: dict = {}
    for h in shelf:
        by_x.setdefault(h.x_mm, []).append(h)
    info: list = []
    for x in sorted(by_x):
        hs = sorted(by_x[x], key=lambda h: h.y_mm)
        info.append({
            "x": x, "y1": hs[0].y_mm, "count": len(hs),
            "dia": hs[0].diameter_mm, "depth": hs[0].depth_mm,
        })
    # shelf_pin rupe se NE vraćaju u glavnu listu — prikazuju se kao tekst
    return rest, info


def _holes_equal(ha: list, hb: list) -> bool:
    """True ako su dve liste rupa identične (ista svrha + koordinate)."""
    def _k(h):
        return (h.purpose, h.x_mm, h.y_mm, h.diameter_mm, h.depth_mm)
    return sorted(map(_k, ha)) == sorted(map(_k, hb))


# ---------------------------------------------------------------------------
# Javna funkcija
# ---------------------------------------------------------------------------

def build_drilling_pdf_bytes(
    plans: list,
    kitchen: dict,
    lang: str = "sr",
) -> bytes:
    """
    Generiše PDF plan bušenja i vraća ga kao bytes.

    Args:
        plans:   Lista ModuleDrillPlan objekata (iz drilling_plan.build_drilling_plan).
        kitchen: Dict kuhinje (za meta podatke).
        lang:    Jezik dokumenta.

    Returns:
        PDF kao bytes, spreman za download.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, KeepTogether,
    )

    _lang = str(lang or "sr").lower().strip()
    # normalize pt, zh → pt-br, zh-cn
    if _lang == "pt":
        _lang = "pt-br"
    if _lang in ("zh", "zh_cn"):
        _lang = "zh-cn"
    if _lang not in _EDU:
        _lang = "sr"

    def _t(key: str) -> str:
        return _e(key, _lang)

    font_reg, font_bold = _register_fonts()

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=_t("doc_title"),
    )
    W = A4[0] - 36 * mm  # širina sadržaja

    # ── Paleta boja ─────────────────────────────────────────────────────────
    C_DARK   = colors.HexColor("#1C2833")   # naslov
    C_ACCENT = colors.HexColor("#1A5276")   # plava
    C_RULE   = colors.HexColor("#2874A6")
    C_EDU_BG = colors.HexColor("#EAF4FB")   # svetlo plava pozadina edu sekcije
    C_TBL_H  = colors.HexColor("#1A5276")   # header tabele
    C_TBL_A  = colors.HexColor("#F2F3F4")   # alternativni red
    C_WARN   = colors.HexColor("#784212")   # "Važno" boja
    C_GREEN  = colors.HexColor("#1E8449")   # "Pravilo" boja
    C_GRAY   = colors.HexColor("#717D7E")
    C_ASM_BG = colors.HexColor("#EAFAF1")   # svetlo zelena — uputstvo za sklapanje
    C_ASM_BD = colors.HexColor("#1E8449")   # zelena ivica
    C_GOLD   = colors.HexColor("#7D6608")   # zlatno pravilo tekst
    C_GOLD_BG= colors.HexColor("#FDFCE5")   # zlatno pravilo pozadina
    C_GEN_BG = colors.HexColor("#F4F6F7")   # siva pozadina — opšta pravila
    C_IMP_BG = colors.HexColor("#FEF9E7")   # žuta pozadina — važno za montažu
    C_IMP_BD = colors.HexColor("#D4AC0D")   # zlatna ivica — važno za montažu
    C_SHELF  = colors.HexColor("#1E8449")   # zelena za shelf summary
    C_SHELF_A= colors.HexColor("#E8F8F0")   # zelena alternacija

    # ── Stilovi ─────────────────────────────────────────────────────────────
    def _style(name, font=font_reg, size=9, leading=13, color=C_DARK,
               align=0, space_before=0, space_after=2, left_indent=0):
        return ParagraphStyle(
            name,
            fontName=font,
            fontSize=size,
            leading=leading,
            textColor=color,
            alignment=align,
            spaceBefore=space_before,
            spaceAfter=space_after,
            leftIndent=left_indent,
        )

    st_doc_title  = _style("DocTitle",   font=font_bold, size=20, leading=24,
                            color=C_DARK, space_before=6, space_after=2)
    st_doc_sub    = _style("DocSub",     size=9, color=C_GRAY, space_after=6)
    st_edu_title  = _style("EduTitle",   font=font_bold, size=13, leading=17,
                            color=C_ACCENT, space_before=8, space_after=4)
    st_edu_intro  = _style("EduIntro",   size=10, leading=14, space_after=6)
    st_edu_hdr    = _style("EduHdr",     font=font_bold, size=9, color=C_DARK,
                            space_before=5, space_after=1)
    st_edu_item   = _style("EduItem",    size=9, leading=12, left_indent=10, space_after=1)
    st_edu_rule   = _style("EduRule",    font=font_bold, size=11, leading=15,
                            color=C_GREEN, align=1, space_before=8, space_after=4)
    st_edu_imp    = _style("EduImp",     size=9, leading=13, color=C_WARN, left_indent=10)
    st_mod_title  = _style("ModTitle",   font=font_bold, size=11, leading=14,
                            color=C_ACCENT, space_before=10, space_after=3)
    st_sec_title  = _style("SecTitle",   font=font_bold, size=9, color=C_WARN,
                            space_before=6, space_after=2)
    st_note_item  = _style("NoteItem",   size=8, leading=11, left_indent=8, space_after=1)
    st_step_item  = _style("StepItem",   size=8, leading=11, left_indent=8,
                            color=C_GREEN, space_after=1)
    # --- Stilovi za opšta pravila i važno za montažu ---
    st_gen_title  = _style("GenTitle", font=font_bold, size=10, leading=14,
                            color=C_DARK, space_before=8, space_after=3)
    st_gen_body   = _style("GenBody",  size=9, leading=13, color=C_DARK,
                            left_indent=6, space_after=3)
    st_imp_title  = _style("ImpTitle", font=font_bold, size=12, leading=16,
                            color=C_GOLD, space_before=6, space_after=5)
    st_imp_item   = _style("ImpItem",  size=9, leading=13, color=C_DARK,
                            left_indent=10, space_after=3)
    st_shelf_note  = _style("ShelfN",    size=7.5, color=C_SHELF,
                            left_indent=8, space_after=2)
    st_shelf_title = _style("ShelfTitle", font=font_bold, size=8.5, color=C_SHELF,
                             space_before=5, space_after=2)
    st_shelf_body  = _style("ShelfBody",  size=8.5, leading=12, color=C_DARK,
                             left_indent=8, space_after=1)
    st_shelf_bullet= _style("ShelfBullet",size=8.5, leading=12, color=C_DARK,
                             left_indent=16, space_after=2)
    st_univ_note   = _style("UnivNote",   size=8, leading=11,
                             color=colors.HexColor("#5D6D7E"),
                             left_indent=0, space_before=4, space_after=8)
    # --- Stilovi za uputstvo za sklapanje ---
    st_asm_title  = _style("AsmTitle",  font=font_bold, size=15, leading=20,
                            color=C_ASM_BD, space_before=6, space_after=4)
    st_asm_intro  = _style("AsmIntro",  size=10, leading=14, color=C_DARK,
                            space_after=8)
    st_asm_hdr    = _style("AsmHdr",    font=font_bold, size=9, color=C_DARK,
                            space_before=6, space_after=2)
    st_asm_step   = _style("AsmStep",   size=9, leading=13, color=C_DARK,
                            left_indent=12, space_after=2)
    st_asm_rule   = _style("AsmRule",   font=font_bold, size=12, leading=16,
                            color=C_GOLD, align=1, space_before=4, space_after=4)
    st_asm_rule_s = _style("AsmRuleSub",size=9, leading=13, color=C_GOLD,
                            left_indent=12, space_after=1)
    st_asm_note   = _style("AsmNote",   size=9, leading=13, color=C_DARK,
                            left_indent=8, space_after=2)
    st_asm_shelf  = _style("AsmShelf",  size=9, leading=13, color=C_DARK,
                            left_indent=12, space_after=2)

    story: list = []

    # ════════════════════════════════════════════════════════════════════════
    # 1. ZAGLAVLJE DOKUMENTA
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph(_t("doc_title"), st_doc_title))
    story.append(Paragraph(_t("doc_sub"), st_doc_sub))
    story.append(HRFlowable(width=W, thickness=1.5, color=C_ACCENT, spaceAfter=10))

    # ════════════════════════════════════════════════════════════════════════
    # 2. EDUKATIVNI UVOD — u svetlom boxu
    # ════════════════════════════════════════════════════════════════════════

    def _edu_box() -> list:
        """Vraća listu flowables za edukativni box."""
        items: list = []

        items.append(Paragraph(_t("edu_title"), st_edu_title))
        items.append(Paragraph(_t("edu_intro"), st_edu_intro))

        # Oznake ploča
        items.append(Paragraph(_t("edu_panels_hdr"), st_edu_hdr))
        for line in _t("edu_panels"):
            items.append(Paragraph(line, st_edu_item))

        items.append(Spacer(1, 4))

        # Kolone
        items.append(Paragraph(_t("edu_cols_hdr"), st_edu_hdr))
        for line in _t("edu_cols"):
            items.append(Paragraph(line, st_edu_item))

        items.append(Spacer(1, 4))

        # Primer
        items.append(Paragraph(_t("edu_example_hdr"), st_edu_hdr))
        for line in _t("edu_example").splitlines():
            items.append(Paragraph(line, st_edu_item))

        items.append(Spacer(1, 4))

        # Tipl fi8
        items.append(Paragraph(_t("edu_dowel_hdr"), st_edu_hdr))
        items.append(Paragraph(_t("edu_dowel"), st_edu_item))

        items.append(Spacer(1, 4))

        # Nosač police fi5
        items.append(Paragraph(_t("edu_shelf_hdr"), st_edu_hdr))
        items.append(Paragraph(_t("edu_shelf"), st_edu_item))

        items.append(Spacer(1, 4))

        # Važno
        items.append(Paragraph(_t("edu_important_hdr"), st_edu_hdr))
        for line in _t("edu_important").splitlines():
            items.append(Paragraph(line, st_edu_imp))

        items.append(Spacer(1, 6))

        # Pravilo
        items.append(HRFlowable(width=W - 10 * mm, thickness=0.8, color=C_RULE, spaceAfter=6))
        items.append(Paragraph(_t("edu_rule"), st_edu_rule))

        return items

    # Pakujemo edu sadržaj u ćeliju tabele da dobijemo background box
    edu_inner = _edu_box()
    edu_table = Table(
        [[edu_inner]],
        colWidths=[W],
    )
    edu_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_EDU_BG),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_EDU_BG]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("BOX",          (0, 0), (-1, -1), 1, C_ACCENT),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(edu_table)
    story.append(Spacer(1, 12))

    # ── Opšta pravila — sistem 32, na istoj strani ────────────────────────────
    gen_items: list = []
    gen_items.append(Paragraph(_t("gen_rules_title"), st_gen_title))
    gen_items.append(HRFlowable(width=W - 8*mm, thickness=0.8, color=C_RULE, spaceAfter=5))
    gen_items.append(Paragraph(
        f"<b>{_t('gen_sys32_title')}</b>", st_gen_body,
    ))
    gen_items.append(Paragraph(_t("gen_sys32_text"), st_gen_body))

    gen_table = Table([[gen_items]], colWidths=[W])
    gen_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_GEN_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("BOX",          (0, 0), (-1, -1), 0.8, C_RULE),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(gen_table)
    story.append(Spacer(1, 8))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════════════════════
    # 3. TEHNIČKE TABELE — po elementu
    # ════════════════════════════════════════════════════════════════════════

    # Univerzalna napomena o policama — jednom na vrhu, ne ponavlja se po ploči
    story.append(Paragraph(
        f"ℹ  {_t('shelf_universal')}",
        st_univ_note,
    ))
    story.append(HRFlowable(width=W, thickness=0.5,
                             color=colors.HexColor("#BDC3C7"), spaceAfter=6))

    if not plans:
        story.append(Paragraph(_t("tbl_no_modules"), st_edu_intro))
    else:
        _purpose_map = {
            "hinge":     _t("purpose_hinge"),
            "dowel":     _t("purpose_dowel"),
            "shelf_pin": _t("purpose_shelf"),
            "slide":     _t("purpose_slide"),
        }

        def _purpose_lbl(p: str) -> str:
            return _purpose_map.get(p, p)

        # Zaglavlja tabele rupa
        hole_hdr = [
            _t("tbl_purpose"),
            _t("tbl_x"),
            _t("tbl_y"),
            _t("tbl_dia"),
            _t("tbl_depth"),
            _t("tbl_note"),
        ]
        col_w = [40*mm, 20*mm, 20*mm, 18*mm, 22*mm, W - 120*mm]

        tbl_hdr_style = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), C_TBL_H),
            ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
            ("FONTNAME",     (0, 0), (-1, 0), font_bold),
            ("FONTSIZE",     (0, 0), (-1, -1), 7.5),
            ("LEADING",      (0, 0), (-1, -1), 10),
            ("ALIGN",        (1, 0), (-1, -1), "RIGHT"),
            ("ALIGN",        (0, 0), (0, -1), "LEFT"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, C_TBL_A]),
            ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
            ("TOPPADDING",   (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
            ("LEFTPADDING",  (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ])

        # Stil za shelf summary tabelu
        sh_style = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_SHELF),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), font_bold),
            ("FONTSIZE",      (0, 0), (-1, -1), 7),
            ("LEADING",       (0, 0), (-1, -1), 9),
            ("ALIGN",         (0, 0), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C_SHELF_A]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#A9DFBF")),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ])
        sh_col_w = [30*mm, 30*mm, 24*mm, 20*mm, 24*mm]
        sh_hdr = [
            _t("gen_shelf_x"), _t("gen_shelf_y1"),
            _t("gen_shelf_count"), "Ø (mm)", _t("tbl_depth"),
        ]

        for plan in plans:
            block: list = []

            # ── Naslov elementa ────────────────────────────────────────────
            block.append(Paragraph(
                f"E{plan.module_id} — {plan.module_label}"
                f"  |  {_t('tbl_zone')}: {plan.zone.upper()}",
                st_mod_title,
            ))
            block.append(HRFlowable(width=W, thickness=0.8, color=C_ACCENT, spaceAfter=4))

            # ── Detekcija ogledalo parova (LS / DS) ───────────────────────
            _ls = next((p for p in plan.panels
                        if "LS" in str(p.part_code).upper()), None)
            _ds = next((p for p in plan.panels
                        if "DS" in str(p.part_code).upper()), None)
            _mirrors = (_ls and _ds and _holes_equal(_ls.holes, _ds.holes))

            for panel in plan.panels:
                _code = str(panel.part_code).upper()
                _pan_lbl = (
                    f"E{plan.module_id} – {panel.part_code}  —  {panel.part_name}"
                    f"  ({panel.width_mm} × {panel.height_mm} mm)"
                )
                st_pan = _style(f"PH{id(panel)}", font=font_bold, size=8.5,
                                color=C_DARK, space_before=5, space_after=2)

                # DS panel = ogledalo LS: samo napomena, bez ponovljene tabele
                if "DS" in _code and _mirrors:
                    block.append(Paragraph(_pan_lbl, st_pan))
                    block.append(Paragraph(
                        _t("gen_mirror_note"),
                        _style(f"MN{id(panel)}", size=8, color=C_GRAY,
                               left_indent=12, space_after=4),
                    ))
                    continue

                # Kondenzuj shelf_pin rupe
                _main_holes, _shelf_info = _condense_holes(panel.holes)

                block.append(Paragraph(_pan_lbl, st_pan))

                if not _main_holes:
                    block.append(Paragraph(
                        _t("tbl_no_holes"),
                        _style(f"NH{id(panel)}", size=7.5, color=C_GRAY, left_indent=8),
                    ))
                else:
                    # Glavna tabela: sve rupe osim ponavljajućih shelf_pin
                    rows = [hole_hdr]
                    for h in sorted(_main_holes,
                                    key=lambda x: (x.purpose != "hinge",
                                                   x.purpose != "dowel", x.y_mm)):
                        rows.append([
                            _purpose_lbl(h.purpose),
                            str(h.x_mm),
                            str(h.y_mm),
                            str(h.diameter_mm),
                            str(h.depth_mm),
                            h.note or "",
                        ])
                    t = Table(rows, colWidths=col_w, repeatRows=1)
                    t.setStyle(tbl_hdr_style)
                    block.append(t)

                # Tekstualni blok za nosače polica (bez tabele, bez stotina redova)
                if _shelf_info:
                    block.append(Paragraph(_t("shelf_blk_title"), st_shelf_title))
                    block.append(Paragraph(_t("shelf_blk_intro"), st_shelf_body))
                    block.append(Paragraph(
                        f"•  {_t('shelf_blk_raster')}",
                        st_shelf_bullet,
                    ))
                    # Prva Y (uzima se od prve X kolone; obično iste za sve stubove)
                    _first_y = _shelf_info[0]["y1"]
                    block.append(Paragraph(
                        f"•  {_t('shelf_blk_first_y')} {_first_y} mm",
                        st_shelf_bullet,
                    ))
                    # X pozicije — sve u jednoj liniji
                    _x_str = "  ,  ".join(f"{si['x']} mm" for si in _shelf_info)
                    block.append(Paragraph(
                        f"•  {_t('shelf_blk_x_pos')} {_x_str}",
                        st_shelf_bullet,
                    ))
                    block.append(Paragraph(_t("shelf_blk_outro"), st_shelf_body))

                block.append(Spacer(1, 4))

            # Napomene za radionicu (samo ako postoje)
            if plan.workshop_notes:
                block.append(Paragraph(_t("tbl_workshop"), st_sec_title))
                for note in plan.workshop_notes:
                    block.append(Paragraph(f"• {note}", st_note_item))

            block.append(Spacer(1, 8))
            block.append(HRFlowable(width=W, thickness=0.5,
                                     color=colors.HexColor("#BDC3C7"), spaceAfter=4))

            story.append(KeepTogether(block[:8]))   # drži naslov + prvu ploču
            story.extend(block[8:])                  # ostatak slobodan za prelom

    # ════════════════════════════════════════════════════════════════════════
    # 4. VAŽNO ZA MONTAŽU — kompaktna profesionalna sekcija
    # ════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    imp_items: list = []
    imp_items.append(Paragraph(_t("imp_title"), st_imp_title))
    imp_items.append(HRFlowable(width=W - 32*mm, thickness=1.2,
                                color=C_IMP_BD, spaceAfter=6))
    _imp_list = _t("imp_items")
    if isinstance(_imp_list, list):
        for item in _imp_list:
            imp_items.append(Paragraph(f"✔  {item}", st_imp_item))

    imp_table = Table([[imp_items]], colWidths=[W])
    imp_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_IMP_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("BOX",          (0, 0), (-1, -1), 1.5, C_IMP_BD),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(imp_table)
    story.append(Spacer(1, 16))

    # ════════════════════════════════════════════════════════════════════════
    # 5. UPUTSTVO ZA SKLAPANJE — korak-po-korak za početnike
    # ════════════════════════════════════════════════════════════════════════

    def _asm_section() -> list:
        """Vraća listu flowables za uputstvo za sklapanje."""
        items: list = []

        # Naslov sekcije
        items.append(Paragraph(_t("asm_title"), st_asm_title))
        items.append(HRFlowable(width=W - 32*mm, thickness=1.5, color=C_ASM_BD, spaceAfter=8))

        # Uvodni red
        items.append(Paragraph(_t("asm_intro"), st_asm_intro))

        # ── Numerisani koraci ────────────────────────────────────────────────
        items.append(Paragraph("Koraci sklapanja:" if _lang == "sr" else
                                "Assembly steps:" if _lang == "en" else
                                "Montageschritte:" if _lang == "de" else
                                "Pasos de montaje:" if _lang == "es" else
                                "Etapes de montage:" if _lang == "fr" else
                                "Etapas de montagem:" if _lang == "pt-br" else
                                "Etapy sborki:" if _lang == "ru" else
                                "组装步骤：" if _lang == "zh-cn" else
                                "असेंबली चरण:",
                                st_asm_hdr))

        steps = _t("asm_steps")
        if isinstance(steps, list):
            for i, step in enumerate(steps, 1):
                items.append(Paragraph(f"{i}.  {step}", st_asm_step))

        items.append(Spacer(1, 10))

        # ── Zlatno pravilo — u žutom boxu ────────────────────────────────────
        # Unutrašnja širina: W minus levi/desni padding asm_table (16mm svaka strana)
        _inner_w = W - 32 * mm
        rule_items: list = [
            Paragraph(_t("asm_rule_title"), st_asm_hdr),
            Spacer(1, 2),
            Paragraph(_t("asm_rule"), st_asm_rule),
            Paragraph(f"•  {_t('asm_rule_tipl')}", st_asm_rule_s),
            Paragraph(f"•  {_t('asm_rule_sraf')}", st_asm_rule_s),
        ]
        rule_table = Table([[rule_items]], colWidths=[_inner_w])
        rule_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_GOLD_BG),
            ("LEFTPADDING",  (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("BOX",          (0, 0), (-1, -1), 1, colors.HexColor("#C9A400")),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ]))
        items.append(rule_table)
        items.append(Spacer(1, 10))

        # ── Napomena ─────────────────────────────────────────────────────────
        items.append(Paragraph(_t("asm_note_title"), st_asm_hdr))
        items.append(Paragraph(_t("asm_note"), st_asm_note))
        items.append(Spacer(1, 8))

        # ── Police ───────────────────────────────────────────────────────────
        items.append(Paragraph(_t("asm_shelf_title"), st_asm_hdr))
        shelf_list = _t("asm_shelf")
        if isinstance(shelf_list, list):
            for line in shelf_list:
                items.append(Paragraph(f"•  {line}", st_asm_shelf))

        return items

    # Pakujemo u zeleni box — vizualno odvojen od tehničkog dela
    asm_inner = _asm_section()
    asm_table = Table([[asm_inner]], colWidths=[W])
    asm_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_ASM_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
        ("BOX",          (0, 0), (-1, -1), 1.5, C_ASM_BD),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(asm_table)

    # ════════════════════════════════════════════════════════════════════════
    doc.build(story)
    return buf.getvalue()
