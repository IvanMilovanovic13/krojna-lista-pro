# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List
import logging

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_LOG = logging.getLogger(__name__)


def _find_font_file(filename: str) -> str | None:
    """Find font file in typical locations: ./fonts, module folder, cwd."""
    candidates: list[Path] = []
    here = Path(__file__).resolve().parent
    cwd = Path.cwd()
    candidates += [
        here / "fonts" / filename,
        here / filename,
        cwd / "fonts" / filename,
        cwd / filename,
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def _register_fonts() -> None:
    """Register DejaVu fonts once (safe to call multiple times)."""
    try:
        pdfmetrics.getFont("DejaVuSans")
        pdfmetrics.getFont("DejaVuSans-Bold")
        return
    except Exception as ex:
        _LOG.debug("DejaVu font not registered yet or unavailable: %s", ex)

    regular = _find_font_file("DejaVuSans.ttf")
    bold = _find_font_file("DejaVuSans-Bold.ttf")
    if regular:
        pdfmetrics.registerFont(TTFont("DejaVuSans", regular))
    if bold:
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))


MANUFACTURING_PROFILES: Dict[str, Dict[str, Any]] = {
    "EU_SRB": {
        "label": "EU / SRB – frameless (на фугу)",
        "front_gap_mm": 2.0,
        "cut_rounding_step_mm": 0.5,
        "cut_rounding_only_cut": True,
        "mounting_tolerance_total_mm": 10,  # укупно (лево+десно)
        "handle_pull_mm": 2,
        "back_inset_mm": 10,
    },
    "EU_SRB_BLUM": {
        "label": "EU / SRB – Blum",
        "front_gap_mm": 2.0,
        "cut_rounding_step_mm": 0.5,
        "cut_rounding_only_cut": True,
        "mounting_tolerance_total_mm": 10,
        "handle_pull_mm": 2,
        "back_inset_mm": 10,
    },
    "EU_SRB_HETTICH": {
        "label": "EU / SRB – Hettich",
        "front_gap_mm": 2.0,
        "cut_rounding_step_mm": 0.5,
        "cut_rounding_only_cut": True,
        "mounting_tolerance_total_mm": 10,
        "handle_pull_mm": 2,
        "back_inset_mm": 10,
    },
    "EU_SRB_GTV": {
        "label": "EU / SRB – GTV",
        "front_gap_mm": 2.0,
        "cut_rounding_step_mm": 0.5,
        "cut_rounding_only_cut": True,
        "mounting_tolerance_total_mm": 10,
        "handle_pull_mm": 2,
        "back_inset_mm": 10,
    },
}


HARDWARE_BRAND_CATALOGS: Dict[str, Dict[str, str]] = {
    "BLUM": {
        "hinge": "Blum CLIP-top 110° (71B...)",
        "slide": "Blum TANDEM plus BLUMOTION (par)",
        "liftup": "Blum AVENTOS HK-S (par)",
        "dish_hinge": "Blum 79T9550",
        "handle": "Po izboru korisnika",
        "hinge_screw": "3.5x16 mm",
        "slide_screw": "3.5x16 mm",
        "back_fix": "3x16 mm / ekser 1.4x25 mm",
        "wall_mount_screw": "5x60 mm",
        "confirmat": "7x50 mm",
        "dowel": "8x30 mm",
        "shelf_pin": "5 mm",
        "leg": "Podesiva h=100 mm",
        "hang_rail": "Nosac + sina za visece elemente",
        "wall_anchor": "Tipl + vijak 8x80 mm",
        "cabinet_connector": "Spojnica korpusa + vijak",
        "plinth_clip": "Klipsa za soklu",
        "worktop_fix": "Vijak / ugaonik za radnu plocu",
        "anti_tip": "Anti-tip ugaonik / traka",
        "appliance_hookup": "Prikljucni set uredjaja",
        "sliding_track":   "Hafele Slido / Accuride klizni sistem vrata (set)",
        "hanging_rod":     "Okrugla sipka za vesanje O25mm + par nosaca",
        "hinge_plate":     "Blum CLIP-top Montageplatte 175H71 / 175L71",
        "handle_screw":    "M4 x 50mm vijak za rucku",
    },
    "HETTICH": {
        "hinge": "Hettich Sensys 110°",
        "slide": "Hettich Quadro (par)",
        "liftup": "Hettich Free flap (par)",
        "dish_hinge": "Hettich set za front MZS",
        "handle": "Po izboru korisnika",
        "hinge_screw": "3.5x16 mm",
        "slide_screw": "3.5x16 mm",
        "back_fix": "3x16 mm / ekser 1.4x25 mm",
        "wall_mount_screw": "5x60 mm",
        "confirmat": "7x50 mm",
        "dowel": "8x30 mm",
        "shelf_pin": "5 mm",
        "leg": "Podesiva h=100 mm",
        "hang_rail": "Nosac + sina za visece elemente",
        "wall_anchor": "Tipl + vijak 8x80 mm",
        "cabinet_connector": "Spojnica korpusa + vijak",
        "plinth_clip": "Klipsa za soklu",
        "worktop_fix": "Vijak / ugaonik za radnu plocu",
        "anti_tip": "Anti-tip ugaonik / traka",
        "appliance_hookup": "Prikljucni set uredjaja",
        "sliding_track":   "Hettich EKU Porta 50 klizni sistem vrata (set)",
        "hanging_rod":     "Okrugla sipka za vesanje O25mm + par nosaca",
        "hinge_plate":     "",
        "handle_screw":    "M4 x 50mm vijak za rucku",
    },
    "GTV": {
        "hinge": "GTV zglobna sarka 110°",
        "slide": "GTV klizac fioke (par)",
        "liftup": "GTV lift-up mehanizam (par)",
        "dish_hinge": "GTV set za front MZS",
        "handle": "Po izboru korisnika",
        "hinge_screw": "3.5x16 mm",
        "slide_screw": "3.5x16 mm",
        "back_fix": "3x16 mm / ekser 1.4x25 mm",
        "wall_mount_screw": "5x60 mm",
        "confirmat": "7x50 mm",
        "dowel": "8x30 mm",
        "shelf_pin": "5 mm",
        "leg": "Podesiva h=100 mm",
        "hang_rail": "Nosac + sina za visece elemente",
        "wall_anchor": "Tipl + vijak 8x80 mm",
        "cabinet_connector": "Spojnica korpusa + vijak",
        "plinth_clip": "Klipsa za soklu",
        "worktop_fix": "Vijak / ugaonik za radnu plocu",
        "anti_tip": "Anti-tip ugaonik / traka",
        "appliance_hookup": "Prikljucni set uredjaja",
        "sliding_track":   "GTV klizni sistem kliznih vrata (set)",
        "hanging_rod":     "Okrugla sipka za vesanje O25mm + par nosaca",
        "hinge_plate":     "GTV montazna ploca za sarku",
        "handle_screw":    "M4 x 50mm vijak za rucku",
    },
}

# Dubina utora za leđnu ploču (standardni EU/SRB frameless)
GROOVE_DEPTH: int = 8  # mm

# Konstante za sanduk fioke
_SLIDE_CLEARANCE_MM: float = 12.0   # oslobađanje po strani za klizač fioke [mm]
_DRAWER_SETBACK_MM:  float = 20.0   # sanduk kraći od dubine elementa [mm]
_DRAWER_BOX_REVEAL:  float = 4.0    # sanduk niži od fronta (propust/reveal) [mm]


def _round_cut(mm_val: float, step: float) -> float:
    if step <= 0:
        return float(mm_val)
    return round(float(mm_val) / step) * step


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        return int(default)


def _position_from_deo(deo: str) -> str:
    d = str(deo or "").lower()
    if "leva" in d:
        return "LEVA"
    if "desna" in d:
        return "DESNA"
    if "dno" in d or "sokla" in d:
        return "DOLE"
    if "plafon" in d or "gornja" in d:
        return "GORE"
    if "leđ" in d or "ledj" in d or "ledn" in d:
        return "ZADNJA"
    if "front" in d or "vrata" in d:
        return "PREDNJA"
    if "srednja" in d:
        return "SREDINA"
    if "nosač" in d or "nosac" in d:
        return "GORE"
    return "-"


def _assembly_step_for(section: str, deo: str) -> str:
    s = str(section or "").lower()
    d = str(deo or "").lower()
    if s == "carcass":
        if "leva" in d or "desna" in d or ("strana" in d and "ugaon" in d):
            return "1"
        if "dno" in d or "plafon" in d or "gornja" in d:
            return "2"
        if "srednja" in d or "pregrada" in d or "polica" in d or "kutna" in d:
            return "3"
        return "2"
    if s == "backs":
        return "4"
    if s in ("fronts", "drawer_boxes"):
        return "5"
    if s in ("worktop", "plinth"):
        return "6"
    if s == "hardware":
        return "7"
    return "-"


def _section_prefix(section: str) -> str:
    return {
        "carcass": "C",
        "backs": "B",
        "fronts": "F",
        "drawer_boxes": "D",
        "worktop": "W",
        "plinth": "P",
        "hardware": "H",
    }.get(str(section or "").lower(), "X")


def _annotate_parts(df: pd.DataFrame, section: str) -> pd.DataFrame:
    """Adds production-friendly columns: PartCode, Pozicija, SklopKorak."""
    if df is None or df.empty:
        return df
    out = df.copy()
    pref = _section_prefix(section)
    counters: Dict[tuple, int] = {}
    part_codes: List[str] = []
    positions: List[str] = []
    steps: List[str] = []

    for _, row in out.iterrows():
        _rid = _safe_int(row.get("ID", 0), 0)
        mod_key = f"M{_rid}" if _rid > 0 else "M0"
        key = (mod_key, pref)
        counters[key] = counters.get(key, 0) + 1
        part_codes.append(f"{mod_key}-{pref}{counters[key]:02d}")
        _deo = str(row.get("Deo", row.get("Naziv", "")) or "")
        positions.append(_position_from_deo(_deo))
        steps.append(_assembly_step_for(section, _deo))

    out["PartCode"] = part_codes
    out["Pozicija"] = positions
    out["SklopKorak"] = steps
    return out


def _attach_wall_column(df: pd.DataFrame, modules: List[Dict[str, Any]]) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    wall_by_id = {
        int(m.get("id", 0)): f"Zid {str(m.get('wall_key', 'A') or 'A').upper()}"
        for m in (modules or [])
        if int(m.get("id", 0) or 0) > 0
    }

    def _wall_for_row(row: pd.Series) -> str:
        current = str(row.get("Zid", "") or "").strip()
        if current:
            return current
        rid = _safe_int(row.get("ID", 0), 0)
        if rid > 0:
            return wall_by_id.get(rid, "")
        modul = str(row.get("Modul", "") or "")
        if "Zid " in modul:
            idx = modul.find("Zid ")
            return modul[idx:].strip()
        return ""

    out["Zid"] = out.apply(_wall_for_row, axis=1)
    return out


def _hardware_brand_from_profile(profile_key: str, mfg: Dict[str, Any]) -> str:
    brand = str((mfg or {}).get("hardware_brand", "")).strip().upper()
    if brand in HARDWARE_BRAND_CATALOGS:
        return brand
    p = str(profile_key or "").upper()
    if "HETTICH" in p:
        return "HETTICH"
    if "GTV" in p:
        return "GTV"
    return "BLUM"


def _hinges_per_door(door_h_mm: float) -> int:
    if door_h_mm >= 2000:  # vrata >= 2000mm trebaju 5 sarki
        return 5
    if door_h_mm > 1200:
        return 4
    if door_h_mm > 900:
        return 3
    return 2


def _module_spans_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    ax0 = float(a.get("x_mm", 0) or 0)
    ax1 = ax0 + float(a.get("w_mm", 0) or 0)
    bx0 = float(b.get("x_mm", 0) or 0)
    bx1 = bx0 + float(b.get("w_mm", 0) or 0)
    return max(ax0, bx0) < min(ax1, bx1)


