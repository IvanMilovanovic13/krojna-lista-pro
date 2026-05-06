# -*- coding: utf-8 -*-
"""UI tab — Plan bušenja i sklapanja za radionicu."""
from __future__ import annotations

import logging
from typing import Any, Callable

_LOG = logging.getLogger(__name__)

# ── i18n stringovi za tab ─────────────────────────────────────────────────
_TAB_STRINGS: dict[str, dict[str, str]] = {
    "sr": {
        "title":            "Plan bušenja za radionicu",
        "subtitle":         "Tipl vodi — šraf steže.",
        "no_modules":       "Nema elemenata u projektu.",
        "panel":            "Ploča",
        "dimensions":       "Dim. (mm)",
        "holes":            "Rupe",
        "purpose_hinge":    "Šarka fi35",
        "purpose_dowel":    "Tipl fi8",
        "purpose_shelf":    "Nosač police fi5",
        "purpose_slide":    "Klizač fioke",
        "pos_from_bottom":  "od dna",
        "pos_from_left":    "od leve ivice",
        "pos_from_edge":    "od ivice",
        "assembly_title":   "Uputstvo za sklapanje",
        "workshop_title":   "Napomene za radionicu",
        "depth":            "dubina",
        "count":            "kom",
        "at_x":             "x=",
        "at_y":             "y=",
        "no_holes":         "—",
        "export_pdf":       "Izvezi PDF",
        "export_csv":       "Izvezi CSV",
        "module_label":     "Element",
        "zone_label":       "Zona",
        "total_modules":    "Ukupno elemenata:",
        # kolone tabele rupa
        "col_code":         "Oznaka",
        "col_type":         "Tip",
        "col_note":         "Napomena",
        # police blok
        "shelf_title":      "Rupe za police — sistem 32 mm",
        "shelf_holes_word": "rupa",
        "shelf_first_y":    "Prva rupa od dna:",
        "shelf_every_32":   "pa na svakih 32 mm",
        "shelf_x_pos":      "X pozicije:",
    },
    "en": {
        "title":            "Drilling plan for workshop",
        "subtitle":         "Dowel guides — screw tightens.",
        "no_modules":       "No elements in project.",
        "panel":            "Panel",
        "dimensions":       "Dim. (mm)",
        "holes":            "Holes",
        "purpose_hinge":    "Hinge fi35",
        "purpose_dowel":    "Dowel fi8",
        "purpose_shelf":    "Shelf pin fi5",
        "purpose_slide":    "Drawer slide",
        "pos_from_bottom":  "from bottom",
        "pos_from_left":    "from left",
        "pos_from_edge":    "from edge",
        "assembly_title":   "Assembly instructions",
        "workshop_title":   "Workshop notes",
        "depth":            "depth",
        "count":            "pcs",
        "at_x":             "x=",
        "at_y":             "y=",
        "no_holes":         "—",
        "export_pdf":       "Export PDF",
        "export_csv":       "Export CSV",
        "module_label":     "Element",
        "zone_label":       "Zone",
        "total_modules":    "Total elements:",
        "col_code":         "Code",
        "col_type":         "Type",
        "col_note":         "Note",
        "shelf_title":      "Shelf holes — 32 mm system",
        "shelf_holes_word": "holes",
        "shelf_first_y":    "First hole from bottom:",
        "shelf_every_32":   "then every 32 mm",
        "shelf_x_pos":      "X positions:",
    },
    "de": {
        "title":            "Bohrplan für die Werkstatt",
        "subtitle":         "Dübel führt — Schraube zieht.",
        "no_modules":       "Keine Elemente im Projekt.",
        "panel":            "Platte",
        "dimensions":       "Maße (mm)",
        "holes":            "Bohrungen",
        "purpose_hinge":    "Scharnier Ø35",
        "purpose_dowel":    "Dübel Ø8",
        "purpose_shelf":    "Regalträger Ø5",
        "purpose_slide":    "Schubladenführung",
        "pos_from_bottom":  "vom Boden",
        "pos_from_left":    "von links",
        "pos_from_edge":    "vom Rand",
        "assembly_title":   "Montageanleitung",
        "workshop_title":   "Werkstatthinweise",
        "depth":            "Tiefe",
        "count":            "Stk",
        "at_x":             "x=",
        "at_y":             "y=",
        "no_holes":         "—",
        "export_pdf":       "PDF exportieren",
        "export_csv":       "CSV exportieren",
        "module_label":     "Element",
        "zone_label":       "Zone",
        "total_modules":    "Elemente gesamt:",
        "col_code":         "Kürzel",
        "col_type":         "Typ",
        "col_note":         "Hinweis",
        "shelf_title":      "Regalbohrungen — 32-mm-System",
        "shelf_holes_word": "Bohrungen",
        "shelf_first_y":    "Erste Bohrung vom Boden:",
        "shelf_every_32":   "dann alle 32 mm",
        "shelf_x_pos":      "X-Positionen:",
    },
    "fr": {
        "title":            "Plan de perçage pour l'atelier",
        "subtitle":         "La cheville guide — la vis serre.",
        "no_modules":       "Aucun élément dans le projet.",
        "panel":            "Panneau",
        "dimensions":       "Dim. (mm)",
        "holes":            "Perçages",
        "purpose_hinge":    "Charnière Ø35",
        "purpose_dowel":    "Cheville Ø8",
        "purpose_shelf":    "Téton d'étagère Ø5",
        "purpose_slide":    "Coulisse tiroir",
        "pos_from_bottom":  "du bas",
        "pos_from_left":    "de la gauche",
        "pos_from_edge":    "du bord",
        "assembly_title":   "Instructions de montage",
        "workshop_title":   "Notes pour l'atelier",
        "depth":            "profondeur",
        "count":            "pc",
        "at_x":             "x=",
        "at_y":             "y=",
        "no_holes":         "—",
        "export_pdf":       "Exporter PDF",
        "export_csv":       "Exporter CSV",
        "module_label":     "Élément",
        "zone_label":       "Zone",
        "total_modules":    "Total éléments :",
        "col_code":         "Code",
        "col_type":         "Type",
        "col_note":         "Note",
        "shelf_title":      "Trous de tasseaux — système 32 mm",
        "shelf_holes_word": "trous",
        "shelf_first_y":    "Premier trou depuis le bas :",
        "shelf_every_32":   "puis tous les 32 mm",
        "shelf_x_pos":      "Positions X :",
    },
    "es": {
        "title":            "Plan de taladrado para el taller",
        "subtitle":         "La clavija guía — el tornillo aprieta.",
        "no_modules":       "No hay elementos en el proyecto.",
        "panel":            "Panel",
        "dimensions":       "Dim. (mm)",
        "holes":            "Agujeros",
        "purpose_hinge":    "Bisagra Ø35",
        "purpose_dowel":    "Clavija Ø8",
        "purpose_shelf":    "Soporte estante Ø5",
        "purpose_slide":    "Corredera cajón",
        "pos_from_bottom":  "desde abajo",
        "pos_from_left":    "desde la izquierda",
        "pos_from_edge":    "desde el borde",
        "assembly_title":   "Instrucciones de montaje",
        "workshop_title":   "Notas para el taller",
        "depth":            "profundidad",
        "count":            "uds",
        "at_x":             "x=",
        "at_y":             "y=",
        "no_holes":         "—",
        "export_pdf":       "Exportar PDF",
        "export_csv":       "Exportar CSV",
        "module_label":     "Elemento",
        "zone_label":       "Zona",
        "total_modules":    "Total elementos:",
        "col_code":         "Código",
        "col_type":         "Tipo",
        "col_note":         "Nota",
        "shelf_title":      "Agujeros de soportes — sistema 32 mm",
        "shelf_holes_word": "agujeros",
        "shelf_first_y":    "Primer agujero desde abajo:",
        "shelf_every_32":   "luego cada 32 mm",
        "shelf_x_pos":      "Posiciones X:",
    },
}

