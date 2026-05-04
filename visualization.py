# -*- coding: utf-8 -*-
# visualization.py
from __future__ import annotations

import math
import base64
from io import BytesIO
from typing import Any, Dict, List, Tuple, Optional
import unicodedata

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from cutlist import MANUFACTURING_PROFILES
from i18n import tr as _tr_i18n
from module_rules import default_shelf_count, dishwasher_installation_metrics


# =========================================================
# Helpers: manufacturing clearance / wall size / zone baselines
# =========================================================
def _profile_clearance_mm(kitchen: Dict[str, Any]) -> Tuple[int, int, int]:
    mfg = (kitchen.get("manufacturing", {}) or {})
    profile_key = mfg.get("profile", "EU_SRB")
    prof = MANUFACTURING_PROFILES.get(profile_key, MANUFACTURING_PROFILES.get("EU_SRB", {})) or {}

    left = int(mfg.get("mounting_tolerance_left_mm", prof.get("mounting_tolerance_left_mm", 5)))
    right = int(mfg.get("mounting_tolerance_right_mm", prof.get("mounting_tolerance_right_mm", 5)))

    if (
        ("mounting_tolerance_total_mm" in prof)
        and ("mounting_tolerance_left_mm" not in mfg)
        and ("mounting_tolerance_right_mm" not in mfg)
    ):
        total_prof = int(prof.get("mounting_tolerance_total_mm", left + right))
        left = total_prof // 2
        right = total_prof - left

    if ("mounting_tolerance_total_mm" in mfg) and (
        ("mounting_tolerance_left_mm" not in mfg) and ("mounting_tolerance_right_mm" not in mfg)
    ):
        total_usr = int(mfg.get("mounting_tolerance_total_mm", left + right))
        left = total_usr // 2
        right = total_usr - left

    total = left + right
    return left, right, total


def _wall_len_h(kitchen: Dict[str, Any]) -> Tuple[int, int]:
    wall = (kitchen.get("wall", {}) or {})
    wall_len = int(round(float(wall.get("length_mm", kitchen.get("wall_len", 300.0) * 10.0))))
    wall_h = int(round(float(wall.get("height_mm", kitchen.get("wall_h", 260.0) * 10.0))))
    return wall_len, wall_h


def _zone_baseline_and_height(kitchen: Dict[str, Any], zone: str) -> Tuple[int, int]:
    zones = (kitchen.get("zones", {}) or {})
    base_h = int(kitchen.get("base_korpus_h_mm", (zones.get("base", {}) or {}).get("height_mm", 720)))
    wall_h_elem = int((zones.get("wall", {}) or {}).get("height_mm", 720))
    wall_gap = int((zones.get("wall", {}) or {}).get("gap_from_base_mm", 800))
    tall_h = int((zones.get("tall", {}) or {}).get("height_mm", 2200))

    if "foot_height_mm" in kitchen:
        foot_mm = int(kitchen["foot_height_mm"])
    else:
        foot_mm = int(round(float(kitchen.get("foot_height", 0.0)) * 10.0))

    z = str(zone).lower().strip()
    if z == "wall":
        return wall_gap, wall_h_elem
    if z == "tall":
        return foot_mm, tall_h
    return foot_mm, base_h


def _get_foot_mm(kitchen: Dict[str, Any]) -> int:
    if "foot_height_mm" in kitchen:
        return int(kitchen["foot_height_mm"])
    return int(round(float(kitchen.get("foot_height", 0.0)) * 10.0))


def _y_for_tall_top(kitchen: Dict[str, Any], m: Dict[str, Any], mods: List[Dict[str, Any]]) -> int:
    foot_mm = _get_foot_mm(kitchen)
    x = int(m.get("x_mm", 0))
    w = int(m.get("w_mm", 0))
    for t in mods:
        if str(t.get("zone", "")).lower().strip() != "tall":
            continue
        tx = int(t.get("x_mm", 0))
        tw = int(t.get("w_mm", 0))
        if tx < (x + w) and (tx + tw) > x:
            tid = str(t.get("template_id", "")).upper()
            if "FRIDGE" in tid:
                return int(t.get("h_mm", 2100))
            return foot_mm + int(t.get("h_mm", 2100))
    wall_h = _wall_len_h(kitchen)[1]
    return wall_h - int(m.get("h_mm", 400)) - 50

def _y_for_wall_upper(kitchen: Dict[str, Any], m: Dict[str, Any], mods: List[Dict[str, Any]]) -> int:
    """Y koordinata wall_upper elementa = vrh wall elementa ispod njega."""
    x = int(m.get("x_mm", 0))
    w = int(m.get("w_mm", 0))
    wall_gap, _ = _zone_baseline_and_height(kitchen, "wall")
    for wm in mods:
        if str(wm.get("zone", "")).lower().strip() != "wall":
            continue
        wx = int(wm.get("x_mm", 0))
        ww = int(wm.get("w_mm", 0))
        # Preklapa li se X opseg wall_upper-a sa ovim wall elementom?
        if wx < (x + w) and (wx + ww) > x:
            return wall_gap + int(wm.get("h_mm", 720))
    # Fallback: postavi uz vrh wall zone
    wall_h = _wall_len_h(kitchen)[1]
    return wall_h - int(m.get("h_mm", 400)) - 50


# =========================================================
# Boje i stilovi po zoni
# =========================================================
# Neutralne čiste boje — bez artificijelnig tint-ova
# Material boja fronta se bira globalno (kitchen.front_color)
ZONE_FACE   = {"base": "#F8F8F6", "wall": "#F7F7F5", "tall": "#F8F8F6", "tall_top": "#F7F7F5", "wall_upper": "#F6F6F4"}
ZONE_EDGE   = {"base": "#2C2C2C", "wall": "#2C2C2C", "tall": "#2C2C2C", "tall_top": "#2C2C2C", "wall_upper": "#2C2C2C"}
ZONE_ACCENT = {"base": "#7A7A7A", "wall": "#7A7A7A", "tall": "#7A7A7A", "tall_top": "#7A7A7A", "wall_upper": "#7A7A7A"}
GLOBAL_FRONT_DEFAULT = "#FDFDFB"
APPLIANCE_COLOR      = "#B0B4BA"

# Boja bočne ivice (vidljiva siva sena za 3D efekat u 2D — katalog stil)
ZONE_SIDE_COLOR = "#8C8C8C"   # tamnija siva bočna ivica
ZONE_SIDE_WIDTH = 0.065       # ~6.5% širine elementa

FONT_DIM  = 8.5
FONT_ID   = 7
FONT_WALL = 11
FONT_LBL  = 8.5   # povećano 7.5→8.5 za bolju čitljivost elemenata


# ── Per-element front color helpers ──────────────────────────────────────────

def _darken_color(hex_color: str, factor: float = 0.5) -> str:
    """
    Tamni hex boju množenjem RGB vrijednosti sa faktorom.
    factor 0.0 = crna, 1.0 = originalna boja.
    """
    h = str(hex_color).lstrip("#")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return f"#{int(r * factor):02X}{int(g * factor):02X}{int(b * factor):02X}"
    except Exception:
        return str(hex_color)


def _contrast_accent(hex_color: str) -> str:
    """
    Vraća accent boju (za linije vrata, detalje) koja je vidljiva na hex_color pozadini.
    - Svjetla pozadina (brightness > 160) → tamne linije
    - Tamna pozadina (brightness < 60)   → svijetle linije
    - Srednja pozadina                   → potamnjena varijanta same boje
    """
    h = str(hex_color).lstrip("#")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        if brightness > 160:
            return "#2C2C2C"          # tamne linije na svijetloj pozadini
        elif brightness < 60:
            return "#C0C0C0"          # svijetle linije na tamnoj pozadini
        else:
            return _darken_color(hex_color, 0.42)   # potamnjena varijanta
    except Exception:
        return "#444444"


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _norm_text(v: Any) -> str:
    s = str(v or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def _ui_lang(kitchen: Dict[str, Any]) -> str:
    return str((kitchen or {}).get("language", "sr") or "sr").lower().strip()


def _wall_label(kitchen: Dict[str, Any], wall_len: int) -> str:
    return f"{wall_len}mm"


def _free_space_label(kitchen: Dict[str, Any], mm: int, *, arrow: str = "←") -> str:
    _suffix = "free" if _ui_lang(kitchen) == "en" else "slobodno"
    return f"{arrow} {mm}mm {_suffix}"


def _draw_l_layout_inset(
    ax: Any,
    kitchen: Dict[str, Any],
    room: Optional[Dict[str, Any]],
    *,
    active_wall: str,
) -> None:
    if str(kitchen.get("layout", kitchen.get("kitchen_layout", "")) or "").lower().strip() != "l_oblik":
        return
    if room is None:
        return
    try:
        _lang = str((kitchen or {}).get("language", "sr") or "sr").lower().strip()
        _wall_a_lbl = _tr_i18n("room.wall_a", _lang)
        _wall_b_lbl = _tr_i18n("room.wall_b", _lang)
        _walls = list((room.get("walls", []) or []))
        _wa = next((w for w in _walls if str(w.get("key", "")).upper() == "A"), None)
        _wb = next((w for w in _walls if str(w.get("key", "")).upper() == "B"), None)
        if _wa is None or _wb is None:
            return
        _la = float(_wa.get("length_mm", 0) or 0)
        _lb = float(_wb.get("length_mm", 0) or 0)
        if _la <= 0 or _lb <= 0:
            return
        _mods = kitchen.get("modules", []) or []
        iax = ax.inset_axes([0.77, 0.70, 0.20, 0.24])
        iax.set_facecolor("#F6F4EF")
        iax.set_xticks([])
        iax.set_yticks([])
        iax.set_title("L plan", fontsize=7, pad=2)
        _depth = 600.0
        iax.add_patch(plt.Rectangle((0, 0), _la, _depth, facecolor="#E3DED3", edgecolor="#4A4A4A", lw=0.8))
        iax.add_patch(plt.Rectangle((-_depth, 0), _depth, _lb, facecolor="#E3DED3", edgecolor="#4A4A4A", lw=0.8))
        def _add_corner_plan(_wk: str, _x: float, _w: float, _tid: str, _fc: str) -> None:
            _in = 18.0
            _dep = _depth - 36.0
            _arm = max(120.0, min(_dep, _w * 0.34))
            _diag = "DIAGONAL" in _tid
            if _wk == "A":
                _x0 = _x
                _x1 = _x + _w
                if _diag:
                    _pts = [
                        (_x0, _in),
                        (_x1, _in),
                        (_x1, _in + _dep * 0.52),
                        (_x0 + _arm * 0.56, _in + _dep),
                        (_x0, _in + _dep),
                    ]
                    iax.add_patch(mpatches.Polygon(_pts, closed=True, facecolor=_fc, edgecolor="#4A4A4A", lw=0.7))
                else:
                    _pts = [
                        (_x0, _in),
                        (_x1, _in),
                        (_x1, _in + _dep),
                        (_x0 + _arm, _in + _dep),
                        (_x0 + _arm, _in + _dep * 0.42),
                        (_x0, _in + _dep * 0.42),
                    ]
                    iax.add_patch(mpatches.Polygon(_pts, closed=True, facecolor=_fc, edgecolor="#4A4A4A", lw=0.7))
            elif _wk == "B":
                _y0 = _x
                _y1 = _x + _w
                if _diag:
                    _pts = [
                        (-_in, _y0),
                        (-_in, _y1),
                        (-_in - _dep * 0.52, _y1),
                        (-_depth, _y0 + _arm * 0.56),
                        (-_depth, _y0),
                    ]
                    iax.add_patch(mpatches.Polygon(_pts, closed=True, facecolor=_fc, edgecolor="#4A4A4A", lw=0.7))
                else:
                    _pts = [
                        (-_in, _y0),
                        (-_in, _y1),
                        (-_depth, _y1),
                        (-_depth, _y0 + _arm),
                        (-_in - _dep * 0.42, _y0 + _arm),
                        (-_in - _dep * 0.42, _y0),
                    ]
                    iax.add_patch(mpatches.Polygon(_pts, closed=True, facecolor=_fc, edgecolor="#4A4A4A", lw=0.7))

        for _m in _mods:
            _wk = str(_m.get("wall_key", "A")).upper()
            _x = float(_m.get("x_mm", 0) or 0)
            _w = float(_m.get("w_mm", 0) or 0)
            _z = str(_m.get("zone", "")).lower().strip()
            _tid = str(_m.get("template_id", "")).upper()
            if _w <= 0 or _z not in ("base", "tall", "wall", "wall_upper", "tall_top"):
                continue
            _fc = "#C7D9C8" if _wk == active_wall else "#D9D9D9"
            if "CORNER" in _tid and _wk in ("A", "B"):
                _add_corner_plan(_wk, _x, _w, _tid, _fc)
            elif _wk == "A":
                iax.add_patch(plt.Rectangle((_x, 18), _w, _depth - 36, facecolor=_fc, edgecolor="#4A4A4A", lw=0.6))
            elif _wk == "B":
                iax.add_patch(plt.Rectangle((-_depth + 18, _x), _depth - 36, _w, facecolor=_fc, edgecolor="#4A4A4A", lw=0.6))
        iax.plot([0, 0], [0, _depth], color="#1F2937", lw=1.0)
        iax.text(_la * 0.5, _depth + 45, _wall_a_lbl, ha="center", va="bottom", fontsize=6.5, color="#374151")
        iax.text(-_depth - 30, _lb * 0.5, _wall_b_lbl, ha="right", va="center", rotation=90, fontsize=6.5, color="#374151")
        iax.set_xlim(-_depth - 120, _la + 120)
        iax.set_ylim(-40, max(_lb, _depth) + 140)
        for _sp in iax.spines.values():
            _sp.set_edgecolor("#9A9488")
            _sp.set_linewidth(0.8)
    except Exception:
        return


def _has_front_panel(m: Dict[str, Any], etype: str) -> bool:
    """Da li element treba da prati globalnu boju fronta."""
    tid = str(m.get("template_id", "")).upper()

    # Specijalni 2D slučajevi:
    # - BASE_COOKING_UNIT ne sme obojiti ceo modul u boju fronta,
    #   samo donju fioku.
    # - Integrisani frižideri moraju pratiti boju fronta.
    if etype == "oven_hob" or tid in ("BASE_COOKING_UNIT", "OVEN_HOB"):
        return False
    if tid in ("TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "FRIDGE_UNDER"):
        return True

    params = m.get("params", {}) or {}
    if "has_front_panel" in params:
        return bool(params.get("has_front_panel"))

    lbl = str(m.get("label", "")).lower()
    txt = f"{tid} {lbl}"

    if etype in ("doors", "drawers", "doors_drawers", "glass", "liftup", "narrow", "corner", "pantry", "sink", "dishwasher"):
        return True
    if etype in ("open", "hob", "oven", "oven_micro", "hood", "microwave"):
        return False
    if etype == "fridge":
        if tid in ("TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "FRIDGE_UNDER"):
            return True
        if "FREESTANDING" in tid:
            return False
        if any(k in txt for k in ("integris", "ugradni", "under", "panel")):
            return True
        if any(k in txt for k in ("samostoj", "standalone", "side-by-side")):
            return False
        return False
    return True


# =========================================================
# Detekcija tipa elementa iz template_id / labele
# =========================================================
def _detect_type(m: Dict[str, Any]) -> str:
    """
    Vraca tip elementa:
      'drawers', 'sink', 'hob', 'oven', 'dishwasher', 'fridge',
      'corner', 'narrow', 'hood', 'microwave', 'glass', 'liftup',
      'open', 'doors_drawers', 'doors'
    """
    tid = str(m.get("template_id", "")).upper()
    lbl = str(m.get("label", "")).lower()
    features = m.get("params", {}) or {}
    # Iz template_id-a (pouzdan)
    if tid == "BASE_DISHWASHER_FREESTANDING": return "dishwasher_freestanding"
    if tid == "BASE_OVEN_HOB_FREESTANDING": return "oven_hob_freestanding"
    if "DISHWASHER"    in tid: return "dishwasher"
    if "END_PANEL"     in tid: return "panel"
    if "FILLER_PANEL"  in tid: return "panel"
    if "COOKING_UNIT"  in tid: return "oven_hob"
    if "OVEN_HOB"      in tid: return "oven_hob"
    if "HOB"           in tid: return "hob"
    if "SINK"          in tid: return "sink"
    if "OVEN_MICRO"    in tid: return "oven_micro"
    if "OVEN"          in tid: return "oven"
    if "FRIDGE_FREEZE" in tid: return "fridge"
    if "FRIDGE_UNDER"  in tid: return "fridge_under"   # donji dio ugradnog frižidera (base zona)
    if "FRIDGE"        in tid: return "fridge"
    if "HOOD"          in tid: return "hood"
    if "MICRO"         in tid: return "microwave"
    if "NARROW"        in tid: return "narrow"
    if "CORNER"        in tid: return "corner"
    if "GLASS"         in tid: return "glass"
    if "LIFTUP"        in tid: return "liftup"
    if "DRAWERS"       in tid: return "drawers"
    if "DOORS_DRAW"    in tid: return "doors_drawers"
    if "DOOR_DRAWER"   in tid: return "doors_drawers"
    if "OPEN"          in tid: return "open"
    if "PANTRY"        in tid: return "pantry"
    # Iz labele
    if any(k in lbl for k in ("fiok", "ladic", "drawer")): return "drawers"
    if any(k in lbl for k in ("sudoper", "cesm", "sink")):  return "sink"
    if any(k in lbl for k in ("ploc", "hob", "ringla")):    return "hob"
    if any(k in lbl for k in ("rerna", "oven")):            return "oven"
    if any(k in lbl for k in ("masina", "dishwash")):       return "dishwasher"
    if any(k in lbl for k in ("frizider", "fridge")):       return "fridge"
    if any(k in lbl for k in ("napa", "aspirat", "hood")):  return "hood"
    if any(k in lbl for k in ("mikrotal", "micro")):        return "microwave"
    if any(k in lbl for k in ("uski", "narrow")):           return "narrow"
    if any(k in lbl for k in ("coskast", "ugaon", "corner")): return "corner"
    if any(k in lbl for k in ("stakl", "glass")):           return "glass"
    if any(k in lbl for k in ("klapna", "podiz", "liftup")): return "liftup"
    if any(k in lbl for k in ("otvor", "polica", "open")):  return "open"
    if any(k in lbl for k in ("ostava", "spajz", "pant")):  return "pantry"
    return "doors"


def _is_sink(m: Optional[Dict[str, Any]]) -> bool:
    if not m:
        return False
    tid = str(m.get("template_id", "")).upper()
    params = m.get("params", {}) or {}
    return "SINK" in tid or bool(params.get("is_sink", False))


# =========================================================
# Pomoci za crtanje detalja
# =========================================================

# =========================================================
# Pomoci za crtanje detalja
#   RUČKE: moderan "bar" dizajn, fiksne dimenzije (ne zavise od širine elementa)
# =========================================================

# Ručke prate svetlinu fronta:
# - svetli frontovi -> tamne ručke
# - tamni frontovi  -> svetle ručke
HANDLE_FILL = "#111111"
HANDLE_EDGE = "#111111"

# Fiksne dimenzije u mm (naš 2D crtež je u mm koordinatama)
DOOR_HANDLE_V_LEN = 200.0
DOOR_HANDLE_V_W   = 20.0

DRAWER_HANDLE_H_LEN = 200.0
DRAWER_HANDLE_H_H   = 8.0

OVEN_HANDLE_H_LEN = 220.0
OVEN_HANDLE_H_H   = 9.0

FRIDGE_HANDLE_V_LEN = 380.0
FRIDGE_HANDLE_V_W   = 20.0

HANDLE_ROUNDING = 3.0


def _handle_palette_for_face(hex_color: str) -> tuple[str, str]:
    h = str(hex_color or "").lstrip("#")
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        if brightness >= 150:
            return ("#111111", "#111111")
        return ("#E7E9ED", "#C9CED6")
    except Exception:
        return ("#111111", "#111111")


def _set_handle_palette(face_color: str) -> None:
    global HANDLE_FILL, HANDLE_EDGE
    HANDLE_FILL, HANDLE_EDGE = _handle_palette_for_face(face_color)

def _bar_handle_h(ax, cx: float, cy: float, length: float, height: float, technical: bool = False) -> None:
    face = HANDLE_FILL if not technical else "none"
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - length/2, cy - height/2),
        length, height,
        boxstyle=f"round,pad=0.02,rounding_size={HANDLE_ROUNDING}",
        facecolor=face,
        edgecolor=HANDLE_EDGE,
        linewidth=0.8 if not technical else 0.6,
        zorder=25
    ))

def _bar_handle_v(ax, cx: float, cy: float, length: float, width: float, technical: bool = False) -> None:
    face = HANDLE_FILL if not technical else "none"
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - width/2, cy - length/2),
        width, length,
        boxstyle=f"round,pad=0.02,rounding_size={HANDLE_ROUNDING}",
        facecolor=face,
        edgecolor=HANDLE_EDGE,
        linewidth=0.8 if not technical else 0.6,
        zorder=25
    ))

def _handle_h(ax, cx: float, cy: float, hw: float = 22, technical: bool = False) -> None:
    """Horizontalna ručica — uvek ista veličina (za fioke / rernu)."""
    # hw se IGNORIŠE namerno (fiksna dimenzija po zahtevu)
    _bar_handle_h(ax, cx, cy, DRAWER_HANDLE_H_LEN, DRAWER_HANDLE_H_H, technical=technical)

def _handle_h_oven(ax, cx: float, cy: float, technical: bool = False) -> None:
    """Horizontalna ručka rerne — fiksna."""
    _bar_handle_h(ax, cx, cy, OVEN_HANDLE_H_LEN, OVEN_HANDLE_H_H, technical=technical)

def _handle_v(ax, cx: float, cy: float, hh: float = 40, technical: bool = False) -> None:
    """Vertikalna ručica — uvek ista veličina (za vrata)."""
    # hh se IGNORIŠE namerno (fiksna dimenzija po zahtevu)
    _bar_handle_v(ax, cx, cy, DOOR_HANDLE_V_LEN, DOOR_HANDLE_V_W, technical=technical)

def _handle_v_fridge(ax, cx: float, cy: float, technical: bool = False) -> None:
    """Vertikalna ručka frižidera — duža."""
    _bar_handle_v(ax, cx, cy, FRIDGE_HANDLE_V_LEN, FRIDGE_HANDLE_V_W, technical=technical)

def _clamp_handle_cy(y: float, h: float, cy: float) -> float:
    """Osiguraj da vertikalna ručka (fiksne dužine) ostane unutar elementa."""
    handle_half = DOOR_HANDLE_V_LEN / 2.0
    return max(y + handle_half + 10, min(cy, y + h - handle_half - 10))