def _manufacturing_warnings(
    modules: List[Dict[str, Any]],
    *,
    kitchen: Dict[str, Any] | None = None,
    wall_h_mm: float,
    foot_h_mm: float,
    front_gap_mm: float,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def _row(mid: int, zone: str, modul: str, code: str, opis: str, preporuka: str) -> Dict[str, Any]:
        return {
            "ID": mid,
            "TYPE": str(zone or "").upper(),
            "Modul": modul,
            "Kategorija": "warning",
            "Naziv": f"UPOZORENJE ({code})",
            "Tip / Šifra": "CHECK",
            "Kol.": 1,
            "Napomena": f"{opis} | Preporuka: {preporuka}",
        }

    # Global profile warning
    if front_gap_mm < 1.0 or front_gap_mm > 4.0:
        rows.append(_row(
            0, "GLOBAL", "Projekat",
            "FRONT_GAP",
            f"Front fuga je {front_gap_mm:.1f} mm (van preporuke 1.0–4.0 mm).",
            "Postavi front_gap na 2.0 mm za stabilnu montažu."
        ))

    # Per-module warnings
    for m in modules:
        mid = int(m.get("id", 0) or 0)
        zone = str(m.get("zone", "")).lower()
        lbl = str(m.get("label", "") or m.get("template_id", ""))
        w = float(m.get("w_mm", 0) or 0)
        h = float(m.get("h_mm", 0) or 0)
        d = float(m.get("d_mm", 0) or 0)
        tid = str(m.get("template_id", "")).upper()
        params = m.get("params", {}) or {}
        wk = str(m.get("wall_key", "A") or "A").upper()

        if zone in ("wall", "wall_upper") and d > 400:
            rows.append(_row(
                mid, zone, lbl, "WALL_DEPTH",
                f"Dubina visećeg elementa {d:.0f} mm je velika za ergonomiju.",
                "Preporuka je 300–380 mm dubine za gornje elemente."
            ))

        if zone == "base" and d < 500:
            rows.append(_row(
                mid, zone, lbl, "BASE_DEPTH",
                f"Dubina donjeg elementa {d:.0f} mm je mala za standardne uređaje/sudoperu.",
                "Preporuka je min 560 mm za kuhinjske donje module."
            ))

        if zone == "tall" and "FREESTANDING" not in tid and d < 500:
            rows.append(_row(
                mid, zone, lbl, "TALL_DEPTH",
                f"Dubina visokog elementa {d:.0f} mm je mala za stabilan kuhinjski korpus.",
                "Preporuka je min 560 mm za visoke elemente."
            ))

        if zone == "tall" and h > max(wall_h_mm - foot_h_mm - 20, 0):
            rows.append(_row(
                mid, zone, lbl, "TALL_HEIGHT",
                f"Visoki element {h:.0f} mm je blizu/iznad raspoložive visine.",
                "Smanji visinu ili proveri realnu visinu plafona i stopice."
            ))

        if zone == "wall_upper":
            _supported = any(
                str(mm.get("zone", "")).lower() == "wall"
                and str(mm.get("wall_key", "A") or "A").upper() == wk
                and float(mm.get("x_mm", 0) or 0) <= float(m.get("x_mm", 0) or 0)
                and (float(mm.get("x_mm", 0) or 0) + float(mm.get("w_mm", 0) or 0))
                >= (float(m.get("x_mm", 0) or 0) + w)
                for mm in modules
            )
            if not _supported:
                rows.append(_row(
                    mid, zone, lbl, "WALL_UPPER_SUPPORT",
                    "Element drugog reda nema pun oslonac na gornjem elementu ispod sebe.",
                    "Poravnaj ga tako da cela širina leži na elementu ispod."
                ))

        if zone == "tall_top":
            _supported = any(
                str(mm.get("zone", "")).lower() == "tall"
                and str(mm.get("wall_key", "A") or "A").upper() == wk
                and float(mm.get("x_mm", 0) or 0) <= float(m.get("x_mm", 0) or 0)
                and (float(mm.get("x_mm", 0) or 0) + float(mm.get("w_mm", 0) or 0))
                >= (float(m.get("x_mm", 0) or 0) + w)
                for mm in modules
            )
            if not _supported:
                rows.append(_row(
                    mid, zone, lbl, "TALL_TOP_SUPPORT",
                    "Popuna iznad visokog nema pun oslonac na visokom elementu ispod sebe.",
                    "Poravnaj je tako da cela širina leži na elementu ispod."
                ))

        if "DRAWER" in tid and d < 450:
            rows.append(_row(
                mid, zone, lbl, "DRAWER_DEPTH",
                f"Fioke na dubini {d:.0f} mm mogu imati ograničen izbor klizača.",
                "Koristi kraće klizače (npr. 350/400) ili povećaj dubinu korpusa."
            ))

        if "LIFTUP" in tid and w > 1200:
            rows.append(_row(
                mid, zone, lbl, "LIFTUP_WIDTH",
                f"Lift-up front širine {w:.0f} mm može biti pretežak.",
                "Razdvoj front na 2 segmenta ili koristi jači/međupodupirač."
            ))

        if tid in {"BASE_DISHWASHER", "BASE_DISHWASHER_FREESTANDING"} and w < 600:
            rows.append(_row(
                mid, zone, lbl, "DISHWASHER_WIDTH",
                f"Širina za mašinu za sudove {w:.0f} mm je manja od standardnih 600 mm.",
                "Povećaj širinu na najmanje 600 mm."
            ))

        if tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_FRIDGE_FREESTANDING"} and w < 600:
            rows.append(_row(
                mid, zone, lbl, "FRIDGE_WIDTH",
                f"Širina za frižider {w:.0f} mm je manja od standardnih 600 mm.",
                "Povećaj širinu na najmanje 600 mm."
            ))

        if tid in {"BASE_COOKING_UNIT", "OVEN_HOB", "BASE_OVEN_HOB_FREESTANDING"} and w < 600:
            rows.append(_row(
                mid, zone, lbl, "COOKING_WIDTH",
                f"Širina za rernu/ploču {w:.0f} mm je manja od standardnih 600 mm.",
                "Povećaj širinu na najmanje 600 mm."
            ))

        if tid == "BASE_HOB" and w < 450:
            rows.append(_row(
                mid, zone, lbl, "HOB_WIDTH",
                f"Samostalna ploča za kuvanje širine {w:.0f} mm je manja od minimalnih 450 mm.",
                "Standardne ploče su 45 cm, 60 cm ili 90 cm — povećaj širinu."
            ))

        if tid in {"TALL_OVEN", "TALL_OVEN_MICRO"} and w < 600:
            rows.append(_row(
                mid, zone, lbl, "TALL_APPLIANCE_WIDTH",
                f"Širina visoke appliance kolone {w:.0f} mm je manja od 600 mm.",
                "Povećaj širinu na najmanje 600 mm."
            ))

        if "SINK" in tid and w < 600:
            rows.append(_row(
                mid, zone, lbl, "SINK_WIDTH",
                f"Sudoperski element širine {w:.0f} mm je suviše mali za stabilan laički workflow.",
                "Koristi najmanje 600 mm širine."
            ))

        if "CORNER" in tid and w < 800:
            rows.append(_row(
                mid, zone, lbl, "CORNER_WIDTH",
                f"Ugaoni element širine {w:.0f} mm je rizičan za stabilan raspored i pristup uglu.",
                "Povećaj širinu na najmanje 800 mm."
            ))
        if "CORNER" in tid:
            _anchor = "desno" if wk == "A" else "levo"
            _wall_len_map = (kitchen or {}).get("wall_lengths_mm", {}) or {}
            _wall_len = float(_wall_len_map.get(wk, ((kitchen or {}).get("wall", {}) or {}).get("length_mm", 3000)) or 3000)
            _x0 = float(m.get("x_mm", 0) or 0)
            _x1 = _x0 + w
            _exp_left = 5.0
            _exp_right = 5.0
            if wk == "A":
                if abs((_wall_len - _exp_right) - _x1) > 5:
                    rows.append(_row(
                        mid, zone, lbl, "CORNER_POSITION",
                        "Ugaoni element nije naslonjen na unutrasnji ugao zida A.",
                        "Postavi ga kao poslednji element desno, uz unutrasnji ugao."
                    ))
            else:
                if abs(_x0 - _exp_left) > 5:
                    rows.append(_row(
                        mid, zone, lbl, "CORNER_POSITION",
                        f"Ugaoni element nije naslonjen na unutrasnji ugao zida {wk}.",
                        f"Postavi ga kao prvi element {_anchor}, uz unutrasnji ugao."
                    ))

        if tid in {"WALL_HOOD", "WALL_MICRO"} and w < 600:
            rows.append(_row(
                mid, zone, lbl, "WALL_APPLIANCE_WIDTH",
                f"Širina modula za napu/mikrotalasnu {w:.0f} mm je manja od 600 mm.",
                "Povećaj širinu na najmanje 600 mm."
            ))

        if tid in {"WALL_HOOD", "WALL_MICRO"} and d < 300:
            rows.append(_row(
                mid, zone, lbl, "WALL_APPLIANCE_DEPTH",
                f"Dubina modula za napu/mikrotalasnu {d:.0f} mm je mala za uređaj i ventilaciju.",
                "Povećaj dubinu na najmanje 300 mm."
            ))

        if tid in {"BASE_DISHWASHER_FREESTANDING", "BASE_OVEN_HOB_FREESTANDING"} and d < 580:
            rows.append(_row(
                mid, zone, lbl, "FREESTANDING_DEPTH",
                f"Dubina samostojećeg uređaja {d:.0f} mm je manja od praktičnog minimuma 580 mm.",
                "Povećaj dubinu na najmanje 580 mm."
            ))

        if tid == "TALL_FRIDGE_FREESTANDING" and d < 600:
            rows.append(_row(
                mid, zone, lbl, "FREESTANDING_FRIDGE_DEPTH",
                f"Dubina samostojećeg frižidera {d:.0f} mm je manja od 600 mm.",
                "Povećaj dubinu na najmanje 600 mm."
            ))

        if tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_OVEN", "TALL_OVEN_MICRO"} and d < 560:
            rows.append(_row(
                mid, zone, lbl, "TALL_APPLIANCE_DEPTH",
                f"Dubina visoke appliance kolone {d:.0f} mm je manja od 560 mm.",
                "Povećaj dubinu na najmanje 560 mm."
            ))

        if ("1DOOR" in tid or tid in {"BASE_1DOOR", "WALL_1DOOR", "WALL_NARROW", "BASE_NARROW"}) and w > 600:
            rows.append(_row(
                mid, zone, lbl, "SINGLE_DOOR_WIDTH",
                f"Jednokrilni front širine {w:.0f} mm može biti nestabilan i težak za podešavanje.",
                "Podeli element na 2 vrata ili smanji širinu."
            ))

        if ("1DOOR" in tid or tid in {"BASE_1DOOR", "WALL_1DOOR", "WALL_UPPER_1DOOR", "WALL_NARROW", "BASE_NARROW"}):
            handle_side = str(params.get("handle_side", "") or "").lower()
            left_clear = 5
            right_clear = 5
            wall = (kitchen or {}).get("wall", {}) or {}
            wall_len = float(wall.get("length_mm", 3000) or 3000)
            mfg = ((kitchen or {}).get("manufacturing", {}) or {})
            profile_key = mfg.get("profile", "EU_SRB")
            prof = MANUFACTURING_PROFILES.get(profile_key, MANUFACTURING_PROFILES.get("EU_SRB", {})) or {}
            left_clear = float(mfg.get("mounting_tolerance_left_mm", prof.get("mounting_tolerance_left_mm", 5)) or 5)
            right_clear = float(mfg.get("mounting_tolerance_right_mm", prof.get("mounting_tolerance_right_mm", 5)) or 5)
            x0 = float(m.get("x_mm", 0) or 0)
            x1 = x0 + w
            if handle_side in ("left", "right") and x0 <= left_clear + 30 and handle_side == "right":
                rows.append(_row(
                    mid, zone, lbl, "SIDE_WALL_DOOR",
                    "Jednokrilna vrata su preblizu levom zidu na strani sarke.",
                    "Promeni stranu rucke ili dodaj filer 30-50 mm uz levi zid."
                ))
            if handle_side in ("left", "right") and x1 >= wall_len - right_clear - 30 and handle_side == "left":
                rows.append(_row(
                    mid, zone, lbl, "SIDE_WALL_DOOR",
                    "Jednokrilna vrata su preblizu desnom zidu na strani sarke.",
                    "Promeni stranu rucke ili dodaj filer 30-50 mm uz desni zid."
                ))

        dh_list = params.get("drawer_heights") or []
        if dh_list:
            if any(float(x) < 80 for x in dh_list):
                rows.append(_row(
                    mid, zone, lbl, "DRAWER_FRONT_MIN",
                    "Bar jedna fioka je niža od 80 mm, što je rizično za front i rukovanje.",
                    "Povećaj najmanju fioku na barem 80 mm."
                ))
            total = sum(float(x) for x in dh_list)
            if total > h - 10:
                rows.append(_row(
                    mid, zone, lbl, "DRAWER_STACK",
                    f"Zbir visina fioka {total:.0f} mm je vrlo blizu visine modula {h:.0f} mm.",
                    "Ostavi tehničku rezervu 10–20 mm za fuge i frontove."
                ))

        if "DOOR_DRAWER" in tid:
            door_h = float(params.get("door_height", h * 0.72) or (h * 0.72))
            if door_h < 180:
                rows.append(_row(
                    mid, zone, lbl, "DOOR_DRAWER_DOOR_MIN",
                    f"Vrata u kombinaciji vrata + fioka imaju samo {door_h:.0f} mm visine.",
                    "Povećaj vrata na najmanje 180 mm."
                ))
            if door_h > h - 120:
                rows.append(_row(
                    mid, zone, lbl, "DOOR_DRAWER_DRAWER_MIN",
                    f"Vrata u kombinaciji vrata + fioka uzimaju skoro celu visinu modula ({door_h:.0f} mm).",
                    "Ostavi barem 120 mm za fioku i tehničke fuge."
                ))

        install_warns = params.get("installation_warnings") or []
        for iw in install_warns:
            rows.append(_row(
                mid, zone, lbl, "INSTALLATION_ZONE",
                str(iw),
                "Proveri pristup instalaciji i ostavi servisni prostor."
            ))

    # ── Out-of-bounds validacija — modul izlazi van duzine zida ──────────────────
    for m in modules:
        mid  = int(m.get("id", 0) or 0)
        zone = str(m.get("zone", "")).lower()
        lbl  = str(m.get("label", "") or m.get("template_id", ""))
        wk   = str(m.get("wall_key", "A") or "A").upper()
        w    = float(m.get("w_mm", 0) or 0)
        x0   = float(m.get("x_mm", 0) or 0)
        x1   = x0 + w
        _wl_map = (kitchen or {}).get("wall_lengths_mm", {}) or {}
        _wl_kt  = (kitchen or {}).get("wall", {}) or {}
        _wall_len = float(_wl_map.get(wk, _wl_kt.get("length_mm", 3000)) or 3000)
        _tol = 2.0  # dozvoljena tolerancija u mm (montažni zazor)
        if x1 > _wall_len + _tol:
            rows.append(_row(
                mid, zone, lbl, "MODULE_OUT_OF_BOUNDS",
                f"Element izlazi van zida {wk}: x={x0:.0f}mm + w={w:.0f}mm = {x1:.0f}mm > duzina zida {_wall_len:.0f}mm.",
                "Pomeri element ulevo ili smanjite mu sirinu da stane u raspored zida."
            ))

    # Overlap warnings in same zone + same wall_key
    for i in range(len(modules)):
        for j in range(i + 1, len(modules)):
            a = modules[i]
            b = modules[j]
            za = str(a.get("zone", "")).lower()
            zb = str(b.get("zone", "")).lower()
            if za != zb:
                continue
            wa = str(a.get("wall_key", "A")).upper()
            wb = str(b.get("wall_key", "A")).upper()
            if wa != wb:
                continue
            if _module_spans_overlap(a, b):
                amid = int(a.get("id", 0) or 0)
                albl = str(a.get("label", "") or a.get("template_id", ""))
                blbl = str(b.get("label", "") or b.get("template_id", ""))
                rows.append(_row(
                    amid, za, albl, "OVERLAP",
                    f"Elementi se preklapaju u zoni {za.upper()} na zidu {wa}: '{albl}' i '{blbl}'.",
                    "Pomeri elemente tako da im se X-rasponi ne preklapaju."
                ))

            atid = str(a.get("template_id", "")).upper()
            btid = str(b.get("template_id", "")).upper()
            ax0 = int(a.get("x_mm", 0) or 0)
            ax1 = ax0 + int(a.get("w_mm", 0) or 0) + int(a.get("gap_after_mm", 0) or 0)
            bx0 = int(b.get("x_mm", 0) or 0)
            bx1 = bx0 + int(b.get("w_mm", 0) or 0) + int(b.get("gap_after_mm", 0) or 0)
            touching = abs(ax1 - bx0) <= 2 or abs(bx1 - ax0) <= 2
            if touching and (("CORNER" in atid and "CORNER" not in btid) or ("CORNER" in btid and "CORNER" not in atid)):
                amid = int(a.get("id", 0) or 0)
                albl = str(a.get("label", "") or a.get("template_id", ""))
                blbl = str(b.get("label", "") or b.get("template_id", ""))
                rows.append(_row(
                    amid, za, albl, "CORNER_OPENING_CLEARANCE",
                    f"Ugaoni element i susedni modul nalezu bez servisnog razmaka: '{albl}' / '{blbl}'.",
                    "Proveri frontove i rucke u otvaranju; po potrebi dodaj filer ili tehnicki razmak."
                ))
                _single_door_tids = {"BASE_1DOOR", "WALL_1DOOR", "WALL_UPPER_1DOOR", "WALL_NARROW", "BASE_NARROW"}
                for _cur, _other, _cur_tid, _other_tid, _cur_lbl in (
                    (a, b, atid, btid, albl),
                    (b, a, btid, atid, blbl),
                ):
                    if "CORNER" in _cur_tid or "CORNER" not in _other_tid:
                        continue
                    if ("1DOOR" not in _cur_tid) and (_cur_tid not in _single_door_tids):
                        continue
                    _cur_x = int(_cur.get("x_mm", 0) or 0)
                    _other_x = int(_other.get("x_mm", 0) or 0)
                    _handle = str((_cur.get("params", {}) or {}).get("handle_side", "") or "").lower()
                    _opens_into_corner = (_handle == "left") if _cur_x < _other_x else (_handle == "right")
                    if _opens_into_corner:
                        rows.append(_row(
                            int(_cur.get("id", 0) or 0),
                            za,
                            _cur_lbl,
                            "CORNER_DOOR_SWING",
                            f"Jednokrilni sused '{_cur_lbl}' otvara vrata ka uglu pored ugaonog modula.",
                            "Promeni stranu rucke ili koristi dvokrilni/fiokar pored ugla."
                        ))
                    _max_corner_neighbor_w = 500 if za == "base" else 450
                    if int(_cur.get("w_mm", 0) or 0) > _max_corner_neighbor_w:
                        rows.append(_row(
                            int(_cur.get("id", 0) or 0),
                            za,
                            _cur_lbl,
                            "CORNER_FRONT_COLLISION",
                            f"Jednokrilni sused '{_cur_lbl}' je preširok uz ugaoni modul ({int(_cur.get('w_mm', 0) or 0)}mm).",
                            f"Koristi max {_max_corner_neighbor_w}mm, dvokrilni element, fiokar ili ostavi filer uz ugao."
                        ))
    return rows


def _kant_desc(n_edge_w: int, n_edge_h: int, edge_thk: float,
               orient: str = "") -> str:
    """
    Kreira opis kantovanih ivica.
      n_edge_w: broj ivica po W osi (za vertikalne: F/prednja; za horizontalne: L+R)
      n_edge_h: broj ivica po H osi (za vertikalne: T/gornja; za horizontalne: F/prednja)
      orient:   "vertikalna" | "horizontalna" — utiče na labele osa
    """
    if n_edge_w == 0 and n_edge_h == 0:
        return "-"
    parts = []
    if orient == "horizontalna":
        # Za dno/plafon: H os = dubina, prednja ivica = H strana → label "F"
        if n_edge_h == 1:
            parts.append("F")
        elif n_edge_h == 2:
            parts.append("F+B")
        if n_edge_w == 1:
            parts.append("L")
        elif n_edge_w == 2:
            parts.append("L+R")
    else:
        # Vertikalne ploče (stranice, frontovi): standardne labele
        if n_edge_h == 1:
            parts.append("T")
        elif n_edge_h == 2:
            parts.append("T+B")
        if n_edge_w == 1:
            parts.append("F")
        elif n_edge_w == 2:
            parts.append("L+R")
    return "+".join(parts) + f" (ABS {edge_thk:.1f}mm)"


def _carcass_piece(
    mid: int, zone: str, label: str, part: str,
    cut_w: float, cut_h: float,
    n_edge_w: int, n_edge_h: int,
    mat: str, thk: float, edge_thk: float, step: float,
    kol: int = 1, nap: str = "",
    orient: str = "",
    L1: int = 0, L2: int = 0, K1: int = 0, K2: int = 0,
    modul: str = "",   # jedinstven naziv modula za krojnu listu (#ID [zona] naziv)
) -> Dict[str, Any]:
    """
    Generiše jedan red carcass DataFrame-a sa ispravnim CUT/FIN i kantom.
      n_edge_w: broj ivica po širini (W) koje imaju kant
      n_edge_h: broj ivica po visini (H) koje imaju kant
      orient:   "vertikalna" | "horizontalna"
      L1/L2/K1/K2: boolean kant flags (za nesting software)
    CUT se zaokružuje na step; FIN = CUT - (n_edge * edge_thk)
    """
    cw = _round_cut(cut_w, step)
    ch = _round_cut(cut_h, step)
    # _round_cut primenjen i na FIN dimenzije (sprečava floating point greške)
    fw = _round_cut(cw - n_edge_w * edge_thk, step)
    fh = _round_cut(ch - n_edge_h * edge_thk, step)
    return {
        "ID": mid,
        "TYPE": zone.upper(),
        "Modul": modul if modul else label,
        "Element": label,
        "Deo": part,
        "Materijal": mat,
        "Deb.": thk,
        "Kol.": kol,
        "Kant": _kant_desc(n_edge_w, n_edge_h, edge_thk, orient=orient),
        "L1": L1, "L2": L2, "K1": K1, "K2": K2,
        "Orijentacija": orient,
        "Duzina [mm]": fw,   # FIN dimenzija (gotova mera)
        "Sirina [mm]": fh,   # FIN dimenzija (gotova mera)
        "CUT_W [mm]": cw,    # sirova mera pre kanta
        "CUT_H [mm]": ch,    # sirova mera pre kanta
        "CUT (W×H)": f"{cw:.1f} × {ch:.1f}",
        "FIN (W×H)": f"{fw:.1f} × {fh:.1f}",
        "Smer goda": "V" if orient == "vertikalna" else ("H" if orient == "horizontalna" else "-"),
        "Napomena": nap,
    }


def _front_row(
    mid: int, zone: str, label: str, part_name: str,
    w: float, h: float,
    front_mat: str, front_thk: float,
    edge_thk: float = 2.0,
    step: float = 0.5,
    kol: int = 1,
    napomena: str = "",
    modul: str = "",   # jedinstven naziv modula za krojnu listu
    grain_dir: str = "V",  # smer goda fronta: V/H/N
) -> Dict[str, Any]:
    """Helper: pravi jedan red frontova. Frontovi imaju kant na sve 4 ivice (L1=L2=K1=K2=1)."""
    cw = _round_cut(w, step)
    ch = _round_cut(h, step)
    # _round_cut primenjen i na FIN dimenzije (sprečava floating point greške)
    fw = _round_cut(cw - 2 * edge_thk, step)
    fh = _round_cut(ch - 2 * edge_thk, step)
    _sg = grain_dir.upper() if grain_dir and grain_dir.upper() in ("H", "V", "N") else "V"
    return {
        "ID": mid,
        "TYPE": zone.upper(),
        "Modul": modul if modul else label,
        "Element": label,
        "Deo": part_name,
        "Materijal": front_mat,
        "Deb.": front_thk,
        "Kol.": kol,
        "Kant": _kant_desc(2, 2, edge_thk),  # sve 4 ivice = L+R + T+B
        "L1": 1, "L2": 1, "K1": 1, "K2": 1,
        "Orijentacija": "vertikalna",
        "Duzina [mm]": fw,   # FIN dimenzija (gotova mera)
        "Sirina [mm]": fh,   # FIN dimenzija (gotova mera)
        "CUT_W [mm]": cw,
        "CUT_H [mm]": ch,
        "CUT (W×H)": f"{cw:.1f} × {ch:.1f}",
        "FIN (W×H)": f"{fw:.1f} × {fh:.1f}",
        "Smer goda": _sg,
        "Napomena": napomena,
    }


def _drawer_box_rows(
    mid: int, zone: str, label: str, modul: str,
    W: float, D: float,
    carcass_thk: float, edge_thk: float,
    carcass_mat: str, step: float,
    front_gap: float,
    drawer_heights: list,
    slide_mm: float = _SLIDE_CLEARANCE_MM,
    setback_mm: float = _DRAWER_SETBACK_MM,
    reveal_mm: float = _DRAWER_BOX_REVEAL,
) -> List[Dict[str, Any]]:
    """
    Generiše redove krojne liste za sanduke fioka (telo fioke, bez dekorativnog fronta).
    Sve ploče su iverica iste debljine kao korpus (carcass_thk).

    Konstrukcija sanduka (butt joint, sve iverica carcass_thk):
      • 2× Bočna ploča        : box_d × box_h  (prednja + gornja ivica kantovane)
      • 1× Prednja strana sand.: inner_w × box_h  (gornja ivica kantovana)
      • 1× Zadnja strana      : inner_w × (box_h − carcass_thk)  (bez kanta)
      • 1× Dno               : inner_w × inner_d  (prednja ivica kantovana)

    Dimenzije:
      box_w   = W − 2×carcass_thk − 2×slide_mm   (spoljna širina sanduka)
      box_d   = D − setback_mm                    (dubina sanduka)
      box_h   = dh − 2×front_gap − reveal_mm      (visina sanduka po fioci)
      inner_w = box_w − 2×carcass_thk             (unutrašnja širina)
      inner_d = box_d − 2×carcass_thk             (unutrašnja dubina dna)
    """
    rows: List[Dict[str, Any]] = []

    if not drawer_heights or len(drawer_heights) == 0:
        return rows

    box_w   = W - 2 * carcass_thk - 2 * slide_mm
    box_d   = D - setback_mm
    inner_w = box_w - 2 * carcass_thk
    inner_d = box_d - 2 * carcass_thk

    if box_w <= 0 or box_d <= 0 or inner_w <= 0 or inner_d <= 0:
        return rows  # dimenzije nevalidne za ovu konfiguraciju

    for i, dh in enumerate(drawer_heights):
        box_h = float(dh) - 2 * front_gap - reveal_mm
        if box_h <= 0:
            continue

        # ── 2× Bočna ploča: box_d (dubina) × box_h ──────────────────────
        # Vertikalna; prednja ivica (L1) + gornja ivica (K1) kantovane
        rows.append(_carcass_piece(
            mid, zone, label, f"F{i + 1} — Bočna ploča",
            cut_w=box_d, cut_h=box_h,
            n_edge_w=1, n_edge_h=1,
            mat=carcass_mat, thk=carcass_thk, edge_thk=edge_thk, step=step,
            kol=2,
            orient="vertikalna",
            L1=1, L2=0, K1=1, K2=0,
            modul=modul,
        ))

        # ── 1× Prednja strana sanduka: inner_w × box_h ───────────────────
        # Vertikalna; samo gornja ivica (K1) kantovana
        rows.append(_carcass_piece(
            mid, zone, label, f"F{i + 1} — Prednja strana sanduka",
            cut_w=inner_w, cut_h=box_h,
            n_edge_w=0, n_edge_h=1,
            mat=carcass_mat, thk=carcass_thk, edge_thk=edge_thk, step=step,
            kol=1,
            orient="vertikalna",
            L1=0, L2=0, K1=1, K2=0,
            modul=modul,
        ))

        # ── 1× Zadnja strana: inner_w × (box_h − carcass_thk) ────────────
        # Vertikalna; bez kanta (dno proviruje ispod)
        zadnja_h = box_h - carcass_thk
        if zadnja_h > 0:
            rows.append(_carcass_piece(
                mid, zone, label, f"F{i + 1} — Zadnja strana sanduka",
                cut_w=inner_w, cut_h=zadnja_h,
                n_edge_w=0, n_edge_h=0,
                mat=carcass_mat, thk=carcass_thk, edge_thk=edge_thk, step=step,
                kol=1,
                orient="vertikalna",
                L1=0, L2=0, K1=0, K2=0,
                modul=modul,
            ))

        # ── 1× Dno: inner_w × inner_d ────────────────────────────────────
        # Horizontalna; prednja ivica kantovana (n_eh=1 → "F" u horiz. orijentaciji)
        rows.append(_carcass_piece(
            mid, zone, label, f"F{i + 1} — Dno sanduka",
            cut_w=inner_w, cut_h=inner_d,
            n_edge_w=0, n_edge_h=1,
            mat=carcass_mat, thk=carcass_thk, edge_thk=edge_thk, step=step,
            kol=1,
            orient="horizontalna",
            L1=1, L2=0, K1=0, K2=0,
            modul=modul,
        ))

    return rows


def _validate_modules(
    modules: List[Dict[str, Any]],
    carcass_thk: float,
    front_gap: float,
) -> List[tuple]:
    """
    Validira module pre generisanja krojne liste.
    Vraca listu grešaka: [(mid, poruka), ...]
    """
    errors: List[tuple] = []
    for inst in modules:
        mid = inst.get("id", "?")
        w = float(inst.get("w_mm", 0))
        h = float(inst.get("h_mm", 0))
        d = float(inst.get("d_mm", 0))
        params = inst.get("params", {}) or {}

        if w <= 0 or h <= 0 or d <= 0:
            errors.append((mid, f"Dimenzija <= 0: w={w}, h={h}, d={d}"))
            continue
        if w - 2 * carcass_thk <= 0:
            errors.append((mid, f"Unutrašnja širina {w - 2*carcass_thk:.0f}mm <= 0"))
        if d - carcass_thk <= 0:
            errors.append((mid, f"Unutrašnja dubina {d - carcass_thk:.0f}mm <= 0"))
        dh_list = params.get("drawer_heights", [])
        if dh_list:
            total = sum(float(x) for x in dh_list)
            if total > h:
                errors.append((mid, f"Zbir visina fioka {total:.0f}mm > visina modula {h:.0f}mm"))
            for i, dh in enumerate(dh_list):
                if float(dh) <= 0:
                    errors.append((mid, f"Visina fioke #{i+1} = {dh} <= 0"))
    return errors


def generate_cutlist(kitchen: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Production-accurate krojna lista po CUTLIST SPEC v1.0 – SRB/EU.

    Vraca sekcije:
      - carcass  (stranice, dno, plafon — WALL/TALL imaju plafon, BASE NEMA)
      - backs    (leđne ploče — HDF/iverica, groove ili overlay)
      - fronts   (frontovi / vrata / fioke, kant 4×)
      - worktop  (radna ploča, 1 segment)
      - plinth   (sokla/lajsna)
    """
    modules = kitchen.get("modules", []) or []
    mats = kitchen.get("materials", {}) or {}

    # -------------------------------------------------------
    # Manufacturing profil
    # -------------------------------------------------------
    mfg = kitchen.get("manufacturing", {}) or {}
    profile_key = mfg.get("profile", "EU_SRB")
    prof = MANUFACTURING_PROFILES.get(profile_key, MANUFACTURING_PROFILES["EU_SRB"])
    hw_brand = _hardware_brand_from_profile(profile_key, mfg)
    hwc = HARDWARE_BRAND_CATALOGS.get(hw_brand, HARDWARE_BRAND_CATALOGS["BLUM"])
    front_gap  = float(prof.get("front_gap_mm", 2.0))
    step       = float(prof.get("cut_rounding_step_mm", 0.5))
    back_inset = float(prof.get("back_inset_mm", 10))

    # -------------------------------------------------------
    # Materijali
    # -------------------------------------------------------
    edge_thk    = float(mats.get("edge_abs_thk", 2))
    carcass_mat = mats.get("carcass_material", "Iverica")
    carcass_thk = float(mats.get("carcass_thk", 18))
    front_mat   = mats.get("front_material", "MDF")
    front_thk   = float(mats.get("front_thk", 18))
    back_thk    = float(mats.get("back_thk", 8))
    # Materijal leđne ploče: HDF za tanke (<=6mm), inače isti kao korpus
    back_mat    = "HDF" if back_thk <= 6 else carcass_mat
    # Groove ili overlay: ako back_inset > 0 → groove mode
    back_mode   = "groove" if back_inset > 0 else "overlay"

    # -------------------------------------------------------
    # Validacija
    # -------------------------------------------------------
    _errors = _validate_modules(modules, carcass_thk, front_gap)
    _error_map: Dict[int, str] = {mid: msg for mid, msg in _errors}

    # -------------------------------------------------------
    # Pomocne lambda za carcass
    # -------------------------------------------------------
    # _cp se poziva unutar for petlje — modul_label se prosledjuje eksplicitno pri svakom pozivu
    def _cp(mid, zone, label, part, cut_w, cut_h, n_ew, n_eh, kol=1, nap="",
            orient="", L1=0, L2=0, K1=0, K2=0, _mlbl=""):
        """Shortcut za _carcass_piece sa fiksnim mat/thk/edge/step."""
        err = _error_map.get(mid, "")
        return _carcass_piece(
            mid, zone, label, part, cut_w, cut_h, n_ew, n_eh,
            carcass_mat, carcass_thk, edge_thk, step, kol=kol,
            nap=f"GREŠKA: {err}" if err else nap,
            orient=orient, L1=L1, L2=L2, K1=K1, K2=K2,
            modul=_mlbl,
        )

    rows_carcass:       List[Dict[str, Any]] = []
    rows_backs:         List[Dict[str, Any]] = []
    rows_fronts:        List[Dict[str, Any]] = []
    rows_drawer_boxes:  List[Dict[str, Any]] = []
    _PANEL_ONLY_TIDS = {"FILLER_PANEL", "END_PANEL"}

    # -------------------------------------------------------
    # Loop kroz module
    # -------------------------------------------------------
    _DOOR_TIDS = {
        "BASE_1DOOR", "BASE_2DOOR", "BASE_DOORS",
        "WALL_1DOOR", "WALL_2DOOR", "WALL_DOORS", "WALL_LIFTUP",
        "WALL_UPPER_1DOOR", "WALL_UPPER_2DOOR",
        "TALL_DOORS", "TALL_TOP_DOORS",
    }
    _GLASS_TIDS = {"WALL_GLASS", "TALL_GLASS"}

    for inst in modules:
        mid   = int(inst.get("id", 0))
        zone  = str(inst.get("zone", "")).lower().strip()
        tid   = str(inst.get("template_id", "")).upper()
        label = inst.get("label", tid)
        params = inst.get("params", {}) or {}
        grain_dir = str(params.get("grain_dir", "V") or "V").upper()
        if grain_dir not in ("H", "V", "N"):
            grain_dir = "V"

        # Jedinstveni naziv modula za krojnu listu: "#ID [zona_abbr] naziv — WxH"
        # Npr: "#3 [G] Gornji (2 vrata) — 800×720"
        _zone_abbr = {"base": "D", "wall": "G", "wall_upper": "G2", "tall": "V", "tall_top": "VT"}.get(zone, zone.upper())
        _w_lbl = int(inst.get("w_mm", 0))
        _h_lbl = int(inst.get("h_mm", 0))
        modul_label = f"#{mid} [{_zone_abbr}] {label} — {_w_lbl}×{_h_lbl}"

        w = float(inst.get("w_mm", 0))
        h = float(inst.get("h_mm", 0))
        d = float(inst.get("d_mm", 0))
        _is_corner = "CORNER" in tid

        if w <= 0 or h <= 0 or d <= 0:
            continue

        if tid in _PANEL_ONLY_TIDS:
            if tid == "FILLER_PANEL":
                _pw = w
                _ph = h
                _deo = "Filer panel"
                _nap = "Panel-only element; širina popune × visina. Vidljiva dekorativna ploča."
            else:
                _pw = d
                _ph = h
                _deo = "Završna bočna ploča"
                _nap = "Panel-only element; dubina korpusa × visina. Vidljiva završna bočna strana."

            rows_carcass.append(_carcass_piece(
                mid, zone, label, _deo,
                _pw, _ph,
                1, 2,
                front_mat, front_thk, edge_thk, step,
                kol=1,
                nap=_nap,
                orient="vertikalna",
                L1=1, L2=0, K1=1, K2=1,
                modul=modul_label,
            ))
            continue

        # Unutrašnje dimenzije
        inner_w = w - 2 * carcass_thk   # širina dna/plafona
        inner_d = d - carcass_thk        # dubina dna/plafona (pozadi ulazi leđna ploča)

        # ===================================================
        # FAZA B: CARCASS
        # Stranice:  kant T+F (gornja+prednja) → n_ew=1(F), n_eh=1(T), vertikalna
        #            L1=1(prednja/dugačka), K1=1(gornja/kratka)
        # Dno:       kant F (prednja) → n_ew=0, n_eh=1(F), horizontalna
        #            L1=1(prednja ivica dugačke = frontalna strana)
        # Plafon:    isti kao Dno — samo WALL/TALL, BASE NEMA
        #
        # UREĐAJI BEZ SOPSTVENOG KORPUSA (frižider, napa...):
        # Ovi elementi su slobodnostojeći uređaji — ne pravimo im korpus od iverice.
        # Krojna lista za njih je prazna (CARCASS i BACKS se preskakuju).
        # ===================================================
        # DISHWASHER — ugradna MZS: nema bočnih ploča/dna/leđne ploče;
        #              jedina ploča je vezna letva (gornji vez) — dodaje se posebno
        _NO_CARCASS_TIDS = {
            "BASE_DISHWASHER",
            "BASE_DISHWASHER_FREESTANDING",
            "BASE_OVEN_HOB_FREESTANDING",
            "TALL_FRIDGE_FREESTANDING",
        }
        _skip_carcass = tid in _NO_CARCASS_TIDS

        if not _skip_carcass:
            if _is_corner:
                # ===================================================
                # UGAONI MODUL — L-oblik korpusa
                # Geometrija: oba kraka jednaka, sirina w, dubina d
                #   Krak 1 ide uz zid A (sirina w, dubina d)
                #   Krak 2 ide uz zid B (sirina w, dubina d, simetricno)
                # Delovi:
                #   Strana 1 + 2 (spoljna krajnja ploča): h × d  (kao standardna strana)
                #   Kutna vertikala (unutrašnji separator, 2×): h × d
                #   Dno Krak 1 (kvadratni ugao + produženje Kraka 1): (w-2t) × (d-t)
                #   Dno Krak 2 (produženje Kraka 2 van kvadrata): (d-2t) × (w-d-t)
                #   Za WALL zone: isti Plafon komadi kao Dno
                # ===================================================
                _corner_nap = "L-ugaoni korpus"
                # Spoljna strana 1 i 2 (krajnje bočne ploče ugaonog elementa)
                rows_carcass.append(_cp(mid, zone, label, "Strana 1 (ugaona)",
                                        d, h, n_ew=1, n_eh=1,
                                        orient="vertikalna", L1=1, L2=0, K1=1, K2=0,
                                        _mlbl=modul_label, nap=_corner_nap))
                rows_carcass.append(_cp(mid, zone, label, "Strana 2 (ugaona)",
                                        d, h, n_ew=1, n_eh=1,
                                        orient="vertikalna", L1=1, L2=0, K1=1, K2=0,
                                        _mlbl=modul_label, nap=_corner_nap))
                # Kutna vertikala — unutrašnji separator (2×, po jedna za svaki krak)
                rows_carcass.append(_cp(mid, zone, label, "Kutna vertikala",
                                        d, h, n_ew=1, n_eh=1,
                                        kol=2, orient="vertikalna", L1=1, L2=0, K1=1, K2=0,
                                        _mlbl=modul_label,
                                        nap=f"{_corner_nap}; unutrašnji pregradni zid (2×)"))
                # Dno Krak 1 — pokriva kvadratni ugao + produženje Kraka 1
                rows_carcass.append(_cp(mid, zone, label, "Dno — Krak 1",
                                        inner_w, inner_d, n_ew=0, n_eh=1,
                                        orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                        _mlbl=modul_label, nap=_corner_nap))
                # Dno Krak 2 — produženje drugog kraka van ugaonog kvadrata
                _dk2_w = d - 2 * carcass_thk
                _dk2_h = w - d - carcass_thk
                if _dk2_w > 0 and _dk2_h > 0:
                    rows_carcass.append(_cp(mid, zone, label, "Dno — Krak 2",
                                            _dk2_w, _dk2_h, n_ew=0, n_eh=1,
                                            orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                            _mlbl=modul_label,
                                            nap=f"{_corner_nap}; produženje drugog kraka"))
                # Plafon — SAMO za WALL zone (gornji ugaoni element)
                if zone in ("wall", "wall_upper", "tall", "tall_top"):
                    rows_carcass.append(_cp(mid, zone, label, "Plafon — Krak 1",
                                            inner_w, inner_d, n_ew=0, n_eh=1,
                                            orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                            _mlbl=modul_label, nap=_corner_nap))
                    if _dk2_w > 0 and _dk2_h > 0:
                        rows_carcass.append(_cp(mid, zone, label, "Plafon — Krak 2",
                                                _dk2_w, _dk2_h, n_ew=0, n_eh=1,
                                                orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                                _mlbl=modul_label, nap=_corner_nap))
            else:
                # Stranice (iste za sve zone)
                rows_carcass.append(_cp(mid, zone, label, "Leva strana",  d, h, n_ew=1, n_eh=1,
                                        orient="vertikalna",   L1=1, L2=0, K1=1, K2=0, _mlbl=modul_label))
                rows_carcass.append(_cp(mid, zone, label, "Desna strana", d, h, n_ew=1, n_eh=1,
                                        orient="vertikalna",   L1=1, L2=0, K1=1, K2=0, _mlbl=modul_label))
                # Dno — kant samo prednja (L1)
                rows_carcass.append(_cp(mid, zone, label, "Dno", inner_w, inner_d, n_ew=0, n_eh=1,
                                        orient="horizontalna", L1=1, L2=0, K1=0, K2=0, _mlbl=modul_label))
                # Plafon — SAMO za WALL, WALL_UPPER, TALL, TALL_TOP (BASE nema — tu je radna ploča)
                if zone in ("wall", "wall_upper", "tall", "tall_top"):
                    rows_carcass.append(_cp(mid, zone, label, "Plafon", inner_w, inner_d, n_ew=0, n_eh=1,
                                            orient="horizontalna", L1=1, L2=0, K1=0, K2=0, _mlbl=modul_label))
                # Srednja vertikalna ploča — za 2-vrata KRILNA elemente
                # Klizna vrata (SLIDING) nemaju srednju vertikalu — vrata klize po cijeloj širini
                if "2DOOR" in tid and "SLIDING" not in tid:
                    rows_carcass.append(_cp(mid, zone, label, "Srednja vertikala",
                                            d, h, n_ew=1, n_eh=1,
                                            orient="vertikalna", L1=1, L2=0, K1=1, K2=0,
                                            _mlbl=modul_label))

        # Police — za elemente koji imaju otvorene police (OPEN, GLASS, PANTRY)
        # Dimenzije police = iste kao dno (inner_w × inner_d), kant samo prednja ivica (L1)
        _N_SHELVES: Dict[str, int] = {
            "BASE_OPEN": 1,
            "WALL_OPEN": 1, "WALL_GLASS": 1,
            "WALL_UPPER_OPEN": 1,
            "TALL_PANTRY": 3, "TALL_OPEN": 2,
        }
        _n_sh = 0
        for _kp, _nv in _N_SHELVES.items():
            if _kp in tid.upper():
                _n_sh = _nv
                break
        if _n_sh > 0:
            rows_carcass.append(_cp(mid, zone, label, "Polica",
                                    inner_w, inner_d, n_ew=0, n_eh=1,
                                    orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                    kol=_n_sh, _mlbl=modul_label))

        # Police iz params — za standardne zatvorene elemente (1DOOR, 2DOOR, LIFTUP, itd.)
        # Korisnik unosi broj polica u UI params panelu → params["n_shelves"]
        # ISKLJUČENI: aparati, sudopera, napa, i moduli koji već imaju police iz _N_SHELVES
        _NO_SHELF_TIDS = (
            "FRIDGE", "DISHWASHER", "COOKING_UNIT", "OVEN_HOB", "OVEN",
            "SINK", "HOOD", "HOB", "TRASH", "OPEN", "GLASS", "PANTRY", "NARROW", "DRAWER",
        )
        if _n_sh == 0 and not _skip_carcass and not any(k in tid for k in _NO_SHELF_TIDS):
            _n_sh_params = int((params or {}).get("n_shelves", 0) or 0)
            if _n_sh_params > 0:
                rows_carcass.append(_cp(mid, zone, label, "Polica (podesiva)",
                                        inner_w, inner_d, n_ew=0, n_eh=1,
                                        orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                        kol=_n_sh_params, _mlbl=modul_label))

        # Horizontalne pregrade za TALL aparat module (odvajaju zone: fioka / rerna / mikrovalna)
        # TALL_OVEN_MICRO mora biti provjeren PRIJE TALL_OVEN (sadrži isti substring)
        if not _skip_carcass:
            if "TALL_OVEN_MICRO" in tid:
                rows_carcass.append(_cp(mid, zone, label, "Horizontalna pregrada",
                                        inner_w, inner_d, n_ew=0, n_eh=1,
                                        orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                        kol=2, _mlbl=modul_label,
                                        nap="Pregrada između zona (rerna / mikrovalna)"))
            elif "TALL_OVEN" in tid:
                rows_carcass.append(_cp(mid, zone, label, "Horizontalna pregrada",
                                        inner_w, inner_d, n_ew=0, n_eh=1,
                                        orient="horizontalna", L1=1, L2=0, K1=0, K2=0,
                                        _mlbl=modul_label,
                                        nap="Pregrada između zona (iznad rerne)"))

        # ===================================================
        # FAZA C: LEĐNE PLOČE (backs)
        # groove: back_W = w - 2*GROOVE_DEPTH, back_H = h - GROOVE_DEPTH
        # overlay: back_W = w, back_H = h
        # Nema kanta; FIN = CUT
        # Uređaji bez korpusa (npr. MZS slot) nemaju ni leđnu ploču
        # ===================================================
        err_nap = f"GREŠKA: {_error_map[mid]}" if mid in _error_map else ""
        if not _skip_carcass:
            if _is_corner:
                # Ugaoni modul: 2 leđne ploče — po jedna za svaki krak produženja
                # Kvadratni ugaoni prostor (d×d) naslonjen je na zidove — leđna ploča tamo nije potrebna.
                # Svaki krak produženja ima sopstvenu leđnu ploču širine (w - d).
                _arm_bw_raw = w - d   # sirina krakova van ugaonog kvadrata
                if back_mode == "groove":
                    _bw_arm = _round_cut(_arm_bw_raw - 2 * GROOVE_DEPTH, step)
                    _bh_arm = _round_cut(h - GROOVE_DEPTH, step)
                    _back_nap_arm = f"utor {GROOVE_DEPTH}mm; leđna ploča ugaonog kraka"
                else:
                    _bw_arm = _round_cut(_arm_bw_raw, step)
                    _bh_arm = _round_cut(h, step)
                    _back_nap_arm = "overlay; leđna ploča ugaonog kraka"
                for _arm_lbl in ("Leđna ploča — Krak 1", "Leđna ploča — Krak 2"):
                    rows_backs.append({
                        "ID":          mid,
                        "TYPE":        zone.upper(),
                        "Modul":       modul_label,
                        "Element":     label,
                        "Deo":         _arm_lbl,
                        "Materijal":   back_mat,
                        "Deb.":        back_thk,
                        "Kol.":        1,
                        "Kant":        "-",
                        "L1": 0, "L2": 0, "K1": 0, "K2": 0,
                        "Orijentacija": "vertikalna",
                        "Duzina [mm]": _bw_arm,
                        "Sirina [mm]": _bh_arm,
                        "CUT_W [mm]":  _bw_arm,
                        "CUT_H [mm]":  _bh_arm,
                        "CUT (W×H)":   f"{_bw_arm:.1f} × {_bh_arm:.1f}",
                        "FIN (W×H)":   f"{_bw_arm:.1f} × {_bh_arm:.1f}",
                        "Napomena":    err_nap if err_nap else _back_nap_arm,
                    })
            else:
                if back_mode == "groove":
                    bw = _round_cut(w - 2 * GROOVE_DEPTH, step)
                    bh = _round_cut(h - GROOVE_DEPTH, step)
                    back_nap = f"utor {GROOVE_DEPTH}mm"
                else:
                    bw = _round_cut(w, step)
                    bh = _round_cut(h, step)
                    back_nap = "overlay"
                if "HOOD" in tid:
                    back_nap = f"{back_nap}; ostaviti otvor/prolaz za odvod nape prema modelu uređaja"
                elif "MICRO" in tid:
                    back_nap = f"{back_nap}; ostaviti otvor za kabl i ventilaciju mikrotalasne"
                elif "SINK" in tid:
                    back_nap = f"{back_nap}; ostaviti otvor za dovod/odvod vode prema poziciji instalacija"
                rows_backs.append({
                    "ID":          mid,
                    "TYPE":        zone.upper(),
                    "Modul":       modul_label,
                    "Element":     label,
                    "Deo":         "Leđna ploča",
                    "Materijal":   back_mat,
                    "Deb.":        back_thk,
                    "Kol.":        1,
                    "Kant":        "-",
                    "L1": 0, "L2": 0, "K1": 0, "K2": 0,
                    "Orijentacija": "vertikalna",
                    "Duzina [mm]": bw,   # FIN = CUT (nema kanta)
                    "Sirina [mm]": bh,   # FIN = CUT (nema kanta)
                    "CUT_W [mm]":  bw,
                    "CUT_H [mm]":  bh,
                    "CUT (W×H)":   f"{bw:.1f} × {bh:.1f}",
                    "FIN (W×H)":   f"{bw:.1f} × {bh:.1f}",
                    "Napomena":    err_nap if err_nap else back_nap,
                })

        # ===================================================
        # FAZA E: FRONTOVI (po tipu modula)
        # Frontovi uvek imaju kant 4× (sve 4 ivice)
        # fw = širina fronta = w - 2 * front_gap
        # ===================================================
        fw = w - 2 * front_gap

        def fr(part_name, fw_, fh_, kol_=1, nap_=""):
            """Shortcut za _front_row sa fiksnim mat/thk/edge/step."""
            return _front_row(mid, zone, label, part_name, fw_, fh_,
                              front_mat, front_thk, edge_thk, step, kol=kol_, napomena=nap_,
                              modul=modul_label, grain_dir=grain_dir)

        # Vrata (1 ili 2 krila) — BASE, WALL, TALL_DOORS + ormarni ugaoni (CORNER)
        # WARDROBE+SLIDING i 2DOOR+SLIDING moraju biti isključeni — obrađuju se posebno ispod
        if (tid in _DOOR_TIDS or "1DOOR" in tid
                or ("2DOOR" in tid and "SLIDING" not in tid)
                or ("WARDROBE" in tid and "CORNER" in tid and "DRAWERS" not in tid and "SLIDING" not in tid)):
            num_doors = 2 if (w > 500 and "1DOOR" not in tid) else 1
            door_w = (fw - front_gap) / num_doors if num_doors > 1 else fw
            door_h = h - 2 * front_gap
            rows_fronts.append(fr("Vrata", door_w, door_h, kol_=num_doors))

        # Uski bazni izvlačni modul — jedan front, unutra ide gotov uski izvlačni set
        elif "BASE_NARROW" in tid:
            rows_fronts.append(fr(
                "Front uskog izvlačnog modula", fw, h - 2 * front_gap, kol_=1,
                nap_="Uski modul za flaše/ulja/začine; unutrašnjost je kupovni izvlačni program"
            ))

        # Uski gornji zidni modul — standardna uska vrata
        elif "WALL_NARROW" in tid:
            rows_fronts.append(fr(
                "Vrata", fw, h - 2 * front_gap, kol_=1,
                nap_="Uski zidni element; proveriti smer otvaranja prema položaju na zidu"
            ))

        # Kuhinjski ugaoni elementi — L-korpus; front zavisi od mehanizma (lazy Susan / blind-corner)
        elif "CORNER" in tid:
            corner_front_w = fw
            corner_front_h = h - 2 * front_gap
            _is_diag_corner = "DIAGONAL" in tid
            _corner_front_nap = (
                "Dijagonalni ugaoni element; 2 manja fronta za krilna vrata ugla — dimenziju uskladiti sa mehanizmom"
                if _is_diag_corner
                else "L-ugaoni element; 2 manja fronta ugla (lazy Susan okretna ili blind-corner pull-out) — dimenziju i mehanizam proveriti prema stvarnom rasporedu"
            )
            rows_fronts.append(fr(
                "Ugaoni front", corner_front_w, corner_front_h, kol_=1,
                nap_=_corner_front_nap
            ))

        # Američki plakar — klizna vrata (TALL_WARDROBE_AMERICAN)
        elif "WARDROBE_AMERICAN" in tid:
            # Broj kliznih panela: ~1 panel na svakih 700mm širine
            _ap_n = max(2, int(round(w / 700)))
            _ap_w = (fw - (_ap_n - 1) * front_gap) / _ap_n
            _ap_h = h - 2 * front_gap
            rows_fronts.append(fr(
                f"Klizna vrata — američki plakar", _ap_w, _ap_h, kol_=_ap_n,
                nap_=f"{_ap_n} klizna panela × {_ap_w:.0f}mm"
            ))

        # Klizni ormari — TALL_WARDROBE_2DOOR_SLIDING i TALL_WARDROBE_CORNER_SLIDING
        # Pažnja: NE smeju pasti u "2DOOR" granu iznad (imaju šarnirska vrata umesto kliznih)
        elif "WARDROBE" in tid and "SLIDING" in tid:
            _sl_n = max(2, int(round(w / 700)))
            _sl_w = (fw - (_sl_n - 1) * front_gap) / _sl_n
            _sl_h = h - 2 * front_gap
            rows_fronts.append(fr(
                "Klizna vrata — ormar", _sl_w, _sl_h, kol_=_sl_n,
                nap_=f"{_sl_n} klizna panela × {_sl_w:.0f}mm; klizni sistem po celoj širini"
            ))

        # Staklena vrata
        elif tid in _GLASS_TIDS or "GLASS" in tid:
            num_doors = 2 if w > 450 else 1
            door_w = (fw - front_gap) / num_doors if num_doors > 1 else fw
            door_h = h - 2 * front_gap
            rows_fronts.append(fr("Staklena vrata", door_w, door_h, kol_=num_doors, nap_="Staklo"))

        # Kombi: vrata + fioka (BASE_DOOR_DRAWER) — i vrata i fioka front
        # MORA biti PRIJE opšteg "DRAWER" check-a jer TID sadrži "DRAWER"!
        elif "DOOR_DRAWER" in tid:
            _raw_door_h = float(params.get("door_height", h * 0.72))
            # Validacija: door_height ne sme biti veci od h - 80mm (minimum za fioku)
            _min_drawer_h = 80.0
            if _raw_door_h > h - _min_drawer_h:
                _raw_door_h = h * 0.72  # fallback na default proporciju
            _door_h_dd = _raw_door_h - 2 * front_gap
            rows_fronts.append(fr("Vrata", fw, max(1.0, _door_h_dd)))
            _dh_list_dd = params.get("drawer_heights")
            if _dh_list_dd and len(_dh_list_dd) > 0:
                for _i, _dh in enumerate(_dh_list_dd):
                    rows_fronts.append(fr(f"Front fioke {_i + 1}", fw,
                                         max(1.0, float(_dh) - 2 * front_gap)))
                _dh_list_box = list(_dh_list_dd)
            else:
                _fdh_dd = h - _raw_door_h - 2 * front_gap
                rows_fronts.append(fr("Front fioke", fw, max(1.0, _fdh_dd)))
                _dh_list_box = [max(1.0, h - _raw_door_h)]
            rows_drawer_boxes.extend(_drawer_box_rows(
                mid=mid, zone=zone, label=label, modul=modul_label,
                W=w, D=d,
                carcass_thk=carcass_thk, edge_thk=edge_thk,
                carcass_mat=carcass_mat, step=step,
                front_gap=front_gap,
                drawer_heights=_dh_list_box,
            ))

        # Fioke (BASE_DRAWERS, BASE_NARROW_DRAWERS, itd.)
        elif "DRAWER" in tid and "DOORS" not in tid and "OVEN" not in tid:
            drawer_heights = params.get("drawer_heights", None)
            if drawer_heights and len(drawer_heights) > 0:
                for _i, _dh in enumerate(drawer_heights):
                    fh_i = float(_dh) - 2 * front_gap
                    rows_fronts.append(fr(f"Front fioke {_i + 1}", fw, fh_i))
                _dh_list_box = list(drawer_heights)
            else:
                n_d = max(1, int(params.get("n_drawers", 3 if h > 600 else 2)))
                fh_uniform = (h / n_d) - 2 * front_gap
                rows_fronts.append(fr("Front fioke (unif.)", fw, fh_uniform, kol_=n_d))
                _dh_list_box = [float(h) / n_d] * n_d
            # Sanduk fioke — telo (iverica, sve dimenzije)
            if _dh_list_box:
                rows_drawer_boxes.extend(_drawer_box_rows(
                    mid=mid, zone=zone, label=label, modul=modul_label,
                    W=w, D=d,
                    carcass_thk=carcass_thk, edge_thk=edge_thk,
                    carcass_mat=carcass_mat, step=step,
                    front_gap=front_gap,
                    drawer_heights=_dh_list_box,
                ))

        # Kombinovani: vrata + fioka (BASE_DOORS_DRAWERS)
        elif "DOORS_DRAWERS" in tid:
            door_h = (h * 0.72) - 2 * front_gap
            rows_fronts.append(fr("Vrata", fw, door_h))
            drawer_h_dd = (h * 0.28) - 2 * front_gap
            rows_fronts.append(fr("Front fioke", fw, drawer_h_dd))

        # BASE_COOKING_UNIT — kuhinjska jedinica (rerna + HOB ploča za kuvanje)
        # Rerna IMA SOPSTVENI PANEL — ne generiše se ovde!
        # HOB (ploča) nije u krojnoj listi. SAMO front fioke (ako postoji).
        elif "COOKING_UNIT" in tid:
            if params.get("has_drawer", True):  # default: fioka je standard
                dh_list = params.get("drawer_heights", None)
                if dh_list and len(dh_list) > 0:
                    fh_drawer = float(dh_list[0]) - 2 * front_gap
                    _dh_list_box = [float(dh_list[0])]
                else:
                    fh_drawer = 130.0 - 2 * front_gap  # standardna visina fioke kuhinjske jedinice
                    _dh_list_box = [130.0]
                rows_fronts.append(fr("Front fioke (kuhinjska jedinica)", fw, fh_drawer,
                                      nap_="Fioka ispod rerne; rerna ima sopstveni panel"))
                rows_drawer_boxes.extend(_drawer_box_rows(
                    mid=mid, zone=zone, label=label, modul=modul_label,
                    W=w, D=d,
                    carcass_thk=carcass_thk, edge_thk=edge_thk,
                    carcass_mat=carcass_mat, step=step,
                    front_gap=front_gap,
                    drawer_heights=_dh_list_box,
                ))

        # BASE_OVEN_HOB (legacy) — isto kao COOKING_UNIT, zadrzano radi kompatibilnosti
        elif tid == "OVEN_HOB":
            if params.get("has_drawer", True):
                dh_list = params.get("drawer_heights", None)
                if dh_list and len(dh_list) > 0:
                    fh_drawer = float(dh_list[0]) - 2 * front_gap
                    _dh_list_box = [float(dh_list[0])]
                else:
                    fh_drawer = 150.0 - 2 * front_gap
                    _dh_list_box = [150.0]
                rows_fronts.append(fr("Front fioke (ispod rerne)", fw, fh_drawer,
                                      nap_="Fioka ispod rerne; rerna ima sopstveni panel"))
                rows_drawer_boxes.extend(_drawer_box_rows(
                    mid=mid, zone=zone, label=label, modul=modul_label,
                    W=w, D=d,
                    carcass_thk=carcass_thk, edge_thk=edge_thk,
                    carcass_mat=carcass_mat, step=step,
                    front_gap=front_gap,
                    drawer_heights=_dh_list_box,
                ))

        # Samostojeći šporet — nema fronta ni korpusa u ovoj aplikaciji
        elif tid == "BASE_OVEN_HOB_FREESTANDING":
            _LOG.debug("Skipping fronts for freestanding cooker module id=%s", mid)

        # BASE_HOB — ploča za kuvanje je uređaj na radnoj ploči; ispod ide standardni ormar sa vratima
        elif "HOB" in tid:
            num_d_hob = 2 if w > 500 else 1
            door_w_hob = (fw - front_gap) / num_d_hob if num_d_hob > 1 else fw
            door_h_hob = h - 2 * front_gap
            rows_fronts.append(fr(
                "Vrata (ispod ploče za kuvanje)", door_w_hob, door_h_hob, kol_=num_d_hob,
                nap_="Ploča za kuvanje se nabavlja posebno; ispod je standardni bazni ormar bez police"
            ))

        # BASE_TRASH — izvlačni sortirnik sa jednom frontom na mehanizmu
        elif "TRASH" in tid:
            rows_fronts.append(fr(
                "Front sortirnika", fw, h - 2 * front_gap, kol_=1,
                nap_="Jedna fronta na izvlačnom sistemu za kante"
            ))

        # TALL_OVEN — appliance kolona sa donjim servisnim frontom
        elif tid == "TALL_OVEN":
            _service_front_h = max(120.0, min(360.0, h * 0.18) - 2 * front_gap)
            rows_fronts.append(fr(
                "Donji servisni front", fw, _service_front_h, kol_=1,
                nap_="Kolona za ugradnu rernu; gornju appliance zonu zatvara sam uređaj, a ovaj front pokriva donji servisni / skladišni prostor"
            ))

        # TALL_OVEN_MICRO — appliance kolona sa donjim servisnim frontom
        elif tid == "TALL_OVEN_MICRO":
            _service_front_h = max(120.0, min(320.0, h * 0.16) - 2 * front_gap)
            rows_fronts.append(fr(
                "Donji servisni front", fw, _service_front_h, kol_=1,
                nap_="Kolona za ugradnu mikrotalasnu i rernu; appliance zone zatvaraju uređaji, a ovaj front pokriva donji servisni / skladišni prostor"
            ))

        # Rerna (BASE_OVEN) — ima vrata
        elif "OVEN" in tid:
            oven_door_h = h - 2 * front_gap
            rows_fronts.append(fr("Vrata rerne", fw, oven_door_h))

        # Aspirator/napa
        elif "HOOD" in tid:
            _LOG.debug("Skipping fronts for hood module id=%s", mid)

        # Sudopera — vrata ispod
        elif "SINK" in tid:
            door_h = h - 2 * front_gap
            num_d = 2 if w > 600 else 1
            door_w2 = (fw - front_gap) / num_d if num_d > 1 else fw
            rows_fronts.append(fr("Vrata (ispod sudopere)", door_w2, door_h, kol_=num_d))

        # ── Ugradna mašina za sudove ──────────────────────────────────────────
        # Nema sopstveni korpus — bočne ploče obezbeđuju susedni elementi.
        # Jedina korpusna ploča: VEZNA LETVA (gornji vez ispod radne ploče).
        # Opciono: integrisani front panel.
        elif tid == "BASE_DISHWASHER":
            # 1. Vezna letva — jedina ploča MZS slota
            #    Širina  = širina slota (w), dubina = 100mm, debljina = carcass_thk
            #    Kant    = samo prednja ivica (L1, frontalna strana)
            _VEZNA_H = 100.0   # standardna visina/dubina vezne letve [mm]
            rows_carcass.append(_cp(
                mid, zone, label,
                "Vezna letva — MZS (ugradna)",
                w,           # CUT_W = puna širina slota
                _VEZNA_H,    # CUT_H = dubina letve (front-back)
                n_ew=0, n_eh=1,   # 1 kant na H smeru = prednja (F) ivica
                orient="horizontalna",
                L1=1, L2=0, K1=0, K2=0,
                nap="Gornji vez ugradne MZS — prednja ivica kantovana; "
                    "oslanja se na susedne korpuse",
                _mlbl=modul_label,
            ))
            # 2. Front panel (integrisana MZS — vrata u ravni sa ostalim frontovima)
            rows_fronts.append(fr(
                "Front — mašina za sudove",
                fw, h - 2 * front_gap,
                nap_="Integrisani front ugradne MZS",
            ))

        # Pantry/ostava
        elif "PANTRY" in tid:
            num_d = 2 if w > 500 else 1
            door_w3 = (fw - front_gap) / num_d if num_d > 1 else fw
            door_h3 = h - 2 * front_gap
            rows_fronts.append(fr("Vrata", door_w3, door_h3, kol_=num_d))

        # Integrisani frižider — ima appliance front/frontove
        elif tid == "TALL_FRIDGE":
            rows_fronts.append(fr(
                "Front integrisanog frižidera", fw, h - 2 * front_gap, kol_=1,
                nap_="Front se vezuje na vrata ugradnog frižidera prema fabričkom setu"
            ))

        elif tid == "TALL_FRIDGE_FREEZER":
            upper_h = (h * 0.60) - 2 * front_gap
            lower_h = (h * 0.40) - 2 * front_gap
            rows_fronts.append(fr(
                "Gornji front frižidera", fw, upper_h, kol_=1,
                nap_="Gornji appliance front za integrisani frižider/zamrzivač"
            ))
            rows_fronts.append(fr(
                "Donji front zamrzivača", fw, lower_h, kol_=1,
                nap_="Donji appliance front za integrisani frižider/zamrzivač"
            ))

        # Samostojeći frižider — bez fronta
        elif tid == "TALL_FRIDGE_FREESTANDING":
            _LOG.debug("Skipping fronts for freestanding fridge module id=%s", mid)

        # Otvoreni elementi — nema fronta
        elif "OPEN" in tid:
            _LOG.debug("Skipping fronts for open module id=%s", mid)

    # -------------------------------------------------------
    # FAZA D: SOKLA (plinth)
    # -------------------------------------------------------
    rows_plinth: List[Dict[str, Any]] = []
    foot_h = int(kitchen.get("foot_height_mm", 100))
    base_mods = [m for m in modules if str(m.get("zone", "")).lower().strip() == "base"]
    _base_by_wall: Dict[str, List[Dict[str, Any]]] = {}
    for _bm in base_mods:
        _bwk = str(_bm.get("wall_key", "A") or "A").upper()
        _base_by_wall.setdefault(_bwk, []).append(_bm)
    if base_mods and foot_h > 0:
        for _bwk, _bmods in sorted(_base_by_wall.items()):
            x0 = min(int(m.get("x_mm", 0)) for m in _bmods)
            x1 = max(int(m.get("x_mm", 0)) + int(m.get("w_mm", 0)) for m in _bmods)
            rows_plinth.append({
                "ID":          "-",
                "Modul":       f"Sokla - Zid {_bwk}",
                "Zid":         f"Zid {_bwk}",
                "Deo":         "Sokla (lajsna)",
                "Materijal":   "MDF",
                "Deb. [mm]":   16,
                "Duzina [mm]": x1 - x0,
                "Visina [mm]": foot_h,
                "Kol.":        1,
                "Napomena":    f"Segment zida {_bwk}, raspon {x0}–{x1}mm",
            })

    # -------------------------------------------------------
    # Radna ploca — jedan segment
    # -------------------------------------------------------
    rows_worktop: List[Dict[str, Any]] = []
    wt = kitchen.get("worktop", {}) or {}
    wt_thk_mm = int(round(float(wt.get("thickness", 0.0)) * 10.0))
    if wt_thk_mm > 0:
        if base_mods:
            wt_depth = float(wt.get("width", 600.0))
            _is_l_kitchen = str((kitchen or {}).get("kitchen_layout", "")) == "l_oblik"
            for _bwk, _bmods in sorted(_base_by_wall.items()):
                xs = [int(m.get("x_mm", 0)) for m in _bmods]
                xe = [int(m.get("x_mm", 0)) + int(m.get("w_mm", 0)) for m in _bmods]
                total_wt_w = max(xe) - min(xs)
                _x_start = min(xs)
                # Napomena za ugaono spajanje radne ploče u L-kuhinji
                if _is_l_kitchen and _bwk != "A":
                    from layout_engine import _l_corner_offsets_mm as _co_off
                    _lo, _ro = _co_off(kitchen, _bwk)
                    if _lo > 0:
                        _wt_note = (
                            f"Zid {_bwk} — radna ploča počinje na x={_x_start}mm. "
                            f"Ugaono spajanje s Zidom A: rezati/stepenasto obradi lijevu stranu "
                            f"({_lo}mm dubine Zida A). Dužina segmenta: {total_wt_w}mm."
                        )
                    elif _ro > 0:
                        _wt_note = (
                            f"Zid {_bwk} — radna ploča dužine {total_wt_w}mm. "
                            f"Ugaono spajanje s Zidom A: rezati/stepenasto obradi desnu stranu "
                            f"({_ro}mm dubine Zida A)."
                        )
                    else:
                        _wt_note = f"1 segment na zidu {_bwk}, ukupna dužina base zone {total_wt_w}mm"
                else:
                    _wt_note = f"1 segment na zidu {_bwk}, ukupna dužina base zone {total_wt_w}mm"
                rows_worktop.append({
                    "ID":           "-",
                    "Modul":        f"Radna ploča - Zid {_bwk}",
                    "Zid":          f"Zid {_bwk}",
                    "Deo":          "Radna ploča",
                    "Materijal":    wt.get("material", "Radna ploča"),
                    "Deb.":         wt_thk_mm,
                    "Kol.":         1,
                    "Kant":         "-",
                    "L1": 1, "L2": 0, "K1": 0, "K2": 0,
                    "Orijentacija": "horizontalna",
                    "Duzina [mm]":  float(total_wt_w),
                    "Sirina [mm]":  float(wt_depth),
                    "CUT_W [mm]":   float(total_wt_w),
                    "CUT_H [mm]":   float(wt_depth),
                    "Napomena":     _wt_note,
                })
            # Nosači radne ploče: 2 daske po BASE elementu (100mm × širina_elementa × carcass_thk)
            # Služe za pričvršćivanje radne ploče na gornji deo korpusa
            # DISHWASHER — nema korpus; gornji vez (vezna letva) dodat posebno u carcass
            _NO_NOSAC_KW = ("DISHWASHER",)
            for _bm in base_mods:
                _bm_tid = str(_bm.get("template_id", "")).upper()
                if any(_kw in _bm_tid for _kw in _NO_NOSAC_KW):
                    continue
                _bw = int(_bm.get("w_mm", 600))
                _blbl = str(_bm.get("label", ""))
                _nosac_w = float(_bw) - 2 * carcass_thk  # unutrašnja širina
                _nosac_h = 96.0  # standardna visina nosača radne ploče
                rows_worktop.append({
                    "ID":           int(_bm.get("id", 0)),
                    "Modul":        _blbl,
                    "Deo":          "Nosač radne ploče",
                    "Materijal":    carcass_mat,
                    "Deb.":         carcass_thk,
                    "Kol.":         2,
                    "Kant":         "F (ABS 0.5mm)",
                    "L1": 1, "L2": 0, "K1": 0, "K2": 0,
                    "Orijentacija": "horizontalna",
                    "Duzina [mm]":  _nosac_w,
                    "Sirina [mm]":  _nosac_h,
                    "CUT_W [mm]":   _nosac_w + edge_thk,
                    "CUT_H [mm]":   _nosac_h,
                    "Napomena":     "Gornji vez — pričvršćuje radnu ploču (prednja ivica kantovana)",
                })

    # -------------------------------------------------------
    # FAZA F: OKOVI (šarke, klizači, liftup mehanizmi)
    # Kalkulacija po tipu elementa i visini vrata:
    #   ≤ 900mm  → 2 šarke/vrata
    #   901–1200 → 3 šarke/vrata
    #   > 1200   → 4 šarke/vrata
    # -------------------------------------------------------
    rows_hardware: List[Dict[str, Any]] = []

    def _hw(
        mid_: int, zone_: str, lbl_: str, naziv: str, tip: str, kol: int,
        nap: str = "", kategorija: str = "okov",
    ) -> Dict[str, Any]:
        return {
            "ID":        mid_,
            "TYPE":      zone_.upper(),
            "Modul":     lbl_,
            "Kategorija": kategorija,
            "Naziv":     naziv,
            "Tip / Šifra": tip,
            "Kol.":      kol,
            "Napomena":  nap,
        }

    # Aparati bez okova — preskačemo
    _NO_HW = ()

    for _hm in modules:
        _hmid   = int(_hm.get("id", 0))
        _hzone  = str(_hm.get("zone", "base")).lower()
        _hlbl   = str(_hm.get("label", ""))
        _htid   = str(_hm.get("template_id", "") or "").upper()
        _hh     = float(_hm.get("h_mm", 720))
        _hw_mm  = float(_hm.get("w_mm", 600))
        _hp     = _hm.get("params") or {}
        _hmlbl  = _hlbl or _htid

        if _htid in _PANEL_ONLY_TIDS:
            _panel_qty = 4 if _htid == "FILLER_PANEL" else 6
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Vijak / spojnica za panel",
                "4x30 mm",
                _panel_qty,
                "Za pričvršćenje dekorativnog panela uz susjedni korpus ili zidnu letvu",
                kategorija="potrosni",
            ))
            continue

        if any(_k in _htid for _k in _NO_HW):
            continue

        _is_liftup   = "LIFTUP" in _htid
        _is_drawer_m = "DRAWER" in _htid and "DOOR" not in _htid
        _is_trash_m  = "TRASH" in _htid
        _is_hob_m    = "HOB" in _htid
        _is_hood_m   = "HOOD" in _htid
        _is_micro_m  = "MICRO" in _htid
        _is_narrow_m = "BASE_NARROW" in _htid
        _is_wall_narrow_m = "WALL_NARROW" in _htid
        _is_glass_m  = "GLASS" in _htid
        _is_cooking_m = _htid in {"BASE_COOKING_UNIT", "OVEN_HOB"}
        _is_fridge_tall_m = _htid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER"}
        _is_freestanding_fridge_m = _htid == "TALL_FRIDGE_FREESTANDING"
        _is_freestanding_dish_m = _htid == "BASE_DISHWASHER_FREESTANDING"
        _is_freestanding_cooker_m = _htid == "BASE_OVEN_HOB_FREESTANDING"
        _is_tall_oven_m = _htid in {"TALL_OVEN", "TALL_OVEN_MICRO"}
        _is_open_m   = any(_k in _htid for k in ("OPEN", "GLASS", "NARROW") for _k in [k])
        _is_door_m   = (
            (any(_k in _htid for _k in ("DOOR", "PANTRY", "SINK", "OVEN")) or _is_hob_m)
            and not _is_drawer_m
            and not _is_open_m
        )
        _is_dishw    = _htid == "BASE_DISHWASHER"
        _is_ddraw    = "DOORS_DRAWERS" in _htid  # kombi: vrata + fioka
        _is_wardrobe_sliding  = "WARDROBE" in _htid and "SLIDING" in _htid
        _is_wardrobe_american = _htid == "TALL_WARDROBE_AMERICAN"
        _is_wardrobe_hang     = _htid == "TALL_WARDROBE_INT_HANG"

        # ── Liftup mehanizam ────────────────────────────────
        if _is_liftup:
            _pair_cnt = 1 if _hw_mm <= 1000 else 2
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Lift-up mehanizam",
                hwc.get("liftup", ""),
                _pair_cnt,
                f"Liftup vrata š={_hw_mm:.0f} × v={_hh:.0f}mm",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Nosač / vijci za lift-up front",
                "Set za montažu fronta",
                1,
                "Prateći montažni set uz lift-up mehanizam",
                kategorija="potrosni",
            ))

        # ── Klizači za fioke ─────────────────────────────────
        elif _is_drawer_m:
            _n_dr = max(1, int(_hp.get("n_drawers", 3 if _hh > 600 else 2)))
            _dh_list = _hp.get("drawer_heights")
            if _dh_list:
                _n_dr = len(_dh_list)
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Klizač za fioku",
                hwc.get("slide", ""),
                _n_dr,
                f"{_n_dr} × 1 par klizača (lijevi + desni)",
            ))

        elif _is_trash_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Izvlačni mehanizam sortirnika",
                "Sortirnik / pull-out set",
                1,
                "Komplet klizača/nosača za kante za otpad",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Kante za otpad",
                "2x kanta + nosac",
                1,
                "Kupuje se kao gotov set; ne izrađuje se iz pločastog materijala",
            ))

        elif _is_cooking_m:
            if _hp.get("has_drawer", True):
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Klizač za fioku",
                    hwc.get("slide", ""),
                    1,
                    "1 fioka ispod rerne × 1 par klizača",
                ))
            if _hp.get("has_drawer", True):
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Nosač fronta fioke",
                    "Set nosača / ugaonika",
                    1,
                    "Za front fioke ispod rerne",
                ))

        elif _is_fridge_tall_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Ventilaciona rešetka / set",
                "Ulaz/izlaz vazduha",
                1,
                "Obezbediti propisan dovod i odvod vazduha za rashladni uređaj",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Set za vezu appliance fronta",
                "Klizni / door-on-door set",
                2 if _htid == "TALL_FRIDGE_FREEZER" else 1,
                "Set za spajanje fronta/frontova sa vratima integrisanog uređaja",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Anti-tip set",
                "Zidni ugaonik / traka",
                1,
                "Obavezno učvršćenje visoke kolone za zid zbog bezbednosti",
                kategorija="potrosni",
            ))

        elif _is_tall_oven_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Ventilacioni razmak / maska",
                "Distancer / ventilacioni set",
                1,
                "Za appliance kolonu i zaštitu od pregrevanja uređaja",
            ))

        elif "SINK" in _htid:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Sudopera",
                "Ugradna sudopera",
                1,
                "Kupuje se kao gotov proizvod; otvor se reže u radnoj ploči prema šablonu",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Sifon i odvodni set",
                "Sifon + preliv + spojnice",
                1,
                "Kupovni vodoinstalaterski set za sudoperu",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Slavina",
                "Baterija za sudoperu",
                1,
                "Kupuje se posebno prema izboru korisnika",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Sanitarni silikon",
                "Transparentni / sivi",
                1,
                "Za zaptivanje ruba sudopere i spojeva uz radnu ploču",
                kategorija="potrosni",
            ))

        elif _is_freestanding_dish_m:
            continue

        elif _is_freestanding_cooker_m:
            continue

        elif _is_freestanding_fridge_m:
            continue

        elif _is_narrow_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Uski izvlačni mehanizam",
                "Bottle pull-out / cargo set",
                1,
                "Gotov uski izvlačni program za flaše, ulja i začine",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Korpe / nosači uskog izvlačnog modula",
                "2 nivoa / set",
                1,
                "Kupuje se kao gotov set; broj i tip korpi proveriti prema širini modula",
            ))

        elif _is_wall_narrow_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka (CLIP-top 110°)",
                hwc.get("hinge", ""),
                2,
                "Uski zidni element sa jednim krilom",
            ))

        elif _is_glass_m:
            _n_vrata_gl = 2 if _hw_mm > 450 else 1
            _dh_gl = _hh - 4.0
            _sharke_gl = _hinges_per_door(_dh_gl)
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka za staklena vrata",
                hwc.get("hinge", ""),
                _n_vrata_gl * _sharke_gl,
                f"{_n_vrata_gl} staklena vrata × {_sharke_gl} šarki; proveriti tačan tip prema sistemu vitrine",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Magnetni zatvarač vitrine",
                "Magnet / odbojnik",
                1 if _n_vrata_gl == 1 else 2,
                "Za mekše naleganje i sigurno zatvaranje staklenih vrata",
            ))

        elif _is_wardrobe_sliding or _is_wardrobe_american:
            # ── Klizni sistem za orman (klizna vrata) ──────────────────────────
            _n_panels = 3 if _is_wardrobe_american else 2
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Klizni sistem vrata (gornja sina + donja vodilica)",
                hwc.get("sliding_track", "Klizni sistem kliznih vrata"),
                1,
                f"Komplet za {_n_panels} klizna krila; duzina sine = sirina otvora + preklapanje",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Set tockica / nosaca kliznih krila",
                "2 gornja + 2 donja tockica po krilu",
                _n_panels,
                f"{_n_panels} seta (1 set po krilu = 4 tockica)",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Gumeni stop / krajnji odbojnik",
                "Odbojnik za kraj sine",
                2,
                "Na oba kraja sine — sprecava udar krila na krajnjoj poziciji",
                kategorija="potrosni",
            ))

        elif "CORNER" in _htid:
            _hinge_qty = 2 if _hzone == "wall" else 2
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka za ugaoni front",
                hwc.get("hinge", ""),
                _hinge_qty,
                "Osnovni set za ugaoni front; tačan tip i ugao proveriti prema izvedbi",
            ))

        elif _is_hood_m:
            continue

        elif _is_micro_m:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Ventilacioni distancer / razmak",
                "Distancer / resetka",
                1,
                "Za sigurnu ventilaciju i provod kabla kod ugradne mikrotalasne",
                kategorija="potrosni",
            ))

        # ── Šarke za vrata ───────────────────────────────────
        elif _is_door_m:
            _n_vrata = 2 if (_hw_mm > 500 and "1DOOR" not in _htid) else 1
            if "SINK" in _htid:
                _n_vrata = 2 if _hw_mm > 600 else 1
            # Visina vrata ≈ visina modula (front gap ~4mm obostrano)
            _dh = _hh - 4.0
            _sharke_po = _hinges_per_door(_dh)
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka (CLIP-top 110°)",
                hwc.get("hinge", ""),
                _n_vrata * _sharke_po,
                f"{_n_vrata} vrata × {_sharke_po} sarke (v vrata={_dh:.0f}mm); busenje: O35mm dubina 13mm, 22.5mm od ruba vrata",
            ))

        # ── Kombi: vrata + fioka ─────────────────────────────
        if _is_ddraw:
            # Šarke za donja vrata
            _dh2 = _hh * 0.72 - 4.0
            _sharke2 = _hinges_per_door(_dh2)
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka (CLIP-top 110°)",
                hwc.get("hinge", ""),
                _sharke2,
                f"Vrata donjeg dijela (v={_dh2:.0f}mm)",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Klizač za fioku",
                hwc.get("slide", ""),
                1,
                "1 fioka × 1 par klizača",
            ))

        # ── Klizač za fioku BASE_DOOR_DRAWER (šarke su dodane via _is_door_m) ──
        if "DOOR_DRAWER" in _htid:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Klizač za fioku",
                hwc.get("slide", ""),
                1,
                "1 fioka (vrata + fioka kombi)",
            ))

        # ── Šarke za integrisanu MZS (ugradnu mašinu za sudove) ─
        if _is_dishw:
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Šarka za front MZS",
                hwc.get("dish_hinge", ""),
                2,
                "Integrisani front ugradne mašine za sudove",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Montažni set za front MZS",
                "Nosači + vijci + šablon",
                1,
                "Prateći set za vezu fronta sa vratima mašine",
                kategorija="potrosni",
            ))

        # ── Vešalica (sipka za vesanje odece) — wardrobe hang sekcija ───────
        if _is_wardrobe_hang:
            _n_sip = int(_hp.get("hanger_sections", 1))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Sipka za vesanje odece",
                hwc.get("hanging_rod", "Okrugla sipka O25mm + par nosaca"),
                _n_sip,
                f"{_n_sip} sipka/e × 1 par nosaca; duzina = sirina sekcije - 5mm",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Nosaci sipke za vesanje",
                "Ugradbeni nosac O25mm",
                _n_sip * 2,
                f"{_n_sip} sipke × 2 nosaca = {_n_sip * 2} kom ukupno",
            ))

        # ── Ručke / pulls ────────────────────────────────────────────────
        # Svaki front (vrata, front fioke, liftup) dobija jednu ručku.
        # MZS i napa (bez kabinet fronta) ne dobijaju ručku.
        # BASE_HOB ima vrata ispod ploče za kuvanje — dobija ručke normalno (_is_hob_m se ne isključuje ovde).
        if not _skip_carcass and not _is_dishw and not _is_hood_m:
            _n_handles = 0
            if _is_liftup:
                _n_handles = 1
            elif _is_drawer_m:
                _n_dr_rucke = max(1, int(_hp.get("n_drawers", 3 if _hh > 600 else 2)))
                if _hp.get("drawer_heights"):
                    _n_dr_rucke = len(_hp.get("drawer_heights"))
                _n_handles = _n_dr_rucke
            elif _is_glass_m:
                _n_handles = 2 if _hw_mm > 450 else 1
            elif _is_wardrobe_sliding or _is_wardrobe_american:
                # Svako klizno krilo dobija 1 ručku (J-pull ili lajsna)
                _n_handles = 3 if _is_wardrobe_american else 2
            elif _is_door_m:
                if "DOOR_DRAWER" in _htid:
                    _n_handles = 1  # uvek 1 vrata (gornji deo kombinovanog elem.)
                else:
                    _n_handles = 2 if (_hw_mm > 500 and "1DOOR" not in _htid) else 1
                    if "SINK" in _htid:
                        _n_handles = 2 if _hw_mm > 600 else 1
            if _is_ddraw:
                _n_handles += 2  # donja vrata + front fioke
            elif "DOOR_DRAWER" in _htid:
                _n_handles += 1  # front fioke (vrata je vec u _is_door_m)
            if _n_handles > 0:
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Ručka / pull",
                    hwc.get("handle", "Po izboru korisnika"),
                    _n_handles,
                    f"{_n_handles} × 1 ručka — odabrati po projektu",
                ))

        # ── Bazni montažni potrošni materijal (po modulu) ─────────────────
        # Dodajemo za sve module koji imaju korpus (nije sam uređaj).
        if not _skip_carcass and not any(_kw in _htid for _kw in ("DISHWASHER",)):
            _n_shelves = int((_hp.get("n_shelves", 0) or 0))
            if _n_shelves <= 0:
                if "PANTRY" in _htid or "TALL_OPEN" in _htid:
                    _n_shelves = 4
                elif "WALL_UPPER_OPEN" in _htid or "TALL_TOP_OPEN" in _htid:
                    _n_shelves = 1
                elif "OPEN" in _htid or "GLASS" in _htid:
                    _n_shelves = 2
            _conf_qty = 20 if _hzone == "tall" else 16
            _dowel_qty = 12 if _hzone == "tall" else 8
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Konfirmat vijak",
                hwc.get("confirmat", ""),
                _conf_qty,
                "Standardno za spoj korpusa (bočne+dno+plafon)",
                kategorija="potrosni",
            ))
            rows_hardware.append(_hw(
                _hmid, _hzone, _hmlbl,
                "Drvena tipla",
                hwc.get("dowel", ""),
                _dowel_qty,
                "Pomoćni spoj i poravnanje",
                kategorija="potrosni",
            ))
            if _n_shelves > 0:
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Nosač police (klin)",
                    hwc.get("shelf_pin", ""),
                    _n_shelves * 4,
                    f"{_n_shelves} polica × 4 klina",
                ))
            if _hzone in ("base", "tall"):
                _legs = 6 if _hw_mm >= 900 else 4
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Stopica (nogica)",
                    hwc.get("leg", ""),
                    _legs,
                    "Osnovni set po elementu",
                ))
            if _hzone in ("wall", "wall_upper"):
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Zidni nosac elementa",
                    hwc.get("hang_rail", ""),
                    1,
                    "Set za kačenje visećeg elementa",
                ))
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Anker za zid",
                    hwc.get("wall_anchor", ""),
                    2 if _hw_mm <= 800 else 3,
                    "Preporučena količina po modulu",
                    kategorija="potrosni",
                ))
            if _hzone == "tall" and not (_is_fridge_tall_m or _is_tall_oven_m or _is_freestanding_fridge_m):
                rows_hardware.append(_hw(
                    _hmid, _hzone, _hmlbl,
                    "Anti-tip set",
                    hwc.get("anti_tip", "Anti-tip ugaonik / traka"),
                    1,
                    "Preporučeno učvršćenje visokog elementa za zid zbog bezbednosti",
                    kategorija="potrosni",
                ))

    # Projektni potrosni materijal koji se ne vidi uvek na nivou jednog elementa.
    _mods_by_wall = {}
    for _m in modules:
        _wk = str(_m.get("wall_key", "A") or "A").upper()
        _mods_by_wall.setdefault(_wk, []).append(_m)

    _connector_pairs = 0
    for _wk, _mods in _mods_by_wall.items():
        for _zone_key in ("base", "wall", "wall_upper", "tall", "tall_top"):
            _zone_mods = [
                _m for _m in _mods
                if str(_m.get("zone", "")).lower() == _zone_key
                and "FREESTANDING" not in str(_m.get("template_id", "")).upper()
                and str(_m.get("template_id", "")).upper() != "BASE_DISHWASHER"
            ]
            _zone_mods.sort(key=lambda _m: (int(_m.get("x_mm", 0)), int(_m.get("id", 0))))
            for _i in range(len(_zone_mods) - 1):
                _a = _zone_mods[_i]
                _b = _zone_mods[_i + 1]
                _a_end = int(_a.get("x_mm", 0)) + int(_a.get("w_mm", 0)) + int(_a.get("gap_after_mm", 0))
                _b_x = int(_b.get("x_mm", 0))
                if abs(_a_end - _b_x) <= 2:
                    _connector_pairs += 1

    if _connector_pairs > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Spojnica susednih korpusa",
            hwc.get("cabinet_connector", "Spojnica korpusa + vijak"),
            _connector_pairs * 2,
            "Osnovno 2 spojnice po spoju susednih korpusa u istoj zoni",
            kategorija="potrosni",
        ))

    _base_tall_mods = [
        _m for _m in modules
        if str(_m.get("zone", "")).lower() in ("base", "tall")
        and "FREESTANDING" not in str(_m.get("template_id", "")).upper()
        and str(_m.get("template_id", "")).upper() != "BASE_DISHWASHER"
    ]
    _leg_total = 0
    for _m in _base_tall_mods:
        _mw = float(_m.get("w_mm", 600) or 600)
        _leg_total += 6 if _mw >= 900 else 4
    if _leg_total > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Klipsa za soklu",
            hwc.get("plinth_clip", "Klipsa za soklu"),
            _leg_total,
            "Po jedna klipsa po stopici za prihvat sokle",
            kategorija="potrosni",
        ))

    if rows_worktop:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak / ugaonik za radnu plocu",
            hwc.get("worktop_fix", "Vijak / ugaonik za radnu plocu"),
            max(4, len(base_mods) * 2),
            "Osnovni set za pricvrscenje radne ploce na nosace i korpuse",
            kategorija="potrosni",
        ))
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Zaptivna lajsna / silikon uz zid",
            "Zidna lajsna ili sanitarni silikon",
            1,
            "Zavrsno zaptivanje spoja radne ploce prema zidu po izboru korisnika",
            kategorija="potrosni",
        ))

    _total_hinge_units = sum(
        int(_r.get("Kol.", 0) or 0)
        for _r in rows_hardware
        if "Šarka" in str(_r.get("Naziv", "")) or "Sarka" in str(_r.get("Naziv", ""))
    )
    if _total_hinge_units > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak za sarku",
            hwc.get("hinge_screw", "3.5x16 mm"),
            _total_hinge_units * 8,
            "Osnovno 8 vijaka po sarki ako nisu ukljuceni u set",
            kategorija="potrosni",
        ))

    _total_slide_pairs = sum(
        int(_r.get("Kol.", 0) or 0)
        for _r in rows_hardware
        if str(_r.get("Naziv", "")) == "Klizač za fioku"
    )
    if _total_slide_pairs > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak za klizac",
            hwc.get("slide_screw", "3.5x16 mm"),
            _total_slide_pairs * 12,
            "Osnovno 12 vijaka po paru klizaca ako nisu ukljuceni u set",
            kategorija="potrosni",
        ))

    _back_fix_qty = 0
    for _row in rows_backs:
        try:
            _back_fix_qty += int(_row.get("Kol.", 0) or 0) * 20
        except Exception:
            continue
    if _back_fix_qty > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak / ekser za ledja",
            hwc.get("back_fix", "3x16 mm / ekser 1.4x25 mm"),
            _back_fix_qty,
            "Osnovno pricvrscenje ledja po korpusu; broj proveriti prema standardu radionice",
            kategorija="potrosni",
        ))

    _wall_mount_modules = [
        _m for _m in modules
        if str(_m.get("zone", "")).lower() in ("wall", "wall_upper", "tall")
        and "FREESTANDING" not in str(_m.get("template_id", "")).upper()
    ]
    if _wall_mount_modules:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak za zidni nosac / sinu",
            hwc.get("wall_mount_screw", "5x60 mm"),
            len(_wall_mount_modules) * 4,
            "Za pricvrscenje nosaca, sine ili anti-tip seta; tip vijka prilagoditi zidu",
            kategorija="potrosni",
        ))

    # ── Montažne ploče za šarke (samo BLUM CLIP-top sistem) ───────────────
    # Svaka šarka zahteva posebnu montažnu ploču (prodaje se odvojeno)
    _hinge_plate_brand = hwc.get("hinge_plate", "")
    if _hinge_plate_brand:
        _total_hinges_for_plate = sum(
            int(_r.get("Kol.", 0) or 0)
            for _r in rows_hardware
            if "arka" in str(_r.get("Naziv", ""))
            and str(_r.get("ID", 0)) != "0"   # preskoci projektne redove
        )
        if _total_hinges_for_plate > 0:
            rows_hardware.append(_hw(
                0, "project", "Projekat",
                "Montazna ploca za sarku",
                _hinge_plate_brand,
                _total_hinges_for_plate,
                "1 montazna ploca po sarki (BLUM CLIP-top sistem: ploca + sarki odvojeni)",
            ))

    # ── Vijci za ručke ─────────────────────────────────────────────────────
    # Svaka ručka se montira sa 2 vijka M4 kroz vrata/front fioke.
    _total_handles_proj = sum(
        int(_r.get("Kol.", 0) or 0)
        for _r in rows_hardware
        if "pull" in str(_r.get("Naziv", "")).lower()
        and str(_r.get("ID", 0)) != "0"
    )
    if _total_handles_proj > 0:
        rows_hardware.append(_hw(
            0, "project", "Projekat",
            "Vijak za rucku",
            hwc.get("handle_screw", "M4 x 50mm vijak za rucku"),
            _total_handles_proj * 2,
            "2 vijka M4 po rucki; duzinu vijka prilagoditi debljini fronta",
            kategorija="potrosni",
        ))

    # Manufacturing warnings (dimenzije, preklapanja, montažni rizici)
    wall_h_mm = float((kitchen.get("wall", {}) or {}).get("height_mm", 2600) or 2600)
    foot_h_mm = float(kitchen.get("foot_height_mm", 100) or 100)
    rows_hardware.extend(_manufacturing_warnings(
        modules,
        kitchen=kitchen,
        wall_h_mm=wall_h_mm,
        foot_h_mm=foot_h_mm,
        front_gap_mm=front_gap,
    ))
    _sections = {
        "carcass":       pd.DataFrame(rows_carcass),
        "backs":         pd.DataFrame(rows_backs),
        "fronts":        pd.DataFrame(rows_fronts),
        "drawer_boxes":  pd.DataFrame(rows_drawer_boxes),
        "worktop":       pd.DataFrame(rows_worktop),
        "plinth":        pd.DataFrame(rows_plinth),
        "hardware":      pd.DataFrame(rows_hardware),
    }
    # Production-friendly numeracija i pozicije po svim sekcijama.
    for _skey, _sdf in list(_sections.items()):
        _sections[_skey] = _attach_wall_column(_annotate_parts(_sdf, _skey), modules)
    return _sections


# --- Compatibility: main.py у неким варијантама очекује овај назив ---
def build_cutlist_sections(kitchen: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """Compatibility wrapper: alias за generate_cutlist()."""
    return generate_cutlist(kitchen)


def build_project_header(kitchen: Dict[str, Any]) -> pd.DataFrame:
    """Project header for workshop / end-user packet."""
    wall = kitchen.get("wall", {}) or {}
    meta = kitchen.get("project", {}) or {}
    room = str(meta.get("room", "") or kitchen.get("room_name", "") or "Kuhinja")
    project_name = str(meta.get("name", "") or kitchen.get("project_name", "") or "Krojna Lista PRO")
    version = str(meta.get("version", "") or kitchen.get("version", "") or "v1")
    customer = str(meta.get("customer", "") or kitchen.get("customer_name", "") or "-")
    wall_name = str(meta.get("wall_name", "") or wall.get("name", "") or "Zid A")
    measured_by = str(meta.get("measured_by", "") or "-")
    designed_by = str(meta.get("designed_by", "") or "-")
    workshop_note = str(
        meta.get("workshop_note", "")
        or "U servisu raditi secenje i kantovanje po CUT merama. Otvore i posebne obrade proveriti po napomenama."
    )
    today = datetime.now().strftime("%d.%m.%Y %H:%M")

    return pd.DataFrame([
        {"Polje": "Projekat", "Vrednost": project_name},
        {"Polje": "Kupac", "Vrednost": customer},
        {"Polje": "Prostorija", "Vrednost": room},
        {"Polje": "Zid", "Vrednost": wall_name},
        {"Polje": "Mera zida", "Vrednost": f"{wall.get('length_mm', 0)} x {wall.get('height_mm', 0)} mm"},
        {"Polje": "Verzija", "Vrednost": version},
        {"Polje": "Generisano", "Vrednost": today},
        {"Polje": "Merio", "Vrednost": measured_by},
        {"Polje": "Crtano", "Vrednost": designed_by},
        {"Polje": "Napomena za servis", "Vrednost": workshop_note},
    ])


def build_service_packet(
    kitchen: Dict[str, Any],
    sections: Dict[str, pd.DataFrame] | None = None,
) -> Dict[str, pd.DataFrame]:
    """Workshop-oriented packet: cuts, edging, processing, shopping, checklist."""
    sections = sections or generate_cutlist(kitchen)
    packet: Dict[str, pd.DataFrame] = {}

    header_df = build_project_header(kitchen)
    packet["project_header"] = header_df

    board_frames = []
    for _key in ("carcass", "backs", "fronts", "drawer_boxes", "worktop", "plinth"):
        _df = sections.get(_key)
        if _df is not None and not _df.empty:
            board_frames.append(_df.copy())
    board_df = pd.concat(board_frames, ignore_index=True) if board_frames else pd.DataFrame()

    if not board_df.empty:
        for _col in ("Materijal", "Deb.", "CUT_W [mm]", "CUT_H [mm]", "Kol.", "Kant", "Napomena"):
            if _col not in board_df.columns:
                board_df[_col] = ""
        if "Zid" not in board_df.columns:
            board_df["Zid"] = ""

        service_cuts = (
            board_df.groupby(
                ["Zid", "Materijal", "Deb.", "CUT_W [mm]", "CUT_H [mm]", "Kant"],
                as_index=False,
            )
            .agg({"Kol.": "sum"})
            .sort_values(["Zid", "Materijal", "CUT_W [mm]", "CUT_H [mm]"], ascending=[True, True, False, False])
            .reset_index(drop=True)
        )
        service_cuts.insert(0, "RB", range(1, len(service_cuts) + 1))
        service_cuts["Napomena za servis"] = "U servisu seci po CUT merama i proveri kantovanje u posebnoj tabeli"
        packet["service_cuts"] = service_cuts

        edge_df = board_df[
            board_df["Kant"].astype(str).str.strip().replace("", "-") != "-"
        ].copy()
        if not edge_df.empty:
            edge_df = edge_df[[
                c for c in [
                    "PartCode", "Zid", "Modul", "Deo", "Kol.", "Materijal", "Deb.",
                    "CUT_W [mm]", "CUT_H [mm]", "Kant", "L1", "L2", "K1", "K2", "Napomena",
                ] if c in edge_df.columns
            ]]
            packet["service_edge"] = edge_df.reset_index(drop=True)

        def _proc_row(
            part: str,
            zid: str,
            modul: str,
            deo: str,
            cut_w: Any,
            cut_h: Any,
            kol: Any,
            tip: str,
            izvodi: str,
            osnov: str,
            nap: str,
        ) -> Dict[str, Any]:
            return {
                "PartCode": part,
                "Zid": zid,
                "Modul": modul,
                "Deo": deo,
                "CUT_W [mm]": cut_w,
                "CUT_H [mm]": cut_h,
                "Kol.": kol,
                "Tip obrade": tip,
                "Izvodi": izvodi,
                "Osnov izvođenja": osnov,
                "Obrada / napomena": nap,
            }

        proc_rows: list[dict[str, Any]] = []
        proc_mask = pd.Series(False, index=board_df.index)
        for _kw in ("otvor", "utor", "ventil", "kabl", "odvod", "dovod", "instal", "prolaz", "sudoper", "napa"):
            proc_mask = proc_mask | board_df["Napomena"].astype(str).str.lower().str.contains(_kw, na=False)
        proc_df = board_df[proc_mask].copy()
        if not proc_df.empty:
            for _r in proc_df.to_dict("records"):
                _nap = str(_r.get("Napomena", "") or "")
                _nap_l = _nap.lower()
                _tip = "Posebna obrada"
                _izv = "Servis"
                _osnov = "Po meri iz projekta"
                if "utor" in _nap_l:
                    _tip = "Utor za ledja"
                elif "sudoper" in _nap_l:
                    _tip = "Otvor za sudoperu"
                    _osnov = "Po šablonu proizvođača"
                elif "napa" in _nap_l or "ventil" in _nap_l:
                    _tip = "Ventilacija / otvor"
                    _osnov = "Po šablonu proizvođača"
                elif "kabl" in _nap_l:
                    _tip = "Prolaz za kabl"
                    _izv = "Kuća / lice mesta"
                elif "odvod" in _nap_l or "dovod" in _nap_l or "instal" in _nap_l:
                    _tip = "Instalacioni prolaz"
                    _izv = "Kuća / lice mesta"
                proc_rows.append(_proc_row(
                    str(_r.get("PartCode", "")),
                    str(_r.get("Zid", "")),
                    str(_r.get("Modul", "")),
                    str(_r.get("Deo", "")),
                    _r.get("CUT_W [mm]", ""),
                    _r.get("CUT_H [mm]", ""),
                    _r.get("Kol.", ""),
                    _tip,
                    _izv,
                    _osnov,
                    _nap,
                ))

        for _m in (kitchen.get("modules", []) or []):
            _tid = str((_m or {}).get("template_id", "")).upper()
            _mid = int((_m or {}).get("id", 0))
            _lbl = str((_m or {}).get("label", _tid) or _tid)
            _zid = f"Zid {str((_m or {}).get('wall_key', 'A') or 'A').upper()}"
            if _tid == "SINK_BASE":
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Radna ploca", "-", "-", 1,
                    "Otvor za sudoperu", "Servis", "Po šablonu proizvođača",
                    "Izrezati otvor za sudoperu u radnoj ploci prema sablonu proizvodjaca sudopere.",
                ))
            elif _tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Radna ploca", "-", "-", 1,
                    "Otvor za plocu", "Servis", "Po šablonu proizvođača",
                    "Izrezati otvor za plocu za kuvanje u radnoj ploci prema sablonu proizvodjaca.",
                ))
            elif _tid == "WALL_HOOD":
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Ledja / prolaz", "-", "-", 1,
                    "Ventilacija / otvor", "Servis", "Po šablonu proizvođača",
                    "Obezbediti otvor i prolaz za odvod nape prema modelu i osi instalacije.",
                ))
            elif _tid == "WALL_MICRO":
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Ledja / prolaz", "-", "-", 1,
                    "Prolaz za kabl", "Kuća / lice mesta", "Po šablonu proizvođača",
                    "Obezbediti prolaz za kabl i ventilacioni razmak za ugradnu mikrotalasnu.",
                ))
            elif _tid == "BASE_DISHWASHER":
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Zona prikljucka", "-", "-", 1,
                    "Instalacioni prolaz", "Kuća / lice mesta", "Po meri iz projekta",
                    "Proveriti prolaz creva i kabla za MZS bez konflikta sa korpusom i susednim elementima.",
                ))
            elif _tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER"}:
                proc_rows.append(_proc_row(
                    f"M{_mid:02d}", _zid, _lbl, "Ventilacija kolone", "-", "-", 1,
                    "Ventilacija / otvor", "Servis", "Po šablonu proizvođača",
                    "Obezbediti ulaz/izlaz vazduha za integrisani rashladni uredjaj prema preporuci proizvodjaca.",
                ))

        if proc_rows:
            proc_df = pd.DataFrame(proc_rows).drop_duplicates().reset_index(drop=True)
            packet["service_processing"] = proc_df

    hw_df = sections.get("hardware", pd.DataFrame())
    hw_df = hw_df.copy() if hw_df is not None else pd.DataFrame()
    if not hw_df.empty:
        shop_df = hw_df[hw_df["Kategorija"].astype(str).str.lower() != "warning"].copy()
        _ready_mask = pd.Series(False, index=shop_df.index)
        for _kw in (
            "frižider", "frizider", "rerna", "mikrotalas", "mašina za sudove", "masina za sudove",
            "sudopera", "slavina", "sifon", "napa", "aspirator", "ploča za kuvanje", "ploca za kuvanje",
        ):
            _ready_mask = _ready_mask | shop_df["Naziv"].astype(str).str.lower().str.contains(_kw, na=False)
        def _shopping_group(_row: pd.Series) -> str:
            _naziv = str(_row.get("Naziv", "")).lower()
            _kat = str(_row.get("Kategorija", "")).lower()
            _mod = str(_row.get("Modul", ""))
            if any(_kw in _naziv for _kw in ("zidni nosac", "anker za zid", "anti-tip", "zidni ")):
                return "Montaza na zid"
            if _mod == "Projekat":
                return "Projektni potrosni materijal"
            if _kat == "okov":
                return "Okovi i mehanizmi po elementu"
            if _kat == "potrosni":
                return "Sitni materijal po elementu"
            return "Kupuje se posebno"

        shop_df["Grupa"] = shop_df.apply(_shopping_group, axis=1)
        shop_df.loc[_ready_mask, "Grupa"] = "Kupuje se gotovo"
        shop_df = (
            shop_df.groupby(["Grupa", "Naziv", "Tip / Šifra"], as_index=False)
            .agg({"Kol.": "sum", "Napomena": "first"})
            .sort_values(["Grupa", "Naziv"])
            .reset_index(drop=True)
        )

        extra_rows = [
            {"Grupa": "Alat koji treba kod kuce", "Naziv": "Aku srafilica / odvijac", "Tip / Šifra": "-", "Kol.": 1,
             "Napomena": "Treba za sklapanje korpusa i montazu okova"},
            {"Grupa": "Alat koji treba kod kuce", "Naziv": "Metar + libela", "Tip / Šifra": "-", "Kol.": 1,
             "Napomena": "Treba za proveru mera, ravni i nivelacije"},
            {"Grupa": "Alat koji treba kod kuce", "Naziv": "Stege", "Tip / Šifra": "-", "Kol.": 2,
             "Napomena": "Pomazu da delovi ostanu poravnati tokom sklapanja"},
        ]
        if any(str((m or {}).get("zone", "")).lower() in ("wall", "wall_upper", "tall") for m in (kitchen.get("modules", []) or [])):
            extra_rows.append({
                "Grupa": "Za montazu na zid",
                "Naziv": "Tipli / ankeri za zid",
                "Tip / Šifra": "-",
                "Kol.": 1,
                "Napomena": "Izabrati prema tipu zida na licu mesta",
            })
        shop_df = pd.concat([shop_df, pd.DataFrame(extra_rows)], ignore_index=True)
        packet["shopping_list"] = shop_df
        ready_df = shop_df[shop_df["Grupa"].astype(str) == "Kupuje se gotovo"].copy()
        if not ready_df.empty:
            packet["ready_made_items"] = ready_df.reset_index(drop=True)

    packet["user_guide"] = pd.DataFrame([
        {"Korak": 1, "Sta radis": "Proveri projekat pre narucivanja", "Napomena": "Potvrdi zid, mere, verziju i da li je ovo poslednja izmena"},
        {"Korak": 2, "Sta radis": "U servis nosis samo secenje, kantovanje i obradu", "Napomena": "Servis koristi samo tabele iz servis paketa"},
        {"Korak": 3, "Sta radis": "Posebno kupujes gotove uredjaje, okove i alat", "Napomena": "To nije deo secenja i mora da se nabavi posebno"},
        {"Korak": 4, "Sta radis": "Kod kuce razvrstas delove po modulu", "Napomena": "Prvo odvoji korpuse, zatim frontove, pa okove"},
        {"Korak": 5, "Sta radis": "Prvo sklapas korpuse, pa vrata, fioke i uredjaje", "Napomena": "Visoke i zidne elemente obavezno pricvrsti za zid"},
    ])

    packet["workshop_checklist"] = pd.DataFrame([
        {"RB": 1, "Stavka": "Proveri da li su tacni materijal i debljine za korpus, front i ledja", "Status": ""},
        {"RB": 2, "Stavka": "Proveri da li su upisane sve CUT mere i broj komada", "Status": ""},
        {"RB": 3, "Stavka": "Proveri kantovanje po svakoj ivici pre predaje u servis", "Status": ""},
        {"RB": 4, "Stavka": "Proveri da li su ubaceni frontovi, ledja, sokla i posebni paneli", "Status": ""},
        {"RB": 5, "Stavka": "Proveri da li je sve sto se kupuje gotovo izdvojeno van secenja", "Status": ""},
        {"RB": 6, "Stavka": "Proveri sve otvore i posebne obrade za instalacije i ventilaciju", "Status": ""},
        {"RB": 7, "Stavka": "Proveri da shopping lista sadrzi okove, sitni materijal i alat", "Status": ""},
    ])
    packet["home_checklist"] = pd.DataFrame([
        {"RB": 1, "Stavka": "Prebroj sve isečene ploce i uporedi ih sa listom", "Status": ""},
        {"RB": 2, "Stavka": "Razvrstaj delove po elementu pre pocetka sklapanja", "Status": ""},
        {"RB": 3, "Stavka": "Proveri da li su kupljeni svi okovi, uredjaji i alat", "Status": ""},
        {"RB": 4, "Stavka": "Prvo sastavi korpuse, zatim vrata i fioke, pa tek onda uredjaje", "Status": ""},
        {"RB": 5, "Stavka": "Visoke i zidne elemente obavezno pricvrsti za zid", "Status": ""},
    ])

    packet["service_instructions"] = pd.DataFrame([
        {"RB": 1, "Stavka": "Secenje", "Instrukcija": "Seci iskljucivo po CUT merama iz servis paketa."},
        {"RB": 2, "Stavka": "Kantovanje", "Instrukcija": "Kantuj samo ivice oznacene u tabeli kantovanja i proveri tip ABS-a."},
        {"RB": 3, "Stavka": "Obrade", "Instrukcija": "Posebne otvore, utore i ventilaciju radi samo tamo gde su eksplicitno navedeni."},
        {"RB": 4, "Stavka": "Radna ploca", "Instrukcija": "Otvor za sudoperu ili plocu radi po sablonu proizvodjaca, ne po slobodnoj proceni."},
        {"RB": 5, "Stavka": "Ko izvodi", "Instrukcija": "Kolona 'Izvodi' jasno razlikuje da li posao radi servis ili se obrada potvrđuje kod kuce / na licu mesta."},
        {"RB": 6, "Stavka": "Po kom pravilu", "Instrukcija": "Kolona 'Osnov izvođenja' pokazuje da li se radi po meri iz projekta ili po šablonu proizvođača uređaja."},
        {"RB": 7, "Stavka": "Instalacije", "Instrukcija": "Ako pozicija instalacija odstupa od projekta, obrade potvrditi pre secenja ili na licu mesta."},
        {"RB": 8, "Stavka": "Kontrola", "Instrukcija": "Pre isporuke proveriti broj komada, oznake delova i da li su svi paneli/frontovi ukljuceni."},
    ])

    return packet


def build_cutlist_pdf_bytes(
    kitchen: Dict[str, Any],
    cutlist_sections: Dict[str, pd.DataFrame],
    project_title: str = "Krojna lista PRO – M1 (један зид)",
) -> bytes:
    _register_fonts()
    service_packet = build_service_packet(kitchen, cutlist_sections)

    # Pick a font that supports Cyrillic
    try:
        pdfmetrics.getFont("DejaVuSans")
        FONT_REGULAR = "DejaVuSans"
        FONT_BOLD = "DejaVuSans-Bold"
    except Exception as ex:
        _LOG.debug("Falling back to Helvetica fonts for PDF build: %s", ex)
        FONT_REGULAR = "Helvetica"
        FONT_BOLD = "Helvetica-Bold"

    profile_key = (kitchen.get("manufacturing", {}) or {}).get("profile", "EU_SRB")
    profile = MANUFACTURING_PROFILES.get(profile_key, MANUFACTURING_PROFILES["EU_SRB"])
    mats = kitchen.get("materials", {}) or {}

    materials_line = (
        f"{mats.get('carcass_material','')}/{mats.get('carcass_thk',18)}, "
        f"{mats.get('front_material','')}/{mats.get('front_thk',19)}, "
        f"{mats.get('back_material','')}/{mats.get('back_thk',3)}"
    )

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=project_title,
    )

    styles = getSampleStyleSheet()
    s_title = ParagraphStyle(
        "TitleCyr",
        parent=styles["Title"],
        fontName=FONT_BOLD,
        fontSize=16,
        leading=18,
        spaceAfter=8,
    )
    s_norm = ParagraphStyle(
        "NormCyr",
        parent=styles["Normal"],
        fontName=FONT_REGULAR,
        fontSize=10,
        leading=12,
    )
    s_h2 = ParagraphStyle(
        "H2Cyr",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=12,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
    )

    # ---- Helper: napravi ReportLab tabelu iz DataFrame-a ----
    def _df_to_table(df: pd.DataFrame, cols: List[str]) -> Table:
        _available_cols = [c for c in cols if c in df.columns]
        data = [_available_cols] + df[_available_cols].astype(str).fillna("").values.tolist()
        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONT", (0, 0), (-1, 0), FONT_BOLD),
            ("FONT", (0, 1), (-1, -1), FONT_REGULAR),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            # Alternirajuce boje redova
            *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8F8F8"))
              for i in range(2, len(data), 2)],
        ]))
        return tbl

    story: List[Any] = []

    # ---- Zaglavlje dokumenta ----
    story.append(Paragraph(project_title, s_title))
    story.append(Paragraph(
        f"Profil: {profile.get('label', profile_key)} | Standard: {kitchen.get('standard', 'SRB')} | "
        f"Generisano: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        s_norm
    ))
    story.append(Paragraph(f"Materijali: {materials_line}", s_norm))
    story.append(Spacer(1, 4 * mm))

    # ---- Radni nalog / project header ----
    story.append(Paragraph("Radni nalog / project header", s_h2))
    _hdr_df = service_packet.get("project_header", pd.DataFrame())
    if _hdr_df is not None and not _hdr_df.empty:
        story.append(_df_to_table(_hdr_df, ["Polje", "Vrednost"]))
    story.append(Spacer(1, 4 * mm))

    # ---- Tehnicki crtez ----
    try:
        from visualization import _render as _viz_render  # type: ignore

        _fig = plt.figure(figsize=(16, 5))
        _ax = _fig.add_subplot(111)
        _viz_render(
            ax=_ax,
            kitchen=kitchen,
            view_mode="tehnicki",
            show_grid=False,
            grid_mm=50,
            show_bounds=True,
            kickboard=True,
            ceiling_filler=False,
        )
        _img_buf = BytesIO()
        _fig.savefig(_img_buf, format="png", dpi=150, bbox_inches="tight",
                     facecolor="white", edgecolor="none")
        plt.close(_fig)
        _img_buf.seek(0)
        # Prilagodi visinu slike prema A4 landscape proporciji
        _img = RLImage(_img_buf, width=270 * mm, height=70 * mm)
        story.append(_img)
    except Exception as _viz_err:
        story.append(Paragraph(f"[Tehnicki crtez nije dostupan: {_viz_err}]", s_norm))

    story.append(Spacer(1, 5 * mm))

    # ---- Sekcija: Koordinate projekta ----
    wall = kitchen.get("wall", {}) or {}
    foot_mm = kitchen.get("foot_height_mm", 100)
    base_h = kitchen.get("base_korpus_h_mm", 720)
    wt = kitchen.get("worktop", {}) or {}
    wt_mm = int(round(float(wt.get("thickness", 0.0)) * 10.0))
    radna_visina = foot_mm + base_h + wt_mm

    story.append(Paragraph("Koordinate projekta", s_h2))
    _coord_data = [
        ["Zid (duz. x vis.)", f"{wall.get('length_mm', 0):.0f} x {wall.get('height_mm', 0):.0f} mm"],
        ["Stopice", f"{foot_mm} mm"],
        ["Korpus donjih el.", f"{base_h} mm"],
        ["Radna ploca debljina", f"{wt_mm} mm"],
        ["Radna visina (ukupno)", f"{radna_visina} mm"],
    ]
    _ct = Table(_coord_data)
    _ct.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONT", (0, 0), (0, -1), FONT_BOLD),
        ("FONT", (1, 0), (1, -1), FONT_REGULAR),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(_ct)
    story.append(Spacer(1, 5 * mm))

    # ---- Sumarna krojna lista (identično PDF strana 4) ----
    _summary_pdf = generate_cutlist_summary(cutlist_sections)
    df_sum_all = _summary_pdf.get("summary_all", pd.DataFrame())

    story.append(Paragraph("Sumarna krojna lista — ploce", s_h2))
    story.append(Paragraph("Dimenzije su gotove mere (posle kanta).", s_norm))
    if df_sum_all is None or df_sum_all.empty:
        story.append(Paragraph("Nema stavki.", s_norm))
    else:
        _cols_sum = ["RB", "Deo", "Kom", "Duzina [mm]", "Sirina [mm]", "Deb.",
                     "Materijal", "Orijentacija", "L1", "L2", "K1", "K2"]
        story.append(_df_to_table(df_sum_all, _cols_sum))

    story.append(Spacer(1, 8 * mm))

    # ---- Sokla ----
    story.append(Paragraph("Sokla (lajsna)", s_h2))
    df_pl = cutlist_sections.get("plinth", pd.DataFrame())
    if df_pl is None or df_pl.empty:
        story.append(Paragraph("Nema sokle (dodaj BASE elemente).", s_norm))
    else:
        _cols_pl = ["ID", "Zid", "Deo", "Materijal", "Deb. [mm]", "Duzina [mm]", "Visina [mm]", "Kol.", "Napomena"]
        story.append(_df_to_table(df_pl, _cols_pl))

    story.append(Spacer(1, 8 * mm))

    # ---- Detaljna krojna lista po modulima (identično PDF strane 5-7) ----
    df_det = _summary_pdf.get("summary_detaljna", pd.DataFrame())
    story.append(Paragraph("Detaljna krojna lista — po modulima", s_h2))
    story.append(Paragraph("Svaki deo prikazan po modulu. Dimenzije su gotove mere (posle kanta).", s_norm))
    if df_det is None or df_det.empty:
        story.append(Paragraph("Nema podataka.", s_norm))
    else:
        _cols_det = ["PartCode", "Zid", "Modul", "Deo", "Pozicija", "SklopKorak", "Kom", "Duzina [mm]", "Sirina [mm]", "Deb.",
                     "Materijal", "Orijentacija", "L1", "L2", "K1", "K2"]
        story.append(_df_to_table(df_det, _cols_det))

    story.append(Spacer(1, 8 * mm))

    # ---- Servis paket ----
    story.append(Paragraph("Servis paket za plocasti materijal", s_h2))
    story.append(Paragraph("Ovo se nosi u servis: secenje po CUT merama, kantovanje po tabeli i obrade po napomenama.", s_norm))
    _svc_cuts = service_packet.get("service_cuts", pd.DataFrame())
    if _svc_cuts is not None and not _svc_cuts.empty:
        story.append(Paragraph("Tabela za secenje", s_norm))
        story.append(_df_to_table(_svc_cuts, ["RB", "Zid", "Materijal", "Deb.", "CUT_W [mm]", "CUT_H [mm]", "Kant", "Kol.", "Napomena za servis"]))
        story.append(Spacer(1, 3 * mm))
    _svc_edge = service_packet.get("service_edge", pd.DataFrame())
    if _svc_edge is not None and not _svc_edge.empty:
        story.append(Paragraph("Tabela za kantovanje", s_norm))
        story.append(_df_to_table(_svc_edge, ["PartCode", "Zid", "Modul", "Deo", "Kol.", "CUT_W [mm]", "CUT_H [mm]", "Kant", "Napomena"]))
        story.append(Spacer(1, 3 * mm))
    _svc_proc = service_packet.get("service_processing", pd.DataFrame())
    if _svc_proc is not None and not _svc_proc.empty:
        story.append(Paragraph("Tabela za obradu", s_norm))
        story.append(_df_to_table(_svc_proc, ["PartCode", "Zid", "Modul", "Deo", "CUT_W [mm]", "CUT_H [mm]", "Tip obrade", "Izvodi", "Osnov izvođenja", "Kol.", "Obrada / napomena"]))
        story.append(Spacer(1, 3 * mm))
    _svc_instr = service_packet.get("service_instructions", pd.DataFrame())
    if _svc_instr is not None and not _svc_instr.empty:
        story.append(Paragraph("Instrukcije za servis", s_norm))
        story.append(_df_to_table(_svc_instr, ["RB", "Stavka", "Instrukcija"]))
        story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Napomena: uredjaji, sudopera, slavina, sifon i slicno se kupuju kao gotovi proizvodi i ne ulaze u secenje.", s_norm))
    story.append(Spacer(1, 8 * mm))

    # ---- Montazna mapa po modulu ----
    story.append(Paragraph("Montazna mapa po modulu (orijentacija delova)", s_h2))
    _all_for_map = []
    for _k in ("carcass", "backs", "fronts", "drawer_boxes", "worktop", "plinth"):
        _dfk = cutlist_sections.get(_k, pd.DataFrame())
        if _dfk is not None and not _dfk.empty:
            _all_for_map.append(_dfk.copy())
    if not _all_for_map:
        story.append(Paragraph("Nema podataka.", s_norm))
    else:
        _mm = pd.concat(_all_for_map, ignore_index=True)
        if "ID" in _mm.columns:
            _mm["ID"] = pd.to_numeric(_mm["ID"], errors="coerce")
            _mm = _mm[_mm["ID"].notna()].copy()
        if _mm.empty:
            story.append(Paragraph("Nema podataka po modulima.", s_norm))
        else:
            _mm["ID"] = _mm["ID"].astype(int)
            _mm["_korak"] = pd.to_numeric(_mm.get("SklopKorak", "-"), errors="coerce").fillna(99).astype(int)
            for _mid in sorted(_mm["ID"].unique().tolist()):
                _mrows = _mm[_mm["ID"] == _mid].sort_values(["_korak", "PartCode"]).copy()
                _modul = str(_mrows.iloc[0].get("Modul", f"Modul {_mid}"))
                story.append(Paragraph(f"#{_mid} - {_modul}", s_norm))

                _map_data = [
                    ["", "GORE", ""],
                    ["LEVO", "CENTAR", "DESNO"],
                    ["", "DOLE", ""],
                ]
                _map_tbl = Table(_map_data, colWidths=[18 * mm, 22 * mm, 18 * mm], rowHeights=[8 * mm, 10 * mm, 8 * mm])
                _map_tbl.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONT", (0, 0), (-1, -1), FONT_BOLD),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#F3F3F3")),
                ]))

                _plist = _mrows.copy()
                if "Kol." in _plist.columns:
                    _plist = _plist.rename(columns={"Kol.": "Kom"})
                _cols_mp = ["PartCode", "Deo", "Pozicija", "SklopKorak", "Kom"]
                _avail = [c for c in _cols_mp if c in _plist.columns]
                _pt = _df_to_table(_plist, _avail)

                _row = Table([[_map_tbl, _pt]], colWidths=[62 * mm, 190 * mm])
                _row.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))
                story.append(_row)
                story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 8 * mm))

    # ---- Okovi ----
    story.append(Paragraph("Okovi i potrosni materijal", s_h2))
    df_hw = cutlist_sections.get("hardware", pd.DataFrame())
    if df_hw is None or df_hw.empty:
        story.append(Paragraph("Nema stavki.", s_norm))
    else:
        _cols_hw = ["PartCode", "Modul", "Kategorija", "Naziv", "Tip / Šifra", "Kol.", "SklopKorak", "Napomena"]
        story.append(_df_to_table(df_hw, _cols_hw))
        if "Kategorija" in df_hw.columns:
            _wdf = df_hw[df_hw["Kategorija"].astype(str).str.lower() == "warning"]
            if _wdf is not None and not _wdf.empty:
                story.append(Spacer(1, 4 * mm))
                story.append(Paragraph("Kriticna upozorenja pre proizvodnje", s_h2))
                _cols_w = ["Modul", "Naziv", "Napomena"]
                story.append(_df_to_table(_wdf, _cols_w))

    # ---- Shopping list ----
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Shopping list za laika", s_h2))
    _shop_df = service_packet.get("shopping_list", pd.DataFrame())
    if _shop_df is None or _shop_df.empty:
        story.append(Paragraph("Nema stavki.", s_norm))
    else:
        story.append(_df_to_table(_shop_df, ["Grupa", "Naziv", "Tip / Šifra", "Kol.", "Napomena"]))

    _ready_df = service_packet.get("ready_made_items", pd.DataFrame())
    if _ready_df is not None and not _ready_df.empty:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Ovo se kupuje gotovo - ne ulazi u secenje", s_h2))
        story.append(_df_to_table(_ready_df, ["Grupa", "Naziv", "Tip / Šifra", "Kol.", "Napomena"]))

    _guide_df = service_packet.get("user_guide", pd.DataFrame())
    if _guide_df is not None and not _guide_df.empty:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Kratak vodic za korisnika", s_h2))
        story.append(_df_to_table(_guide_df, ["Korak", "Sta radis", "Napomena"]))

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Checklist pre servisa i sklapanja", s_h2))
    _wcl = service_packet.get("workshop_checklist", pd.DataFrame())
    if _wcl is not None and not _wcl.empty:
        story.append(Paragraph("Pre odlaska u servis", s_norm))
        story.append(_df_to_table(_wcl, ["RB", "Stavka", "Status"]))
        story.append(Spacer(1, 3 * mm))
    _hcl = service_packet.get("home_checklist", pd.DataFrame())
    if _hcl is not None and not _hcl.empty:
        story.append(Paragraph("Pre kucnog sklapanja", s_norm))
        story.append(_df_to_table(_hcl, ["RB", "Stavka", "Status"]))

    doc.build(story)
    return buf.getvalue()


def generate_cutlist_pdf(kitchen: Dict[str, Any], title: str = "Krojna lista PRO – M1 (jedan zid)") -> bytes:
    """Returns PDF bytes."""
    sections = generate_cutlist(kitchen)
    return build_cutlist_pdf_bytes(kitchen, sections, project_title=title)


def generate_cutlist_excel(
    kitchen: Dict[str, Any],
    title: str = "Krojna lista PRO",
) -> bytes:
    """
    Generiše Excel fajl (.xlsx) sa kompletnom krojnom listom.

    Struktura sheetova:
      Sheet 1  "Pregled"   — sve ploče agregirane po materijalu + deb + dimenzijama
      Sheet 2  "Korpus"    — carcass ploče (stranice, dno, plafon)
      Sheet 3  "Ledne"     — leđne ploče
      Sheet 4  "Frontovi"  — frontovi
      Sheet 5  "Fioke"     — sanduci fioka
      Sheet 6  "Radna"     — radna ploča i nosači
      Sheet 7  "Sokla"     — sokla / lajsna

    Vraća bytes kompletnog .xlsx fajla.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    sections = generate_cutlist(kitchen)
    service_packet = build_service_packet(kitchen, sections)
    mats = kitchen.get("materials", {}) or {}
    wall = kitchen.get("wall", {}) or {}

    # ── Boje ────────────────────────────────────────────────────────────────
    CLR_HDR_BG = "1F3864"   # tamno plava — header
    CLR_HDR_FG = "FFFFFF"
    CLR_TTL_BG = "2E75B6"   # srednje plava — naslov lista
    CLR_TTL_FG = "FFFFFF"
    CLR_ODD    = "EBF3FB"   # svijetlo plava — neparne vrste
    CLR_EVEN   = "FFFFFF"
    CLR_WARN   = "FFF2CC"   # žuta — vrste sa greškom
    CLR_BORDER = "BFBFBF"

    def _hdr_fill():  return PatternFill("solid", fgColor=CLR_HDR_BG)
    def _ttl_fill():  return PatternFill("solid", fgColor=CLR_TTL_BG)
    def _odd_fill():  return PatternFill("solid", fgColor=CLR_ODD)
    def _warn_fill(): return PatternFill("solid", fgColor=CLR_WARN)
    def _border():
        s = Side(style="thin", color=CLR_BORDER)
        return Border(left=s, right=s, top=s, bottom=s)

    def _hdr_font():  return Font(name="Calibri", bold=True,  color=CLR_HDR_FG, size=10)
    def _ttl_font():  return Font(name="Calibri", bold=True,  color=CLR_TTL_FG, size=11)
    def _norm_font(): return Font(name="Calibri", bold=False, size=10)
    def _info_font(): return Font(name="Calibri", italic=True, size=9, color="555555")

    _now  = datetime.now().strftime("%d.%m.%Y  %H:%M")
    _wl   = wall.get("length_mm", 0)
    _wh   = wall.get("height_mm", 0)
    _info = (
        f"Zid: {_wl}×{_wh} mm   |   "
        f"Korpus: {mats.get('carcass_material','?')} / {mats.get('carcass_thk','?')} mm   |   "
        f"Front: {mats.get('front_material','?')} / {mats.get('front_thk','?')} mm   |   "
        f"Generisano: {_now}"
    )

    # ── Specifikacija kolona ─────────────────────────────────────────────────
    # (df_field, excel_header, col_width)
    SEC_COLS = [
        ("PartCode",    "PartCode",      12),
        ("Zid",         "Zid",           10),
        ("Modul",       "Modul",        22),
        ("Deo",         "Deo",          24),
        ("Pozicija",    "Pozicija",      9),
        ("SklopKorak",  "Korak",         7),
        ("Materijal",   "Materijal",    12),
        ("Deb.",        "Deb.",          6),
        ("Kol.",        "Kol.",          5),
        ("CUT_W [mm]",  "CUT Duz.",      9),
        ("CUT_H [mm]",  "CUT Sir.",      9),
        ("Duzina [mm]", "FIN Duz.",      9),
        ("Sirina [mm]", "FIN Sir.",      9),
        ("Smer goda",   "Smer goda",     8),
        ("Kant",        "Kant",         24),
        ("L1",          "L1",            4),
        ("L2",          "L2",            4),
        ("K1",          "K1",            4),
        ("K2",          "K2",            4),
        ("Napomena",    "Napomena",     30),
    ]
    HARDWARE_COLS = [
        ("PartCode",    "PartCode",      12),
        ("Zid",         "Zid",           10),
        ("Modul",       "Modul",         22),
        ("Kategorija",  "Kategorija",    12),
        ("Naziv",       "Naziv",         20),
        ("Tip / Šifra", "Tip / Sifra",   20),
        ("Kol.",        "Kol.",           6),
        ("SklopKorak",  "Korak",          7),
        ("Napomena",    "Napomena",      32),
    ]
    PROJECT_COLS = [
        ("Polje", "Polje", 24),
        ("Vrednost", "Vrednost", 60),
    ]
    SERVICE_CUTS_COLS = [
        ("RB", "RB", 6),
        ("Zid", "Zid", 10),
        ("Materijal", "Materijal", 18),
        ("Deb.", "Deb.", 8),
        ("CUT_W [mm]", "CUT Duzina", 12),
        ("CUT_H [mm]", "CUT Sirina", 12),
        ("Kant", "Kant", 24),
        ("Kol.", "Kol.", 8),
        ("Napomena za servis", "Napomena za servis", 42),
    ]
    SERVICE_EDGE_COLS = [
        ("PartCode", "PartCode", 12),
        ("Zid", "Zid", 10),
        ("Modul", "Modul", 22),
        ("Deo", "Deo", 24),
        ("Kol.", "Kol.", 6),
        ("CUT_W [mm]", "CUT Duzina", 10),
        ("CUT_H [mm]", "CUT Sirina", 10),
        ("Kant", "Kant", 24),
        ("Napomena", "Napomena", 36),
    ]
    SERVICE_PROC_COLS = [
        ("PartCode", "PartCode", 12),
        ("Zid", "Zid", 10),
        ("Modul", "Modul", 22),
        ("Deo", "Deo", 24),
        ("CUT_W [mm]", "CUT Duzina", 10),
        ("CUT_H [mm]", "CUT Sirina", 10),
        ("Tip obrade", "Tip obrade", 18),
        ("Izvodi", "Izvodi", 12),
        ("Osnov izvođenja", "Osnov izvođenja", 20),
        ("Kol.", "Kol.", 6),
        ("Obrada / napomena", "Obrada / napomena", 30),
    ]
    SERVICE_INSTR_COLS = [
        ("RB", "RB", 6),
        ("Stavka", "Stavka", 20),
        ("Instrukcija", "Instrukcija", 70),
    ]
    SHOP_COLS = [
        ("Grupa", "Grupa", 20),
        ("Naziv", "Naziv", 24),
        ("Tip / Šifra", "Tip / Sifra", 22),
        ("Kol.", "Kol.", 8),
        ("Napomena", "Napomena", 40),
    ]
    GUIDE_COLS = [
        ("Korak", "Korak", 8),
        ("Sta radis", "Sta radis", 36),
        ("Napomena", "Napomena", 48),
    ]
    CHECK_COLS = [
        ("RB", "RB", 6),
        ("Stavka", "Stavka", 70),
        ("Status", "Status", 14),
    ]
    SUM_COLS = [
        ("Materijal",   "Materijal",    14),
        ("Deb.",        "Deb.",          6),
        ("CUT_W [mm]",  "CUT Duzina",    9),
        ("CUT_H [mm]",  "CUT Sirina",    9),
        ("Duzina [mm]", "FIN Duzina",    9),
        ("Sirina [mm]", "FIN Sirina",    9),
        ("Kol.",        "Kol.",          6),
        ("Kant",        "Kant",         24),
    ]
    NUM_FIELDS = {
        "Deb.", "Kol.", "CUT_W [mm]", "CUT_H [mm]",
        "Duzina [mm]", "Sirina [mm]", "L1", "L2", "K1", "K2",
    }

    # ── Pomoćna funkcija za pisanje jednog lista ─────────────────────────────
    def _write_sheet(
        ws,
        df,
        cols: list,
        sheet_title: str,
    ) -> None:
        n = len(cols)

        # Red 1: Naslov lista
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
        c = ws.cell(1, 1, sheet_title)
        c.font      = _ttl_font()
        c.fill      = _ttl_fill()
        c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 22

        # Red 2: Info o projektu
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
        c = ws.cell(2, 1, _info)
        c.font      = _info_font()
        c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[2].height = 15

        # Red 3: Zaglavlje kolona
        for ci, (field, lbl, w) in enumerate(cols, 1):
            c = ws.cell(3, ci, lbl)
            c.font      = _hdr_font()
            c.fill      = _hdr_fill()
            c.border    = _border()
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.column_dimensions[get_column_letter(ci)].width = w
        ws.row_dimensions[3].height = 30
        ws.freeze_panes = "A4"
        ws.auto_filter.ref = f"A3:{get_column_letter(n)}3"

        # Prazna sekcija
        if df is None or df.empty:
            ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=n)
            c = ws.cell(4, 1, "— nema podataka —")
            c.font      = _info_font()
            c.alignment = Alignment(horizontal="center")
            return

        # Redovi s podacima
        for ri, (_, row) in enumerate(df.iterrows(), 4):
            nap = str(row.get("Napomena", "") or "")
            _nap_u = nap.upper()
            if ("GREŠKA" in _nap_u or "GRJEŠKA" in _nap_u or "UPOZORENJE" in _nap_u
                    or "WARNING" in _nap_u or str(row.get("Kategorija", "")).lower() == "warning"):
                row_fill = _warn_fill()
            elif ri % 2 == 0:
                row_fill = _odd_fill()
            else:
                row_fill = PatternFill("solid", fgColor=CLR_EVEN)

            for ci, (field, _lbl, _w) in enumerate(cols, 1):
                raw = row.get(field, "")
                if field in NUM_FIELDS:
                    try:
                        val = round(float(raw), 1) if raw != "" and raw is not None else ""
                    except (TypeError, ValueError):
                        val = raw
                else:
                    val = raw if raw is not None else ""

                c = ws.cell(ri, ci, val)
                c.font   = _norm_font()
                c.fill   = row_fill
                c.border = _border()
                if field in NUM_FIELDS:
                    c.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)

    # ── Kreira workbook ─────────────────────────────────────────────────────
    wb = openpyxl.Workbook()
    wb.remove(wb.active)   # ukloni default prazan sheet

    # ── Sheet 1: Pregled ─────────────────────────────────────────────────────
    ws_sum = wb.create_sheet("Pregled")
    all_dfs = [df for df in sections.values() if df is not None and not df.empty]
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        # Osiguraj da kolone postoje
        for col in ["Duzina [mm]", "Sirina [mm]", "Kant"]:
            if col not in combined.columns:
                combined[col] = ""
        grp = [c for c in
               ["Materijal", "Deb.", "CUT_W [mm]", "CUT_H [mm]", "Duzina [mm]", "Sirina [mm]", "Kant"]
               if c in combined.columns]
        summary = (
            combined
            .groupby(grp, as_index=False)
            .agg({"Kol.": "sum"})
            .sort_values(
                ["Materijal", "CUT_W [mm]", "CUT_H [mm]"],
                ascending=[True, False, False],
            )
            .reset_index(drop=True)
        )
    else:
        summary = pd.DataFrame(columns=[f for f, _, _ in SUM_COLS])
    _write_sheet(ws_sum, summary, SUM_COLS, f"{title}  |  Pregled svih ploca")

    # ── Sheetovi 2–7: po sekcijama ────────────────────────────────────────────
    SHEET_CFG = [
        ("carcass",      "Korpus",    "Korpus — stranice, dno, plafon"),
        ("backs",        "Ledne",     "Ledne ploce"),
        ("fronts",       "Frontovi",  "Frontovi"),
        ("drawer_boxes", "Fioke",     "Sanduk fioke"),
        ("worktop",      "Radna",     "Radna ploca i nosaci"),
        ("plinth",       "Sokla",     "Sokla i lajsne"),
    ]
    for key, sheet_name, long_name in SHEET_CFG:
        ws = wb.create_sheet(sheet_name)
        _write_sheet(ws, sections.get(key), SEC_COLS, f"{title}  |  {long_name}")

    ws_hw = wb.create_sheet("Okovi")
    _write_sheet(ws_hw, sections.get("hardware"), HARDWARE_COLS, f"{title}  |  Okovi i potrosni materijal")

    ws_proj = wb.create_sheet("Radni nalog")
    _write_sheet(ws_proj, service_packet.get("project_header"), PROJECT_COLS, f"{title}  |  Radni nalog")

    ws_sc = wb.create_sheet("Servis secenje")
    _write_sheet(ws_sc, service_packet.get("service_cuts"), SERVICE_CUTS_COLS, f"{title}  |  Servis paket - secenje")

    ws_se = wb.create_sheet("Servis kant")
    _write_sheet(ws_se, service_packet.get("service_edge"), SERVICE_EDGE_COLS, f"{title}  |  Servis paket - kantovanje")

    ws_sp = wb.create_sheet("Servis obrada")
    _write_sheet(ws_sp, service_packet.get("service_processing"), SERVICE_PROC_COLS, f"{title}  |  Servis paket - obrada")

    ws_si = wb.create_sheet("Servis uputstvo")
    _write_sheet(ws_si, service_packet.get("service_instructions"), SERVICE_INSTR_COLS, f"{title}  |  Instrukcije za servis")

    ws_shop = wb.create_sheet("Shopping")
    _write_sheet(ws_shop, service_packet.get("shopping_list"), SHOP_COLS, f"{title}  |  Shopping list")

    ws_ready = wb.create_sheet("Kupuje se")
    _write_sheet(ws_ready, service_packet.get("ready_made_items"), SHOP_COLS, f"{title}  |  Ovo se kupuje gotovo")

    ws_guide = wb.create_sheet("Vodic")
    _write_sheet(ws_guide, service_packet.get("user_guide"), GUIDE_COLS, f"{title}  |  Kratak vodic za laika")

    ws_wchk = wb.create_sheet("Checklist servis")
    _write_sheet(ws_wchk, service_packet.get("workshop_checklist"), CHECK_COLS, f"{title}  |  Checklist pre servisa")

    ws_hchk = wb.create_sheet("Checklist dom")
    _write_sheet(ws_hchk, service_packet.get("home_checklist"), CHECK_COLS, f"{title}  |  Checklist pre sklapanja")

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