_PURPOSE_ICON = {
    "hinge":     "🔩",
    "dowel":     "🔘",
    "shelf_pin": "📌",
    "slide":     "↔",
}

_ZONE_ICON = {
    "base":       "🟫",
    "wall":       "🟦",
    "tall":       "🟩",
    "tall_top":   "🟩",
    "wall_upper": "🟦",
}


def _t(key: str, lang: str) -> str:
    return (_TAB_STRINGS.get(lang) or _TAB_STRINGS["sr"]).get(
        key, (_TAB_STRINGS["sr"].get(key, key))
    )


def _purpose_label(purpose: str, lang: str) -> str:
    mapping = {
        "hinge":     _t("purpose_hinge", lang),
        "dowel":     _t("purpose_dowel", lang),
        "shelf_pin": _t("purpose_shelf", lang),
        "slide":     _t("purpose_slide", lang),
    }
    return mapping.get(purpose, purpose)


def _holes_summary(holes: list, lang: str) -> str:
    """Kratki tekstualni pregled rupa za prikaz u tabeli."""
    if not holes:
        return _t("no_holes", lang)
    by_purpose: dict[str, list] = {}
    for h in holes:
        by_purpose.setdefault(h.purpose, []).append(h)
    parts = []
    for purpose, hs in by_purpose.items():
        lbl = _purpose_label(purpose, lang)
        icon = _PURPOSE_ICON.get(purpose, "•")
        parts.append(f"{icon} {lbl} ×{len(hs)}")
    return "  |  ".join(parts)


