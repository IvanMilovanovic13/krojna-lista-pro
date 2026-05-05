# -*- coding: utf-8 -*-
"""Plan bušenja i sklapanja za radionicu — generisanje po modulu."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# i18n rečnik
# ---------------------------------------------------------------------------

_STRINGS: Dict[str, Dict[str, str]] = {
    "sr": {
        "left_side": "Leva stranica",
        "right_side": "Desna stranica",
        "bottom": "Dno",
        "top": "Vrh / Plafon",
        "back": "Leđa",
        "front": "Front / Vrata",
        "shelf": "Polica",
        "hinge_note": "Rupa fi 35mm za šarke, 22mm od ivice",
        "dowel_note": "Tipl fi 8mm, dubina 12mm",
        "shelf_pin_note": "Rupa fi 5mm za nosač police",
        "slide_note": "Pozicija klizača fioke",
        "step_dowels": "Ubaci drvene tiplove u pripremljene rupe.",
        "step_join": "Spoji označene ploče prema oznakama.",
        "step_square": "Proveri da ploče naležu pod 90°.",
        "step_screws": "Zategni šrafove/konfirmate na označenim mestima.",
        "step_back": "Postavi leđa elementa.",
        "step_shelves": "Postavi police na nosače.",
        "step_doors": "Okači vrata i podesi šarke.",
        "step_drawers": "Ugradi klizače i postavi fioke.",
        "workshop_philosophy": "Tipl vodi — šraf steže.",
    },
    "en": {
        "left_side": "Left side",
        "right_side": "Right side",
        "bottom": "Bottom",
        "top": "Top panel",
        "back": "Back panel",
        "front": "Front / Door",
        "shelf": "Shelf",
        "hinge_note": "fi 35mm hinge hole, 22mm from edge",
        "dowel_note": "8mm dowel, 12mm depth",
        "shelf_pin_note": "fi 5mm shelf pin hole",
        "slide_note": "Drawer slide position",
        "step_dowels": "Insert wooden dowels into prepared holes.",
        "step_join": "Join marked panels according to labels.",
        "step_square": "Check panels meet at 90°.",
        "step_screws": "Tighten screws/confirmats at marked positions.",
        "step_back": "Install back panel.",
        "step_shelves": "Place shelves on pins.",
        "step_doors": "Hang doors and adjust hinges.",
        "step_drawers": "Install drawer slides and drawers.",
        "workshop_philosophy": "Dowel guides — screw tightens.",
    },
    "de": {
        "left_side": "Linke Seite",
        "right_side": "Rechte Seite",
        "bottom": "Boden",
        "top": "Deckel",
        "back": "Rückwand",
        "front": "Front / Tür",
        "shelf": "Einlegeboden",
        "hinge_note": "Ø 35mm Scharnierbohrung, 22mm vom Rand",
        "dowel_note": "8mm Dübel, 12mm Tiefe",
        "shelf_pin_note": "Ø 5mm Regalträgerbohrung",
        "slide_note": "Schubladenführung Position",
        "step_dowels": "Holzdübel in vorbereitete Löcher einsetzen.",
        "step_join": "Markierte Platten gemäß Bezeichnung verbinden.",
        "step_square": "Prüfen, ob Platten im 90°-Winkel anliegen.",
        "step_screws": "Schrauben/Konfirmaten an markierten Stellen festziehen.",
        "step_back": "Rückwand einsetzen.",
        "step_shelves": "Einlegeböden auf Träger legen.",
        "step_doors": "Türen einhängen und Scharniere einstellen.",
        "step_drawers": "Schubladenführungen und Schubladen einbauen.",
        "workshop_philosophy": "Dübel führt — Schraube zieht.",
    },
    "fr": {
        "left_side": "Côté gauche",
        "right_side": "Côté droit",
        "bottom": "Fond de caisson",
        "top": "Dessus / Plafond",
        "back": "Fond arrière",
        "front": "Façade / Porte",
        "shelf": "Étagère",
        "hinge_note": "Ø 35mm trou de charnière, 22mm du bord",
        "dowel_note": "Cheville 8mm, profondeur 12mm",
        "shelf_pin_note": "Ø 5mm trou de tasseau",
        "slide_note": "Position coulisse tiroir",
        "step_dowels": "Insérer les chevilles en bois dans les trous préparés.",
        "step_join": "Assembler les panneaux marqués selon les repères.",
        "step_square": "Vérifier que les panneaux se rejoignent à 90°.",
        "step_screws": "Serrer les vis/confirmats aux positions marquées.",
        "step_back": "Poser le fond arrière.",
        "step_shelves": "Placer les étagères sur les tasseaux.",
        "step_doors": "Accrocher les portes et régler les charnières.",
        "step_drawers": "Installer les coulisses et les tiroirs.",
        "workshop_philosophy": "La cheville guide — la vis serre.",
    },
    "es": {
        "left_side": "Lado izquierdo",
        "right_side": "Lado derecho",
        "bottom": "Fondo",
        "top": "Techo / Cubierta",
        "back": "Panel trasero",
        "front": "Frente / Puerta",
        "shelf": "Balda",
        "hinge_note": "Ø 35mm taladro bisagra, 22mm del borde",
        "dowel_note": "Clavija 8mm, profundidad 12mm",
        "shelf_pin_note": "Ø 5mm taladro soporte balda",
        "slide_note": "Posición guía cajón",
        "step_dowels": "Insertar clavijas de madera en los orificios preparados.",
        "step_join": "Unir los paneles marcados según las indicaciones.",
        "step_square": "Verificar que los paneles encajan a 90°.",
        "step_screws": "Apretar tornillos/confirmats en las posiciones marcadas.",
        "step_back": "Colocar el panel trasero.",
        "step_shelves": "Colocar las baldas sobre los soportes.",
        "step_doors": "Colgar las puertas y ajustar las bisagras.",
        "step_drawers": "Instalar las guías y los cajones.",
        "workshop_philosophy": "La clavija guía — el tornillo aprieta.",
    },
}


def _s(key: str, lang: str = "sr") -> str:
    """Dohvata string za dati jezik, fallback na srpski."""
    return _STRINGS.get(lang, _STRINGS["sr"]).get(key, _STRINGS["sr"].get(key, key))


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DrillHole:
    x_mm: int          # od leve/donje referentne ivice
    y_mm: int          # od dna/prednje referentne ivice
    diameter_mm: int   # 35 za šarke, 8 za tiplove, 5 za nosače polica
    depth_mm: int      # 12 za tiplove, 15 za nosače, 12.5 za šarke (Blum standard)
    purpose: str       # "hinge" | "dowel" | "shelf_pin" | "slide"
    note: str = ""


@dataclass
class PanelDrillPlan:
    part_code: str      # npr "E1-LS"
    part_name: str      # npr "Leva stranica"
    width_mm: int       # širina ploče
    height_mm: int      # visina ploče
    holes: List[DrillHole] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class ModuleDrillPlan:
    module_id: int
    module_label: str
    template_id: str
    zone: str
    panels: List[PanelDrillPlan] = field(default_factory=list)
    assembly_steps: List[str] = field(default_factory=list)
    workshop_notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pomoćne funkcije — šarke
# ---------------------------------------------------------------------------

def _hinge_count(h_mm: int) -> int:
    """Vraća broj šarki prema visini vrata."""
    if h_mm < 900:
        return 2
    if h_mm < 1500:
        return 3
    return 4


def _hinge_positions(h_mm: int) -> List[int]:
    """Vraća Y pozicije centara šarki od dna vrata (mm).

    Standard Blum: rupa fi 35mm, 22mm od bočne ivice vrata,
    centar prihvatne čašice 100mm od gornje/donje ivice vrata.
    """
    n = _hinge_count(h_mm)
    positions: List[int] = [100, h_mm - 100]
    if n == 3:
        positions.insert(1, h_mm // 2)
    elif n == 4:
        positions.insert(1, h_mm // 3)
        positions.insert(2, (2 * h_mm) // 3)
    return sorted(positions)


# ---------------------------------------------------------------------------
# Pomoćne funkcije — tiplovi
# ---------------------------------------------------------------------------

def _dowel_positions(length_mm: int, min_count: int = 2) -> List[int]:
    """Vraća pozicije tiplova duž spoja (mm od jednog kraja).

    Raster: 50mm od kraja, pa svakih 256mm (32mm × 8).
    Tipl fi 8mm, dubina 10-12mm.
    """
    if length_mm <= 0:
        return []

    positions: List[int] = []
    pos = 50
    while pos <= length_mm - 50:
        positions.append(pos)
        pos += 256

    # Osiguraj minimalni broj tiplova ravnomerno raspoređenih
    if len(positions) < min_count:
        positions = []
        if min_count == 1:
            positions = [length_mm // 2]
        else:
            step = length_mm // (min_count + 1)
            for i in range(1, min_count + 1):
                positions.append(step * i)

    return sorted(set(positions))


# ---------------------------------------------------------------------------
# Detekcija karakteristika modula
# ---------------------------------------------------------------------------

def _has_doors(tid: str) -> bool:
    """Da li modul ima vrata (ne open, ne glass, ne samo prolaz)."""
    t = tid.upper()
    if "OPEN" in t or "GLASS" in t:
        return False
    return "DOOR" in t or "DOORS" in t or "LIFTUP" in t


def _has_drawers(tid: str) -> bool:
    """Da li modul ima fioke."""
    t = tid.upper()
    return "DRAWER" in t or "DRAWERS" in t


def _has_shelves(tid: str, zone: str, h_mm: int, params: Dict[str, Any]) -> bool:
    """Da li modul podržava podesive police."""
    try:
        from module_rules import module_supports_adjustable_shelves, default_shelf_count
        if not module_supports_adjustable_shelves(tid):
            return False
        n = default_shelf_count(tid, zone=zone, h_mm=h_mm, params=params)
        return n > 0
    except Exception:
        return False


def _shelf_count(tid: str, zone: str, h_mm: int, params: Dict[str, Any]) -> int:
    """Broj polica u modulu."""
    try:
        from module_rules import default_shelf_count
        return default_shelf_count(tid, zone=zone, h_mm=h_mm, params=params)
    except Exception:
        return 0


def _has_top_panel(zone: str) -> bool:
    """Base zona nema vrh (ima radnu ploču) — ostale zone imaju."""
    return zone.lower() not in ("base",)


# ---------------------------------------------------------------------------
# Generisanje rupa za bočne stranice
# ---------------------------------------------------------------------------

def _build_side_panel(
    part_code: str,
    part_name: str,
    panel_w: int,   # dubina korpusa
    panel_h: int,   # visina korpusa
    inner_w: int,   # unutrašnja širina (za dowel pozicije)
    has_shelves: bool,
    has_drawers: bool,
    n_drawers: int,
    carcass_thk: int,
    lang: str,
) -> PanelDrillPlan:
    """Kreira plan bušenja za jednu bočnu stranicu (LS ili DS)."""
    holes: List[DrillHole] = []
    notes: List[str] = []

    # Tiplovi za spoj sa dnom (Y=carcass_thk od dna ploče, duž X ose)
    dno_dowels = _dowel_positions(inner_w)
    for x_pos in dno_dowels:
        holes.append(DrillHole(
            x_mm=x_pos,
            y_mm=carcass_thk // 2,
            diameter_mm=8,
            depth_mm=12,
            purpose="dowel",
            note=_s("dowel_note", lang),
        ))

    # Tiplovi za spoj sa vrhom (Y=panel_h - carcass_thk//2 od dna ploče)
    vrh_dowels = _dowel_positions(inner_w)
    for x_pos in vrh_dowels:
        holes.append(DrillHole(
            x_mm=x_pos,
            y_mm=panel_h - carcass_thk // 2,
            diameter_mm=8,
            depth_mm=12,
            purpose="dowel",
            note=_s("dowel_note", lang),
        ))

    # Nosači polica — fi 5mm, dve kolone (prednja i zadnja), raster 32mm
    if has_shelves:
        front_x = 37
        back_x = panel_w - 37
        pin_y = 100
        while pin_y <= panel_h - 100:
            for col_x in (front_x, back_x):
                holes.append(DrillHole(
                    x_mm=col_x,
                    y_mm=pin_y,
                    diameter_mm=5,
                    depth_mm=15,
                    purpose="shelf_pin",
                    note=_s("shelf_pin_note", lang),
                ))
            pin_y += 32
        notes.append(_s("shelf_pin_note", lang))

    # Klizači fioka — montirani na bočnoj stranici, 37mm od prednje ivice
    if has_drawers and n_drawers > 0:
        for i in range(1, n_drawers + 1):
            slide_y = int(panel_h / (n_drawers + 1) * i)
            holes.append(DrillHole(
                x_mm=37,
                y_mm=slide_y,
                diameter_mm=5,
                depth_mm=15,
                purpose="slide",
                note=_s("slide_note", lang),
            ))
        notes.append(_s("slide_note", lang))

    return PanelDrillPlan(
        part_code=part_code,
        part_name=part_name,
        width_mm=panel_w,
        height_mm=panel_h,
        holes=holes,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Generisanje rupa za dno i vrh
# ---------------------------------------------------------------------------

def _build_horizontal_panel(
    part_code: str,
    part_name: str,
    panel_w: int,
    panel_d: int,
    lang: str,
) -> PanelDrillPlan:
    """Kreira plan bušenja za horizontalnu ploču (dno ili vrh)."""
    holes: List[DrillHole] = []
    notes: List[str] = []

    # Tiplovi za spoj sa levom stranicom (X=0 strana)
    left_dowels = _dowel_positions(panel_d)
    for y_pos in left_dowels:
        holes.append(DrillHole(
            x_mm=0,
            y_mm=y_pos,
            diameter_mm=8,
            depth_mm=12,
            purpose="dowel",
            note=_s("dowel_note", lang),
        ))

    # Tiplovi za spoj sa desnom stranicom (X=panel_w strana)
    right_dowels = _dowel_positions(panel_d)
    for y_pos in right_dowels:
        holes.append(DrillHole(
            x_mm=panel_w,
            y_mm=y_pos,
            diameter_mm=8,
            depth_mm=12,
            purpose="dowel",
            note=_s("dowel_note", lang),
        ))

    notes.append(_s("dowel_note", lang))

    return PanelDrillPlan(
        part_code=part_code,
        part_name=part_name,
        width_mm=panel_w,
        height_mm=panel_d,
        holes=holes,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Generisanje rupa za front / vrata
# ---------------------------------------------------------------------------

def _build_front_panel(
    part_code: str,
    part_name: str,
    door_w: int,
    door_h: int,
    hinge_side_offset: int,
    lang: str,
) -> PanelDrillPlan:
    """Kreira plan bušenja za front/vrata — šarke fi 35mm."""
    holes: List[DrillHole] = []
    notes: List[str] = []

    hinge_ys = _hinge_positions(door_h)
    for y_pos in hinge_ys:
        holes.append(DrillHole(
            x_mm=hinge_side_offset,
            y_mm=y_pos,
            diameter_mm=35,
            depth_mm=13,   # Blum standard 12.5mm, zaokruženo na 13mm
            purpose="hinge",
            note=_s("hinge_note", lang),
        ))

    notes.append(_s("hinge_note", lang))

    return PanelDrillPlan(
        part_code=part_code,
        part_name=part_name,
        width_mm=door_w,
        height_mm=door_h,
        holes=holes,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Glavna funkcija
# ---------------------------------------------------------------------------

def build_drilling_plan(
    kitchen: Dict[str, Any],
    lang: str = "sr",
) -> List[ModuleDrillPlan]:
    """Generisanje plana bušenja za sve module u kuhinji.

    Args:
        kitchen: Dict sa ključevima 'modules', 'materials', 'manufacturing' itd.
        lang:    Jezik za tekstualne opise ('sr', 'en', 'de', 'fr', 'es').

    Returns:
        Lista ModuleDrillPlan objekata, jedan po modulu.
    """
    result: List[ModuleDrillPlan] = []

    try:
        modules: List[Dict[str, Any]] = kitchen.get("modules") or []
        materials: Dict[str, Any] = kitchen.get("materials") or {}
        carcass_thk: int = int(materials.get("carcass_thk", 18) or 18)
    except Exception as exc:
        log.error("drilling_plan: greška pri čitanju kitchen dict-a: %s", exc)
        return result

    for m in modules:
        try:
            mid: int = int(m.get("id", 0))
            tid: str = str(m.get("template_id", "") or "").upper().strip()
            zone: str = str(m.get("zone", "") or "").lower().strip()
            label: str = str(m.get("label", "") or f"Modul {mid}")
            params: Dict[str, Any] = m.get("params") or {}

            w: int = int(m.get("w_mm", 600) or 600)
            h: int = int(m.get("h_mm", 720) or 720)
            d: int = int(m.get("d_mm", 560) or 560)

            inner_w: int = w - 2 * carcass_thk
            inner_d: int = d - carcass_thk   # leđa su urezana u žleb

            prefix: str = f"E{mid}"

            panels: List[PanelDrillPlan] = []
            has_doors_flag: bool = _has_doors(tid)
            has_drawers_flag: bool = _has_drawers(tid)
            has_shelves_flag: bool = _has_shelves(tid, zone, h, params)
            n_drawers: int = int(params.get("n_drawers", 3) or 3) if has_drawers_flag else 0
            n_shelves: int = _shelf_count(tid, zone, h, params) if has_shelves_flag else 0

            # --- Leva stranica ---
            ls = _build_side_panel(
                part_code=f"{prefix}-LS",
                part_name=_s("left_side", lang),
                panel_w=d,
                panel_h=h,
                inner_w=inner_w,
                has_shelves=has_shelves_flag,
                has_drawers=has_drawers_flag,
                n_drawers=n_drawers,
                carcass_thk=carcass_thk,
                lang=lang,
            )
            panels.append(ls)

            # --- Desna stranica ---
            ds = _build_side_panel(
                part_code=f"{prefix}-DS",
                part_name=_s("right_side", lang),
                panel_w=d,
                panel_h=h,
                inner_w=inner_w,
                has_shelves=has_shelves_flag,
                has_drawers=has_drawers_flag,
                n_drawers=n_drawers,
                carcass_thk=carcass_thk,
                lang=lang,
            )
            panels.append(ds)

            # --- Dno ---
            dno = _build_horizontal_panel(
                part_code=f"{prefix}-DNO",
                part_name=_s("bottom", lang),
                panel_w=inner_w,
                panel_d=d,
                lang=lang,
            )
            panels.append(dno)

            # --- Vrh (samo za wall, wall_upper, tall, tall_top) ---
            if _has_top_panel(zone):
                vrh = _build_horizontal_panel(
                    part_code=f"{prefix}-VRH",
                    part_name=_s("top", lang),
                    panel_w=inner_w,
                    panel_d=d,
                    lang=lang,
                )
                panels.append(vrh)

            # --- Leđa (bez rupa — samo oznaka) ---
            ledja = PanelDrillPlan(
                part_code=f"{prefix}-LEDJA",
                part_name=_s("back", lang),
                width_mm=inner_w,
                height_mm=h,
                holes=[],
                notes=["Leđa se urežu u žleb bočnih stranica."],
            )
            panels.append(ledja)

            # --- Front / vrata ---
            if has_doors_flag:
                # Proveri da li ima jedno ili dva krila
                two_doors = "DOORS" in tid and "W" not in tid  # gruba heuristika
                try:
                    two_doors = bool(params.get("two_doors", False)) or two_doors
                except Exception:
                    pass

                if two_doors:
                    door_w = inner_w // 2
                    for idx, (code_suffix, hinge_x) in enumerate(
                        [("FRONT-L", 22), ("FRONT-D", door_w - 22)]
                    ):
                        front = _build_front_panel(
                            part_code=f"{prefix}-{code_suffix}",
                            part_name=f"{_s('front', lang)} {'L' if idx == 0 else 'D'}",
                            door_w=door_w,
                            door_h=h,
                            hinge_side_offset=hinge_x,
                            lang=lang,
                        )
                        panels.append(front)
                else:
                    front = _build_front_panel(
                        part_code=f"{prefix}-FRONT",
                        part_name=_s("front", lang),
                        door_w=w,
                        door_h=h,
                        hinge_side_offset=22,
                        lang=lang,
                    )
                    panels.append(front)

            # --- Police ---
            for shelf_idx in range(1, n_shelves + 1):
                shelf = PanelDrillPlan(
                    part_code=f"{prefix}-POLICA-{shelf_idx}",
                    part_name=f"{_s('shelf', lang)} {shelf_idx}",
                    width_mm=inner_w,
                    height_mm=d - 20,   # polica je malo kraća od dubine (zazor)
                    holes=[],
                    notes=[_s("shelf_pin_note", lang)],
                )
                panels.append(shelf)

            # --- Koraci sklapanja ---
            assembly_steps: List[str] = [
                _s("step_dowels", lang),
                _s("step_join", lang),
                _s("step_square", lang),
                _s("step_screws", lang),
                _s("step_back", lang),
            ]
            if has_shelves_flag and n_shelves > 0:
                assembly_steps.append(_s("step_shelves", lang))
            if has_doors_flag:
                assembly_steps.append(_s("step_doors", lang))
            if has_drawers_flag:
                assembly_steps.append(_s("step_drawers", lang))

            # --- Napomene za radionicu ---
            workshop_notes: List[str] = [
                _s("workshop_philosophy", lang),
                f"Korpus: {carcass_thk}mm iverica",
            ]
            if has_doors_flag:
                workshop_notes.append(_s("hinge_note", lang))
            # Tiplovi su uvek prisutni
            workshop_notes.append(_s("dowel_note", lang))

            module_plan = ModuleDrillPlan(
                module_id=mid,
                module_label=label,
                template_id=tid,
                zone=zone,
                panels=panels,
                assembly_steps=assembly_steps,
                workshop_notes=workshop_notes,
            )
            result.append(module_plan)

        except Exception as exc:
            log.error(
                "drilling_plan: greška pri obradi modula id=%s tid=%s: %s",
                m.get("id"),
                m.get("template_id"),
                exc,
                exc_info=True,
            )
            continue

    return result