# =========================================================
# Sumarna krojna lista — agregirane ploce po dimenziji
# =========================================================

# Redosled tipova ploča u objedinjenoj sumarnoj listi (identično PDF formatu)
_TIP_ORDER: Dict[str, int] = {
    "Korpus":      0,
    "Leđna ploča": 1,
    "Front":       2,
    "Radna ploča": 3,
}


def generate_cutlist_summary(sections: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Vraca sumarnu krojnu listu po PDF formatu:
      - summary_all: JEDNA objedinjena tabela svih ploča (identično strana 4 PDF-a)
        Kolone: Deo | Kom | Duzina [mm] | Sirina [mm] | Deb. [mm] | Materijal | Orijent. | Kant L1 | Kant L2 | Kant K1 | Kant K2
        Dimenzije su FIN (gotove mere posle kanta), sortirano po Deo

      - summary_detaljna: detaljna lista sa Modul kolonom (identično strane 5-7 PDF-a)
        Kolone: Modul | Deo | Kom | Duzina [mm] | Sirina [mm] | Deb. [mm] | Materijal | Orijent. | ...

      - summary_carcass / summary_fronts / summary_backs: backwards compat
    """
    result: Dict[str, pd.DataFrame] = {
        "summary_all":     pd.DataFrame(),
        "summary_detaljna": pd.DataFrame(),
        "summary_carcass": pd.DataFrame(),
        "summary_fronts":  pd.DataFrame(),
        "summary_backs":   pd.DataFrame(),
    }

    # -------------------------------------------------------
    # summary_all — OBJEDINJENA tabela svih ploča (PDF strana 4)
    # Grupiše iste ploče (isti Deo, iste FIN dimenzije, isti materijal)
    # -------------------------------------------------------
    all_frames = []
    _sec_to_tip = [
        ("carcass", "Korpus"),
        ("backs",   "Leđna ploča"),
        ("fronts",  "Front"),
        ("worktop", "Radna ploča"),
    ]
    _needed_all = {"Deo", "Materijal", "Deb.", "Duzina [mm]", "Sirina [mm]", "Kol."}

    for sec_key, tip_label in _sec_to_tip:
        df = sections.get(sec_key)
        if df is None or df.empty:
            continue
        if not _needed_all.issubset(set(df.columns)):
            continue
        df2 = df.copy()
        df2["_Tip"] = tip_label
        all_frames.append(df2)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        # Grupisanje: Deo + dimenzije + materijal + kant flags (FIN dimenzije)
        grp_cols = ["_Tip", "Deo", "Materijal", "Deb.", "Duzina [mm]", "Sirina [mm]",
                    "Orijentacija", "Smer goda", "L1", "L2", "K1", "K2"]
        grp_cols = [c for c in grp_cols if c in combined.columns]
        try:
            agg_d = {"Kol.": "sum"}
            if "Kant" in combined.columns:
                agg_d["Kant"] = "first"
            agg = (
                combined.groupby(grp_cols, as_index=False)
                .agg(agg_d)
            )
            # Sortiranje: Tip order → Materijal → Duzina desc
            agg["_sort"] = agg["_Tip"].map(_TIP_ORDER).fillna(99)
            agg = agg.sort_values(["_sort", "Materijal", "Duzina [mm]"],
                                  ascending=[True, True, False])
            agg = agg.drop(columns=["_sort", "_Tip"]).reset_index(drop=True)
            # Preimenovati Kol. → Kom (kao u PDF-u)
            agg = agg.rename(columns={"Kol.": "Kom"})
            # Dodati redni broj
            agg.insert(0, "RB", range(1, len(agg) + 1))
            # Uредiti kolone po PDF redosledu
            _cols_order = ["RB", "Deo", "Kom", "Duzina [mm]", "Sirina [mm]", "Deb.",
                           "Materijal", "Smer goda", "Orijentacija", "L1", "L2", "K1", "K2", "Kant"]
            _cols_show = [c for c in _cols_order if c in agg.columns]
            result["summary_all"] = agg[_cols_show]
        except Exception as ex:
            _LOG.debug("Failed summary_all aggregation, using combined fallback: %s", ex)
            result["summary_all"] = combined.copy()

    # -------------------------------------------------------
    # summary_detaljna — detaljna lista sa Modul kolonom (PDF strane 5-7)
    # -------------------------------------------------------
    det_frames = []
    for sec_key, _ in _sec_to_tip:
        df = sections.get(sec_key)
        if df is None or df.empty:
            continue
        det_frames.append(df.copy())

    if det_frames:
        det = pd.concat(det_frames, ignore_index=True)
        _det_needed = {"Modul", "Deo", "Kol.", "Duzina [mm]", "Sirina [mm]", "Deb.", "Materijal"}
        if _det_needed.issubset(set(det.columns)):
            det = det.rename(columns={"Kol.": "Kom"})
            det = det.sort_values(["Modul", "Deo"]).reset_index(drop=True)
            _det_cols = ["PartCode", "Modul", "Deo", "Pozicija", "SklopKorak", "Kom", "Duzina [mm]", "Sirina [mm]", "Deb.",
                         "Materijal", "Smer goda", "Orijentacija", "L1", "L2", "K1", "K2", "Kant", "Napomena"]
            _det_cols = [c for c in _det_cols if c in det.columns]
            result["summary_detaljna"] = det[_det_cols]
        else:
            result["summary_detaljna"] = det.copy()

    # -------------------------------------------------------
    # Backwards compat — odvojene sekcije
    # -------------------------------------------------------
    for sec_key, out_key in (
        ("carcass", "summary_carcass"),
        ("fronts",  "summary_fronts"),
        ("backs",   "summary_backs"),
    ):
        df = sections.get(sec_key)
        if df is None or df.empty:
            continue
        needed = {"Materijal", "Deb.", "Duzina [mm]", "Sirina [mm]", "Kol."}
        if not needed.issubset(set(df.columns)):
            result[out_key] = df.copy()
            continue
        try:
            agg2 = (
                df.groupby(["Materijal", "Deb.", "Duzina [mm]", "Sirina [mm]"], as_index=False)
                .agg({"Kol.": "sum"})
                .sort_values(["Materijal", "Duzina [mm]"])
                .reset_index(drop=True)
            )
            agg2.insert(0, "RB", range(1, len(agg2) + 1))
            result[out_key] = agg2
        except Exception as ex:
            _LOG.debug("Failed %s aggregation, using section fallback: %s", out_key, ex)
            result[out_key] = df.copy()

    return result


# =========================================================
# Lista ugradjenih uredjaja (frizider, rerna, ploca, napa...)
# =========================================================
_APPLIANCE_KEYWORDS: Dict[str, str] = {
    "FRIDGE_FREEZE": "Frizider sa zamrzivačem",
    "FRIDGE":        "Frizider",
    "OVEN_HOB":      "Rerna + ploča za kuvanje (kombo)",
    "OVEN_MICRO":    "Rerna + mikrotalasna (kombo)",
    "HOB":           "Ploča za kuvanje",
    "OVEN":          "Ugradna rerna",
    "MICRO":         "Mikrotalasna pećnica",
    "DISHWASHER":    "Mašina za sudove",
    "HOOD":          "Aspirator / napa",
    "SINK":          "Sudopera",
}


def generate_appliance_list(kitchen: Dict[str, Any]) -> pd.DataFrame:
    """
    Vraca DataFrame sa listom ugradnih uredjaja koji se NABAVLJAJU
    (ne seku se iz ploce — frizider, rerna, ploca za kuvanje, mašina itd.)
    """
    modules = kitchen.get("modules", []) or []
    rows: List[Dict[str, Any]] = []

    for m in modules:
        tid = str(m.get("template_id", "")).upper()
        for kw, naziv in _APPLIANCE_KEYWORDS.items():
            if kw in tid:
                rows.append({
                    "ID":           m.get("id", "?"),
                    "Uređaj":       naziv,
                    "Oznaka":       m.get("label", tid),
                    "Zona":         str(m.get("zone", "")).capitalize(),
                    "Š [mm]":       m.get("w_mm", ""),
                    "V [mm]":       m.get("h_mm", ""),
                    "D [mm]":       m.get("d_mm", ""),
                    "Kol.":         1,
                    "Napomena":     "",
                })
                break  # svaki modul samo jednom

    return pd.DataFrame(rows)



def generate_wardrobe_sections_csv(kitchen: Dict[str, Any]) -> bytes:
    """Generise CSV za americke sekcije ormara (leva/centar/desna/spremnik)."""
    import csv
    from io import StringIO

    mats = kitchen.get("materials", {}) or {}
    carcass_mat = str(mats.get("carcass_material", "Iverica"))
    front_mat = str(mats.get("front_material", carcass_mat))
    dflt_thk = float(mats.get("carcass_thk", 18) or 18)

    header = [
        "module_id", "module_label", "section", "component", "qty",
        "width_mm", "height_mm", "depth_mm", "material", "thickness_mm", "status", "note",
    ]
    out = StringIO()
    wr = csv.writer(out)
    wr.writerow(header)

    def _safe_int(v: Any, default: int = 0) -> int:
        try:
            return int(float(v))
        except Exception:
            return int(default)

    for m in (kitchen.get("modules", []) or []):
        tid = str(m.get("template_id", "")).upper()
        p = m.get("params", {}) or {}
        is_wardrobe = bool(p.get("wardrobe", False)) or ("WARDROBE" in tid)
        if not is_wardrobe:
            continue

        mid = _safe_int(m.get("id", 0), 0)
        mlbl = str(m.get("label", tid))
        mw = _safe_int(m.get("w_mm", 0), 0)
        mh = _safe_int(m.get("h_mm", 0), 0)
        md = _safe_int(m.get("d_mm", 0), 0)
        if mw <= 0 or mh <= 0 or md <= 0:
            wr.writerow([mid, mlbl, "-", "validation", 0, mw, mh, md, "-", dflt_thk, "ERROR", "Nevalidne dimenzije modula"])
            continue

        sec = p.get("american_sections") if isinstance(p.get("american_sections"), dict) else {}
        if sec:
            lp = max(1, _safe_int(sec.get("left_pct", 33), 33))
            cp = max(1, _safe_int(sec.get("center_pct", 34), 34))
            rp = max(1, _safe_int(sec.get("right_pct", 33), 33))
            s = lp + cp + rp
            top_h = max(80, min(_safe_int(sec.get("top_h_mm", 420), 420), int(mh * 0.45)))
            base_h = max(80, mh - top_h)
            lw = int(mw * lp / s)
            cw = int(mw * cp / s)
            rw = max(40, mw - lw - cw)

            parts = [
                ("left", lw, sec.get("left", {}) or {}),
                ("center", cw, sec.get("center", {}) or {}),
                ("right", rw, sec.get("right", {}) or {}),
                ("top", mw, sec.get("top", {}) or {}),
            ]
            for sname, sw, sp in parts:
                sh = top_h if sname == "top" else base_h
                ns = max(0, _safe_int(sp.get("shelves", 0), 0))
                nd = max(0, _safe_int(sp.get("drawers", 0), 0))
                nh = max(0, _safe_int(sp.get("hangers", 0), 0))

                if ns > 0:
                    wr.writerow([mid, mlbl, sname, "shelf", ns, max(40, sw - 16), 18, max(120, md - 20), carcass_mat, dflt_thk, "OK", "Polica"])
                if nd > 0:
                    dh = max(80, int((sh * 0.30) / max(1, nd)))
                    wr.writerow([mid, mlbl, sname, "drawer_front", nd, max(40, sw - 16), dh, 18, front_mat, dflt_thk, "OK", "Fioka front"])
                    wr.writerow([mid, mlbl, sname, "drawer_box", nd, max(40, sw - 24), max(60, dh - 12), max(120, md - 40), carcass_mat, dflt_thk, "OK", "Fioka sanduk"])
                if nh > 0:
                    wr.writerow([mid, mlbl, sname, "hanger_rod", nh, max(60, sw - 20), 20, 20, "Metal", 20, "OK", "Sipka za vesanje"])

                used_h = (18 * max(0, ns)) + (max(80, int((sh * 0.30) / max(1, nd))) * max(0, nd))
                if used_h > sh:
                    wr.writerow([mid, mlbl, sname, "validation", 0, sw, sh, md, "-", dflt_thk, "WARN", "Police/Fioke prekoracile visinu sekcije"])
        else:
            ns = max(0, _safe_int(p.get("n_shelves", 4), 4))
            nd = max(0, _safe_int(p.get("n_drawers", 2), 2))
            nh = max(0, _safe_int(p.get("hanger_sections", 1), 1))
            if ns > 0:
                wr.writerow([mid, mlbl, "generic", "shelf", ns, max(40, mw - 16), 18, max(120, md - 20), carcass_mat, dflt_thk, "OK", "Polica"])
            if nd > 0:
                dh = max(80, int((mh * 0.22) / max(1, nd)))
                wr.writerow([mid, mlbl, "generic", "drawer_front", nd, max(40, mw - 16), dh, 18, front_mat, dflt_thk, "OK", "Fioka front"])
            if nh > 0:
                wr.writerow([mid, mlbl, "generic", "hanger_rod", nh, max(60, mw - 20), 20, 20, "Metal", 20, "OK", "Sipka za vesanje"])

    return out.getvalue().encode("utf-8-sig")