def render_drilling_tab(
    *,
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    build_drilling_plan: Callable[..., list],
) -> None:
    """Renderuje tab 'Plan bušenja za radionicu'."""
    _lang = str(getattr(state, "language", "sr") or "sr").lower().strip()

    def _tr(key: str) -> str:
        return _t(key, _lang)

    with ui.column().classes("w-full max-w-5xl mx-auto px-4 py-6 gap-4"):

        # ── Zaglavlje ────────────────────────────────────────────────────
        with ui.row().classes("w-full items-center justify-between"):
            with ui.column().classes("gap-0"):
                ui.label(_tr("title")).classes("text-2xl font-bold text-gray-900")
                ui.label(_tr("subtitle")).classes(
                    "text-sm text-gray-500 italic"
                )
            # Dugme za PDF export
            def _export_pdf():
                try:
                    from ui_drilling_pdf import build_drilling_pdf_bytes
                    _plans = build_drilling_plan(state.kitchen, lang=_lang)
                    _pdf_bytes = build_drilling_pdf_bytes(_plans, state.kitchen, lang=_lang)
                    ui.download(_pdf_bytes, filename="plan_busenja.pdf")
                except Exception as _ex:
                    _LOG.exception("PDF export greška: %s", _ex)
                    ui.notify(f"Greška pri generisanju PDF-a: {_ex}", type="negative")

            ui.button(
                _tr("export_pdf"),
                on_click=_export_pdf,
            ).props("icon=picture_as_pdf outline color=primary").classes("text-sm")

        ui.separator()

        # ── Generiši plan ─────────────────────────────────────────────────
        try:
            plans = build_drilling_plan(state.kitchen, lang=_lang)
        except Exception as ex:
            _LOG.exception("build_drilling_plan greška: %s", ex)
            plans = []

        modules = state.kitchen.get("modules", []) or []
        if not modules:
            ui.label(_tr("no_modules")).classes("text-gray-400 text-sm py-8 text-center w-full")
            return

        ui.label(f"{_tr('total_modules')} {len(plans)}").classes(
            "text-xs text-gray-500 font-semibold uppercase tracking-wide"
        )

        # ── Po elementu ───────────────────────────────────────────────────
        for plan in plans:
            zone_icon = _ZONE_ICON.get(plan.zone, "⬜")
            with ui.expansion(
                f"{zone_icon}  #{plan.module_id} — {plan.module_label}",
                icon="construction",
            ).classes("w-full border border-gray-200 rounded-lg"):

                with ui.column().classes("w-full gap-3 p-2"):

                    # Tabela ploča
                    with ui.column().classes("w-full gap-1"):
                        ui.label(_tr("panel")).classes(
                            "text-xs font-semibold uppercase tracking-wide text-gray-500"
                        )
                        columns = [
                            {"name": "code",   "label": _tr("col_code"),  "field": "code",   "align": "left"},
                            {"name": "name",   "label": _tr("panel"),     "field": "name",   "align": "left"},
                            {"name": "dims",   "label": _tr("dimensions"),"field": "dims",   "align": "left"},
                            {"name": "holes",  "label": _tr("holes"),     "field": "holes",  "align": "left"},
                        ]
                        rows = []
                        for p in plan.panels:
                            rows.append({
                                "code":  p.part_code,
                                "name":  p.part_name,
                                "dims":  f"{p.width_mm} × {p.height_mm}",
                                "holes": _holes_summary(p.holes, _lang),
                            })
                        ui.table(
                            columns=columns,
                            rows=rows,
                        ).classes("w-full text-xs").props("dense flat bordered")

                    # Detalji rupa po ploči (ekspandabilno)
                    for panel in plan.panels:
                        if not panel.holes:
                            continue
                        with ui.expansion(
                            f"🔍 {panel.part_code} — {panel.part_name}",
                        ).classes("w-full bg-gray-50 rounded border border-gray-100"):
                            with ui.column().classes("gap-1 p-1"):
                                hole_cols = [
                                    {"name": "purpose", "label": _tr("col_type"),        "field": "purpose", "align": "left"},
                                    {"name": "x",       "label": f"X ({_tr('pos_from_left')})", "field": "x", "align": "right"},
                                    {"name": "y",       "label": f"Y ({_tr('pos_from_bottom')})", "field": "y", "align": "right"},
                                    {"name": "dia",     "label": "Ø (mm)",               "field": "dia",     "align": "right"},
                                    {"name": "dep",     "label": _tr("depth"),            "field": "dep",     "align": "right"},
                                    {"name": "note",    "label": _tr("col_note"),         "field": "note",    "align": "left"},
                                ]
                                # Odvoji police od ostalih rupa
                                shelf_holes = [h for h in panel.holes if h.purpose == "shelf_pin"]
                                other_holes = [h for h in panel.holes if h.purpose != "shelf_pin"]

                                hole_rows = []
                                for h in other_holes:
                                    icon = _PURPOSE_ICON.get(h.purpose, "•")
                                    hole_rows.append({
                                        "purpose": f"{icon} {_purpose_label(h.purpose, _lang)}",
                                        "x":       f"{h.x_mm} mm",
                                        "y":       f"{h.y_mm} mm",
                                        "dia":     f"{h.diameter_mm}",
                                        "dep":     f"{h.depth_mm} mm",
                                        "note":    h.note or "",
                                    })
                                if hole_rows:
                                    ui.table(
                                        columns=hole_cols,
                                        rows=hole_rows,
                                    ).classes("w-full text-xs").props("dense flat")

                                # Tekstualni blok za police (sistem 32 mm)
                                if shelf_holes:
                                    by_x: dict = {}
                                    for h in shelf_holes:
                                        by_x.setdefault(h.x_mm, []).append(h)
                                    x_positions = sorted(by_x)
                                    first_y = min(h.y_mm for h in shelf_holes)
                                    total_count = len(shelf_holes)
                                    dia = shelf_holes[0].diameter_mm
                                    dep = shelf_holes[0].depth_mm
                                    x_str = "  ·  ".join(f"{x} mm" for x in x_positions)
                                    with ui.column().classes(
                                        "w-full gap-1 mt-2 p-3 rounded-lg bg-blue-50 border border-blue-200"
                                    ):
                                        ui.label(
                                            f"📌  {_tr('shelf_title')}  "
                                            f"({total_count} {_tr('shelf_holes_word')}, "
                                            f"Ø{dia}, {_tr('depth')} {dep} mm)"
                                        ).classes("text-xs font-semibold text-blue-800")
                                        ui.label(
                                            f"• {_tr('shelf_first_y')} {first_y} mm, {_tr('shelf_every_32')}"
                                        ).classes("text-xs text-blue-700")
                                        ui.label(
                                            f"• {_tr('shelf_x_pos')} {x_str}"
                                        ).classes("text-xs text-blue-700")

                    # Napomene za radionicu
                    if plan.workshop_notes:
                        with ui.column().classes("w-full gap-1"):
                            ui.label(_tr("workshop_title")).classes(
                                "text-xs font-semibold uppercase tracking-wide text-amber-700"
                            )
                            for note in plan.workshop_notes:
                                ui.label(f"• {note}").classes("text-xs text-gray-700")

                    # Uputstvo za sklapanje
                    if plan.assembly_steps:
                        with ui.column().classes("w-full gap-1"):
                            ui.label(_tr("assembly_title")).classes(
                                "text-xs font-semibold uppercase tracking-wide text-green-700"
                            )
                            for i, step in enumerate(plan.assembly_steps, 1):
                                ui.label(f"{i}. {step}").classes("text-xs text-gray-700")