def _inset_rect(ax, x, y, w, h, inset, face, edge, lw=0.8, alpha=1.0, ls="-") -> None:
    i = inset
    rw = max(2, w - 2 * i)
    rh = max(2, h - 2 * i)
    ax.add_patch(plt.Rectangle(
        (x + i, y + i), rw, rh,
        facecolor=face, edgecolor=edge, linewidth=lw, alpha=alpha,
        linestyle=ls, zorder=11
    ))


# =========================================================
# Crtaci za svaki tip elementa (katalog prikaz)
# =========================================================


def _draw_base_doors(ax, x, y, w, h, accent, face, technical, m=None):
    """Donji sa 1 ili 2 vrata — okvir + VERTIKALNE ručke (fiksne)."""
    mid = x + w / 2
    door_inset = max(6, int(min(w, h) * 0.05))
    handle_edge_off = 30.0  # udaljenost ivice ručke od spoja / unutrašnjeg okvira
    handle_side = str((m or {}).get("params", {}).get("handle_side", "right")).lower()

    tid = str(m.get("template_id", "")).upper() if m else ""
    force_one = "1DOOR" in tid
    force_two = ("2DOOR" in tid) or ("DOORS" in tid and "1DOOR" not in tid)
    if (not force_one and (force_two or w > 650)):
        # 2 krila — vertikalna linija razdvajanja
        ax.plot([mid, mid], [y, y + h], color=accent, linewidth=0.8, zorder=12)
        # Okviri vrata
        ax.add_patch(plt.Rectangle(
            (x + door_inset, y + door_inset),
            max(2, mid - x - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.52, zorder=11
        ))
        ax.add_patch(plt.Rectangle(
            (mid + door_inset, y + door_inset),
            max(2, w - (mid - x) - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.52, zorder=11
        ))

        # Ručke: 30mm od spoja ka spolja
        handle_cy = _clamp_handle_cy(y, h, y + h - 50 - DOOR_HANDLE_V_LEN / 2)
        seam_off = handle_edge_off + DOOR_HANDLE_V_W / 2.0
        _handle_v(ax, mid - seam_off, handle_cy, technical=technical)
        _handle_v(ax, mid + seam_off, handle_cy, technical=technical)

    else:
        # 1 krilo — okvir
        ax.add_patch(plt.Rectangle(
            (x + door_inset, y + door_inset), max(2, w - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.52, zorder=11
        ))

        # Ručka: 50mm od gornje ivice, 30mm od unutrašnjeg okvira (levo/desno)
        handle_cy = _clamp_handle_cy(y, h, y + h - 50 - DOOR_HANDLE_V_LEN / 2)
        if handle_side == "left":
            handle_cx = (x + door_inset) + (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        else:
            handle_cx = (x + w - door_inset) - (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        _handle_v(ax, handle_cx, handle_cy, technical=technical)

    _draw_shelf_hints(ax, x, y, w, h, accent, face, technical, m=m, zone_hint='base')

# ── Drawer gap constant & segment computation ─────────────────────────────
_FRONT_GAP_MM = 2  # mm gap at top, bottom and between each drawer front


def _compute_drawer_segments(h_total: int, weights, gap_mm: int = _FRONT_GAP_MM,
                              min_drawer_h: int = 60) -> list:
    """Convert weights (top-to-bottom, index 0 = top drawer) into actual draw
    heights (mm) that fill h_total exactly with gap_mm gaps around/between.

    Gap layout (top → bottom in visual space):
        top_gap | drawer[0] | gap | drawer[1] | gap | ... | drawer[N-1] | bottom_gap
    Total gaps = (N+1) * gap_mm.
    """
    N = len(weights)
    if N == 0:
        return []
    W = [max(0.01, float(w)) for w in weights]
    H_usable = max(N * min_drawer_h, h_total - gap_mm * (N + 1))
    sum_W = sum(W)
    segs = [round(H_usable * w / sum_W) for w in W]
    # Fix rounding remainder on last segment
    diff = H_usable - sum(segs)
    segs[-1] = max(min_drawer_h, segs[-1] + diff)
    return segs


def _draw_base_drawers(ax, x, y, w, h, accent, technical, n_drawers=3,
                       drawer_heights=None, gap_mm: int = _FRONT_GAP_MM):
    """Donji sa fiokama.
    drawer_heights: lista težina/visina odozgo prema dolje (index 0 = gornja fioka).
    Tretiraju se kao težine — normalizuju se automatski sa razmacima gap_mm.
    Fallback: jednake težine.
    """
    weights = drawer_heights if (drawer_heights and len(drawer_heights) > 0) else [1] * n_drawers
    segs = _compute_drawer_segments(h, weights, gap_mm=gap_mm)
    fsize = max(4, int(w * 0.011))
    # Draw top-to-bottom: start from top of element zone (y+h), move down
    cursor_y = y + h - gap_mm  # below the top gap
    for i, dh in enumerate(segs):
        cursor_y -= dh  # descend by this drawer's height
        _handle_h(ax, x + w / 2, cursor_y + dh * 0.5, hw=w * 0.35, technical=technical)
        if technical:
            ax.text(x + w - 5, cursor_y + dh * 0.5, f"F{i+1}",
                    fontsize=max(3.5, fsize - 1), ha='right', va='center',
                    color=accent, alpha=0.28, zorder=13)
        if i < len(segs) - 1:
            # Dividing line at the bottom edge of this drawer
            ax.plot([x, x + w], [cursor_y, cursor_y], color=accent, linewidth=0.8, zorder=12)
            cursor_y -= gap_mm  # skip the between-gap


def _draw_base_doors_drawers(ax, x, y, w, h, accent, face, technical, params=None, m=None):
    """Donji kombinovani: dole DVOJA vrata, gore fioka (standardni raspored).
    Čita door_height i drawer_heights iz params ako postoje.
    """
    params = params or {}
    drawer_heights = params.get("drawer_heights", None)
    door_height    = params.get("door_height", None)

    if door_height is not None:
        door_h = int(door_height)
    elif drawer_heights and len(drawer_heights) > 0:
        door_h = h - int(drawer_heights[0])
    else:
        door_h = int(h * 0.72)

    drawer_h = h - door_h
    door_y   = y
    drawer_y = y + door_h
    mid      = x + w / 2

    # ── Linija između vrata i fioke ───────────────────────────────────────────
    ax.plot([x, x + w], [drawer_y, drawer_y], color=accent, linewidth=0.8, zorder=12)

    # ── 2 vrata (uvek 2 krila — standardni dizajn) ────────────────────────────
    door_inset = max(6, int(min(w, door_h) * 0.05))

    # Vertikalna linija razdvajanja između krila
    ax.plot([mid, mid], [door_y, drawer_y], color=accent, linewidth=0.8, zorder=12)

    # Okviri krila
    ax.add_patch(plt.Rectangle(
        (x + door_inset, door_y + door_inset),
        max(2, mid - x - 2 * door_inset), max(2, door_h - 2 * door_inset),
        facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.52, zorder=11,
    ))
    ax.add_patch(plt.Rectangle(
        (mid + door_inset, door_y + door_inset),
        max(2, w - (mid - x) - 2 * door_inset), max(2, door_h - 2 * door_inset),
        facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.52, zorder=11,
    ))

    # Ručke vrata — vertikalne, okrenute prema sredini (30 mm od spoja)
    handle_cy   = _clamp_handle_cy(door_y, door_h, door_y + door_h - 50 - DOOR_HANDLE_V_LEN / 2)
    seam_off    = 30.0 + DOOR_HANDLE_V_W / 2.0
    _handle_v(ax, mid - seam_off, handle_cy, technical=technical)
    _handle_v(ax, mid + seam_off, handle_cy, technical=technical)

    # ── Ručica na fioci (gap-aware: small top & bottom gap within drawer zone) ─
    _gap = _FRONT_GAP_MM
    _vdh = max(20, drawer_h - 2 * _gap)   # visible drawer height minus gaps
    _vdy = drawer_y + _gap                 # visual start (above the dividing line + gap)
    _handle_h(ax, mid, _vdy + _vdh * 0.5, hw=w * 0.35, technical=technical)


def _draw_sink(ax, x, y, w, h, accent, face, technical, worktop_thk_mm: int = 38):
    """Sudopera — front kao 2-door base, uz vidljivu česmu.

    Napomena: vrata se crtaju odvojeno kroz _draw_base_doors() poziv u glavnoj
    petlji — ovde crtamo SAMO česmu iznad radne ploče.
    Duple dveri se ne crtaju.
    """
    top = y + h
    wt  = float(worktop_thk_mm)
    if wt <= 0:
        return

    # ── Česma iznad radne ploče — realistični gooseneck ──────────────────────
    base_y = top + wt
    # Pozicija baze česme — blago levo od centra (standardno za montažu)
    faucet_base_x = x + w * 0.48

    # Boje — inox / chrome ton
    C_DARK  = "#787878"
    C_MID   = "#A0A0A0"
    C_LIGHT = "#D4D4D4"

    # Debljine linija — srazmerne, tanje od starog koda
    LW_BODY = 2.8    # cev tela
    LW_BASE = 4.5    # baza (širi prihvat)
    LW_SPOUT= 2.2    # izlazna cev (malo tanja)

    # ── 1. Baza — kratki stub koji izlazi iz radne ploče ─────────────────────
    base_stub = 16
    ax.plot([faucet_base_x, faucet_base_x],
            [base_y, base_y + base_stub],
            color=C_DARK, linewidth=LW_BASE * 1.5,
            solid_capstyle="butt", zorder=17)

    # ── 2. Vertikalno telo gooseneck česme ───────────────────────────────────
    stem_h   = 120
    stem_top = base_y + base_stub + stem_h
    ax.plot([faucet_base_x, faucet_base_x],
            [base_y + base_stub, stem_top],
            color=C_DARK, linewidth=LW_BODY,
            solid_capstyle="butt", zorder=17)

    # ── 3. Ručica (single-lever) — horizontalna poluga na ~40% visine tela ───
    lever_y   = base_y + base_stub + stem_h * 0.40
    lever_len = 26
    ax.plot([faucet_base_x - 2, faucet_base_x + lever_len],
            [lever_y, lever_y],
            color=C_MID, linewidth=LW_BODY * 0.9,
            solid_capstyle="round", zorder=18)
    # Kuglasti završetak ručice
    ax.add_patch(plt.Circle(
        (faucet_base_x + lever_len, lever_y), 4.0,
        facecolor=C_MID, edgecolor=C_DARK, linewidth=0.6, zorder=19
    ))

    # ── 4. Gooseneck luk — kompaktni polukrug ────────────────────────────────
    arc_r  = 20
    arc_cx = faucet_base_x + arc_r
    arc_top_y = stem_top
    theta = np.linspace(np.pi, 0, 30)   # polukrug: levo → gore → desno
    ax.plot(arc_cx + arc_r * np.cos(theta),
            arc_top_y + arc_r * np.sin(theta),
            color=C_DARK, linewidth=LW_BODY,
            solid_capstyle="round", zorder=17)

    # ── 5. Kratki horizontalni segment pre spusta ─────────────────────────────
    horiz_y  = arc_top_y           # vrh luka = arc_top_y (sin=0 na krajevima)
    spout_x  = arc_cx + arc_r      # desni kraj luka

    # ── 6. Izlazna cev spusta se nadole ──────────────────────────────────────
    spout_len = 38
    spout_bot = horiz_y - spout_len
    ax.plot([spout_x, spout_x],
            [horiz_y, spout_bot],
            color=C_DARK, linewidth=LW_SPOUT,
            solid_capstyle="butt", zorder=17)

    # ── 7. Aerator — kratka šira kapica na vrhu izlaza ───────────────────────
    aerator_w = 6
    ax.add_patch(plt.Rectangle(
        (spout_x - aerator_w / 2, spout_bot - 7), aerator_w, 7,
        facecolor=C_MID, edgecolor=C_DARK, linewidth=0.7, zorder=18
    ))

    # ── 8. Kap vode — sićušna, diskretna ─────────────────────────────────────
    ax.add_patch(plt.Circle(
        (spout_x, spout_bot - 11),
        2.2,
        facecolor="#BBDDF0" if not technical else "none",
        edgecolor="#6699AA", linewidth=0.5, zorder=19
    ))

    # ── 9. Chrome sjaj na telu (samo katalog) ────────────────────────────────
    if not technical:
        ax.plot([faucet_base_x - LW_BODY * 0.25, faucet_base_x - LW_BODY * 0.25],
                [base_y + base_stub + 8, stem_top - 8],
                color=C_LIGHT, linewidth=max(0.5, LW_BODY * 0.25),
                solid_capstyle="round", zorder=20)




def _draw_hob(ax, x, y, w, h, accent, face, technical):
    """Ploca za kuvanje: 4 ringlje (arhitektonski tlocrt)."""
    # Pozadinska ploča (tamna, staklena keramička ili inox)
    hob_inset = max(4, int(min(w, h) * 0.03))
    ax.add_patch(plt.Rectangle(
        (x + hob_inset, y + hob_inset), w - 2 * hob_inset, h - 2 * hob_inset,
        facecolor="#2E2E2E" if not technical else "none",
        edgecolor="#1A1A1A" if not technical else accent,
        linewidth=0.9, zorder=12
    ))

    # 4 ringlje — 2 reda × 2 kolone
    r_outer = max(8, min(w * 0.14, h * 0.20))
    r_mid   = r_outer * 0.68
    r_inner = r_outer * 0.35
    col_gap = w / 3.0
    row_gap = h / 3.0
    positions = [
        (x + col_gap,         y + row_gap),
        (x + 2 * col_gap,     y + row_gap),
        (x + col_gap,         y + 2 * row_gap),
        (x + 2 * col_gap,     y + 2 * row_gap),
    ]
    for (cx, cy) in positions:
        # Spoljni prsten — svetlosivi (grejač)
        ax.add_patch(plt.Circle((cx, cy), r_outer,
                                facecolor="#C8C0B8" if not technical else "none",
                                edgecolor="#888888" if not technical else accent,
                                linewidth=0.8, zorder=14))
        # Srednji prsten — malo tamniji
        ax.add_patch(plt.Circle((cx, cy), r_mid,
                                facecolor="#A8A098" if not technical else "none",
                                edgecolor="#666666" if not technical else accent,
                                linewidth=0.5, zorder=15))
        # Unutrašnji krug — tamno (centar ringlje)
        ax.add_patch(plt.Circle((cx, cy), r_inner,
                                facecolor="#484038" if not technical else "none",
                                edgecolor="#333333" if not technical else accent,
                                linewidth=0.4, zorder=16))

    # Komandni panel (malo kolo na dnu) — simbolizuje dugmiće
    knob_y = y + h * 0.92
    knob_r = max(3, int(w * 0.025))
    knob_spacing = w / 5.0
    for i in range(4):
        kx = x + knob_spacing * (i + 1)
        ax.add_patch(plt.Circle((kx, knob_y), knob_r,
                                facecolor="#888888" if not technical else "none",
                                edgecolor="#555555", linewidth=0.5, zorder=17))


def _draw_oven(ax, x, y, w, h, accent, face, technical):
    """Ugradna rerna: prozor + dugmici + rucica.
    Standardni raspored (odozdo): dugmici dole → rucica → prozor.
    """
    inset = max(8, int(w * 0.08))
    win_x = x + inset
    win_w = w - 2 * inset

    # Dugmici — pri dnu rerne (y + 8%)
    btn_y = y + int(h * 0.08)
    btn_r = max(3, int(win_w * 0.04))
    n_btn = 4
    btn_spacing = win_w / (n_btn + 1)
    for i in range(n_btn):
        bx = win_x + btn_spacing * (i + 1)
        ax.add_patch(plt.Circle((bx, btn_y), btn_r,
                                facecolor="#AAAAAA" if not technical else "none",
                                edgecolor="#444444", linewidth=0.6, zorder=15))

    # Rucica — iznad dugmica (y + 20%)
    handle_y = y + int(h * 0.20)
    _handle_h_oven(ax, x + w / 2, handle_y, technical=technical)

    # Prozor rerne — zauzima gornji deo (od 30% do 92%)
    win_y = y + int(h * 0.30)
    win_h = int(h * 0.62)
    ax.add_patch(plt.Rectangle(
        (win_x, win_y), win_w, win_h,
        facecolor="#2A2A2A" if not technical else "none",
        edgecolor="#555555", linewidth=1.0, zorder=14
    ))
    # Unutrasnjost prozora
    if not technical:
        ax.add_patch(plt.Rectangle(
            (win_x + 4, win_y + 4), win_w - 8, win_h - 8,
            facecolor="#1A1A1A", edgecolor="none", zorder=15
        ))
        # Sjaj stakla
        ax.add_patch(plt.Rectangle(
            (win_x + 6, win_y + 6), max(4, win_w // 5), max(4, win_h // 4),
            facecolor="#5A5A5A", edgecolor="none", alpha=0.5, zorder=16
        ))

def _draw_oven_micro(ax, x, y, w, h, accent, face, technical):
    """Kolona: rerna dole + mikrotalasna gore."""
    split = int(h * 0.52)
    # Gornji deo - mikrotalasna
    micro_y = y + split
    micro_h = h - split
    ax.plot([x, x + w], [micro_y, micro_y], color=accent, linewidth=0.9, zorder=13)
    # Mikrotalasna
    _draw_microwave_inner(ax, x, micro_y, w, micro_h, accent, face, technical)
    # Rerna dole
    _draw_oven(ax, x, y, w, split, accent, face, technical)


def _draw_tall_oven(ax, x, y, w, h, accent, face, technical):
    """Visoka kolona: rerna u sredini + servisni/front panel pri dnu."""
    service_h = max(120, min(220, int(h * 0.20)))
    oven_h = max(380, min(620, int(h * 0.34)))
    top_fill_h = max(80, h - service_h - oven_h)

    service_y = y
    oven_y = y + service_h

    ax.add_patch(plt.Rectangle(
        (x + 3, service_y + 3), max(4, w - 6), max(4, service_h - 6),
        facecolor=face if not technical else "none",
        edgecolor=accent, linewidth=0.9, zorder=12
    ))
    _handle_h(ax, x + w / 2, service_y + service_h * 0.55, hw=w * 0.34, technical=technical)
    ax.plot([x, x + w], [oven_y, oven_y], color=accent, linewidth=0.8, zorder=13)

    _draw_oven(ax, x, oven_y, w, oven_h, accent, face, technical)

    if top_fill_h > 20:
        top_y = oven_y + oven_h
        ax.plot([x, x + w], [top_y, top_y], color=accent, linewidth=0.7, alpha=0.6, zorder=13)


def _draw_tall_oven_micro(ax, x, y, w, h, accent, face, technical):
    """Visoka kolona: servisni/front panel dole, rerna u sredini, mikrotalasna gore."""
    service_h = max(120, min(220, int(h * 0.18)))
    oven_h = max(360, min(560, int(h * 0.28)))
    micro_h = max(220, min(360, int(h * 0.20)))

    service_y = y
    oven_y = y + service_h
    micro_y = oven_y + oven_h

    ax.add_patch(plt.Rectangle(
        (x + 3, service_y + 3), max(4, w - 6), max(4, service_h - 6),
        facecolor=face if not technical else "none",
        edgecolor=accent, linewidth=0.9, zorder=12
    ))
    _handle_h(ax, x + w / 2, service_y + service_h * 0.55, hw=w * 0.34, technical=technical)
    ax.plot([x, x + w], [oven_y, oven_y], color=accent, linewidth=0.8, zorder=13)

    _draw_oven(ax, x, oven_y, w, oven_h, accent, face, technical)
    ax.plot([x, x + w], [micro_y, micro_y], color=accent, linewidth=0.8, zorder=13)
    _draw_microwave_inner(ax, x, micro_y, w, min(h - (micro_y - y), micro_h), accent, face, technical)


def _draw_oven_hob(ax, x, y, w, h, accent, face, technical,
                   drawer_face: str | None = None,
                   has_drawer: bool = True, worktop_thk_mm: int = 38):
    """
    Industrijski standard BASE_OVEN_HOB:
      - Dno: fioka sa horizontalnom ručicom
      - Gore: ugradna rerna — komande gore, ručka pri vrhu vrata, staklo ispod
      - U front tehničkom prikazu ne crtamo ploču gore kao zaseban tamni blok.
    """
    # --- 1. FIOKA (dno) ---
    drawer_h = min(150, max(120, int(h * 0.18)))
    oven_h   = h - drawer_h
    drawer_y = y
    oven_y   = y + drawer_h

    # Front fioke mora da prati boju fronta, ne boju uredjaja.
    _drawer_face = drawer_face if drawer_face else face
    ax.add_patch(plt.Rectangle(
        (x + 2, drawer_y + 2), max(4, w - 4), max(4, drawer_h - 4),
        facecolor=_drawer_face if not technical else "none",
        edgecolor=accent, linewidth=0.9, zorder=12
    ))
    ax.plot([x, x + w], [oven_y, oven_y], color=accent, linewidth=0.9, zorder=13)
    _handle_h(ax, x + w / 2, drawer_y + drawer_h * 0.5, hw=w * 0.42, technical=technical)

    # --- 2. RERNA ---
    oven_margin = max(18, int(w * 0.04))
    ox  = x + oven_margin
    ow  = w - 2 * oven_margin
    oh  = oven_h

    # Ručica rerne — pri vrhu vrata (standardno otvaranje na dole)
    _handle_h_oven(ax, ox + ow / 2, oven_y + int(oh * 0.80), technical=technical)

    # Razdvajanje između ploče i rerne (shadow gap)
    gap_y = y + h
    ax.plot([x, x + w], [gap_y, gap_y], color=accent, linewidth=0.6, zorder=16)

    # Mali dugmici — u redu pri vrhu rerne (spušteno ispod ploče)
    win_inset = max(5, int(ow * 0.06))
    win_x = ox + win_inset
    win_w = ow - 2 * win_inset
    btn_r = max(4, int(win_w * 0.035))
    btn_y = oven_y + int(oh * 0.90)
    bsp   = win_w / 5   # 4 dugmica na 5 intervala
    for i in range(4):
        ax.add_patch(plt.Circle((win_x + bsp * (i + 1), btn_y), btn_r,
            facecolor="#AAAAAA" if not technical else "none",
            edgecolor="#555555", linewidth=0.5, zorder=15))

    # Prozor rerne — ispod komandi i ručke
    win_y = oven_y + int(oh * 0.20)
    win_h = int(oh * 0.52)
    ax.add_patch(plt.Rectangle(
        (win_x, win_y), win_w, win_h,
        facecolor="#2A2A2A" if not technical else "none",
        edgecolor="#555555", linewidth=1.0, zorder=14))
    if not technical:
        ax.add_patch(plt.Rectangle(
            (win_x + 4, win_y + 4), win_w - 8, win_h - 8,
            facecolor="#1A1A1A", edgecolor="none", zorder=15))
        ax.add_patch(plt.Rectangle(
            (win_x + 6, win_y + 6), max(4, win_w // 5), max(4, win_h // 4),
            facecolor="#5A5A5A", edgecolor="none", alpha=0.5, zorder=16))

    # --- 3. HOB ZONA ---
    # U tehničkom frontalnom prikazu ne crtamo ploču za kuvanje ovde,
    # da bi radna ploča izgledala kao jedinstvena linija preko svih elemenata.


def _draw_microwave_inner(ax, x, y, w, h, accent, face, technical):
    """Simboli mikrotalasne."""
    inset = max(6, int(w * 0.06))
    win_y = y + int(h * 0.15)
    win_h = int(h * 0.55)
    win_x = x + inset
    win_w = int(w * 0.65)
    ax.add_patch(plt.Rectangle(
        (win_x, win_y), win_w, win_h,
        facecolor="#2A2A2A" if not technical else "none",
        edgecolor="#555555", linewidth=0.8, zorder=14
    ))
    if not technical:
        ax.add_patch(plt.Rectangle(
            (win_x + 4, win_y + 4), max(6, win_w - 8), max(6, win_h - 8),
            facecolor="#171717", edgecolor="none", zorder=15
        ))
        ax.add_patch(plt.Rectangle(
            (win_x + 6, win_y + 6), max(4, win_w * 0.22), max(4, win_h * 0.20),
            facecolor="#5B5B5B", edgecolor="none", alpha=0.45, zorder=16
        ))
    # Kontrolni panel desno
    panel_x = win_x + win_w + 4
    panel_w = w - 2 * inset - win_w - 4
    if panel_w > 8:
        ax.add_patch(plt.Rectangle(
            (panel_x, win_y), panel_w, win_h,
            facecolor="#D7DCE2" if not technical else "none",
            edgecolor=accent, linewidth=0.6, alpha=0.72, zorder=14
        ))
        for i in range(4):
            by = win_y + int(win_h * (i + 0.5) / 4)
            ax.add_patch(plt.Circle((panel_x + panel_w / 2, by), max(2, panel_w * 0.25),
                                    facecolor="#AAAAAA" if not technical else "none",
                                    edgecolor="#444444", linewidth=0.5, zorder=15))


def _draw_microwave(ax, x, y, w, h, accent, face, technical):
    """Gornji element sa mikrotalasnom."""
    _inset_rect(ax, x, y, w, h, max(6, int(w * 0.06)),
                face, accent, lw=0.8)
    _draw_microwave_inner(ax, x, y, w, h, accent, face, technical)



def _draw_dishwasher(ax, x, y, w, h, accent, face, technical, *, kitchen=None, m=None):
    """Mašina za sudove: integrisani front panel (boja fronta), kontrolna traka, ručka."""
    _k = kitchen if kitchen is not None else globals().get("state", None).kitchen if globals().get("state", None) is not None else {}
    _dish = dishwasher_installation_metrics(_k, m or {"h_mm": h})
    _raised = bool(_dish.get("dishwasher_raised_mode", False))
    _front_h = float(_dish.get("dishwasher_front_height", 720))
    _lower_fill_h = float(_dish.get("dishwasher_lower_filler_height", 0))
    inset = max(5, int(w * 0.05))
    mid = x + w / 2

    if _raised and _lower_fill_h > 0:
        _front_vis_h = max(40.0, min(h, _front_h))
        _filler_vis_h = max(20.0, min(h - _front_vis_h, _lower_fill_h))
        _front_y = y + _filler_vis_h

        ax.add_patch(plt.Rectangle(
            (x + inset, _front_y + inset),
            w - 2 * inset, max(2.0, _front_vis_h - 2 * inset),
            facecolor=face if not technical else "none",
            edgecolor=accent,
            linewidth=0.9 if not technical else 0.8,
            alpha=0.95 if not technical else 0.55,
            zorder=12,
        ))
        ax.add_patch(plt.Rectangle(
            (x + inset, y + inset),
            w - 2 * inset, max(2.0, _filler_vis_h - 2 * inset),
            facecolor=face if not technical else "none",
            edgecolor=accent,
            linewidth=0.75,
            alpha=0.88 if not technical else 0.50,
            zorder=11,
        ))
        ax.plot([x, x + w], [_front_y, _front_y], color=accent, linewidth=0.75, zorder=13)

        ctrl_h = max(10, int(_front_vis_h * 0.10))
        ctrl_y = _front_y + _front_vis_h - inset - ctrl_h
        ax.add_patch(plt.Rectangle(
            (x + inset, ctrl_y),
            w - 2 * inset, ctrl_h,
            facecolor="#D7DCE2" if not technical else "none",
            edgecolor=accent, linewidth=0.7, alpha=0.75, zorder=13
        ))
        if not technical:
            ax.add_patch(plt.Rectangle(
                (x + inset + 4, ctrl_y + 2), max(8, (w - 2 * inset) * 0.34), max(3, ctrl_h - 4),
                facecolor="#AAB3BD", edgecolor="none", alpha=0.45, zorder=14
            ))
            led_y = ctrl_y + ctrl_h * 0.55
            for i, col in enumerate(["#00CC66", "#FF9900", "#CC3300"]):
                lx = x + inset + (w - 2 * inset) * (0.75 + i * 0.07)
                ax.add_patch(plt.Circle((lx, led_y), max(2, int(ctrl_h * 0.20)),
                                        facecolor=col, edgecolor="none", zorder=15))

        handle_cx = mid
        handle_cy = ctrl_y - 28.0
        _handle_h_oven(ax, handle_cx, handle_cy, technical=technical)
        ax.plot([x + inset + 5, x + w - inset - 5], [ctrl_y - 6, ctrl_y - 6],
                color=accent, linewidth=0.45, alpha=0.35, zorder=14)

        ax.text(mid, _front_y + _front_vis_h * 0.42, "DW",
                fontsize=max(7, int(w * 0.052)),
                color="#666666" if not technical else "#999999",
                ha="center", va="center", alpha=0.85, zorder=16)
        return

    # Glavna vrata (integrisani front u boji kuhinje)
    ax.add_patch(plt.Rectangle(
        (x + inset, y + inset),
        w - 2 * inset, h - 2 * inset,
        facecolor=face if not technical else "none",
        edgecolor=accent,
        linewidth=0.9 if not technical else 0.8,
        alpha=0.95 if not technical else 0.55,
        zorder=12,
    ))

    # Kontrolna traka — pri vrhu
    ctrl_h = max(10, int(h * 0.10))
    ctrl_y = y + h - inset - ctrl_h
    ax.add_patch(plt.Rectangle(
        (x + inset, ctrl_y),
        w - 2 * inset, ctrl_h,
        facecolor="#D7DCE2" if not technical else "none",
        edgecolor=accent, linewidth=0.7, alpha=0.75, zorder=13
    ))
    if not technical:
        ax.add_patch(plt.Rectangle(
            (x + inset + 4, ctrl_y + 2), max(8, (w - 2 * inset) * 0.34), max(3, ctrl_h - 4),
            facecolor="#AAB3BD", edgecolor="none", alpha=0.45, zorder=14
        ))

    # LED indikatori
    if not technical:
        led_y = ctrl_y + ctrl_h * 0.55
        for i, col in enumerate(["#00CC66", "#FF9900", "#CC3300"]):
            lx = x + inset + (w - 2 * inset) * (0.75 + i * 0.07)
            ax.add_patch(plt.Circle((lx, led_y), max(2, int(ctrl_h * 0.20)),
                                    facecolor=col, edgecolor="none", zorder=15))

    # Ručka — HORIZONTALNA pri vrhu vrata (mašina za suđe se otvara prema dolje,
    # ručka je gore u sredini, identično rernu/oven)
    handle_cx = mid
    handle_cy = ctrl_y - 28.0  # 28mm ispod donje ivice kontrolne trake
    _handle_h_oven(ax, handle_cx, handle_cy, technical=technical)
    ax.plot([x + inset + 5, x + w - inset - 5], [ctrl_y - 6, ctrl_y - 6],
            color=accent, linewidth=0.45, alpha=0.35, zorder=14)

    # Oznaka "DW" (dishwasher)
    ax.text(mid, y + h * 0.42, "DW",
            fontsize=max(7, int(w * 0.052)),
            color="#666666" if not technical else "#999999",
            ha="center", va="center", alpha=0.85, zorder=16)


def _draw_dishwasher_freestanding(ax, x, y, w, h, accent, technical):
    """Samostojeća mašina za sudove: front kao realan appliance sa gornjom komandnom trakom i nožicama."""
    inset = max(4, int(w * 0.035))
    body_c = "#F7F7F5"
    panel_c = "#ECECE8"
    dark_c = "#6E7278"
    ax.add_patch(plt.Rectangle(
        (x + inset, y + inset),
        w - 2 * inset, h - 2 * inset,
        facecolor=body_c if not technical else "none",
        edgecolor=accent, linewidth=0.9, zorder=12
    ))
    ctrl_h = max(16, int(h * 0.10))
    ctrl_y = y + h - inset - ctrl_h - 2
    ax.add_patch(plt.Rectangle(
        (x + inset, ctrl_y),
        w - 2 * inset, ctrl_h,
        facecolor=panel_c if not technical else "none",
        edgecolor=accent, linewidth=0.7, alpha=0.85, zorder=13
    ))
    if not technical:
        ax.add_patch(plt.Rectangle(
            (x + inset + 6, ctrl_y + 3),
            max(18, (w - 2 * inset) * 0.26), max(4, ctrl_h - 6),
            facecolor="#BFC4CB", edgecolor="none", alpha=0.45, zorder=14
        ))
    # Ručka u gornjoj zoni, kao na referenci.
    hx0 = x + w * 0.36
    hx1 = x + w * 0.60
    hy = ctrl_y - max(10, int(h * 0.05))
    ax.plot([hx0, hx1], [hy, hy], color=accent, linewidth=1.0, zorder=15)
    ax.plot([hx0, hx0], [hy, hy + 5], color=accent, linewidth=0.8, zorder=15)
    ax.plot([hx1, hx1], [hy, hy + 5], color=accent, linewidth=0.8, zorder=15)
    # Desni display i dugmad.
    disp_w = max(12, int(w * 0.12))
    disp_h = max(5, int(ctrl_h * 0.30))
    disp_x = x + w * 0.74
    disp_y = ctrl_y + ctrl_h * 0.46 - disp_h / 2
    ax.add_patch(plt.Rectangle(
        (disp_x, disp_y), disp_w, disp_h,
        facecolor="#FAFAFA" if not technical else "none",
        edgecolor=accent, linewidth=0.5, zorder=15
    ))
    for i in range(2):
        bx = x + w * (0.90 + i * 0.04)
        by = ctrl_y + ctrl_h * 0.48
        ax.add_patch(plt.Circle((bx, by), max(1.5, int(ctrl_h * 0.10)),
                                facecolor="none",
                                edgecolor=accent, linewidth=0.6, zorder=15))
    # Donji postolni lim i male nožice.
    plinth_h = max(10, int(h * 0.06))
    ax.plot([x + inset, x + w - inset], [y + plinth_h, y + plinth_h], color=accent, linewidth=0.8, zorder=14)
    foot_w = max(10, int(w * 0.10))
    foot_h = max(4, int(h * 0.016))
    for px in (x + w * 0.10, x + w * 0.82):
        ax.add_patch(plt.Rectangle(
            (px, y + 1), foot_w, foot_h,
            facecolor=dark_c if not technical else "none",
            edgecolor=accent, linewidth=0.5, zorder=15
        ))


def _draw_oven_hob_freestanding(ax, x, y, w, h, accent, technical):
    """Samostojeći šporet — čisti frontalni 2D pogled.

    Važno:
    - u 2D front modu ne prikazujemo dubinu ploče kao pogled odozgo
    - zato ne crtamo sva 4 grejna mesta; vidi se samo prednja linija/oznaka ploče
    """
    inset = max(4, int(w * 0.035))
    body_c = "#F7F7F5"
    panel_c = "#F0F0EC"
    base_c = "#6F6F72"
    glass_c = "#8C8C8E"
    ctrl_h = max(34, int(h * 0.13))
    top_h = max(14, int(h * 0.07))
    base_h = max(18, int(h * 0.10))
    oven_h = h - ctrl_h - top_h - base_h
    ctrl_y = y + h - top_h - ctrl_h
    top_y = y + h - top_h
    ax.add_patch(plt.Rectangle(
        (x + inset, y + inset + base_h),
        w - 2 * inset, max(4, oven_h),
        facecolor=body_c if not technical else "none",
        edgecolor=accent, linewidth=0.9, zorder=12
    ))
    ax.add_patch(plt.Rectangle(
        (x + inset, ctrl_y),
        w - 2 * inset, ctrl_h,
        facecolor=panel_c if not technical else "none",
        edgecolor=accent, linewidth=0.7, alpha=0.85, zorder=13
    ))
    ax.add_patch(plt.Rectangle(
        (x + inset, top_y),
        w - 2 * inset, top_h - inset,
        facecolor="#EBEBE7" if not technical else "none",
        edgecolor=accent, linewidth=0.7, alpha=0.9, zorder=13
    ))
    # Frontalni pogled: vidi se samo prednja linija ploče i dve prednje zone.
    hob_line_y = top_y + top_h * 0.55
    ax.plot([x + inset + 4, x + w - inset - 4], [hob_line_y, hob_line_y],
            color=accent, linewidth=0.7, alpha=0.85, zorder=15)
    ring_rx = max(8, int(w * 0.12))
    ring_ry = max(1.8, top_h * 0.16)
    for cx in (x + w * 0.30, x + w * 0.70):
        ax.add_patch(plt.matplotlib.patches.Ellipse(
            (cx, top_y + top_h * 0.72),
            ring_rx * 2.0, ring_ry * 2.0,
            facecolor="none",
            edgecolor=accent, linewidth=0.7, zorder=15
        ))
        ax.add_patch(plt.matplotlib.patches.Ellipse(
            (cx, top_y + top_h * 0.72),
            ring_rx * 1.15, ring_ry * 1.15,
            facecolor="none",
            edgecolor=accent, linewidth=0.55, alpha=0.7, zorder=15
        ))
    win_inset = max(12, int(w * 0.10))
    win_x = x + win_inset
    win_w = w - 2 * win_inset
    win_y = y + base_h + int(oven_h * 0.18)
    win_h = int(oven_h * 0.44)
    ax.add_patch(plt.Rectangle(
        (win_x, win_y), win_w, win_h,
        facecolor=glass_c if not technical else "none",
        edgecolor="#555555", linewidth=1.0, zorder=14
    ))
    if not technical:
        for off in (0.20, 0.42, 0.64):
            ax.plot([win_x + win_w * off, win_x + win_w * (off + 0.10)],
                    [win_y + 5, win_y + win_h - 5],
                    color="#D7D7D7", linewidth=2.0, alpha=0.25, zorder=15)
    _handle_h_oven(ax, x + w / 2, y + base_h + int(oven_h * 0.72), technical=technical)
    # Dugmići + mali display.
    for i in range(6):
        bx = x + inset + (w - 2 * inset) * (0.10 + i * 0.12)
        ax.add_patch(plt.Circle((bx, ctrl_y + ctrl_h * 0.52), max(2, int(ctrl_h * 0.12)),
                                facecolor="#666666" if not technical else "none",
                                edgecolor="#444444", linewidth=0.5, zorder=15))
    disp_x = x + w * 0.46
    disp_w = max(14, int(w * 0.10))
    disp_h = max(6, int(ctrl_h * 0.24))
    ax.add_patch(plt.Rectangle(
        (disp_x, ctrl_y + ctrl_h * 0.52 - disp_h / 2), disp_w, disp_h,
        facecolor="#D7D7D7" if not technical else "none",
        edgecolor=accent, linewidth=0.5, zorder=15
    ))
    # Donji sokl uređaja i nožice.
    ax.add_patch(plt.Rectangle(
        (x + inset, y + 2), w - 2 * inset, base_h - 4,
        facecolor=base_c if not technical else "none",
        edgecolor=accent, linewidth=0.7, zorder=13
    ))
    foot_w = max(10, int(w * 0.10))
    foot_h = max(5, int(h * 0.018))
    for px in (x + w * 0.08, x + w * 0.82):
        ax.add_patch(plt.Rectangle(
            (px, y + 1), foot_w, foot_h,
            facecolor=base_c if not technical else "none",
            edgecolor=accent, linewidth=0.5, zorder=15
        ))


def _draw_fridge_under(ax, x, y, w, h, accent, face, technical):
    """Ugradni frižider – donji dio (base zona, integrisani panel).
    Stijl: 1 vrata boje fronta + horizontalni pregrad (zamrzivač gore)
    + standardna vertikalna ručka desno + diskretna 'F' oznaka."""
    door_inset_x = max(4, int(w * 0.05))
    door_inset_y = max(4, int(h * 0.04))
    door_w = max(2, w - 2 * door_inset_x)
    door_h = max(2, h - 2 * door_inset_y)
    mid_x = x + w / 2

    # Vrata panela — integrisana boja fronta (konzistentno s ostalim ugradnim elementima)
    ax.add_patch(plt.Rectangle(
        (x + door_inset_x, y + door_inset_y), door_w, door_h,
        facecolor=face, edgecolor=accent, linewidth=0.8, zorder=12
    ))

    # Horizontalna pregrada ~28% od vrha — vizuelno dijeli zamrzivač (gore) od frižidera (dole)
    div_y = y + door_inset_y + door_h * 0.28
    ax.plot(
        [x + door_inset_x + 4, x + door_inset_x + door_w - 4],
        [div_y, div_y],
        color=accent, linewidth=0.7, alpha=0.50, linestyle='--', zorder=13
    )

    # Vertikalna ručka desno — standardna pozicija (kao 1-vrata base element)
    handle_cx = (x + w - door_inset_x) - (30.0 + DOOR_HANDLE_V_W / 2.0)
    handle_cy = _clamp_handle_cy(y, h, y + h - 50 - DOOR_HANDLE_V_LEN / 2)
    _handle_v(ax, handle_cx, handle_cy, technical=technical)

    # Oznaka 'F' — mala, u donjem dijelu vrata (ispod pregrada = frižider dio)
    ax.text(
        mid_x - 10, y + door_inset_y + door_h * 0.62,
        "F",
        fontsize=max(7, int(w * 0.065)),
        color=accent if not technical else "#999999",
        ha="center", va="center", alpha=0.55, zorder=16,
        fontstyle='italic',
    )


def _draw_fridge(ax, x, y, w, h, accent, face, technical):
    """Ugradni frižider: zamrzivač dole + frižider gore, duge vertikalne ručke uz spoljašnju ivicu."""
    mid = x + w / 2
    split_y = y + int(h * 0.40)  # donji deo (zamrzivač) ~40%
    door_inset = max(6, int(min(w, h) * 0.04))

    # Integrisani frižider mora vizuelno pratiti boju fronta kuhinje.
    ax.add_patch(plt.Rectangle(
        (x + door_inset, split_y + door_inset),
        max(2, w - 2 * door_inset), max(2, y + h - split_y - 2 * door_inset),
        facecolor=face if not technical else "none",
        edgecolor=accent, linewidth=0.8, alpha=0.96 if not technical else 0.55, zorder=10
    ))
    ax.add_patch(plt.Rectangle(
        (x + door_inset, y + door_inset),
        max(2, w - 2 * door_inset), max(2, split_y - y - 2 * door_inset),
        facecolor=face if not technical else "none",
        edgecolor=accent, linewidth=0.8, alpha=0.96 if not technical else 0.55, zorder=10
    ))

    # Linija podele
    ax.plot([x, x + w], [split_y, split_y], color=accent, linewidth=0.8, zorder=12)

    # Okviri vrata
    ax.add_patch(plt.Rectangle(
        (x + door_inset, split_y + door_inset),
        max(2, w - 2 * door_inset), max(2, y + h - split_y - 2 * door_inset),
        facecolor="none", edgecolor=accent, linewidth=0.5, alpha=0.30, zorder=11
    ))
    ax.add_patch(plt.Rectangle(
        (x + door_inset, y + door_inset),
        max(2, w - 2 * door_inset), max(2, split_y - y - 2 * door_inset),
        facecolor="none", edgecolor=accent, linewidth=0.5, alpha=0.30, zorder=11
    ))

    # Ručke: vertikalne, uz spoljašnju ivicu (desno), duge
    fridge_cy = (split_y + y + h) / 2
    freezer_cy = (y + split_y) / 2
    handle_cx = x + w - 40.0
    _handle_v_fridge(ax, handle_cx, fridge_cy, technical=technical)
    _handle_v_fridge(ax, handle_cx, freezer_cy, technical=technical)

    # Oznaka "F"
    ax.text(x + w * 0.18, split_y + (y + h - split_y) * 0.75,
            "F",
            fontsize=max(8, int(w * 0.09)),
            color="#666666" if not technical else "#999999",
            ha="center", va="center", alpha=0.85, zorder=16)

def _draw_pantry(ax, x, y, w, h, accent, face, technical,
                 door_count: int = 2, handle_side: str = "right", n_shelves: int = 4):
    """Visoki za ostavu: 1 ili 2 krila vrata + police."""
    mid = x + w / 2
    n_shelves = max(1, int(n_shelves or 4))
    # Police (horizontalne linije)
    for i in range(1, n_shelves):
        sy = y + int(h * i / n_shelves)
        ax.plot([x + 8, x + w - 8], [sy, sy], color=accent, linewidth=0.5,
                alpha=0.4, linestyle=":", zorder=12)
    if door_count == 1:
        # Jedno vrata — ručka na odabranoj strani
        handle_cx = (x + 20 + w * 0.08) if handle_side == "left" else (x + w - 20 - w * 0.08)
        _handle_v(ax, handle_cx, y + h * 0.5, hh=h * 0.12, technical=technical)
    else:
        # Dva vrata
        ax.plot([mid, mid], [y, y + h], color=accent, linewidth=0.8, zorder=12)
        _handle_v(ax, mid - w * 0.12, y + h * 0.5, hh=h * 0.12, technical=technical)
        _handle_v(ax, mid + w * 0.12, y + h * 0.5, hh=h * 0.12, technical=technical)




def _draw_wardrobe_layout(ax, x, y, w, h, accent, technical, params=None):
    """Crta unutrasnju organizaciju ormara: genericki ili americki sekcioni raspored."""
    p = params or {}
    sections = p.get('american_sections') if isinstance(p.get('american_sections'), dict) else None

    inner_x = x + max(8, int(w * 0.04))
    inner_y = y + max(8, int(h * 0.02))
    inner_w = max(40, w - 2 * max(8, int(w * 0.04)))
    inner_h = max(60, h - 2 * max(8, int(h * 0.02)))

    if sections:
        top_h = max(80, min(int(sections.get('top_h_mm', 420) or 420), int(inner_h * 0.45)))
        base_h = max(40, inner_h - top_h)

        left_pct = float(sections.get('left_pct', 33) or 33)
        center_pct = float(sections.get('center_pct', 34) or 34)
        right_pct = float(sections.get('right_pct', 33) or 33)
        tot = max(1.0, left_pct + center_pct + right_pct)
        left_w = int(inner_w * (left_pct / tot))
        center_w = int(inner_w * (center_pct / tot))
        right_w = max(20, inner_w - left_w - center_w)

        x_left = inner_x
        x_center = x_left + left_w
        x_right = x_center + center_w

        # Delimiting lines for sections and top storage.
        ax.plot([inner_x, inner_x + inner_w], [inner_y + base_h, inner_y + base_h], color=accent, linewidth=0.9, alpha=0.7, zorder=12)
        ax.plot([x_center, x_center], [inner_y, inner_y + base_h], color=accent, linewidth=0.8, alpha=0.6, zorder=12)
        ax.plot([x_right, x_right], [inner_y, inner_y + base_h], color=accent, linewidth=0.8, alpha=0.6, zorder=12)

        def _draw_section(x0, sw, sh, sec):
            ns = max(0, min(12, int(sec.get('shelves', 0) or 0)))
            nd = max(0, min(8, int(sec.get('drawers', 0) or 0)))
            nh = max(0, min(3, int(sec.get('hangers', 0) or 0)))

            drawer_h = int(sh * 0.30) if nd > 0 else 0
            upper_y = inner_y + drawer_h
            upper_h = max(16, sh - drawer_h)

            if ns > 0:
                for i in range(1, ns + 1):
                    sy = upper_y + int((upper_h * i) / (ns + 1))
                    ax.plot([x0 + 4, x0 + sw - 4], [sy, sy], color=accent, linewidth=0.55, alpha=0.65, zorder=12)

            if nh > 0:
                for i in range(nh):
                    cy = upper_y + int((upper_h * (i + 1)) / (nh + 1))
                    ax.plot([x0 + 8, x0 + sw - 8], [cy, cy], color=accent, linewidth=1.1, alpha=0.75, zorder=13)

            if nd > 0 and drawer_h > 16:
                dh = max(10, int(drawer_h / max(1, nd)))
                for i in range(1, nd):
                    dy = inner_y + i * dh
                    ax.plot([x0 + 4, x0 + sw - 4], [dy, dy], color=accent, linewidth=0.8, alpha=0.65, zorder=12)
                if not technical:
                    _handle_h(ax, x0 + (sw / 2), inner_y + max(8, int(dh * 0.5)), technical=technical)

        _draw_section(x_left, left_w, base_h, sections.get('left', {}) or {})
        _draw_section(x_center, center_w, base_h, sections.get('center', {}) or {})
        _draw_section(x_right, right_w, base_h, sections.get('right', {}) or {})

        top_sec = sections.get('top', {}) or {}
        top_shelves = max(0, min(8, int(top_sec.get('shelves', 2) or 2)))
        if top_shelves > 0:
            for i in range(1, top_shelves + 1):
                sy = inner_y + base_h + int((top_h * i) / (top_shelves + 1))
                ax.plot([inner_x + 4, inner_x + inner_w - 4], [sy, sy], color=accent, linewidth=0.55, alpha=0.60, zorder=12)
        return

    # Generic wardrobe fallback
    n_shelves = max(0, min(12, int(p.get('n_shelves', 4) or 4)))
    n_drawers = max(0, min(8, int(p.get('n_drawers', 2) or 2)))
    hanger_sections = max(0, min(3, int(p.get('hanger_sections', 1) or 1)))

    drawer_zone_h = int(inner_h * 0.24) if n_drawers > 0 else 0
    upper_y = inner_y + drawer_zone_h
    upper_h = max(20, inner_h - drawer_zone_h)

    hanger_w = int(inner_w * 0.42) if hanger_sections > 0 else 0
    shelf_w = max(20, inner_w - hanger_w)

    if hanger_w > 0:
        split_x = inner_x + shelf_w
        ax.plot([split_x, split_x], [upper_y, upper_y + upper_h], color=accent, linewidth=0.55, alpha=0.55, zorder=12)

    if n_shelves > 0 and shelf_w > 25:
        for i in range(1, n_shelves + 1):
            sy = upper_y + int((upper_h * i) / (n_shelves + 1))
            ax.plot([inner_x + 4, inner_x + shelf_w - 4], [sy, sy], color=accent, linewidth=0.55, alpha=0.65, zorder=12)

    if hanger_sections > 0 and hanger_w > 30:
        hz_x0 = inner_x + shelf_w + 8
        hz_x1 = inner_x + inner_w - 8
        for i in range(hanger_sections):
            cy = upper_y + int((upper_h * (i + 1)) / (hanger_sections + 1))
            ax.plot([hz_x0, hz_x1], [cy, cy], color=accent, linewidth=1.2, alpha=0.7, zorder=13)
            ax.plot([hz_x0 + 8, hz_x0 + 12, hz_x0 + 16], [cy - 6, cy - 2, cy - 6], color=accent, linewidth=0.7, alpha=0.55, zorder=13)

    if n_drawers > 0 and drawer_zone_h > 16:
        d_h = max(12, int(drawer_zone_h / max(1, n_drawers)))
        for i in range(1, n_drawers):
            dy = inner_y + i * d_h
            ax.plot([inner_x + 4, inner_x + inner_w - 4], [dy, dy], color=accent, linewidth=0.8, alpha=0.65, zorder=12)
        if not technical:
            _handle_h(ax, inner_x + (inner_w / 2), inner_y + max(8, int(d_h * 0.5)), technical=technical)

def _draw_tall_doors(ax, x, y, w, h, accent, face, technical, m=None):
    """Visoki sa 2 vrata (jedan iznad drugog ili jedno pored drugog) — vertikalne ručke."""
    mid = x + w / 2
    door_inset = max(6, int(min(w, h) * 0.05))
    handle_edge_off = 30.0
    handle_side = str((m or {}).get("params", {}).get("handle_side", "right")).lower()
    half_len = DOOR_HANDLE_V_LEN / 2.0
    tid = str(m.get("template_id", "")).upper() if m else ""
    _params = (m.get("params", {}) or {}) if m else {}
    _door_mode = str(_params.get("door_mode", "sliding" if "SLIDING" in tid else "hinged")).lower()
    _is_wardrobe = "WARDROBE" in tid
    _is_sliding = _door_mode == "sliding" or "SLIDING" in tid

    if _is_sliding:
        mid = x + w / 2
        ax.plot([x + 4, x + w - 4], [y + h - 8, y + h - 8], color=accent, linewidth=1.2, alpha=0.8, zorder=12)
        ax.plot([x + 4, x + w - 4], [y + 8, y + 8], color=accent, linewidth=1.2, alpha=0.8, zorder=12)
        ax.plot([mid - 8, mid - 8], [y + 10, y + h - 10], color=accent, linewidth=1.0, alpha=0.7, zorder=12)
        ax.plot([mid + 8, mid + 8], [y + 10, y + h - 10], color=accent, linewidth=1.0, alpha=0.7, zorder=12)
        _handle_v(ax, mid - 24, y + h * 0.5, technical=technical)
        _handle_v(ax, mid + 24, y + h * 0.5, technical=technical)
        return

    # Broj vrata — iz params (door_count), fallback na tid
    _door_count = int(_params.get("door_count", 0) or 0)
    force_one = (_door_count == 1) or ("1DOOR" in tid)
    force_two = (_door_count == 2) or ("2DOOR" in tid) or ("DOORS" in tid and "1DOOR" not in tid and _door_count != 1)

    if force_one:
        # Jedno vrata — puna širina, ručka na odabranoj strani
        handle_cy = _clamp_handle_cy(y, h, y + h * 0.50)
        if handle_side == "left":
            handle_cx = (x + door_inset) + (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        else:
            handle_cx = (x + w - door_inset) - (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        _handle_v(ax, handle_cx, handle_cy, technical=technical)
    elif (not force_one and (force_two or w > 650)):
        # Dva vrata jedan pored drugog
        ax.plot([mid, mid], [y, y + h], color=accent, linewidth=0.8, zorder=12)
        handle_cy = _clamp_handle_cy(y, h, y + h * 0.50)
        seam_off = handle_edge_off + DOOR_HANDLE_V_W / 2.0
        _handle_v(ax, mid - seam_off, handle_cy, technical=technical)
        _handle_v(ax, mid + seam_off, handle_cy, technical=technical)
    else:
        # Dva vrata jedan iznad drugog
        split_y = y + int(h * 0.5)
        ax.plot([x, x + w], [split_y, split_y], color=accent, linewidth=0.8, zorder=12)

        # Gornja vrata (iznad) — ručka centrirana po visini krila
        top_y0, top_h = split_y, (y + h) - split_y
        top_cy = _clamp_handle_cy(top_y0, top_h, top_y0 + top_h * 0.50)
        if handle_side == "left":
            handle_cx = (x + door_inset) + (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        else:
            handle_cx = (x + w - door_inset) - (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        _handle_v(ax, handle_cx, top_cy, technical=technical)

        # Donja vrata (ispod) — ručka centrirana po visini krila
        bot_y0, bot_h = y, split_y - y
        bot_cy = _clamp_handle_cy(bot_y0, bot_h, bot_y0 + bot_h * 0.50)
        if handle_side == "left":
            handle_cx = (x + door_inset) + (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        else:
            handle_cx = (x + w - door_inset) - (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        _handle_v(ax, handle_cx, bot_cy, technical=technical)

    _draw_shelf_hints(ax, x, y, w, h, accent, face, technical, m=m, zone_hint='tall')

def _draw_open(ax, x, y, w, h, accent, face, technical, n_shelves=3):
    """Otvoreni element sa policama (iverica + kant)."""
    n_shelves = max(0, min(12, int(n_shelves or 0)))
    if n_shelves <= 0:
        return

    _panel_fill = "#D9CBB8" if not technical else "none"
    _panel_edge = "#6F5A43" if not technical else accent
    _back_fill = "#C6C0B7" if not technical else "none"
    _shadow_fill = "#B9AE9F" if not technical else "none"
    _shelf_face = "#E8DCCB" if not technical else "none"
    _shelf_edge = "#6F5A43" if not technical else accent
    _th = max(3, int(min(10, h * 0.02)))
    _side_w = max(5, int(min(16, w * 0.08)))
    _top_h = max(5, int(min(16, h * 0.06)))
    _inner_x = x + _side_w
    _inner_y = y + _top_h
    _inner_w = max(8, w - (_side_w * 2))
    _inner_h = max(8, h - (_top_h * 2))

    # Bočne stranice, gornja/donja ploča i leđna ploča.
    ax.add_patch(plt.Rectangle((x, y), _side_w, h, facecolor=_panel_fill, edgecolor=_panel_edge, linewidth=0.8, zorder=10))
    ax.add_patch(plt.Rectangle((x + w - _side_w, y), _side_w, h, facecolor=_shadow_fill if not technical else "none", edgecolor=_panel_edge, linewidth=0.8, zorder=10))
    ax.add_patch(plt.Rectangle((x, y + h - _top_h), w, _top_h, facecolor=_panel_fill, edgecolor=_panel_edge, linewidth=0.8, zorder=10))
    ax.add_patch(plt.Rectangle((x, y), w, _top_h, facecolor=_shadow_fill if not technical else "none", edgecolor=_panel_edge, linewidth=0.8, zorder=10))
    ax.add_patch(plt.Rectangle((_inner_x + 1, _inner_y + 1), max(4, _inner_w - 2), max(4, _inner_h - 2),
                               facecolor=_back_fill, edgecolor=_panel_edge, linewidth=0.4, alpha=0.72 if not technical else 0.45, zorder=9))

    for i in range(1, n_shelves + 1):
        sy = _inner_y + int((_inner_h * i) / (n_shelves + 1))
        ax.add_patch(plt.Rectangle(
            (_inner_x + 2, sy - _th / 2), max(8, _inner_w - 4), _th,
            facecolor=_shelf_face, edgecolor=_shelf_edge,
            linewidth=0.7, zorder=12
        ))
        # Prednja kant ivica police
        ax.plot([_inner_x + 2, _inner_x + _inner_w - 2], [sy + (_th / 2), sy + (_th / 2)],
                color=_shelf_edge, linewidth=1.0, zorder=13)
        if not technical:
            ax.plot([_inner_x + 4, _inner_x + _inner_w - 4], [sy - (_th / 2), sy - (_th / 2)],
                    color="#F4EBDD", linewidth=0.6, alpha=0.6, zorder=13)


def _draw_hood(ax, x, y, w, h, accent, face, technical):
    """Aspirator/napa: trapezoidni oblik + rešetka."""
    # Trapezoidni oblik nape
    bot_inset = int(w * 0.08)
    top_inset = int(w * 0.20)
    bot_y = y
    top_y = y + h
    verts = [
        (x + bot_inset, bot_y),
        (x + w - bot_inset, bot_y),
        (x + w - top_inset, top_y),
        (x + top_inset, top_y),
        (x + bot_inset, bot_y),
    ]
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    ax.fill(xs, ys, facecolor="#D8D8D8" if not technical else "none",
            edgecolor=accent, linewidth=0.9, zorder=11)
    # Rešetka (horizontalne linije)
    n_lines = 3
    for i in range(1, n_lines + 1):
        ry = y + int(h * i / (n_lines + 1))
        frac = i / (n_lines + 1)
        inset_at_y = bot_inset + (top_inset - bot_inset) * frac
        ax.plot([x + inset_at_y + 4, x + w - inset_at_y - 4], [ry, ry],
                color=accent, linewidth=0.6, alpha=0.7, zorder=13)
    if not technical:
        ax.plot([x + w * 0.28, x + w * 0.70], [y + h * 0.84, y + h * 0.25],
                color="#E5E7EB", linewidth=0.8, alpha=0.45, zorder=14)
    # Dugme
    mid = x + w / 2
    ax.add_patch(plt.Circle((mid, y + int(h * 0.85)), max(4, int(w * 0.04)),
                             facecolor="#AAAAAA" if not technical else "none",
                             edgecolor=accent, linewidth=0.6, zorder=14))


def _draw_glass_doors(ax, x, y, w, h, accent, face, technical):
    """Gornji sa staklenim vratima."""
    mid = x + w / 2
    inset = max(8, int(w * 0.07))
    glass_fill = "#D7E9F6" if not technical else "none"
    frame_fill = _darken_color(face, 0.96) if not technical else "none"
    shelf_col = _darken_color(face, 0.84) if not technical else accent
    if w > 450:
        # 2 krila
        ax.plot([mid, mid], [y, y + h], color=accent, linewidth=0.7, zorder=12)
        # Staklo (svetlije fill)
        ax.add_patch(plt.Rectangle(
            (x + inset, y + inset), mid - x - inset, h - 2 * inset,
            facecolor=glass_fill,
            edgecolor=accent, linewidth=0.6, alpha=0.7, zorder=12
        ))
        ax.add_patch(plt.Rectangle(
            (mid, y + inset), w - (mid - x) - inset, h - 2 * inset,
            facecolor=glass_fill,
            edgecolor=accent, linewidth=0.6, alpha=0.7, zorder=12
        ))
        ax.add_patch(plt.Rectangle((x + inset, y + inset), mid - x - inset, h - 2 * inset,
                                   facecolor=frame_fill, edgecolor=accent, linewidth=0.7, fill=False, zorder=13))
        ax.add_patch(plt.Rectangle((mid, y + inset), w - (mid - x) - inset, h - 2 * inset,
                                   facecolor=frame_fill, edgecolor=accent, linewidth=0.7, fill=False, zorder=13))
        for frac in (0.32, 0.60):
            sy = y + inset + (h - 2 * inset) * frac
            ax.plot([x + inset + 6, mid - 6], [sy, sy], color=shelf_col, linewidth=0.55, alpha=0.55, zorder=13)
            ax.plot([mid + 6, x + w - inset - 6], [sy, sy], color=shelf_col, linewidth=0.55, alpha=0.55, zorder=13)
        if not technical:
            ax.plot([x + inset + 5, mid - inset * 0.2], [y + h - inset - 4, y + inset + 6],
                    color="#F7FBFF", linewidth=0.8, alpha=0.45, zorder=14)
            ax.plot([mid + 5, x + w - inset - 5], [y + h - inset - 4, y + inset + 6],
                    color="#F7FBFF", linewidth=0.8, alpha=0.45, zorder=14)
        _handle_v(ax, mid - w * 0.10, y + h * 0.5, hh=h * 0.2, technical=technical)
        _handle_v(ax, mid + w * 0.10, y + h * 0.5, hh=h * 0.2, technical=technical)
    else:
        ax.add_patch(plt.Rectangle(
            (x + inset, y + inset), w - 2 * inset, h - 2 * inset,
            facecolor=glass_fill,
            edgecolor=accent, linewidth=0.6, alpha=0.7, zorder=12
        ))
        for frac in (0.32, 0.60):
            sy = y + inset + (h - 2 * inset) * frac
            ax.plot([x + inset + 6, x + w - inset - 6], [sy, sy], color=shelf_col, linewidth=0.55, alpha=0.55, zorder=13)
        if not technical:
            ax.plot([x + inset + 6, x + w - inset - 8], [y + h - inset - 5, y + inset + 8],
                    color="#F7FBFF", linewidth=0.8, alpha=0.45, zorder=14)
        _handle_v(ax, mid, y + h * 0.5, hh=h * 0.22, technical=technical)


def _draw_liftup(ax, x, y, w, h, accent, face, technical):
    """Podizna vrata (klapna)."""
    mid = x + w / 2
    inset = max(8, int(w * 0.07))
    _inset_rect(ax, x, y, w, h, inset, face, accent, lw=0.7)
    # Ručica na sredini donje ivice
    _handle_h(ax, mid, y + inset + 10, hw=w * 0.30, technical=technical)
    # Linija koja sugerise otvaranje prema gore
    arr_y = y + h * 0.7
    ax.annotate("", xy=(mid, y + h - inset - 5), xytext=(mid, arr_y),
                arrowprops=dict(arrowstyle="-|>", color=accent, lw=0.6),
                zorder=14)



def _draw_wall_doors(ax, x, y, w, h, accent, face, technical, m=None):
    """Gornji sa 1 ili 2 vrata — okvir + VERTIKALNE ručke (fiksne)."""
    mid = x + w / 2
    door_inset = max(6, int(min(w, h) * 0.05))
    handle_edge_off = 30.0
    handle_side = str((m or {}).get("params", {}).get("handle_side", "right")).lower()
    handle_bottom_off = 50.0
    half_len = DOOR_HANDLE_V_LEN / 2.0
    zone_key = str((m or {}).get("zone", "")).lower().strip()
    if zone_key == "tall_top":
        handle_cy = _clamp_handle_cy(y, h, y + h * 0.50)
    else:
        handle_cy = _clamp_handle_cy(y, h, y + handle_bottom_off + half_len)

    tid = str(m.get("template_id", "")).upper() if m else ""
    force_one = "1DOOR" in tid
    force_two = ("2DOOR" in tid) or ("DOORS" in tid and "1DOOR" not in tid)
    if (not force_one and (force_two or w > 650)):
        # 2 krila — vertikalna linija razdvajanja
        ax.plot([mid, mid], [y, y + h], color=accent, linewidth=0.8, zorder=12)
        ax.add_patch(plt.Rectangle(
            (x + door_inset, y + door_inset),
            max(2, mid - x - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.50, zorder=11
        ))
        ax.add_patch(plt.Rectangle(
            (mid + door_inset, y + door_inset),
            max(2, w - (mid - x) - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.50, zorder=11
        ))

        # Ručke: 30mm od spoja ka spolja
        seam_off = handle_edge_off + DOOR_HANDLE_V_W / 2.0
        _handle_v(ax, mid - seam_off, handle_cy, technical=technical)
        _handle_v(ax, mid + seam_off, handle_cy, technical=technical)

    else:
        ax.add_patch(plt.Rectangle(
            (x + door_inset, y + door_inset), max(2, w - 2 * door_inset), max(2, h - 2 * door_inset),
            facecolor="none", edgecolor=accent, linewidth=0.7, alpha=0.50, zorder=11
        ))

        # Ručka: 50mm od gornje ivice, 30mm od unutrašnjeg okvira (levo/desno)
        if handle_side == "left":
            handle_cx = (x + door_inset) + (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        else:
            handle_cx = (x + w - door_inset) - (handle_edge_off + DOOR_HANDLE_V_W / 2.0)
        _handle_v(ax, handle_cx, handle_cy, technical=technical)

    _draw_shelf_hints(ax, x, y, w, h, accent, face, technical, m=m, zone_hint='wall')


def _draw_shelf_hints(ax, x, y, w, h, accent, face, technical, m=None, zone_hint: str = ""):
    params = (m.get("params", {}) or {}) if m else {}
    tid = str((m or {}).get("template_id", "")).upper()
    n_shelves = default_shelf_count(
        tid,
        zone=zone_hint,
        h_mm=h,
        params=params,
        features={},
    )
    n_shelves = max(0, min(12, int(n_shelves or 0)))
    if n_shelves <= 0:
        return

    inset = max(10, int(min(w, h) * 0.08))
    inner_x0 = x + inset
    inner_x1 = x + w - inset
    if inner_x1 - inner_x0 < 30:
        return
    shelf_col = accent if technical else _darken_color(face, 0.78)
    alpha = 0.45 if technical else 0.22
    mid = x + w / 2.0
    two_doors = ("2DOOR" in tid) or ("DOORS" in tid and "1DOOR" not in tid and w > 650)
    for i in range(1, n_shelves + 1):
        sy = y + int((h * i) / (n_shelves + 1))
        if two_doors:
            ax.plot([inner_x0 + 4, mid - 6], [sy, sy], color=shelf_col, linewidth=0.55, alpha=alpha, zorder=10)
            ax.plot([mid + 6, inner_x1 - 4], [sy, sy], color=shelf_col, linewidth=0.55, alpha=alpha, zorder=10)
        else:
            ax.plot([inner_x0 + 4, inner_x1 - 4], [sy, sy], color=shelf_col, linewidth=0.55, alpha=alpha, zorder=10)

def _draw_corner(ax, x, y, w, h, accent, face, technical, zone, m: Optional[Dict[str, Any]] = None):
    """Ugaoni element - razlikuje L front i dijagonalni front."""
    tid = str((m or {}).get("template_id", "")).upper()
    mid = x + w / 2
    inner = max(22.0, min(w, h) * 0.28)
    inset = max(8.0, min(w, h) * 0.05)

    if "DIAGONAL" in tid:
        pts = [
            (x + inset, y + h - inset),
            (x + w - inset, y + h - inset),
            (x + w - inset, y + inner),
            (x + mid, y + inset),
            (x + inset, y + inner),
        ]
        poly = mpatches.Polygon(
            pts,
            closed=True,
            facecolor="none" if technical else _darken_color(face, 0.965),
            edgecolor=accent,
            linewidth=0.9,
            zorder=12,
        )
        ax.add_patch(poly)
        ax.plot(
            [x + inset + 14, x + mid, x + w - inset - 14],
            [y + h - inset - 14, y + inner + 10, y + h - inset - 14],
            color=accent,
            linewidth=0.55,
            alpha=0.26,
            zorder=13,
        )
        _handle_h(ax, mid, y + h * 0.47, hw=w * 0.34, technical=technical)
        return

    side_w = max(16.0, min(w * 0.12, 42.0))
    top_h = max(16.0, min(h * 0.12, 42.0))
    ax.add_patch(plt.Rectangle(
        (x + inset, y + inset),
        max(2, w - side_w - inset * 1.5),
        max(2, h - top_h - inset * 1.5),
        facecolor="none",
        edgecolor=accent,
        linewidth=0.8,
        alpha=0.55,
        zorder=11,
    ))
    ax.add_patch(plt.Rectangle(
        (x + side_w, y + inset),
        max(2, w - side_w - inset * 1.5),
        max(2, h - inner - inset),
        facecolor="none",
        edgecolor=accent,
        linewidth=0.8,
        alpha=0.55,
        zorder=11,
    ))
    ax.plot(
        [x + side_w + 8, x + w - inset],
        [y + inner, y + inner],
        color=accent,
        linewidth=0.75,
        alpha=0.6,
        zorder=12,
    )
    ax.plot(
        [x + side_w, x + side_w],
        [y + inset, y + inner],
        color=accent,
        linewidth=0.75,
        alpha=0.6,
        zorder=12,
    )
    ax.plot(
        [x + side_w + 6, x + w - inset - 6],
        [y + inner + 18, y + h - inset - 18],
        color=accent,
        linewidth=0.55,
        alpha=0.28,
        linestyle="--",
        zorder=12,
    )
    _handle_h(ax, x + w * 0.70, y + inner + 24, hw=w * 0.28, technical=technical)
    _handle_v(ax, x + side_w + 22, y + h * 0.63, technical=technical)


def _draw_narrow(ax, x, y, w, h, accent, face, technical, zone):
    """Uski element (flaše/začini / izvlačni)."""
    mid = x + w / 2

    # Police (indikativno)
    n_s = 4 if zone == "wall" else 3
    for i in range(1, n_s):
        sy = y + int(h * i / n_s)
        ax.plot([x + 2, x + w - 2], [sy, sy], color=accent, linewidth=0.5,
                alpha=0.5, zorder=12)

    # RUČKA: vertikalna, centrirana po širini.
    # - Za BASE/TALL: bliže GORNJOJ ivici (hvatanje odozgo)
    # - Za WALL: bliže DONJOJ ivici (hvatanje odozdo)
    # _handle_v crta oko centra (cx, cy), pa cy računamo tako da gornja/donja ivica
    # bude približno 60mm od ivice fronta.

    half_len = DOOR_HANDLE_V_LEN / 2.0  # fiksna dužina ručke (definisana gore)

    if zone == "wall":
        # donja ivica ručke ~60mm iznad dna fronta
        bottom_off = 60.0
        cy = y + bottom_off + half_len
    else:
        # gornja ivica ručke ~60mm ispod vrha fronta
        top_off = 60.0 if h >= 600 else (45.0 if h >= 420 else 35.0)
        cy = (y + h) - top_off - half_len

    # clamp: da ručka ne izađe van fronta kod nižih elemenata
    cy = max(y + half_len + 10.0, min(y + h - half_len - 10.0, cy))

    cx = mid
    _handle_v(ax, cx, cy, technical=technical)


def _draw_panel(ax, x, y, w, h, accent, face, technical, tid: str = ""):
    """Dekorativni paneli: filer i završna bočna ploča."""
    _tid = str(tid or "").upper()
    if "FILLER" in _tid:
        panel_w = max(10, min(w * 0.34, 42))
        px = x + (w - panel_w) / 2.0
        ax.add_patch(plt.Rectangle(
            (px, y + 2), panel_w, max(4, h - 4),
            facecolor=face if not technical else "none",
            edgecolor=accent, linewidth=0.9, zorder=12
        ))
        for _yy in (0.22, 0.46, 0.70, 0.86):
            gy = y + h * _yy
            ax.plot([px + 3, px + panel_w - 3], [gy, gy],
                    color=accent, linewidth=0.45, alpha=0.30, zorder=13)
    else:
        panel_w = max(18, min(w * 0.46, 64))
        px = x + (w - panel_w) / 2.0 - 3.0
        side_w = max(5, min(panel_w * 0.16, 10))
        ax.add_patch(plt.Rectangle(
            (px, y + 2), panel_w, max(4, h - 4),
            facecolor=face if not technical else "none",
            edgecolor=accent, linewidth=0.9, zorder=12
        ))
        if not technical:
            ax.add_patch(plt.Rectangle(
                (px + panel_w, y + 5), side_w, max(4, h - 10),
                facecolor=_darken_color(face, 0.82),
                edgecolor=accent, linewidth=0.5, alpha=0.95, zorder=11
            ))
        for _yy in (0.24, 0.48, 0.72):
            gy = y + h * _yy
            ax.plot([px + 4, px + panel_w - 4], [gy, gy],
                    color=accent, linewidth=0.45, alpha=0.28, zorder=13)

# =========================================================
# Glavni dispatcher — crta unutrasnjost elementa
# =========================================================
def _draw_module_interior(ax, x: int, y: int, w: int, h: int,
                          zone: str, etype: str, accent: str, face: str,
                          technical: bool,
                          m: Optional[Dict[str, Any]] = None,
                          front_face: Optional[str] = None,
                          worktop_thk_mm: int = 38) -> None:
    """Crta unutrasnji sadrzaj elementa u zavisnosti od tipa."""
    params = (m.get("params", {}) or {}) if m else {}

    _is_wardrobe = bool(params.get('wardrobe', False)) or ('WARDROBE' in str((m or {}).get('template_id', '')).upper())
    if zone == 'tall' and _is_wardrobe:
        _draw_wardrobe_layout(ax, x, y, w, h, accent, technical, params=params)
        if str(params.get('front_style', 'both')).lower() == 'inside':
            return

    if etype == "drawers":
        drawer_heights = params.get("drawer_heights", None)
        n = int(params.get("n_drawers", 4 if h > 600 else 3))
        _draw_base_drawers(ax, x, y, w, h, accent, technical, n_drawers=n, drawer_heights=drawer_heights)
    elif etype == "oven_hob":
        # Fioka je uvek prisutna — industrijski standard
        _draw_oven_hob(ax, x, y, w, h, accent, face, technical,
                       drawer_face=front_face,
                       has_drawer=True, worktop_thk_mm=worktop_thk_mm)
    elif etype == "oven_hob_freestanding":
        _draw_oven_hob_freestanding(ax, x, y, w, h, accent, technical)
    elif etype == "doors_drawers":
        _draw_base_doors_drawers(ax, x, y, w, h, accent, face, technical, params=params, m=m)
    elif etype == "sink":
        _draw_base_doors(ax, x, y, w, h, accent, face, technical, m=m)  # vrata ispod
        if _is_sink(m):
            _draw_sink(ax, x, y, w, h, accent, face, technical, worktop_thk_mm=worktop_thk_mm)
    elif etype == "hob":
        _draw_base_doors(ax, x, y, w, h, accent, face, technical, m=m)  # vrata ispod
        _draw_hob(ax, x, y, w, h, accent, face, technical)
    elif etype == "oven":
        if zone == "tall":
            _draw_tall_oven(ax, x, y, w, h, accent, front_face or face, technical)
        else:
            _draw_oven(ax, x, y, w, h, accent, face, technical)
    elif etype == "oven_micro":
        if zone == "tall":
            _draw_tall_oven_micro(ax, x, y, w, h, accent, front_face or face, technical)
        else:
            _draw_oven_micro(ax, x, y, w, h, accent, face, technical)
    elif etype == "dishwasher":
        _draw_dishwasher(ax, x, y, w, h, accent, face, technical, m=m)
    elif etype == "dishwasher_freestanding":
        _draw_dishwasher_freestanding(ax, x, y, w, h, accent, technical)
    elif etype == "fridge_under":
        _draw_fridge_under(ax, x, y, w, h, accent, face, technical)
    elif etype == "fridge":
        _draw_fridge(ax, x, y, w, h, accent, face, technical)
    elif etype == "pantry":
        _dc = int(params.get("door_count", 2) or 2)
        _hs = str(params.get("handle_side", "right") or "right")
        _ns = int(params.get("n_shelves", 4) or 4)
        _draw_pantry(ax, x, y, w, h, accent, face, technical,
                     door_count=_dc, handle_side=_hs, n_shelves=_ns)
    elif etype == "hood":
        _draw_hood(ax, x, y, w, h, accent, face, technical)
    elif etype == "microwave":
        _draw_microwave(ax, x, y, w, h, accent, face, technical)
    elif etype == "glass":
        _draw_glass_doors(ax, x, y, w, h, accent, face, technical)
    elif etype == "liftup":
        _draw_liftup(ax, x, y, w, h, accent, face, technical)
    elif etype == "open":
        _n_sh = int((m.get("params") or {}).get("n_shelves", 0) or 0)
        if _n_sh <= 0:
            _n_sh = max(1, int((h - 2 * 18) / 250))
        _draw_open(ax, x, y, w, h, accent, face, technical, n_shelves=_n_sh)
    elif etype == "corner":
        _draw_corner(ax, x, y, w, h, accent, face, technical, zone, m=m)
    elif etype == "narrow":
        _draw_narrow(ax, x, y, w, h, accent, face, technical, zone)
    elif etype == "panel":
        _draw_panel(ax, x, y, w, h, accent, face, technical, tid=str((m or {}).get("template_id", "")))
    elif etype in ("tall_doors", "doors"):
        if zone == "tall":
            _draw_tall_doors(ax, x, y, w, h, accent, face, technical, m=m)
        elif zone == "wall":
            _draw_wall_doors(ax, x, y, w, h, accent, face, technical, m=m)
        else:
            _draw_base_doors(ax, x, y, w, h, accent, face, technical, m=m)
    else:
        # Default: vrata
        if zone == "tall":
            _draw_tall_doors(ax, x, y, w, h, accent, face, technical)
        elif zone == "wall":
            _draw_wall_doors(ax, x, y, w, h, accent, face, technical)
        else:
            _draw_base_doors(ax, x, y, w, h, accent, face, technical)


def _preview_short_partcode(value: Any) -> str:
    txt = str(value or "").strip()
    if not txt:
        return ""
    if "-" in txt:
        return txt.rsplit("-", 1)[-1]
    return txt


def _partcodes_for_preview(part_rows: list[dict[str, Any]] | None, m: Dict[str, Any]) -> dict[str, list[str]]:
    if not part_rows:
        return {}
    buckets: dict[str, list[str]] = {
        "front_drawer": [],
        "front_door": [],
        "front_other": [],
        "panel": [],
        "general": [],
    }
    is_panel = _detect_type(m) == "panel"
    for row in part_rows:
        code = _preview_short_partcode(row.get("PartCode", ""))
        if not code:
            continue
        deo = str(row.get("Deo", "") or "").lower()
        buckets["general"].append(code)
        if "panel" in deo or "ploča" in deo or "ploca" in deo:
            buckets["panel"].append(code)
        if code.startswith("F"):
            if "fiok" in deo:
                buckets["front_drawer"].append(code)
            elif "vrat" in deo or "frižider" in deo or "frizider" in deo or "rerna" in deo:
                buckets["front_door"].append(code)
            else:
                buckets["front_other"].append(code)
        elif is_panel and code.startswith(("C", "P", "F")):
            buckets["panel"].append(code)
    return buckets


def _annotate_element_preview_regions(
    ax,
    m: Dict[str, Any],
    x: float,
    y: float,
    w: int,
    h: int,
    *,
    label_mode: str = "zones",
    part_rows: list[dict[str, Any]] | None = None,
) -> None:
    """Diskretne oznake za per-element 2D preview.

    `label_mode="zones"` koristi stabilne F/P zone.
    `label_mode="part_codes"` prikazuje kratke oznake izvedene iz stvarnog PartCode-a.
    """
    etype = _detect_type(m)
    zone = str(m.get("zone", "base")).lower()
    params = (m.get("params", {}) or {})
    code_map = _partcodes_for_preview(part_rows, m) if label_mode == "part_codes" else {}
    fs = max(7, min(10, int(min(w, h) * 0.018)))
    box_fc = "#FFF7D6"
    box_ec = "#9A8A54"
    txt_c = "#4A4230"

    def _pick(group: str, index: int, fallback: str) -> str:
        vals = code_map.get(group) or []
        if index < len(vals):
            return vals[index]
        if group != "general":
            vals = code_map.get("general") or []
            if index < len(vals):
                return vals[index]
        return fallback

    def _tag(px: float, py: float, text: str) -> None:
        ax.text(
            px, py, text,
            fontsize=fs, ha="center", va="center",
            color=txt_c, fontweight="bold", zorder=24,
            bbox=dict(boxstyle="round,pad=0.18", fc=box_fc, ec=box_ec, lw=0.6, alpha=0.92),
        )

    if etype == "doors_drawers":
        drawer_heights = params.get("drawer_heights", None)
        door_height = params.get("door_height", None)
        if door_height is not None:
            door_h = int(door_height)
        elif drawer_heights and len(drawer_heights) > 0:
            door_h = h - int(drawer_heights[0])
        else:
            door_h = int(h * 0.72)
        drawer_h = h - door_h
        _tag(x + w * 0.50, y + door_h + drawer_h * 0.55, _pick("front_drawer", 0, "F1"))
        _tag(x + w * 0.25, y + door_h * 0.50, _pick("front_door", 0, "F2"))
        _tag(x + w * 0.75, y + door_h * 0.50, _pick("front_door", 1, "F3"))
        return

    if etype == "drawers":
        n = int(params.get("n_drawers", 4 if h > 600 else 3))
        n = max(1, min(6, n))
        weights = params.get("drawer_heights", None) or [1] * n
        segs = _compute_drawer_segments(h, weights, gap_mm=_FRONT_GAP_MM)
        cursor_y = y + h - _FRONT_GAP_MM
        for i, dh in enumerate(segs):
            cursor_y -= dh
            _tag(x + w * 0.50, cursor_y + dh * 0.50, _pick("front_drawer", i, f"F{i+1}"))
            if i < len(segs) - 1:
                cursor_y -= _FRONT_GAP_MM
        return

    if etype in ("doors", "tall_doors"):
        num_doors = 1
        tid = str(m.get("template_id", "")).upper()
        lbl = str(m.get("label", "")).lower()
        if ("2DOOR" in tid) or ("DOORS" in tid) or any(k in lbl for k in ("2 vrata", "dvokril")):
            num_doors = 2
        if num_doors == 2:
            _tag(x + w * 0.25, y + h * 0.50, _pick("front_door", 0, "F1"))
            _tag(x + w * 0.75, y + h * 0.50, _pick("front_door", 1, "F2"))
        else:
            _tag(x + w * 0.50, y + h * 0.50, _pick("front_door", 0, "F1"))
        return

    if etype in ("dishwasher", "fridge", "fridge_under"):
        _tag(x + w * 0.50, y + h * 0.50, _pick("front_door", 0, "F1"))
        return

    if etype == "oven_hob":
        _tag(x + w * 0.50, y + h * 0.10, _pick("front_drawer", 0, "F1"))
        return

    if etype == "panel":
        _tag(x + w * 0.50, y + h * 0.50, _pick("panel", 0, "P1"))
        return


# =========================================================
# Crtanje jednog modula (okvir + sadrzaj + id)
# =========================================================
def _draw_module(ax, m: Dict[str, Any], x: int, y: int, w: int, h: int,
                 zone: str, technical: bool, worktop_thk_mm: int = 38,
                 selected: bool = False, global_front_color: str = GLOBAL_FRONT_DEFAULT,
                 appliance_color: str = APPLIANCE_COLOR) -> None:
    """Crta jedan element: pravougaonik okvira + detalji unutra."""
    face   = ZONE_FACE.get(zone, "#F8F8F8")
    edge   = ZONE_EDGE.get(zone, "#1A1A1A")
    accent = ZONE_ACCENT.get(zone, "#555555")

    mid_id = str(m.get("id", "?"))
    etype = _detect_type(m)
    _is_freestanding_appliance = etype in ("dishwasher_freestanding", "oven_hob_freestanding")
    if not technical:
        if etype == "open":
            _fc_open = str(global_front_color or GLOBAL_FRONT_DEFAULT).strip()
            if _fc_open.startswith("#") and len(_fc_open) in (4, 7, 9):
                face = _fc_open
                accent = _contrast_accent(_fc_open)
        elif _has_front_panel(m, etype):
            _fc = str(global_front_color or GLOBAL_FRONT_DEFAULT).strip()
            if _fc.startswith("#") and len(_fc) in (4, 7, 9):
                face = _fc
                accent = _contrast_accent(_fc)
        else:
            _ac = str(appliance_color or APPLIANCE_COLOR).strip()
            if _ac.startswith("#") and len(_ac) in (4, 7, 9):
                face = _ac
                accent = _contrast_accent(_ac)

    _set_handle_palette(face)

    # Glavni okvir
    # NOTE: Za gornje nadgradnje (tall_top / wall_upper) ne crtamo donju ivicu
    # da izbegnemo duplu crnu liniju na spoju sa elementom ispod.
    _border_lw = 2.0 if selected else 1.4
    _border_color = "#1F2937" if selected else edge
    _face = "white" if technical else face
    if zone in ("tall_top", "wall_upper"):
        ax.add_patch(plt.Rectangle(
            (x, y), w, h,
            facecolor=_face,
            edgecolor="none", linewidth=0, zorder=10
        ))
        ax.plot([x, x], [y, y + h], color=_border_color, linewidth=_border_lw, zorder=10)
        ax.plot([x + w, x + w], [y, y + h], color=_border_color, linewidth=_border_lw, zorder=10)
        ax.plot([x, x + w], [y + h, y + h], color=_border_color, linewidth=_border_lw, zorder=10)
    else:
        ax.add_patch(plt.Rectangle(
            (x, y), w, h,
            facecolor=_face,
            edgecolor=_border_color, linewidth=_border_lw, zorder=10
        ))

    # Selected highlight — CAD style (tamna ivica bez popune)

    # Bočna sena (desna ivica) — simulira dubinu elementa, 3D efekat u 2D
    if not technical and not _is_freestanding_appliance:
        side_w = max(5, int(w * 0.055))  # širina bočne sene ~5.5% od w
        side_w = min(side_w, 24)         # maksimum 24mm
        ax.add_patch(plt.Rectangle(
            (x + w - side_w, y), side_w, h,
            facecolor=ZONE_SIDE_COLOR,
            edgecolor="none",
            linewidth=0, zorder=10, alpha=0.55
        ))
        # Gornja sena (tanka traka na vrhu) — perspektivni efekat
        top_h = max(3, int(h * 0.025))
        ax.add_patch(plt.Rectangle(
            (x, y + h - top_h), w - side_w, top_h,
            facecolor="#D0D0D0",
            edgecolor="none",
            linewidth=0, zorder=10, alpha=0.45
        ))

    # Unutrasnja linija (rub fronta) — tanka, diskretna, svetlosiva
    inset_f = max(5, int(min(w, h) * 0.04))
    if not _is_freestanding_appliance:
        ax.add_patch(plt.Rectangle(
            (x + inset_f, y + inset_f), max(2, w - 2 * inset_f), max(2, h - 2 * inset_f),
            facecolor="none",
            edgecolor="#CCCCCC" if not technical else "#AAAAAA",
            linewidth=0.4, alpha=0.5, zorder=11
        ))

    # Unutrasnji sadrzaj (prosledi ceo modul i worktop_thk za params)
    _front_face = str(global_front_color or GLOBAL_FRONT_DEFAULT).strip()
    _draw_module_interior(ax, x, y, w, h, zone, etype, accent, face, technical,
                          m=m, front_face=_front_face, worktop_thk_mm=worktop_thk_mm)

    # Nosač radne ploče — dashed linija u tehničkom modu za base elemente
    _NO_NOSAC_KW = ("FRIDGE", "DISHWASHER", "FREESTANDING")
    if (zone == "base" and technical
            and not any(kw in str(m.get("template_id", "")).upper() for kw in _NO_NOSAC_KW)):
        _NOSAC_H = 96  # standardna visina nosača (ista kao u cutlist.py)
        _yn = y + h - _NOSAC_H
        if _yn > y + 20:  # element mora biti dovoljno visok
            ax.plot([x + 4, x + w - 4], [_yn, _yn],
                    color="#777777", linewidth=0.75,
                    linestyle="--", zorder=12, alpha=0.70)
            if w >= 180:
                ax.text(x + w * 0.5, _yn - 4,
                        "NRP",
                        fontsize=max(4.5, FONT_LBL - 1.5),
                        ha="center", va="top",
                        color="#888888", alpha=0.75, zorder=13)

    # CUSTOM depth marker — narandžasta isprekidana ivica + badge "D"
    _dm_params = m.get("params") or {}
    _dm = str(_dm_params.get("depth_mode", m.get("depth_mode", "STANDARD"))).upper()
    if _dm == "CUSTOM":
        ax.add_patch(plt.Rectangle(
            (x + 1, y + 1), w - 2, h - 2,
            facecolor="none",
            edgecolor="#E07B00",
            linewidth=1.2, linestyle=(0, (4, 3)),
            zorder=28, alpha=0.85
        ))
        _bw, _bh = max(22, int(w * 0.12)), max(12, int(h * 0.06))
        _bw = min(_bw, 36); _bh = min(_bh, 18)
        ax.add_patch(plt.Rectangle(
            (x + w - _bw - 3, y + 3), _bw, _bh,
            facecolor="#E07B00", edgecolor="none",
            linewidth=0, zorder=29, alpha=0.88
        ))
        ax.text(x + w - _bw * 0.5 - 3, y + 3 + _bh * 0.5, "D",
                fontsize=max(4.5, _bh * 0.55),
                ha="center", va="center",
                color="white", fontweight="bold", zorder=30)

    # ── ID broj — diskretan, gornji lijevi ugao ───────────────────────────────
    _mid = int(m.get("id", 0))
    if _mid > 0:
        _id_fs = max(4.5, min(6.5, w / 90.0))
        _pad   = max(5, int(min(w, h) * 0.035))
        ax.text(
            x + _pad, y + h - _pad,
            str(_mid),
            fontsize=_id_fs,
            ha="left", va="top",
            color="#B0B0B0" if not technical else "#888888",
            fontweight="normal",
            zorder=29,
            clip_on=True,
        )


# =========================================================
# Feet + kickboard + countertop + ceiling filler
# =========================================================
def _draw_feet(ax, x: int, w: int, foot_mm: int, technical: bool) -> None:
    if foot_mm <= 0 or w <= 0:
        return
    leg_h = int(foot_mm)
    leg_w = int(max(18, min(40, w * 0.07)))
    inset = int(max(10, min(35, w * 0.07)))
    if leg_w * 2 + inset * 2 > w:
        leg_w = max(10, w // 6)
        inset = max(6, (w - 2 * leg_w) // 4)

    for px in (x + inset, x + w - inset - leg_w):
        ax.add_patch(plt.Rectangle(
            (px, 0), leg_w, leg_h,
            facecolor="none" if technical else "#C8C8C8",
            edgecolor="#888888", linewidth=0.6, zorder=8, alpha=0.9
        ))


def _draw_fridge_vent_plinth(ax, x: int, w: int, foot_mm: int, technical: bool) -> None:
    """Integrated tall fridge sits on a ventilated plinth, not directly on the floor."""
    if foot_mm <= 0 or w <= 0:
        return
    inset = int(max(8, min(28, w * 0.045)))
    h = int(foot_mm)
    px = x + inset
    pw = max(8, w - 2 * inset)
    ax.add_patch(plt.Rectangle(
        (px, 0), pw, h,
        facecolor="none" if technical else "#4A4A4A",
        edgecolor="#333333" if technical else "#222222",
        linewidth=0.9, zorder=9, alpha=0.95
    ))
    grille_w = max(40, min(int(pw * 0.62), pw - 16))
    grille_x = px + (pw - grille_w) / 2
    slat_count = 4
    for i in range(slat_count):
        gy = h * (0.32 + i * 0.11)
        ax.plot(
            [grille_x, grille_x + grille_w],
            [gy, gy],
            color="#D8D8D8" if not technical else "#777777",
            linewidth=1.0 if not technical else 0.8,
            zorder=10,
            alpha=0.95,
        )


def _base_span(mods: List[Dict[str, Any]], zones: Tuple[str, ...]) -> Optional[Tuple[int, int]]:
    xs = []
    for m in mods:
        z = str(m.get("zone", "")).lower().strip()
        if z in zones and int(m.get("w_mm", 0)) > 0:
            x0 = int(m.get("x_mm", 0))
            x1 = x0 + int(m.get("w_mm", 0))
            xs.append((x0, x1))
    if not xs:
        return None
    return min(a for a, _ in xs), max(b for _, b in xs)


def _draw_countertop(ax, kitchen: Dict[str, Any], mods: List[Dict[str, Any]],
                     wall_len: int, technical: bool) -> None:
    wt = (kitchen.get("worktop", {}) or {})
    thickness_mm = int(round(float(wt.get("thickness", 0.0)) * 10.0))
    if thickness_mm <= 0:
        return
    _base_mods = [
        m for m in mods
        if str(m.get("zone", "")).lower().strip() == "base"
        and str(m.get("template_id", "")).upper() not in {"BASE_DISHWASHER_FREESTANDING", "BASE_OVEN_HOB_FREESTANDING"}
        and int(m.get("w_mm", 0)) > 0
    ]
    span = _base_span(_base_mods, ("base",))
    if not span:
        return
    x0_total, x1_total = span
    x0_total = max(0, min(wall_len, x0_total))
    x1_total = max(0, min(wall_len, x1_total))
    if x1_total <= x0_total:
        return
    thickness_mm = max(10, thickness_mm)
    base_y, base_h = _zone_baseline_and_height(kitchen, "base")
    y = base_y + base_h

    # Tall/fridge X-opsezi — radna ploča se NE crta iznad tall/fridge elemenata
    _tall_excl = []
    for _m in mods:
        _mz = str(_m.get("zone", "")).lower().strip()
        if _mz == "tall":
            _ta = int(_m.get("x_mm", 0))
            _tb = _ta + int(_m.get("w_mm", 0))
            _tall_excl.append((_ta, _tb))

    # Podeli radnu ploču na segmente koji zaobilaze tall/fridge X opsege
    # Koristi samo BASE module kao segmente (ne ceo span)
    base_segs = sorted(
        [(int(m.get("x_mm", 0)), int(m.get("x_mm", 0)) + int(m.get("w_mm", 0)))
         for m in mods if str(m.get("zone", "")).lower().strip() == "base"
         and str(m.get("template_id", "")).upper() not in {"BASE_DISHWASHER_FREESTANDING", "BASE_OVEN_HOB_FREESTANDING"}
         and int(m.get("w_mm", 0)) > 0],
        key=lambda s: s[0]
    )

    def _draw_seg(sx0: int, sx1: int) -> None:
        sx0 = max(0, min(wall_len, sx0))
        sx1 = max(0, min(wall_len, sx1))
        if sx1 <= sx0:
            return
        ax.add_patch(plt.Rectangle(
            (sx0, y), sx1 - sx0, thickness_mm,
            facecolor="none" if technical else "#3C3835",
            edgecolor="#555555" if technical else "#282422",
            linewidth=1.0, zorder=6
        ))
        ax.plot([sx0, sx1], [y + thickness_mm, y + thickness_mm],
                color="#1A1816", linewidth=1.3, zorder=7)
        ax.plot([sx0, sx1], [y, y], color="#2A2624", linewidth=0.8, zorder=7)

    if not _tall_excl:
        # Nema tall elemenata — crta se samo nad stvarnim base segmentima
        for (ba, bb) in base_segs:
            _draw_seg(ba, bb)
        return

    # Crta se samo nad BASE modulima koji nisu pokriveni tall/fridge
    for (ba, bb) in base_segs:
        # Proveri da li se ovaj BASE segment preklapa sa nekim tall opsegom
        covered = any(ba >= _ta and bb <= _tb for _ta, _tb in _tall_excl)
        if not covered:
            _draw_seg(ba, bb)


def _draw_kickboard(ax, kitchen: Dict[str, Any], mods: List[Dict[str, Any]],
                    wall_len: int, technical: bool, enabled: bool) -> None:
    if not enabled:
        return
    if "foot_height_mm" in kitchen:
        foot_mm = int(kitchen["foot_height_mm"])
    else:
        foot_mm = int(round(float(kitchen.get("foot_height", 0.0)) * 10.0))
    if foot_mm <= 0:
        return
    _base_mods = [
        m for m in mods
        if str(m.get("zone", "")).lower().strip() == "base"
        and str(m.get("template_id", "")).upper() not in {"BASE_DISHWASHER_FREESTANDING", "BASE_OVEN_HOB_FREESTANDING"}
        and int(m.get("w_mm", 0)) > 0
    ]
    span = _base_span(_base_mods, ("base",))
    if not span:
        return
    x0, x1 = span
    x0 = max(0, min(wall_len, x0))
    x1 = max(0, min(wall_len, x1))
    if x1 <= x0:
        return

    inset = 4
    ax.add_patch(plt.Rectangle(
        (x0 + inset, 0), x1 - x0 - 2 * inset, foot_mm,
        facecolor="none" if technical else "#484848",
        edgecolor="#333333" if technical else "#222222",
        linewidth=1.0, zorder=9, alpha=0.92
    ))


def _draw_ceiling_filler(ax, kitchen: Dict[str, Any], mods: List[Dict[str, Any]],
                          wall_len: int, wall_h: int,
                          technical: bool, enabled: bool) -> None:
    if not enabled:
        return
    span = _base_span(mods, ("wall",))
    if not span:
        return
    y0, h = _zone_baseline_and_height(kitchen, "wall")
    top = y0 + h
    if top >= wall_h - 1:
        return
    x0, x1 = span
    x0 = max(0, min(wall_len, x0))
    x1 = max(0, min(wall_len, x1))
    if x1 <= x0:
        return
    ax.add_patch(plt.Rectangle(
        (x0, top), x1 - x0, wall_h - top,
        facecolor="none" if technical else "#D8D5CE",
        edgecolor="#999999", linewidth=0.6,
        linestyle="--", zorder=7, alpha=0.6
    ))


# =========================================================
# Kotiranje (tehnicko)
# =========================================================
def _dim_arrow(ax, x0: int, x1: int, y: int, txt: str, above: bool = False,
               bold: bool = False) -> None:
    if x1 <= x0:
        return
    clr = "#222222" if not bold else "#111111"
    lw = 0.9 if not bold else 1.1
    tk = 9 if not bold else 11
    ax.plot([x0, x0], [y - tk, y + tk], color=clr, linewidth=lw, zorder=50)
    ax.plot([x1, x1], [y - tk, y + tk], color=clr, linewidth=lw, zorder=50)
    ax.annotate(
        "",
        xy=(x0, y), xytext=(x1, y),
        arrowprops=dict(arrowstyle="<->", color=clr, lw=lw, shrinkA=0, shrinkB=0),
        zorder=51,
    )
    va = "bottom" if above else "top"
    dy = 13 if above else -13
    fw = "bold" if bold else "normal"
    fs = FONT_DIM + 1 if bold else FONT_DIM
    fc = "#F0F0EE" if bold else "white"
    ax.text((x0 + x1) / 2, y + dy, txt,
            fontsize=fs, ha="center", va=va, color=clr, fontweight=fw, zorder=52,
            bbox=dict(boxstyle="round,pad=0.2", fc=fc, ec="#AAAAAA" if bold else "none",
                      alpha=0.90, lw=0.5))


def _dim_chain(ax, segments: List[Tuple[int, int]], y: int, above: bool = False) -> None:
    if not segments:
        return
    for (a, b) in sorted(segments, key=lambda t: t[0]):
        _dim_arrow(ax, a, b, y, f"{int(b - a)}", above=above)


def _dim_vertical_stack(ax, kitchen: Dict[str, Any]) -> None:
    if "foot_height_mm" in kitchen:
        foot_mm = int(kitchen["foot_height_mm"])
    else:
        foot_mm = int(round(float(kitchen.get("foot_height", 0.0)) * 10.0))
    zones = (kitchen.get("zones", {}) or {})
    base_h_mm = int(kitchen.get("base_korpus_h_mm",
                    (zones.get("base", {}) or {}).get("height_mm", 720)))
    wt = (kitchen.get("worktop", {}) or {})
    worktop_thk_mm = int(round(float(wt.get("thickness", 0.0)) * 10.0))

    total_mm = max(0, foot_mm) + max(0, base_h_mm) + max(0, worktop_thk_mm)
    if total_mm <= 0:
        return

    x = -55
    ax.plot([x, x], [0, total_mm], color="#444444", linewidth=0.8, zorder=55)

    cur = 0
    parts = [("stopice", foot_mm), ("korpus", base_h_mm), ("ploca", worktop_thk_mm)]
    for name, h in parts:
        if h <= 0:
            continue
        ax.plot([x - 7, x + 7], [cur, cur], color="#444444", linewidth=0.7, zorder=56)
        ax.plot([x - 7, x + 7], [cur + h, cur + h], color="#444444", linewidth=0.7, zorder=56)
        ax.text(x - 10, cur + h / 2, f"{h}",
                fontsize=FONT_DIM, ha="right", va="center", color="#444444", zorder=57)
        cur += h

    ax.plot([x - 9, x + 9], [total_mm, total_mm], color="#333333", linewidth=1.0, zorder=57)
    ax.text(x - 10, total_mm + 12, f"{total_mm}",
            fontsize=FONT_DIM, ha="right", va="bottom", color="#333333", zorder=57)


def _dim_vertical_wall(ax, kitchen: Dict[str, Any], mods: list) -> None:
    """
    Za svaki WALL i TALL_TOP element, prikazuje vertikalnu kotu
    (visina h_mm) sa desne strane elementa — u tehnickom modu.
    Kota je plava (#1A5276), rotiran tekst, sa dvosmernom strelicom.
    """
    wall_mods = [m for m in mods if str(m.get("zone", "")).lower().strip() in ("wall", "tall_top", "wall_upper")]
    if not wall_mods:
        return

    # X-opsezi TALL elemenata — WALL na istom X se preskaču (nisu nacrtani)
    _tall_r = []
    for _tm in mods:
        if str(_tm.get("zone", "")).lower().strip() == "tall":
            _ta = int(_tm.get("x_mm", 0))
            _tall_r.append((_ta, _ta + int(_tm.get("w_mm", 0))))

    for m in wall_mods:
        x0 = int(m.get("x_mm", 0))
        w  = int(m.get("w_mm", 0))
        h  = int(m.get("h_mm", 0))
        if w <= 0 or h <= 0:
            continue
        x1 = x0 + w
        zone_key = str(m.get("zone", "wall")).lower().strip()
        # Preskoči WALL elemente koji su pokriveni TALL-om (nisu ni nacrtani)
        if zone_key == "wall" and any(x0 >= _ta and x1 <= _tb for _ta, _tb in _tall_r):
            continue
        # tall_top elementi imaju dinamički Y oslonjen na tall element ispod
        if zone_key == "tall_top":
            y0 = _y_for_tall_top(kitchen, m, mods)
        elif zone_key == "wall_upper":
            y0 = _y_for_wall_upper(kitchen, m, mods)
        else:
            y0, _ = _zone_baseline_and_height(kitchen, zone_key)

        # Vertikalna linija kote sa desne strane elementa
        xk = x1 + 18
        ax.plot([xk, xk], [y0, y0 + h], color="#1A5276", linewidth=0.8, zorder=55)
        # Horizontalni tikovi na krajevima
        ax.plot([xk - 5, xk + 5], [y0, y0], color="#1A5276", linewidth=0.7, zorder=56)
        ax.plot([xk - 5, xk + 5], [y0 + h, y0 + h], color="#1A5276", linewidth=0.7, zorder=56)
        # Strelice (gore i dole)
        ax.annotate("", xy=(xk, y0 + h), xytext=(xk, y0 + h * 0.6),
                    arrowprops=dict(arrowstyle="->", color="#1A5276", lw=0.8),
                    zorder=57)
        ax.annotate("", xy=(xk, y0), xytext=(xk, y0 + h * 0.4),
                    arrowprops=dict(arrowstyle="->", color="#1A5276", lw=0.8),
                    zorder=57)
        # Tekst dimenzije — rotiran 90°, sredina kote
        ax.text(xk + 8, y0 + h / 2, f"{h}mm",
                fontsize=FONT_DIM, ha="left", va="center",
                color="#1A5276", rotation=90, zorder=58)


# =========================================================
# Pomoci za prikaz slobodnog prostora
# =========================================================
def _draw_fillers(ax, kitchen: Dict[str, Any], technical: bool) -> None:
    """
    Crta sive filler blokove na mestima gde su obrisani elementi (keep_gap=True).
    Filler je vidljiv kao sivi blok sa isprekidanom ivicom, šrafurom i tekstom.
    """
    fillers = kitchen.get("fillers") or []
    if not fillers:
        return

    for f in fillers:
        x = int(f.get("x_mm", 0))
        w = int(f.get("w_mm", 0))
        if w <= 0:
            continue
        zone = str(f.get("zone", "base")).lower().strip()

        y0, zh = _zone_baseline_and_height(kitchen, zone)

        # Sivi blok sa isprekidanom ivicom
        ax.add_patch(plt.Rectangle(
            (x, y0), w, zh,
            facecolor="#E0E0E0" if not technical else "none",
            edgecolor="#888888",
            linewidth=1.1,
            linestyle="--",
            alpha=0.75,
            zorder=8
        ))

        # Dijagonalne šrafura linije unutar bloka
        n_lines = max(3, w // 100)
        step_x = w / max(n_lines, 1)
        for i in range(n_lines + 2):
            lx0 = x + i * step_x
            lx1 = lx0 + zh * 0.6
            ax.plot(
                [min(lx0, x + w), min(lx1, x + w)],
                [y0, min(y0 + (lx1 - lx0) / 0.6 * 0.6, y0 + zh)],
                color="#BBBBBB", linewidth=0.6, alpha=0.6, zorder=9
            )

        # Tekst u sredini bloka
        cx = x + w / 2
        cy = y0 + zh / 2
        lbl = f.get("label", f"{w}mm")
        _filler_lang = str((kitchen or {}).get("language", "sr") or "sr").lower().strip()
        ax.text(
            cx, cy,
            f"← {w}mm →\n{_tr_i18n('canvas.free_space', _filler_lang)}",
            fontsize=max(5, FONT_LBL),
            ha="center", va="center",
            color="#666666",
            fontweight="bold",
            zorder=20
        )


def _draw_free_space_info(ax, kitchen, mods, wall_len, wall_h, technical):
    """
    Prikazuje slobodan prostor:
      - Horizontalna traka (tanka) desno od zadnjeg elementa u svakoj zoni
      - Iznad visokih elemenata: horizontalna traka do plafona
    """
    left_clear, right_clear, _ = _profile_clearance_mm(kitchen)
    usable_end = wall_len - right_clear

    accent_free = "#CC4444"
    STRIP_H = 30  # visina horizontalne trake u mm

    for zone_key in ("base", "wall", "tall"):
        zone_mods = [m for m in mods if str(m.get("zone","")).lower().strip() == zone_key]
        if not zone_mods:
            continue
        rightmost = max(int(m.get("x_mm", 0)) + int(m.get("w_mm", 0)) for m in zone_mods)
        free_right = usable_end - rightmost
        if free_right > 5:
            y_base, zh = _zone_baseline_and_height(kitchen, zone_key)
            if zone_key == "base":
                zones = kitchen.get("zones", {}) or {}
                base_h_v = int(kitchen.get("base_korpus_h_mm",
                               (zones.get("base", {}) or {}).get("height_mm", 720)))
                cy = y_base + base_h_v / 2  # sredina zone
            elif zone_key == "wall":
                cy = y_base + zh / 2
            else:  # tall
                cy = y_base + zh / 2

            # Horizontalna traka — samo desno od zadnjeg elementa
            strip_y = cy - STRIP_H / 2
            ax.add_patch(plt.Rectangle(
                (rightmost, strip_y), free_right, STRIP_H,
                facecolor="#FFE8E8" if not technical else "none",
                edgecolor=accent_free, linewidth=0.7,
                linestyle="--", alpha=0.55, zorder=5
            ))
            # Strelica + tekst — samo u tehničkom modu
            if technical:
                ax.annotate(
                    _free_space_label(kitchen, free_right),
                    xy=(rightmost, cy), xytext=(rightmost + free_right / 2, cy),
                    fontsize=6.0, ha="center", va="center",
                    color=accent_free, alpha=0.9, zorder=17,
                )

    # Slobodan prostor iznad svakog tall elementa (ako nema tall_top)
    # Prikazuje se kao horizontalna traka pri vrhu tall elementa
    tall_top_mods = [m for m in mods if str(m.get("zone","")).lower().strip() == "tall_top"]
    tall_top_xs = {int(m.get("x_mm", 0)) for m in tall_top_mods}
    foot_mm = _get_foot_mm(kitchen)

    for m in mods:
        if str(m.get("zone","")).lower().strip() != "tall":
            continue
        tx = int(m.get("x_mm", 0))
        th = int(m.get("h_mm", 2100))
        tw = int(m.get("w_mm", 600))
        if tx in tall_top_xs:
            continue  # Vec ima popunu
        top_y = foot_mm + th
        free_h = wall_h - top_y - 20
        if free_h > 30:
            # Horizontalna traka iznad tall-a
            strip_y2 = top_y
            strip_h2 = min(free_h, STRIP_H)
            ax.add_patch(plt.Rectangle(
                (tx, strip_y2), tw, strip_h2,
                facecolor="#FFF7EF" if not technical else "none",
                edgecolor="#B86B2C", linewidth=0.7,
                linestyle="--", alpha=0.55, zorder=5
            ))
            # broj slobodnog prostora iznad tall-a se ne prikazuje ovde

    # Slobodan prostor iznad svakog wall elementa (ako nema wall_upper)
    wall_upper_mods2 = [m for m in mods if str(m.get("zone","")).lower().strip() == "wall_upper"]
    wall_upper_xs = {int(m.get("x_mm", 0)) for m in wall_upper_mods2}
    wall_gap2, _ = _zone_baseline_and_height(kitchen, "wall")

    for m in mods:
        if str(m.get("zone","")).lower().strip() != "wall":
            continue
        wx = int(m.get("x_mm", 0))
        wh = int(m.get("h_mm", 720))
        ww = int(m.get("w_mm", 600))
        if wx in wall_upper_xs:
            continue  # Vec ima gornji red
        top_y3 = wall_gap2 + wh
        free_h3 = wall_h - top_y3 - 20
        if free_h3 > 30:
            strip_h3 = min(free_h3, STRIP_H)
            ax.add_patch(plt.Rectangle(
                (wx, top_y3), ww, strip_h3,
                facecolor="#EFF7EF" if not technical else "none",
                edgecolor="#2E8B57", linewidth=0.7,
                linestyle="--", alpha=0.55, zorder=5
            ))
            # broj slobodnog prostora iznad wall-a se ne prikazuje ovde

    # Vertikalna linija: preostalo do max visine — samo u tehničkom modu
    if technical:
        max_h = int(kitchen.get("max_element_height", 0) or 0)
        if max_h <= 0:
            max_h = int(wall_h)
        max_h = min(int(max_h), int(wall_h))
        wall_gap_v, _ = _zone_baseline_and_height(kitchen, "wall")

        def _draw_vert_line(x0: int, y0: int, y1: int, free_mm: int) -> None:
            if free_mm <= 0:
                return
            ax.plot([x0, x0], [y0, y1], color=accent_free, linewidth=0.8, zorder=18)
            ax.text(
                x0 + 8, (y0 + y1) / 2,
                f"{free_mm}mm",
                fontsize=6.5, ha="left", va="center",
                color=accent_free, fontweight="bold", zorder=19,
            )

        zones_for_line = ("wall", "wall_upper", "tall", "tall_top")
        mods_for_line = [m for m in mods if str(m.get("zone","")).lower().strip() in zones_for_line]

        if not mods_for_line:
            # Nema elemenata: linija na sredini zida od wall_gap do max_h
            free0 = max_h - int(wall_gap_v)
            _draw_vert_line(int(wall_len // 2), int(wall_gap_v), int(max_h), int(free0))
        else:
            foot_mm = _get_foot_mm(kitchen)
            # Prikazi liniju i broj za svaki viseci/visoki element
            def _overlap(a_x: int, a_w: int, b_x: int, b_w: int) -> bool:
                return a_x < (b_x + b_w) and (a_x + a_w) > b_x

            def _top_for(m) -> int:
                z0 = str(m.get("zone","")).lower().strip()
                h0 = int(m.get("h_mm", 0))
                if z0 == "wall":
                    base0 = int(wall_gap_v)
                elif z0 == "wall_upper":
                    base0 = int(_y_for_wall_upper(kitchen, m, mods))
                elif z0 == "tall":
                    tid0 = str(m.get("template_id", "")).upper()
                    base0 = 0 if "FRIDGE" in tid0 else int(foot_mm)
                else:  # tall_top
                    base0 = int(_y_for_tall_top(kitchen, m, mods))
                return int(base0 + h0)

            # Grupisi po redovima: wall/wall_upper i tall/tall_top
            wall_group = [m for m in mods_for_line if str(m.get("zone","")).lower().strip() in ("wall", "wall_upper")]
            tall_group = [m for m in mods_for_line if str(m.get("zone","")).lower().strip() in ("tall", "tall_top")]

            for m in mods_for_line:
                z = str(m.get("zone","")).lower().strip()
                x = int(m.get("x_mm", 0))
                w = int(m.get("w_mm", 0))
                h = int(m.get("h_mm", 0))

                if z in ("wall", "wall_upper"):
                    # Prikazi samo najvisi element u istom X-opsegu
                    my_top = _top_for(m)
                    if any(
                        _overlap(x, w, int(o.get("x_mm", 0)), int(o.get("w_mm", 0)))
                        and _top_for(o) > my_top
                        for o in wall_group
                    ):
                        continue
                    if z == "wall_upper":
                        base = int(_y_for_wall_upper(kitchen, m, mods))
                    else:
                        base = int(wall_gap_v)
                elif z == "tall":
                    # Prikazi samo najvisi element u istom X-opsegu
                    my_top = _top_for(m)
                    if any(
                        _overlap(x, w, int(o.get("x_mm", 0)), int(o.get("w_mm", 0)))
                        and _top_for(o) > my_top
                        for o in tall_group
                    ):
                        continue
                    tid = str(m.get("template_id", "")).upper()
                    base = 0 if "FRIDGE" in tid else int(foot_mm)
                else:  # tall_top
                    base = int(_y_for_tall_top(kitchen, m, mods))

                top = int(base + h)
                free_mm = int(max_h - top)
                xline = int(x + (w / 2))
                _draw_vert_line(xline, int(top), int(max_h), free_mm)


# =========================================================
# Prikaz zida + grid
# =========================================================
def _hide_axes(ax) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def _setup_view(ax, wall_len: int, wall_h: int, *, technical: bool = False) -> None:
    # Asimetrični viewport:
    # - više prostora desno (da se ne seče desna strana/kote)
    # - više prostora dole, pa je ceo zid vizuelno pomeren malo naviše
    if technical:
        left_pad = 130
        right_pad = 260
        bottom_pad = 280
        top_pad = 150
    else:
        left_pad = 170
        right_pad = 620
        bottom_pad = 420
        top_pad = 150
    ax.set_xlim(-left_pad, wall_len + right_pad)
    ax.set_ylim(-bottom_pad, wall_h + top_pad)
    ax.set_aspect("equal", adjustable="box")


def _draw_grid(ax, wall_len: int, wall_h: int, show_grid: bool, step_mm: int) -> None:
    if not show_grid:
        return
    step = max(1, int(step_mm))
    # Vektorizovano crtanje (vlines/hlines) je mnogo brže od hiljada ax.plot poziva.
    xs = np.arange(0, wall_len + 1, step)
    ys = np.arange(0, wall_h + 1, step)

    ax.vlines(xs, 0, wall_h, colors="#AAAAAA", linewidth=0.35, alpha=0.20, zorder=2)
    ax.hlines(ys, 0, wall_len, colors="#AAAAAA", linewidth=0.35, alpha=0.20, zorder=2)

    major_step = step * 10

    if major_step > 0:
        xs_major = np.arange(0, wall_len + 1, major_step)
        ys_major = np.arange(0, wall_h + 1, major_step)
        ax.vlines(xs_major, 0, wall_h, colors="#AAAAAA", linewidth=0.7, alpha=0.45, zorder=2)
        ax.hlines(ys_major, 0, wall_len, colors="#AAAAAA", linewidth=0.7, alpha=0.45, zorder=2)


def _draw_wall(ax, wall_len: int, wall_h: int, show_wall_labels: bool,
               technical: bool = False) -> None:
    if not technical:
        # ── Soba efekat (katalog mod) ──────────────────────────────────────
        # Pozadina axes-a — neutralna soba
        ax.set_facecolor("#CCCAC5")
    else:
        # Tehnički mod — potpuno bijela pozadina, bez dekoracija prostorije.
        # Pod, plafon i bočni zidovi se NE crtaju — dimenzije i kote
        # moraju biti lako čitljive na čistoj beloj podlozi.
        ax.set_facecolor("#FFFFFF")

    # Glavni zid (prednja površina)
    ax.add_patch(plt.Rectangle(
        (0, 0), wall_len, wall_h,
        facecolor="white" if technical else "#ECEAE5",
        edgecolor="#1A1A1A" if technical else "none",
        linewidth=1.8, zorder=2
    ))

    if not technical:
        # Ivice prostorije — jasne linije razdvajanja
        # Pod / zid
        ax.plot([-130, wall_len + 130], [0, 0],
                color="#3A2E24", linewidth=2.2, zorder=3, solid_capstyle="butt")
        # Plafon / zid
        ax.plot([-130, wall_len + 130], [wall_h, wall_h],
                color="#4A4238", linewidth=1.4, zorder=3, solid_capstyle="butt")
        # Levi ugao zida
        ax.plot([0, 0], [-5, wall_h + 5],
                color="#3E3028", linewidth=1.6, zorder=3, solid_capstyle="butt")
        # Desni ugao zida
        ax.plot([wall_len, wall_len], [-5, wall_h + 5],
                color="#3E3028", linewidth=1.6, zorder=3, solid_capstyle="butt")


def _dim_arrow_wall(ax, x0: int, x1: int, y: int, txt: str) -> None:
    """Kota ukupne duzine zida — isti stil kao glavna visinska kota zida."""
    if x1 <= x0:
        return
    clr = "#555555"
    lw = 0.8
    ax.plot([x0, x0], [y - 11, y + 11], color=clr, linewidth=lw, zorder=50)
    ax.plot([x1, x1], [y - 11, y + 11], color=clr, linewidth=lw, zorder=50)
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=clr, lw=lw,
                                shrinkA=0, shrinkB=0),
                zorder=51)
    ax.text((x0 + x1) / 2, y - 14, txt,
            fontsize=FONT_DIM, ha="center", va="top",
            color=clr, fontweight="normal", zorder=52)


# =========================================================
# Glavni render
# =========================================================
def _render(ax, kitchen: Dict[str, Any], view_mode: str, show_grid: bool, grid_mm: int,
            show_bounds: bool, kickboard: bool, ceiling_filler: bool,
            selected_id: Optional[int] = None,
            room: Optional[Dict[str, Any]] = None,
            wall_key: str = "A") -> None:
    wall_len, wall_h = _wall_len_h(kitchen)
    _wk = str(wall_key or "A").upper()
    mods = [
        m for m in (kitchen.get("modules", []) or [])
        if str(m.get("wall_key", "A")).upper() == _wk
    ]
    foot_mm = _get_foot_mm(kitchen)
    _vm = _norm_text(view_mode)
    technical = (_vm in ("tehnicki", "technical"))

    _setup_view(ax, wall_len, wall_h, technical=technical)
    _draw_wall(ax, wall_len, wall_h, show_wall_labels=True, technical=technical)
    _draw_grid(ax, wall_len, wall_h, show_grid=(show_grid and technical), step_mm=grid_mm)

    # ── Zabranjene zone iz prostorije (prozori, vrata) ─────────────────────────
    if room and not technical:
        try:
            from room_constraints import get_wall_constraints, constraints_to_color_bands
            _rc = get_wall_constraints(room, str(wall_key or "A").upper(), kitchen)
            _bands = constraints_to_color_bands(_rc)
            for _b in _bands:
                _bx  = float(_b['x_start'])
                _bw  = float(_b['x_end']) - _bx
                if _bw <= 0:
                    continue
                # Odredi visinski raspon obojanog bloka
                _zones = _b.get('zones', [])
                if 'base' in _zones and 'wall' not in _zones:
                    # Samo baza zona — od poda do vrha baze
                    _by  = 0.0
                    _bh  = float(foot_mm + kitchen.get('base_korpus_h_mm', 720))
                elif 'wall' in _zones and 'base' not in _zones:
                    # Samo gornja zona — od wall_gap do vrha zida
                    _wall_gap_rc = int(
                        (kitchen.get('zones', {}) or {}).get('wall', {}).get('gap_from_base_mm', 0)
                        or (foot_mm + kitchen.get('base_korpus_h_mm', 720)
                            + int(round(float((kitchen.get('worktop', {}) or {}).get('thickness', 3.8)) * 10.0))
                            + kitchen.get('vertical_gap_mm', 600))
                    )
                    _by  = float(_wall_gap_rc)
                    _bh  = float(wall_h) - _by
                else:
                    # Sve zone — cijeli zid od poda do plafona
                    _by  = 0.0
                    _bh  = float(wall_h)
                ax.add_patch(plt.Rectangle(
                    (_bx, _by), _bw, _bh,
                    facecolor=_b['color'], edgecolor=_b['color'],
                    linewidth=1.2, alpha=_b.get('alpha', 0.22), zorder=2,
                ))
                # Mali natpis (tip otvora) u centru bande
                ax.text(
                    _bx + _bw / 2, _by + _bh / 2,
                    _b['label'],
                    fontsize=7, ha='center', va='center',
                    color='#1F2937', alpha=0.75, zorder=3,
                    rotation=90 if _bh > _bw else 0,
                )
        except Exception as _rc_draw_err:
            pass   # ne ruši render ako constraint modul nije dostupan

    # Clearance linije
    left_clear, right_clear, _ = _profile_clearance_mm(kitchen)
    if show_bounds:
        ax.plot([left_clear, left_clear], [0, wall_h],
                linestyle="--", color="#AAAAAA", linewidth=0.8, zorder=3)
        ax.plot([wall_len - right_clear, wall_len - right_clear], [0, wall_h],
                linestyle="--", color="#AAAAAA", linewidth=0.8, zorder=3)

    # Ugaona zona za L-kuhinju (Wall B/C) — sivi overlay zabranjenog prostora
    _kd_viz = kitchen or {}
    _layout_viz = str(_kd_viz.get("layout", _kd_viz.get("kitchen_layout", "")) or "").lower().strip()
    if show_bounds and _layout_viz == "l_oblik" and _wk != "A":
        try:
            _lang_viz = str((kitchen or {}).get("language", "sr") or "sr").lower().strip()
            _corner_lbl = f"{_tr_i18n('canvas.corner_label', _lang_viz)}\n{_tr_i18n('room.wall_a', _lang_viz)}"
            from layout_engine import _l_corner_offsets_mm as _co_viz
            _lo_viz, _ro_viz = _co_viz(kitchen, _wk)
            _zone_h = float(foot_mm + int(kitchen.get("base_korpus_h_mm", 720)))
            if _lo_viz > 0:
                ax.add_patch(plt.Rectangle(
                    (0.0, 0.0), float(_lo_viz), _zone_h,
                    facecolor="#B0B0B0", edgecolor="#888888",
                    linewidth=0.8, alpha=0.30, zorder=3,
                ))
                ax.text(
                    float(_lo_viz) / 2.0, _zone_h / 2.0,
                    f"{_corner_lbl}\n({_lo_viz}mm)",
                    fontsize=6.0, ha="center", va="center",
                    color="#4A4A4A", alpha=0.85, zorder=4,
                )
            if _ro_viz > 0:
                ax.add_patch(plt.Rectangle(
                    (float(wall_len - _ro_viz), 0.0), float(_ro_viz), _zone_h,
                    facecolor="#B0B0B0", edgecolor="#888888",
                    linewidth=0.8, alpha=0.30, zorder=3,
                ))
                ax.text(
                    float(wall_len) - float(_ro_viz) / 2.0, _zone_h / 2.0,
                    f"{_corner_lbl}\n({_ro_viz}mm)",
                    fontsize=6.0, ha="center", va="center",
                    color="#4A4A4A", alpha=0.85, zorder=4,
                )
        except Exception:
            pass  # Ne ruši render ako layout_engine nije dostupan

    # Radna visina (zelena isprekidana linija)
    zones = kitchen.get("zones", {}) or {}
    base_h_z = int(kitchen.get("base_korpus_h_mm",
                   (zones.get("base", {}) or {}).get("height_mm", 720)))
    wt = (kitchen.get("worktop", {}) or {})
    wt_mm = int(round(float(wt.get("thickness", 0.0)) * 10.0))
    _global_front = str(kitchen.get("front_color", GLOBAL_FRONT_DEFAULT) or GLOBAL_FRONT_DEFAULT)
    _appliance_col = str(kitchen.get("appliance_color", APPLIANCE_COLOR) or APPLIANCE_COLOR)
    radna_visina = foot_mm + base_h_z + wt_mm
    if radna_visina > 0 and show_bounds:
        ax.plot([0, wall_len], [radna_visina, radna_visina],
                linestyle=":", color="#2E8B57", linewidth=1.0, alpha=0.55, zorder=4)
        # Tekst radne visine je vidljiv u _dim_vertical_stack (levo) — ovde ne prikazujemo

    # Donja ivica gornjih elemenata (plava isprekidana)
    wall_gap = int((zones.get("wall", {}) or {}).get("gap_from_base_mm", 0))
    if wall_gap > 0 and show_bounds:
        ax.plot([0, wall_len], [wall_gap, wall_gap],
                linestyle=":", color="#3A6FAD", linewidth=1.0, alpha=0.55, zorder=4)
        # Tekst wall_gap je vidljiv u _dim_vertical_stack (levo) — ovde ne prikazujemo

    # Gornja granica elemenata (crvena isprekidana)
    max_h_line = int(kitchen.get("max_element_height", 0) or 0)
    if max_h_line > 0 and show_bounds:
        ax.plot([0, wall_len], [max_h_line, max_h_line],
                linestyle="--", color="#C0392B", linewidth=0.9, alpha=0.7, zorder=4)


    # Fiksni slojevi: radna ploca, lajsna, plafon
    _draw_countertop(ax, kitchen, mods, wall_len, technical=technical)
    _draw_kickboard(ax, kitchen, mods, wall_len, technical=technical, enabled=kickboard)
    _draw_ceiling_filler(ax, kitchen, mods, wall_len, wall_h,
                         technical=technical, enabled=ceiling_filler)

    # Slobodan prostor (uvek vidljiv)
    _draw_free_space_info(ax, kitchen, mods, wall_len, wall_h, technical)

    # Filler blokovi — mesta gde su obrisani elementi (keep_gap=True)
    _draw_fillers(ax, kitchen, technical)

    # Debljina radne ploce u mm (thickness se cuva u cm, mnozi se sa 10)
    wt_thk_mm = max(20, int(round(float(wt.get("thickness", 0.0)) * 10.0)))

    # Crtaj module — tall_top i wall_upper posle ostalih (da budu iznad)
    draw_order = [m for m in mods if str(m.get("zone","")).lower().strip() not in ("tall_top", "wall_upper")]
    draw_order += [m for m in mods if str(m.get("zone","")).lower().strip() == "tall_top"]
    draw_order += [m for m in mods if str(m.get("zone","")).lower().strip() == "wall_upper"]

    # X-opsezi TALL elemenata — WALL na istoj X poziciji se preskacaju (TALL pokriva celu visinu)
    _tall_ranges = []
    for _m in mods:
        if str(_m.get("zone", "")).lower().strip() == "tall":
            _ta = int(_m.get("x_mm", 0))
            _tb = _ta + int(_m.get("w_mm", 0))
            _tall_ranges.append((_ta, _tb))

    for m in draw_order:
        zone = str(m.get("zone", "base")).lower().strip()
        x = int(m.get("x_mm", 0))
        w = int(m.get("w_mm", 0))
        h = int(m.get("h_mm", 0))

        # Preskoči WALL module koji su potpuno unutar X-opsega TALL elementa
        if zone == "wall" and w > 0:
            _x1 = x + w
            if any(x >= _ta and _x1 <= _tb for _ta, _tb in _tall_ranges):
                continue  # TALL pokriva ovaj prostor, WALL se ne crta

        _is_selected = selected_id is not None and int(m.get("id", -1)) == selected_id
        if zone == "tall_top":
            y0 = _y_for_tall_top(kitchen, m, mods)
            if h <= 0:
                h = 400
            # Klamp: tall_top ne sme preći gornju granicu ni vrh zida
            _max_h_tt = int(kitchen.get("max_element_height", 0) or 0)
            _ceil_tt = _max_h_tt if _max_h_tt > 0 else wall_h
            if (y0 + h) > _ceil_tt:
                h = max(1, _ceil_tt - y0)
            _draw_module(ax, m, x, y0, w, h, zone="wall", technical=technical,
                         worktop_thk_mm=wt_thk_mm, selected=_is_selected,
                         global_front_color=_global_front, appliance_color=_appliance_col)
        elif zone == "wall_upper":
            y0 = _y_for_wall_upper(kitchen, m, mods)
            if h <= 0:
                h = 400
            # Klamp: wall_upper ne sme preći gornju granicu ni vrh zida
            _max_h_wu = int(kitchen.get("max_element_height", 0) or 0)
            _ceil_wu = _max_h_wu if _max_h_wu > 0 else wall_h
            if (y0 + h) > _ceil_wu:
                h = max(1, _ceil_wu - y0)
            _draw_module(ax, m, x, y0, w, h, zone="wall", technical=technical,
                         worktop_thk_mm=wt_thk_mm, selected=_is_selected,
                         global_front_color=_global_front, appliance_color=_appliance_col)
        else:
            y0, zone_h = _zone_baseline_and_height(kitchen, zone)
            if h <= 0:
                h = zone_h
            _tid = str(m.get("template_id", "")).upper()
            _skip_feet = "FREESTANDING" in _tid
            _integrated_tall_fridge = zone == "tall" and _tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER"}
            if zone in ("base", "tall") and not _skip_feet:
                if _integrated_tall_fridge:
                    _draw_fridge_vent_plinth(ax, x, w, foot_mm, technical=technical)
                else:
                    _draw_feet(ax, x, w, foot_mm, technical=technical)
            # Samostojeći uređaji: crtaju se od poda (y0=0), bez stopica i bez praznine.
            if _skip_feet and zone in ("base", "tall"):
                y0 = 0
            # Vizuelni sigurnosni klamp: TALL element ne sme preći gornju granicu
            if zone == "tall":
                _max_h_viz = int(kitchen.get("max_element_height", 0) or 0)
                if _max_h_viz > 0 and (y0 + h) > _max_h_viz:
                    h = max(1, _max_h_viz - y0)
            _draw_module(ax, m, x, y0, w, h, zone=zone, technical=technical,
                         worktop_thk_mm=wt_thk_mm, selected=_is_selected,
                         global_front_color=_global_front, appliance_color=_appliance_col)

    if not technical:
        _draw_l_layout_inset(ax, kitchen, room, active_wall=_wk)

    # Tehnicko kotiranje
    if technical:
        base_segs = []
        for m in mods:
            z = str(m.get("zone", "")).lower().strip()
            if z in ("base", "tall") and int(m.get("w_mm", 0)) > 0:
                a = int(m.get("x_mm", 0))
                base_segs.append((a, a + int(m.get("w_mm", 0))))
        if base_segs:
            # Nivo 1: Individualne kote ispod svakog elementa (sive)
            _dim_chain(ax, base_segs, y=-40, above=False)
            # Nivo 2: UKUPNO — uklonjen po zahtevu (ostaje samo ZID)
        # Razmaci po X u BASE zoni — meri do sledeceg elementa desno (BASE ili TALL), fallback na zid
        if base_segs:
            base_candidates = []
            for m in mods:
                z = str(m.get("zone", "")).lower().strip()
                if z in ("base", "tall") and int(m.get("w_mm", 0)) > 0:
                    a = int(m.get("x_mm", 0))
                    base_candidates.append((a, a + int(m.get("w_mm", 0))))
            for a, b in base_segs:
                # sledeci element desno
                right_starts = [x0 for (x0, x1) in base_candidates if x0 > a]
                if right_starts:
                    next_x = min(right_starts)
                    gap = next_x - b
                    if gap > 0:
                        _dim_arrow(ax, b, next_x, -18, f"{gap}mm", above=False)
                else:
                    gap = wall_len - b
                    if gap > 0:
                        _dim_arrow(ax, b, wall_len, -18, f"{gap}mm", above=False)
        # Nivo 3: ZID ukupno — najnize, plavo, boldovano
        _dim_arrow_wall(ax, 0, wall_len, -155, _wall_label(kitchen, wall_len))

        wall_segs = []
        for m in mods:
            z = str(m.get("zone", "")).lower().strip()
            if z in ("wall", "tall_top", "wall_upper") and int(m.get("w_mm", 0)) > 0:
                _mx = int(m.get("x_mm", 0))
                _mw = int(m.get("w_mm", 0))
                # Preskoci WALL elemente koji su pokriveni TALL-om (nisu ni nacrtani)
                if z == "wall":
                    _mx1 = _mx + _mw
                    if any(_mx >= _ta and _mx1 <= _tb for _ta, _tb in _tall_ranges):
                        continue
                a = _mx
                wall_segs.append((a, a + _mw))
        if wall_segs:
            # Individualne kote iznad svakog gornjeg elementa
            _dim_chain(ax, wall_segs, y=wall_h + 45, above=True)
            # Ukupna sirina wall zone — uklonjena po zahtevu
        # Razmaci po X u WALL zoni — meri do sledeceg elementa desno (WALL ili TALL), fallback na zid
        if wall_segs:
            wall_candidates = []
            for m in mods:
                z = str(m.get("zone", "")).lower().strip()
                if z in ("wall", "tall") and int(m.get("w_mm", 0)) > 0:
                    _mx = int(m.get("x_mm", 0))
                    _mw = int(m.get("w_mm", 0))
                    # preskoci WALL koji je pokriven TALL-om (nisu nacrtani)
                    if z == "wall":
                        _mx1 = _mx + _mw
                        if any(_mx >= _ta and _mx1 <= _tb for _ta, _tb in _tall_ranges):
                            continue
                    wall_candidates.append((_mx, _mx + _mw))
            for a, b in wall_segs:
                right_starts = [x0 for (x0, x1) in wall_candidates if x0 > a]
                if right_starts:
                    next_x = min(right_starts)
                    gap = next_x - b
                    if gap > 0:
                        _dim_arrow(ax, b, next_x, wall_h + 18, f"{gap}mm", above=True)
                else:
                    gap = wall_len - b
                    if gap > 0:
                        _dim_arrow(ax, b, wall_len, wall_h + 18, f"{gap}mm", above=True)

        # Kota visine zida — vertikalna dim-linija sa desne strane (pomerena da ne prekriva)
        _x_right = wall_len + 60
        ax.plot([_x_right, _x_right], [0, wall_h],
                color="#555555", linewidth=0.8, zorder=55)
        ax.plot([_x_right - 8, _x_right + 8], [0, 0],
                color="#555555", linewidth=0.8, zorder=55)
        ax.plot([_x_right - 8, _x_right + 8], [wall_h, wall_h],
                color="#555555", linewidth=0.8, zorder=55)
        ax.annotate(
            "", xy=(_x_right, 0), xytext=(_x_right, wall_h),
            arrowprops=dict(arrowstyle="<->", color="#555555", lw=0.8, shrinkA=0, shrinkB=0),
            zorder=56,
        )
        ax.text(_x_right + 10, wall_h / 2, f"{wall_h}mm",
                fontsize=FONT_DIM, ha="left", va="center", color="#555555",
                rotation=90, zorder=57)

        _dim_vertical_stack(ax, kitchen)
        _dim_vertical_wall(ax, kitchen, mods)
        # Eksplicitna desna ivica zida (na vrhu svih slojeva) da ne nestane na uskom viewportu.
        ax.plot([wall_len - 0.5, wall_len - 0.5], [0, wall_h],
                color="#1A1A1A", linewidth=2.0, zorder=120, solid_capstyle="butt")

    _hide_axes(ax)


# =========================================================
# Element preview — 2D front view + 3D oblique view
# =========================================================

def _render_element_2d(
    m: Dict[str, Any],
    kitchen: Dict[str, Any],
    *,
    label_mode: str = "none",
    part_rows: list[dict[str, Any]] | None = None,
) -> str:
    """Čist izolovani prednji pogled elementa — bez pozadine sobe, bez radne ploče.
    Direktno crta samo element (noge + korpus) na neutralnoj pozadini.
    Returns data URI (PNG).
    """
    w_mm  = int(m.get('w_mm', 600))
    h_mm  = int(m.get('h_mm', 720))
    zone  = str(m.get('zone', 'base')).lower()
    tid   = str(m.get('template_id', '')).upper()

    foot_mm = _get_foot_mm(kitchen)
    y0, zh  = _zone_baseline_and_height(kitchen, zone)
    if h_mm <= 0:
        h_mm = zh

    # Fridge i appliance elementi kreću od poda (y0=0, nema nogu)
    _NO_FEET_KW = ('FRIDGE',)
    has_feet = (zone in ('base', 'tall') and foot_mm > 0
                and not any(kw in tid for kw in _NO_FEET_KW))
    if not has_feet:
        y0 = 0
        foot_mm = 0

    # Uske granice osa — samo element + mali padding
    PAD_X = max(18, int(w_mm * 0.04))
    PAD_Y = max(12, int(h_mm * 0.04))
    xlim  = (-PAD_X,          w_mm + PAD_X)
    ylim  = (y0 - foot_mm - PAD_Y, y0 + h_mm + PAD_Y)

    tot_w = xlim[1] - xlim[0]
    tot_h = ylim[1] - ylim[0]

    TARGET_H = 2.8   # visina figure u inčima
    sc    = TARGET_H / max(tot_h, 1)
    fig_w = max(1.4, min(5.0, tot_w * sc))

    fig = plt.figure(figsize=(fig_w, TARGET_H))
    ax  = fig.add_subplot(111)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F5F4F2')   # neutralna krem pozadina

    # Noge (ako postoje)
    if has_feet and foot_mm > 0:
        _draw_feet(ax, 0, w_mm, foot_mm, technical=False)

    # Modul sa x_mm=0 (centrirani, bez offset-a originalnog x_mm)
    m_local = dict(m)
    m_local['x_mm'] = 0
    _global_front = str(kitchen.get("front_color", GLOBAL_FRONT_DEFAULT) or GLOBAL_FRONT_DEFAULT)
    _appliance_col = str(kitchen.get("appliance_color", APPLIANCE_COLOR) or APPLIANCE_COLOR)
    _draw_module(ax, m_local, 0, y0, w_mm, h_mm,
                 zone=zone, technical=False, worktop_thk_mm=0,
                 global_front_color=_global_front, appliance_color=_appliance_col)

    if label_mode != "none":
        _annotate_element_preview_regions(
            ax, m_local, 0, y0, w_mm, h_mm, label_mode=label_mode, part_rows=part_rows
        )

    _hide_axes(ax)
    fig.tight_layout(pad=0.08)
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('ascii')


def _render_element_3d(m: Dict[str, Any], kitchen: Dict[str, Any]) -> str:
    """Oblique (cabinet-projection) 3D view of a single element. Returns data URI (PNG).

    Projection:  depth-direction at 30° upward-right, foreshortened to 0.45.
    Coordinate system: same mm-based units as _render() — the existing
    _draw_module_interior() is called directly on the front face.
    """
    w_mm  = int(m.get('w_mm', 600))
    h_mm  = int(m.get('h_mm', 720))
    d_mm  = int(m.get('d_mm', 560))
    zone  = str(m.get('zone', 'base')).lower()
    tid   = str(m.get('template_id', '')).upper()

    foot_mm = _get_foot_mm(kitchen)
    # Fridge/tall-fridge start from floor (y0=0), no raised feet
    _NO_FEET_KW = ('FRIDGE',)
    _render_plinth_in_body = (zone == "base" and foot_mm > 0)
    _preview_foot_mm = 0 if _render_plinth_in_body else foot_mm
    has_feet = (zone in ('base', 'tall') and _preview_foot_mm > 0
                and not any(kw in tid for kw in _NO_FEET_KW))
    y0 = _preview_foot_mm if has_feet else 0

    # Oblique projection depth vector
    ANG = math.radians(28)
    DS  = 0.32                          # foreshortening factor; softer depth for PDF previews
    DX  = d_mm * DS * math.cos(ANG)    # rightward offset per mm of depth
    DY  = d_mm * DS * math.sin(ANG)    # upward offset per mm of depth

    # Zone colours (reuse palette)
    FACE   = ZONE_FACE.get(zone,   '#FAFAFA')
    EDGE   = ZONE_EDGE.get(zone,   '#2C2C2C')
    ACCENT = ZONE_ACCENT.get(zone, '#444444')
    SIDE_C = '#B0ACA4'
    TOP_C  = '#C8C4BE'
    _etype = _detect_type(m)
    _global_front = str(kitchen.get("front_color", GLOBAL_FRONT_DEFAULT) or GLOBAL_FRONT_DEFAULT)
    _appliance_col = str(kitchen.get("appliance_color", APPLIANCE_COLOR) or APPLIANCE_COLOR)
    if _has_front_panel(m, _etype):
        FACE = _global_front
        ACCENT = _contrast_accent(_global_front)
    else:
        FACE = _appliance_col
        ACCENT = _contrast_accent(_appliance_col)

    # Worktop (only for base zone)
    wt     = kitchen.get('worktop', {}) or {}
    wt_mm  = (int(round(float(wt.get('thickness', 0.0)) * 10.0))
              if zone == 'base' else 0)
    _show_worktop = False
    _top_extra_mm = wt_mm if _show_worktop else 0

    # Axes limits — generous padding so depth faces are fully visible
    PAD    = max(25, int(w_mm * 0.04))
    xlim   = (-PAD, w_mm + DX + PAD)
    ylim   = (-PAD, y0 + h_mm + _top_extra_mm + DY + PAD)
    tot_w  = xlim[1] - xlim[0]
    tot_h  = ylim[1] - ylim[0]

    # Figure size: height ≈ 3.5 in, width proportional
    TARGET_H = 3.0
    sc     = TARGET_H / max(tot_h, 1)
    fig_w  = max(3.2, min(7.4, tot_w * sc * 1.18))

    fig = plt.figure(figsize=(fig_w, TARGET_H))
    ax  = fig.add_subplot(111)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('#F4F1EA')
    ax.set_facecolor('#F4F1EA')

    # Convenience: shift point (px,py) along the depth direction
    def dep(px, py):
        return px + DX, py + DY

    fx, fy = 0.0, float(y0)

    # ── Right side face ───────────────────────────────────────────────────────
    side_pts = [
        (fx + w_mm, fy),
        dep(fx + w_mm, fy),
        dep(fx + w_mm, fy + h_mm),
        (fx + w_mm, fy + h_mm),
    ]
    ax.add_patch(plt.Polygon(side_pts, closed=True,
                             fc=SIDE_C, ec=EDGE, lw=0.8, zorder=5))

    # ── Top face / worktop ────────────────────────────────────────────────────
    if _show_worktop:
        # Worktop front strip (visible front edge, dark)
        ax.add_patch(plt.Polygon([
            (fx,        fy + h_mm),
            (fx + w_mm, fy + h_mm),
            (fx + w_mm, fy + h_mm + wt_mm),
            (fx,        fy + h_mm + wt_mm),
        ], closed=True, fc='#2E2A26', ec=EDGE, lw=0.8, zorder=7))
        # Worktop right side
        ax.add_patch(plt.Polygon([
            (fx + w_mm, fy + h_mm),
            dep(fx + w_mm, fy + h_mm),
            dep(fx + w_mm, fy + h_mm + wt_mm),
            (fx + w_mm, fy + h_mm + wt_mm),
        ], closed=True, fc='#1C1816', ec=EDGE, lw=0.7, zorder=6))
        # Worktop top face
        ax.add_patch(plt.Polygon([
            (fx,        fy + h_mm + wt_mm),
            (fx + w_mm, fy + h_mm + wt_mm),
            dep(fx + w_mm, fy + h_mm + wt_mm),
            dep(fx,        fy + h_mm + wt_mm),
        ], closed=True, fc='#3C3835', ec=EDGE, lw=0.8, zorder=6))
    else:
        if zone == "base":
            _rail_inset_front = max(18.0, min(34.0, d_mm * 0.07))
            _rail_inset_back = max(22.0, min(42.0, d_mm * 0.08))
            _rail_h = max(14.0, min(20.0, h_mm * 0.028))
            _rail_face = "#DDD8D0"
            _rail_side = "#B9B2A9"
            for _depth_off in (_rail_inset_front, d_mm - _rail_inset_back):
                _x0 = fx
                _x1 = fx + w_mm
                _y0 = fy + h_mm - _rail_h
                _f0 = (_x0 + (_depth_off * DS * math.cos(ANG)), _y0 + (_depth_off * DS * math.sin(ANG)))
                _f1 = (_x1 + (_depth_off * DS * math.cos(ANG)), _y0 + (_depth_off * DS * math.sin(ANG)))
                _b1 = (_f1[0], _f1[1] + _rail_h)
                _b0 = (_f0[0], _f0[1] + _rail_h)
                ax.add_patch(plt.Polygon(
                    [_f0, _f1, _b1, _b0],
                    closed=True, fc=_rail_face, ec=EDGE, lw=0.7, zorder=8
                ))
                _cap_depth = max(8.0, min(14.0, d_mm * 0.025))
                ax.add_patch(plt.Polygon(
                    [_f1, (_f1[0] + _cap_depth * DS * math.cos(ANG), _f1[1] + _cap_depth * DS * math.sin(ANG)),
                     (_b1[0] + _cap_depth * DS * math.cos(ANG), _b1[1] + _cap_depth * DS * math.sin(ANG)), _b1],
                    closed=True, fc=_rail_side, ec=EDGE, lw=0.55, zorder=7
                ))
            ax.plot([fx, dep(fx, fy + h_mm)[0]], [fy + h_mm, dep(fx, fy + h_mm)[1]],
                    color=EDGE, linewidth=0.8, alpha=0.85, zorder=10)
            ax.plot([fx + w_mm, dep(fx + w_mm, fy + h_mm)[0]], [fy + h_mm, dep(fx + w_mm, fy + h_mm)[1]],
                    color=EDGE, linewidth=0.8, alpha=0.85, zorder=10)
            ax.plot([dep(fx, fy + h_mm)[0], dep(fx + w_mm, fy + h_mm)[0]],
                    [dep(fx, fy + h_mm)[1], dep(fx + w_mm, fy + h_mm)[1]],
                    color=EDGE, linewidth=0.75, alpha=0.7, zorder=10)
        else:
            ax.add_patch(plt.Polygon([
                (fx,        fy + h_mm),
                (fx + w_mm, fy + h_mm),
                dep(fx + w_mm, fy + h_mm),
                dep(fx,        fy + h_mm),
            ], closed=True, fc=TOP_C, ec=EDGE, lw=0.8, zorder=5))

    # ── Front face (main rectangle) ───────────────────────────────────────────
    ax.add_patch(plt.Polygon([
        (fx, fy), (fx + w_mm, fy), (fx + w_mm, fy + h_mm), (fx, fy + h_mm),
    ], closed=True, fc=FACE, ec=EDGE, lw=1.2, zorder=7))

    # Subtle inner frame (same as _draw_module in 2D)
    _if = max(5, int(min(w_mm, h_mm) * 0.04))
    ax.add_patch(plt.Rectangle(
        (fx + _if, fy + _if), max(2, w_mm - 2 * _if), max(2, h_mm - 2 * _if),
        facecolor='none', edgecolor='#CCCCCC', lw=0.4, alpha=0.5, zorder=8))

    # ── Interior details (doors, drawers, handles …) ─────────────────────────
    etype = _detect_type(m)
    _draw_module_interior(ax, int(fx), int(fy), w_mm, h_mm,
                          zone, etype, ACCENT, FACE, False,
                          m=m, worktop_thk_mm=_top_extra_mm)

    if _render_plinth_in_body:
        _plinth_h = max(72.0, min(100.0, foot_mm * 0.62))
        _plinth_inset = max(26.0, min(42.0, d_mm * 0.07))
        _plinth_face = "#F1EEE8"
        _plinth_side = "#D4CDC3"
        _shadow = "#B8B0A6"
        ax.add_patch(plt.Polygon(
            [
                (fx + _plinth_inset, fy),
                (fx + w_mm - _plinth_inset, fy),
                (fx + w_mm - _plinth_inset, fy + _plinth_h),
                (fx + _plinth_inset, fy + _plinth_h),
            ],
            closed=True, fc=_plinth_face, ec=EDGE, lw=0.7, zorder=9
        ))
        _pr0 = dep(fx + w_mm - _plinth_inset, fy)
        _pr1 = dep(fx + w_mm - _plinth_inset, fy + _plinth_h)
        ax.add_patch(plt.Polygon(
            [
                (fx + w_mm - _plinth_inset, fy),
                _pr0,
                _pr1,
                (fx + w_mm - _plinth_inset, fy + _plinth_h),
            ],
            closed=True, fc=_plinth_side, ec=EDGE, lw=0.6, zorder=8
        ))
        ax.plot(
            [fx + _plinth_inset, fx + w_mm - _plinth_inset],
            [fy + _plinth_h, fy + _plinth_h],
            color=_shadow, linewidth=0.8, alpha=0.65, zorder=10
        )
        ax.plot(
            [fx + _plinth_inset, fx + _plinth_inset],
            [fy, fy + _plinth_h],
            color=_shadow, linewidth=0.55, alpha=0.55, zorder=10
        )

    if etype == "sink" and _show_worktop:
        _params = (m.get("params", {}) or {})
        _cut_w = float(_params.get("sink_cutout_width_mm", max(400.0, min(w_mm - 80.0, 500.0))) or 0.0)
        _cut_d = float(_params.get("sink_cutout_depth_mm", max(400.0, min(d_mm - 40.0, 480.0))) or 0.0)
        _cut_x_local = float(_params.get("sink_cutout_x_mm", max((w_mm - _cut_w) / 2.0, 0.0)) or 0.0)
        _cut_x_local = max(25.0, min(float(w_mm) - _cut_w - 25.0, _cut_x_local))
        _top_y = fy + h_mm + _top_extra_mm
        _front_setback = max(55.0, min(95.0, d_mm * 0.16))
        _back_margin = max(20.0, min(35.0, d_mm * 0.06))
        _cut_d = max(220.0, min(d_mm - _front_setback - _back_margin, _cut_d))
        _sx0 = fx + _cut_x_local
        _sx1 = _sx0 + _cut_w
        _front_left = (_sx0, _top_y)
        _front_right = (_sx1, _top_y)
        _back_right = (
            _sx1 + (_cut_d * DS * math.cos(ANG)),
            _top_y + (_cut_d * DS * math.sin(ANG)),
        )
        _back_left = (
            _sx0 + (_cut_d * DS * math.cos(ANG)),
            _top_y + (_cut_d * DS * math.sin(ANG)),
        )
        # Sink rim / cutout on the worktop top face
        ax.add_patch(plt.Polygon(
            [_front_left, _front_right, _back_right, _back_left],
            closed=True, fc='#CACFD5', ec='#7B8087', lw=0.9, zorder=8
        ))
        _rim = max(12.0, min(18.0, _cut_w * 0.035))
        _bowl_front_left = (_front_left[0] + _rim, _front_left[1] + _rim * 0.18)
        _bowl_front_right = (_front_right[0] - _rim, _front_right[1] + _rim * 0.18)
        _bowl_back_right = (_back_right[0] - _rim, _back_right[1] - _rim * 0.10)
        _bowl_back_left = (_back_left[0] + _rim, _back_left[1] - _rim * 0.10)
        ax.add_patch(plt.Polygon(
            [_bowl_front_left, _bowl_front_right, _bowl_back_right, _bowl_back_left],
            closed=True, fc='#949CA5', ec='#636B73', lw=0.8, zorder=9
        ))
        # Inner bowl shading so it reads as a sink, not just a faucet
        _inner_offset = max(10.0, min(14.0, _cut_w * 0.025))
        ax.add_patch(plt.Polygon(
            [
                (_bowl_front_left[0] + _inner_offset, _bowl_front_left[1] + _inner_offset * 0.08),
                (_bowl_front_right[0] - _inner_offset, _bowl_front_right[1] + _inner_offset * 0.08),
                (_bowl_back_right[0] - _inner_offset, _bowl_back_right[1] - _inner_offset * 0.04),
                (_bowl_back_left[0] + _inner_offset, _bowl_back_left[1] - _inner_offset * 0.04),
            ],
            closed=True, fc='#7C8791', ec='none', alpha=0.85, zorder=10
        ))

    if etype == "corner":
        is_diag = "DIAGONAL" in tid
        wing_w = max(180.0, min(d_mm * 0.72, w_mm * 0.46))
        wing_d = max(180.0, min(w_mm * 0.42, d_mm * 0.92))
        wx0 = max(0.0, w_mm - wing_w)
        wz0 = d_mm
        side_face = [
            (wx0, fy),
            dep(wx0, fy),
            dep(wx0, fy + h_mm),
            (wx0, fy + h_mm),
        ]
        top_face = [
            (wx0, fy + h_mm),
            (w_mm, fy + h_mm),
            (w_mm + (wing_d * DS * math.cos(ANG)), fy + h_mm + (wing_d * DS * math.sin(ANG))),
            (wx0 + (wing_d * DS * math.cos(ANG)), fy + h_mm + (wing_d * DS * math.sin(ANG))),
        ]
        return_face = [
            dep(wx0, fy),
            dep(w_mm, fy),
            dep(w_mm, fy + h_mm),
            dep(wx0, fy + h_mm),
        ]
        ax.add_patch(plt.Polygon(side_face, closed=True, fc=_darken_color(FACE, 0.90), ec=EDGE, lw=0.8, zorder=6))
        ax.add_patch(plt.Polygon(top_face, closed=True, fc=TOP_C, ec=EDGE, lw=0.8, zorder=6))
        ax.add_patch(plt.Polygon(return_face, closed=True, fc=_darken_color(FACE, 0.95), ec=EDGE, lw=0.9, zorder=9))
        if is_diag:
            p1 = dep(wx0 + wing_w * 0.18, fy + h_mm * 0.05)
            p2 = dep(w_mm - wing_w * 0.10, fy + h_mm * 0.95)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=ACCENT, lw=1.0, zorder=10)
        else:
            split_x = wx0 + wing_w * 0.28
            p1 = dep(split_x, fy + h_mm * 0.06)
            p2 = dep(split_x, fy + h_mm * 0.94)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=ACCENT, lw=0.9, zorder=10)
        if _show_worktop and zone == "base":
            wt_top = [
                dep(wx0, fy + h_mm + wt_mm),
                dep(w_mm, fy + h_mm + wt_mm),
                (w_mm + ((wing_d + d_mm) * DS * math.cos(ANG)), fy + h_mm + wt_mm + ((wing_d + d_mm) * DS * math.sin(ANG))),
                (wx0 + ((wing_d + d_mm) * DS * math.cos(ANG)), fy + h_mm + wt_mm + ((wing_d + d_mm) * DS * math.sin(ANG))),
            ]
            ax.add_patch(plt.Polygon(wt_top, closed=True, fc='#3C3835', ec=EDGE, lw=0.7, zorder=7, alpha=0.95))

    # ── Feet / legs ───────────────────────────────────────────────────────────
    if has_feet:
        # Front legs (same as 2D)
        _draw_feet(ax, int(fx), w_mm, foot_mm, technical=False)
        # Back legs (depth-offset, slightly behind)
        leg_w   = int(max(18, min(40, w_mm * 0.07)))
        leg_in  = int(max(10, min(35, w_mm * 0.07)))
        for px in (int(fx) + leg_in, int(fx) + w_mm - leg_in - leg_w):
            bx, by = dep(float(px), 0.0)
            ax.add_patch(plt.Rectangle(
                (bx, by), leg_w, foot_mm,
                facecolor='#B0AEAC', edgecolor='#888888', lw=0.5, zorder=4, alpha=0.65))

    # ── Element ID label (top-left of front face) ─────────────────────────────
    _id_fs = max(6, min(10, int(w_mm * 0.012)))
    ax.text(fx + 8, fy + h_mm - 8, f"#{m.get('id', '?')}",
            fontsize=_id_fs, ha='left', va='top',
            color='#333333', fontweight='bold', zorder=20)
    fig.tight_layout(pad=0.1)
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('ascii')


def render_element_preview(
    m: Dict[str, Any],
    kitchen: Dict[str, Any],
    *,
    label_mode: str = "none",
    part_rows: list[dict[str, Any]] | None = None,
) -> Tuple[str, str]:
    """Return (uri_2d, uri_3d) preview images for a single kitchen element.

    uri_2d — katalog 2D front view (same view as the nacrt katalog mode).
    uri_3d — oblique cabinet-projection 3D view showing depth, top and side.
    Both are PNG data URIs suitable for <img src="...">.
    """
    uri_2d = _render_element_2d(m, kitchen, label_mode=label_mode, part_rows=part_rows)
    uri_3d = _render_element_3d(m, kitchen)
    return uri_2d, uri_3d



