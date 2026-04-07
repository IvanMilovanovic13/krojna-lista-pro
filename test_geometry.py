# -*- coding: utf-8 -*-
"""
test_geometry.py — Geometrijska i matematička verifikacija KrojnaListaPRO

Pokriva 4 kritična područja:
  1. LAYOUT  — preklapanja i izlasci van zida (layout_audit)
  2. DIMENZIJE — FIN = CUT − kanta (matematička preciznost)
  3. KROJNA LISTA — broj komada, sve sekcije prisutne, radna ploča
  4. OKOVI   — ispravne količine šarki, klizača, spojnica

Pokretanje:
    python test_geometry.py
    python test_geometry.py -v          # detaljan ispis
    python test_geometry.py --fail-only # prikaži samo padove
"""
from __future__ import annotations

import sys
import time
import argparse
from typing import Any, Dict, List, Tuple

# ── PATH setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, ".")

from cutlist import generate_cutlist, generate_cutlist_summary
from drawer_logic import rebalance_drawers_proportional, redistribute_drawers_proportional
from layout_engine import layout_audit
from state_logic import _default_kitchen

# ═════════════════════════════════════════════════════════════════════════════
# Pomoćne funkcije
# ═════════════════════════════════════════════════════════════════════════════

EDGE_THK_DEFAULT = 2.0   # ABS kant, mm
STEP = 0.5               # zaokruživanje, mm
TOL = STEP + 0.01        # tolerancija poređenja FIN vs CUT

_results: List[Tuple[bool, str, str]] = []   # (ok, ime_testa, poruka)


def _log(ok: bool, name: str, msg: str = "OK") -> None:
    _results.append((ok, name, msg))


def _kitchen(wall_mm: int = 3000, wall_h_mm: int = 2600,
             modules: List[Dict] = None,
             edge_thk: float = 2.0) -> Dict[str, Any]:
    """Minimalan kitchen dict za testove."""
    k = _default_kitchen()
    k["wall"]["length_mm"] = wall_mm
    k["wall"]["height_mm"] = wall_h_mm
    k["foot_height_mm"] = 150
    k["base_korpus_h_mm"] = 720
    k["vertical_gap_mm"] = 18
    k["worktop"] = {"enabled": True, "material": "Granit",
                    "thickness": 4.0, "depth_mm": 600}
    k["materials"] = {
        "carcass_material": "Iver 18mm", "carcass_thk": 18,
        "front_material": "MDF 19mm",   "front_thk": 19,
        "back_material":  "Iver 8mm",   "back_thk": 8,
        "edge_material":  "ABS 0.5mm",  "edge_thk": 0.5,
        "edge_abs_thk": int(round(edge_thk)),  # 2 → 2mm
    }
    # edge_abs_thk mora biti ispravno setovan
    k["materials"]["edge_abs_thk"] = edge_thk
    k["modules"] = modules or []
    return k


def _mod(idx: int, tid: str, zone: str, x: int, w: int, h: int, d: int,
         params: Dict = None, wall_key: str = "A") -> Dict[str, Any]:
    from module_templates import get_templates
    tmpl = get_templates().get(tid, {})
    return {
        "id": idx,
        "template_id": tid,
        "label": tmpl.get("label", tid),
        "zone": zone,
        "x_mm": x,
        "w_mm": w,
        "h_mm": h,
        "d_mm": d,
        "gap_after_mm": 0,
        "params": params or {},
        "wall_key": wall_key,
    }


def _edge_thk_from_kitchen(k: Dict) -> float:
    """Uzmi stvarnu debljinu kanta iz materials dict."""
    mat = k.get("materials", {}) or {}
    # edge_abs_thk je u mm
    v = mat.get("edge_abs_thk", 2)
    try:
        return float(v)
    except Exception:
        return 2.0


# ═════════════════════════════════════════════════════════════════════════════
# OBLAST 1 — LAYOUT: preklapanja i granice
# ═════════════════════════════════════════════════════════════════════════════

def test_layout_no_overlap_base():
    """Dva BASE elementa rame uz rame — nema preklapanja."""
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR", "base", 5,   600, 720, 560),
        _mod(2, "BASE_2DOOR", "base", 605, 800, 720, 560),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_no_overlap_base", msg)


def test_layout_overlap_detected():
    """Namerno preklапanje BASE elementa — audit mora da javi grešku."""
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR", "base", 5,   600, 720, 560),
        _mod(2, "BASE_1DOOR", "base", 400, 600, 720, 560),  # prekriva sa 1
    ])
    ok, msg = layout_audit(k)
    # Audit MORA da vrati False
    _log(not ok, "layout_overlap_detected",
         "OK (preklapanje detektovano)" if not ok else f"FAIL: nije detektovalo preklapanje — {msg}")


def test_layout_outofbounds_detected():
    """Element koji izlazi van desne granice zida — mora biti detektovan."""
    # Zid 2000mm, clearance 5+5, element na x=1500 sa w=600 → kraj 2100 > 1995
    k = _kitchen(wall_mm=2000, modules=[
        _mod(1, "BASE_1DOOR", "base", 1500, 600, 720, 560),
    ])
    ok, msg = layout_audit(k)
    _log(not ok, "layout_outofbounds_detected",
         "OK (izlazak van zida detektovan)" if not ok else f"FAIL: nije detektovalo out-of-bounds — {msg}")


def test_layout_exact_fit():
    """Element koji tačno staje u zid (uz clearance) — mora biti OK."""
    # Zid 2000, clearance 5+5 = usable 1990
    # Element: x=5, w=1990 → kraj = 1995 = wall-5 ✓
    k = _kitchen(wall_mm=2000, modules=[
        _mod(1, "BASE_2DOOR", "base", 5, 1990, 720, 560),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_exact_fit", msg)


def test_layout_wall_no_overlap():
    """Dva WALL elementa jedan pored drugog — nema overlap."""
    k = _kitchen(modules=[
        _mod(1, "WALL_1DOOR", "wall", 5,   600, 700, 320),
        _mod(2, "WALL_2DOOR", "wall", 605, 800, 700, 320),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_wall_no_overlap", msg)


def test_layout_tall_no_overlap():
    """TALL + BASE rame uz rame — audit mora proći."""
    k = _kitchen(modules=[
        _mod(1, "TALL_PANTRY",  "tall", 5,   600, 2100, 560),
        _mod(2, "BASE_1DOOR",   "base", 605, 600, 720,  560),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_tall_base_no_overlap", msg)


def test_layout_tall_overlap_base_detected():
    """TALL koji preklapa BASE na istom X — mora biti detektovano."""
    k = _kitchen(modules=[
        _mod(1, "TALL_PANTRY", "tall", 5, 600, 2100, 560),
        _mod(2, "BASE_1DOOR",  "base", 5, 600, 720,  560),  # isti X
    ])
    ok, msg = layout_audit(k)
    _log(not ok, "layout_tall_overlap_base_detected",
         "OK (TALL+BASE overlap detektovan)" if not ok else f"FAIL: nije detektovalo - {msg}")


def test_layout_tall_top_valid():
    """TALL_TOP iznad TALL elementa iste sirine — mora biti OK.
    Slobodan prostor: wall_h(2600) - foot(150) - tall_h(2100) - 5 = 345mm.
    Biramo h=320mm da sigurno stane."""
    k = _kitchen(wall_h_mm=2600, modules=[
        _mod(1, "TALL_PANTRY",    "tall",     5, 600, 2100, 560),
        _mod(2, "TALL_TOP_DOORS", "tall_top", 5, 600,  320, 560),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_tall_top_valid", msg)


def test_layout_touching_is_ok():
    """Elementi koji se samo dotiču (isti kraj/početak) — NE preklapaju se."""
    # Element 1: x=5, w=600 → kraj=605
    # Element 2: x=605, w=600 → pocetak=605 — dodiruju se, ne preklapaju
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR", "base", 5,   600, 720, 560),
        _mod(2, "BASE_1DOOR", "base", 605, 600, 720, 560),
    ])
    ok, msg = layout_audit(k)
    _log(ok, "layout_touching_elements_ok", msg)


# ═════════════════════════════════════════════════════════════════════════════
# OBLAST 2 — DIMENZIJE: FIN = CUT − kanta
# ═════════════════════════════════════════════════════════════════════════════

def _verify_fin_cut(sections: Dict, edge_thk: float, test_prefix: str):
    """
    Za svaki red u carcass, fronts, backs, worktop:
    proveri da je 0 ≤ (CUT - FIN) ≤ 2 × edge_thk
    i da je razlika višekratnik edge_thk.
    """
    chk_sections = ["carcass", "fronts", "backs", "worktop", "drawer_boxes"]
    for sec in chk_sections:
        df = sections.get(sec)
        if df is None or df.empty:
            continue
        for i, row in df.iterrows():
            deo = str(row.get("Deo", row.get("Naziv", "?")))
            cut_w = float(row.get("CUT_W [mm]", row.get("Dužina [mm]", row.get("Duzina [mm]", 0))))
            cut_h = float(row.get("CUT_H [mm]", row.get("Širina [mm]", row.get("Sirina [mm]", 0))))
            fin_w = float(row.get("Dužina [mm]", row.get("Duzina [mm]", 0)))
            fin_h = float(row.get("Širina [mm]", row.get("Sirina [mm]", 0)))

            diff_w = cut_w - fin_w
            diff_h = cut_h - fin_h

            # FIN nikad ne sme biti veći od CUT
            if diff_w < -TOL:
                _log(False, f"{test_prefix}_fin_gt_cut_W",
                     f"{sec} '{deo}': FIN_W={fin_w} > CUT_W={cut_w}")
                return
            if diff_h < -TOL:
                _log(False, f"{test_prefix}_fin_gt_cut_H",
                     f"{sec} '{deo}': FIN_H={fin_h} > CUT_H={cut_h}")
                return

            # Razlika mora biti višekratnik edge_thk (0, 1×, 2×)
            # Dozvoljavamo max 2 ivice kantovane po dimenziji
            if edge_thk > 0:
                # Samo provera za non-trivijalne (cut_w > 10 i cut_h > 10)
                if cut_w > 10 and not (abs(diff_w % edge_thk) < TOL):
                    _log(False, f"{test_prefix}_kant_mult_W",
                         f"{sec} '{deo}': diff_W={diff_w:.2f} nije višekratnik edge_thk={edge_thk}")
                    return
                if cut_h > 10 and not (abs(diff_h % edge_thk) < TOL):
                    _log(False, f"{test_prefix}_kant_mult_H",
                         f"{sec} '{deo}': diff_H={diff_h:.2f} nije višekratnik edge_thk={edge_thk}")
                    return

            # Max 2 ivice po dimenziji
            if diff_w > 2 * edge_thk + TOL:
                _log(False, f"{test_prefix}_kant_max_W",
                     f"{sec} '{deo}': diff_W={diff_w:.2f} > 2×edge_thk={2*edge_thk}")
                return
            if diff_h > 2 * edge_thk + TOL:
                _log(False, f"{test_prefix}_kant_max_H",
                     f"{sec} '{deo}': diff_H={diff_h:.2f} > 2×edge_thk={2*edge_thk}")
                return

    _log(True, f"{test_prefix}_fin_cut_math", "Sve FIN=CUT-kant OK")


def test_dim_base_1door():
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "base_1door")


def test_dim_base_2door():
    k = _kitchen(modules=[_mod(1, "BASE_2DOOR", "base", 5, 800, 720, 560)])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "base_2door")


def test_dim_base_drawers():
    k = _kitchen(modules=[
        _mod(1, "BASE_DRAWERS_3", "base", 5, 600, 720, 560,
             params={"n_drawers": 3, "drawer_heights": [140, 140, 220]})
    ])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "base_drawers3")


def test_dim_wall_2door():
    k = _kitchen(modules=[_mod(1, "WALL_2DOOR", "wall", 5, 800, 700, 320)])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "wall_2door")


def test_dim_tall_pantry():
    k = _kitchen(modules=[_mod(1, "TALL_PANTRY", "tall", 5, 600, 2100, 560)])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "tall_pantry")


def test_dim_mixed_full_kitchen():
    """Kompleksna kuhinja sa svim zonama — verifikacija FIN/CUT za sve delove."""
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR",    "base", 5,    600, 720,  560),
        _mod(2, "BASE_2DOOR",    "base", 605,  800, 720,  560),
        _mod(3, "SINK_BASE",     "base", 1405, 600, 720,  560),
        _mod(4, "WALL_2DOOR",    "wall", 5,    800, 700,  320),
        _mod(5, "WALL_1DOOR",    "wall", 805,  600, 700,  320),
        _mod(6, "TALL_PANTRY",   "tall", 2005, 600, 2100, 560),
        _mod(7, "TALL_TOP_DOORS","tall_top", 2005, 600, 300, 560),
    ])
    _verify_fin_cut(generate_cutlist(k), _edge_thk_from_kitchen(k), "mixed_full_kitchen")


# ═════════════════════════════════════════════════════════════════════════════
# OBLAST 3 — KROJNA LISTA: tačnost količina i sadržaja
# ═════════════════════════════════════════════════════════════════════════════

def test_cutlist_base1door_counts():
    """BASE_1DOOR: tačno 1 vrata, 1 leđna ploča, carcass delovi prisutni."""
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    s = generate_cutlist(k)

    # Fronts: 1 vrata
    fronts = s.get("fronts")
    front_kol = int(fronts["Kol."].sum()) if fronts is not None and not fronts.empty else 0
    _log(front_kol == 1, "base1door_fronts_qty",
         f"OK: 1 vrata" if front_kol == 1 else f"FAIL: {front_kol} vrata (očekivano 1)")

    # Backs: 1 leđna ploča
    backs = s.get("backs")
    back_kol = int(backs["Kol."].sum()) if backs is not None and not backs.empty else 0
    _log(back_kol == 1, "base1door_backs_qty",
         f"OK: 1 leđna ploča" if back_kol == 1 else f"FAIL: {back_kol} (očekivano 1)")

    # Carcass: mora biti popunjen
    carcass = s.get("carcass")
    _log(carcass is not None and not carcass.empty, "base1door_carcass_exists")


def test_cutlist_base2door_counts():
    """BASE_2DOOR: tačno 2 vrata."""
    k = _kitchen(modules=[_mod(1, "BASE_2DOOR", "base", 5, 800, 720, 560)])
    s = generate_cutlist(k)
    fronts = s.get("fronts")
    kol = int(fronts["Kol."].sum()) if fronts is not None and not fronts.empty else 0
    _log(kol == 2, "base2door_fronts_qty",
         f"OK: 2 vrata" if kol == 2 else f"FAIL: {kol} vrata (očekivano 2)")


def test_cutlist_drawers3_counts():
    """BASE_DRAWERS_3: tačno 3 front fioka, 3 sanduka fioke."""
    k = _kitchen(modules=[
        _mod(1, "BASE_DRAWERS_3", "base", 5, 600, 720, 560,
             params={"n_drawers": 3, "drawer_heights": [140, 140, 220]})
    ])
    s = generate_cutlist(k)

    fronts = s.get("fronts")
    f_kol = int(fronts["Kol."].sum()) if fronts is not None and not fronts.empty else 0
    _log(f_kol == 3, "drawers3_fronts_qty",
         f"OK" if f_kol == 3 else f"FAIL: {f_kol} fronts (očekivano 3)")

    drawers = s.get("drawer_boxes")
    # Dno sanduka = broj sanduka (svaki sanduk ima dno)
    if drawers is not None and not drawers.empty:
        dna = int(drawers["Deo"].str.contains("Dno sanduka", case=False, na=False).sum())
        _log(dna == 3, "drawers3_box_qty",
             f"OK" if dna == 3 else f"FAIL: {dna} sanduka (očekivano 3)")
    else:
        _log(False, "drawers3_box_qty", "FAIL: prazna drawer_boxes sekcija")


def test_cutlist_summary_all_sections_present():
    """Sumarna KL mora sadržati Korpus, Leđnu ploču, Front, Radnu ploču i Nosač."""
    k = _kitchen(modules=[
        _mod(1, "BASE_2DOOR", "base", 5,  800, 720, 560),
        _mod(2, "WALL_2DOOR", "wall", 5,  800, 700, 320),
    ])
    s = generate_cutlist(k)
    summary = generate_cutlist_summary(s)
    sa = summary.get("summary_all")

    if sa is None or sa.empty:
        _log(False, "summary_all_not_empty", "FAIL: summary_all je prazan")
        return

    deo_vals = set(sa["Deo"].tolist())

    # Mora biti: Leđna ploča
    has_ledna = any("edna" in d or "le" in d.lower() for d in deo_vals
                    if "plo" in d.lower() or "la" in d.lower())
    _log(has_ledna, "summary_has_ledna_ploca",
         "OK" if has_ledna else f"FAIL: nema Leđne ploče. Ima: {sorted(deo_vals)[:8]}")

    # Mora biti: Nosač radne ploče
    has_nosac = any("osa" in d.lower() for d in deo_vals)
    _log(has_nosac, "summary_has_nosac_rp",
         "OK" if has_nosac else f"FAIL: nema Nosača radne ploče. Ima: {sorted(deo_vals)[:8]}")

    # Mora biti: Radna ploča
    has_radna = any("adna" in d and "plo" in d.lower() for d in deo_vals)
    _log(has_radna, "summary_has_radna_ploca",
         "OK" if has_radna else f"FAIL: nema Radne ploče. Ima: {sorted(deo_vals)[:8]}")

    # Mora biti fronts (vrata)
    has_vrata = any("rata" in d or "ront" in d or "iok" in d for d in deo_vals)
    _log(has_vrata, "summary_has_fronts",
         "OK" if has_vrata else f"FAIL: nema frontova u summary_all")


def test_cutlist_worktop_length():
    """
    Radna ploča: ukupna dužina mora biti >= zbir širina svih BASE modula.
    (može biti malo duža zbog tolerancija, ali ne kraća od 90% zbira.)
    """
    base_w = [600, 800, 600]
    mods = [
        _mod(i + 1, ["BASE_1DOOR","BASE_2DOOR","SINK_BASE"][i], "base",
             sum(base_w[:i]) + 5, w, 720, 560)
        for i, w in enumerate(base_w)
    ]
    k = _kitchen(modules=mods)
    s = generate_cutlist(k)
    worktop = s.get("worktop")
    if worktop is None or worktop.empty:
        _log(False, "worktop_length", "FAIL: nema worktop sekcije")
        return

    # Nađi redove sa 'Radna' u Deo
    rp = worktop[worktop["Deo"].str.contains("Radna", case=False, na=False)]
    if rp.empty:
        _log(False, "worktop_length", "FAIL: nema 'Radna ploča' u worktop sekciji")
        return

    total_wt_w = float(rp["Dužina [mm]"].sum())
    expected_min = sum(base_w) * 0.9

    _log(total_wt_w >= expected_min, "worktop_length",
         f"OK: {total_wt_w:.0f}mm >= {expected_min:.0f}mm (90% od {sum(base_w)}mm)" if total_wt_w >= expected_min
         else f"FAIL: radna ploča {total_wt_w:.0f}mm < min {expected_min:.0f}mm")


def test_cutlist_nosaci_count():
    """Nosači radne ploče: mora biti 2 × broj BASE modula."""
    n_base = 3
    mods = [
        _mod(i + 1, "BASE_1DOOR", "base", i * 605 + 5, 600, 720, 560)
        for i in range(n_base)
    ]
    k = _kitchen(modules=mods)
    s = generate_cutlist(k)
    worktop = s.get("worktop")
    if worktop is None or worktop.empty:
        _log(False, "nosaci_count", "FAIL: nema worktop sekcije")
        return

    nosaci = worktop[worktop["Deo"].str.contains("Nosa", case=False, na=False)]
    total_nosaci = int(nosaci["Kol."].sum()) if not nosaci.empty else 0
    expected = n_base * 2
    _log(total_nosaci == expected, "nosaci_count",
         f"OK: {total_nosaci} nosača (={n_base}×2)" if total_nosaci == expected
         else f"FAIL: {total_nosaci} nosača, očekivano {expected} ({n_base}×2)")


def test_cutlist_worktop_follows_base_span_not_full_wall():
    """Radna ploca treba da prati raspon donjih elemenata, ne celu duzinu zida."""
    mods = [
        _mod(1, "BASE_1DOOR", "base", 5, 400, 720, 560),
        _mod(2, "BASE_2DOOR", "base", 405, 800, 720, 560),
        _mod(3, "WALL_2DOOR", "wall", 5, 800, 720, 320),
    ]
    k = _kitchen(modules=mods)
    k["wall"]["length_mm"] = 2400
    s = generate_cutlist(k)
    worktop = s.get("worktop")
    if worktop is None or worktop.empty:
        _log(False, "worktop_follows_base_span", "FAIL: nema worktop sekcije")
        return

    rp = worktop[worktop["Deo"].str.contains("Radna", case=False, na=False)]
    if rp.empty:
        _log(False, "worktop_follows_base_span", "FAIL: nema reda za radnu plocu")
        return

    wt_len = float(rp["Dužina [mm]"].sum())
    expected = 1220.0
    _log(abs(wt_len - expected) < 0.1, "worktop_follows_base_span",
         f"OK: {wt_len:.0f}mm prati base span (ocekivano {expected:.0f}mm)"
         if abs(wt_len - expected) < 0.1
         else f"FAIL: radna ploca {wt_len:.0f}mm, ocekivano {expected:.0f}mm")


def test_cutlist_cooking_unit_uses_partial_back():
    """Cooking unit treba da dobije parcijalna leđa, ne puna leđa preko cele visine."""
    k = _kitchen(modules=[_mod(1, "BASE_COOKING_UNIT", "base", 5, 600, 720, 560)])
    s = generate_cutlist(k)
    backs = s.get("backs")
    if backs is None or backs.empty:
        _log(False, "cooking_unit_partial_back", "FAIL: nema backs sekcije")
        return
    cu = backs[backs["Modul"].astype(str).str.contains("kuhinjska jedinica", case=False, na=False)]
    if cu.empty:
        _log(False, "cooking_unit_partial_back", "FAIL: nema reda za cooking unit backs")
        return
    deo_vals = " | ".join(cu["Deo"].astype(str).tolist())
    nap_vals = " | ".join(cu["Napomena"].astype(str).tolist())
    has_partial = cu["Deo"].astype(str).str.contains("Parcijalna", case=False, na=False).any()
    mentions_open_zone = cu["Napomena"].astype(str).str.contains("otvorena radi ventilacije", case=False, na=False).any()
    max_back_h = float(cu["Širina [mm]"].max())
    _log(has_partial and mentions_open_zone and max_back_h < 400, "cooking_unit_partial_back",
         f"OK: {deo_vals} / H={max_back_h:.0f}mm"
         if has_partial and mentions_open_zone and max_back_h < 400
         else f"FAIL: deo={deo_vals}; napomena={nap_vals}; H={max_back_h:.0f}mm")


def test_cutlist_no_negative_dimensions():
    """Nijedna ploča ne sme imati negativne dimenzije."""
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR",   "base", 5,   600, 720,  560),
        _mod(2, "BASE_DRAWERS_3","base", 605, 600, 720,  560,
             params={"n_drawers": 3}),
        _mod(3, "WALL_2DOOR",   "wall", 5,   800, 700,  320),
        _mod(4, "TALL_PANTRY",  "tall", 1205, 600, 2100, 560),
    ])
    s = generate_cutlist(k)
    all_neg = []
    for sec in ("carcass", "fronts", "backs", "worktop", "drawer_boxes", "plinth"):
        df = s.get(sec)
        if df is None or df.empty:
            continue
        for col in ("Dužina [mm]", "Širina [mm]", "Duzina [mm]", "Sirina [mm]", "CUT_W [mm]", "CUT_H [mm]"):
            if col not in df.columns:
                continue
            neg = df[df[col] < 0]
            if not neg.empty:
                for _, row in neg.iterrows():
                    all_neg.append(
                        f"{sec}/{row.get('Deo','?')}: {col}={row[col]:.1f}"
                    )
    _log(len(all_neg) == 0, "no_negative_dimensions",
         "OK: sve dimenzije ≥ 0" if not all_neg
         else "FAIL: " + "; ".join(all_neg[:5]))


def test_cutlist_fin_le_module_size():
    """
    FIN dimenzije ploče nikad ne smeju biti veće od dimenzija modula.
    Npr. bočna ploča BASE modula: FIN_W ≤ d_mm, FIN_H ≤ h_mm.
    """
    w, h, d = 600, 720, 560
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, w, h, d)])
    s = generate_cutlist(k)
    carcass = s.get("carcass")
    if carcass is None or carcass.empty:
        _log(False, "fin_le_module", "FAIL: prazna carcass sekcija")
        return

    violations = []
    for _, row in carcass.iterrows():
        fw = float(row.get("Dužina [mm]", row.get("Duzina [mm]", 0)))
        fh = float(row.get("Širina [mm]", row.get("Sirina [mm]", 0)))
        # Nijedna ploča ne sme biti šira od d_mm ili viša od h_mm (uz 5mm tolerancije)
        if fw > d + 5:
            violations.append(f"'{row.get('Deo','?')}': FIN_W={fw:.0f} > d_mm={d}")
        if fh > h + 5:
            violations.append(f"'{row.get('Deo','?')}': FIN_H={fh:.0f} > h_mm={h}")

    _log(len(violations) == 0, "fin_le_module",
         "OK" if not violations else "FAIL: " + "; ".join(violations[:3]))


def test_cutlist_detaljna_has_modul_column():
    """summary_detaljna mora imati Modul kolonu popunjenu za sve redove."""
    k = _kitchen(modules=[
        _mod(1, "BASE_2DOOR", "base", 5, 800, 720, 560),
        _mod(2, "WALL_1DOOR", "wall", 5, 600, 700, 320),
    ])
    s = generate_cutlist(k)
    summary = generate_cutlist_summary(s)
    det = summary.get("summary_detaljna")
    if det is None or det.empty:
        _log(False, "detaljna_modul_col", "FAIL: prazna detaljna tabela")
        return

    has_modul = "Modul" in det.columns
    empty_modul = det["Modul"].isna().any() or (det["Modul"].astype(str).str.strip() == "").any() if has_modul else True
    _log(has_modul and not empty_modul, "detaljna_modul_col",
         "OK" if (has_modul and not empty_modul)
         else f"FAIL: Modul kolona {'nije prisutna' if not has_modul else 'ima praznih vrednosti'}")


# ═════════════════════════════════════════════════════════════════════════════
# OBLAST 4 — OKOVI: šarke, klizači, spojnice
# ═════════════════════════════════════════════════════════════════════════════

def test_hardware_sarke_1door():
    """BASE_1DOOR visine 720mm → tačno 2 šarke."""
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    s = generate_cutlist(k)
    hw = s.get("hardware")
    if hw is None or hw.empty:
        _log(False, "sarke_1door", "FAIL: nema hardware sekcije")
        return
    sarke = hw[hw["Naziv"].str.contains("arke|arka", case=False, na=False)]
    kol = int(sarke["Kol."].sum()) if not sarke.empty else 0
    _log(kol == 2, "sarke_1door_qty",
         f"OK: 2 šarke" if kol == 2 else f"FAIL: {kol} šarki (očekivano 2)")


def test_hardware_sarke_tall_door():
    """TALL element visine 2100mm → vrata viša od 900mm → min 3 šarke po vratima."""
    k = _kitchen(modules=[_mod(1, "TALL_PANTRY", "tall", 5, 600, 2100, 560)])
    s = generate_cutlist(k)
    hw = s.get("hardware")
    if hw is None or hw.empty:
        _log(False, "sarke_tall", "FAIL: nema hardware sekcije")
        return
    sarke = hw[hw["Naziv"].str.contains("arke|arka", case=False, na=False)]
    # Isključi projektne (ID=0) jer su to agregirani
    sarke_mod = sarke[sarke["ID"].astype(str) != "0"]
    kol = int(sarke_mod["Kol."].sum()) if not sarke_mod.empty else int(sarke["Kol."].sum())
    # Za 2100mm vrata: front ≈ 1876mm → > 900mm → 3 šarke
    _log(kol >= 3, "sarke_tall_min3",
         f"OK: {kol} šarki (≥3)" if kol >= 3 else f"FAIL: {kol} šarki, očekivano ≥3")


def test_hardware_klizaci_drawers():
    """BASE_DRAWERS_3 -> tacno 3 klizaca za fioke (1 set po fijoci).
    Napomena: 'Vijak za klizac' su vijci za montazu (drugaciji red), ne klizaci."""
    k = _kitchen(modules=[
        _mod(1, "BASE_DRAWERS_3", "base", 5, 600, 720, 560,
             params={"n_drawers": 3, "drawer_heights": [140, 140, 220]})
    ])
    s = generate_cutlist(k)
    hw = s.get("hardware")
    if hw is None or hw.empty:
        _log(False, "klizaci_drawers", "FAIL: nema hardware")
        return
    # Trazimo "Klizac/Klizac za fioku" — iskljucujemo "Vijak za klizac"
    # "Kliza?" prati i "Klizac" i "Klizac" (sa c-kvaci), koristimo "Kliza" kao prefix
    klizaci = hw[
        hw["Naziv"].str.contains("Kliza", case=False, na=False) &
        ~hw["Naziv"].str.contains("Vijak|vijak|screw", case=False, na=False)
    ]
    kol = int(klizaci["Kol."].sum()) if not klizaci.empty else 0
    _log(kol == 3, "klizaci_drawers_qty",
         f"OK: 3 klizaca za fioke" if kol == 3 else f"FAIL: {kol} klizaca (ocekivano 3)")


def test_drawer_proportional_redistribution():
    """Kad se jedna fioka promeni, ostale zadržavaju proporciju međusobno."""
    vals = redistribute_drawers_proportional(
        [100, 200, 300],
        changed_idx=0,
        requested_height=150,
        total_target=600,
    )
    _log(vals == [150, 180, 270], "drawer_proportional_redistribution",
         f"OK: {vals}" if vals == [150, 180, 270] else f"FAIL: dobijeno {vals}")


def test_drawer_proportional_recalc():
    """Recalc čuva ručno menjane fioke, a ostale vraća proporcionalno."""
    vals = rebalance_drawers_proportional(
        [150, 180, 260],
        fixed_indices={0},
        total_target=600,
        basis_heights=[100, 200, 300],
    )
    _log(vals == [150, 180, 270], "drawer_proportional_recalc",
         f"OK: {vals}" if vals == [150, 180, 270] else f"FAIL: dobijeno {vals}")


def test_hardware_spojnice():
    """Dva susedna BASE elementa → mora biti spojnica korpusa."""
    k = _kitchen(modules=[
        _mod(1, "BASE_1DOOR", "base", 5,   600, 720, 560),
        _mod(2, "BASE_1DOOR", "base", 605, 600, 720, 560),
    ])
    s = generate_cutlist(k)
    hw = s.get("hardware")
    if hw is None or hw.empty:
        _log(False, "spojnice", "FAIL: nema hardware")
        return
    spojnice = hw[hw["Naziv"].str.contains("pojnic|Spojnic", case=False, na=False)]
    kol = int(spojnice["Kol."].sum()) if not spojnice.empty else 0
    _log(kol > 0, "spojnice_exist",
         f"OK: {kol} spojnica" if kol > 0 else "FAIL: nema spojnica za susedne korpuse")


def test_hardware_sokla_klipse():
    """BASE moduli → klipse za soklu mora biti u hardware."""
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    s = generate_cutlist(k)
    hw = s.get("hardware")
    if hw is None or hw.empty:
        _log(False, "sokla_klipse", "FAIL: nema hardware")
        return
    klipse = hw[hw["Naziv"].str.contains("lipsa|klips|Klipsa", case=False, na=False)]
    kol = int(klipse["Kol."].sum()) if not klipse.empty else 0
    _log(kol > 0, "sokla_klipse_exist",
         f"OK: {kol} klipsi" if kol > 0 else "FAIL: nema klipsi za soklu")


# ═════════════════════════════════════════════════════════════════════════════
# OBLAST 5 — EDGE CASES: granični slučajevi koji lako prolaze neopaženo
# ═════════════════════════════════════════════════════════════════════════════

def test_edge_very_narrow_module():
    """Veoma uzak modul (300mm) — dimenzije moraju biti pozitivne."""
    k = _kitchen(modules=[_mod(1, "BASE_NARROW", "base", 5, 300, 720, 560)])
    s = generate_cutlist(k)
    carcass = s.get("carcass")
    if carcass is None or carcass.empty:
        _log(False, "narrow_carcass", "FAIL: prazna carcass za uzak modul")
        return
    neg_dims = []
    for col in ("Dužina [mm]", "Širina [mm]", "Duzina [mm]", "Sirina [mm]"):
        if col in carcass.columns:
            bad = carcass[carcass[col] <= 0]
            if not bad.empty:
                neg_dims.append(f"{col}: {bad[col].tolist()}")
    _log(len(neg_dims) == 0, "narrow_positive_dims",
         "OK" if not neg_dims else "FAIL: " + "; ".join(neg_dims))


def test_edge_very_wide_module():
    """Širok modul (1200mm) — mora proći audit i imati dimenzije."""
    k = _kitchen(wall_mm=3000, modules=[_mod(1, "BASE_2DOOR", "base", 5, 1200, 720, 560)])
    ok, msg = layout_audit(k)
    _log(ok, "wide_module_layout", msg)
    if ok:
        s = generate_cutlist(k)
        _verify_fin_cut(s, _edge_thk_from_kitchen(k), "wide_module_dims")


def test_edge_single_module_only():
    """Kuhinja sa samo jednim elementom — KL mora biti potpuna."""
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    s = generate_cutlist(k)
    for sec in ("carcass", "fronts", "backs"):
        df = s.get(sec)
        _log(df is not None and not df.empty, f"single_module_{sec}",
             f"OK" if (df is not None and not df.empty) else f"FAIL: {sec} je prazan")


def test_edge_no_modules():
    """Prazna kuhinja (bez modula) — generate_cutlist ne sme da crasha."""
    k = _kitchen(modules=[])
    try:
        s = generate_cutlist(k)
        _log(True, "empty_kitchen_no_crash", "OK: prazan kitchen prolazi")
    except Exception as ex:
        _log(False, "empty_kitchen_no_crash", f"FAIL: crash — {ex}")


def test_edge_worktop_disabled():
    """Kuhinja bez radne ploče — worktop sekcija prazna ili None."""
    k = _kitchen(modules=[_mod(1, "BASE_1DOOR", "base", 5, 600, 720, 560)])
    k["worktop"]["enabled"] = False
    try:
        s = generate_cutlist(k)
        # Može biti prazna, ali ne sme da crasha
        _log(True, "worktop_disabled_no_crash", "OK")
    except Exception as ex:
        _log(False, "worktop_disabled_no_crash", f"FAIL: crash — {ex}")


def test_edge_tall_plus_wall_same_position():
    """TALL i WALL na istom X — audit mora detektovati overlap."""
    k = _kitchen(modules=[
        _mod(1, "TALL_PANTRY", "tall", 5, 600, 2100, 560),
        _mod(2, "WALL_1DOOR",  "wall", 5, 600, 700,  320),
    ])
    ok, msg = layout_audit(k)
    _log(not ok, "tall_wall_overlap_detected",
         "OK (TALL+WALL overlap detektovan)" if not ok else f"FAIL: nije detektovalo - {msg}")


# ═════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═════════════════════════════════════════════════════════════════════════════

ALL_TESTS = [
    # Layout
    test_layout_no_overlap_base,
    test_layout_overlap_detected,
    test_layout_outofbounds_detected,
    test_layout_exact_fit,
    test_layout_wall_no_overlap,
    test_layout_tall_no_overlap,
    test_layout_tall_overlap_base_detected,
    test_layout_tall_top_valid,
    test_layout_touching_is_ok,
    # Dimenzije
    test_dim_base_1door,
    test_dim_base_2door,
    test_dim_base_drawers,
    test_dim_wall_2door,
    test_dim_tall_pantry,
    test_dim_mixed_full_kitchen,
    # Krojna lista
    test_cutlist_base1door_counts,
    test_cutlist_base2door_counts,
    test_cutlist_drawers3_counts,
    test_cutlist_summary_all_sections_present,
    test_cutlist_worktop_length,
    test_cutlist_worktop_follows_base_span_not_full_wall,
    test_cutlist_cooking_unit_uses_partial_back,
    test_cutlist_nosaci_count,
    test_cutlist_no_negative_dimensions,
    test_cutlist_fin_le_module_size,
    test_cutlist_detaljna_has_modul_column,
    # Okovi
    test_hardware_sarke_1door,
    test_hardware_sarke_tall_door,
    test_hardware_klizaci_drawers,
    test_drawer_proportional_redistribution,
    test_drawer_proportional_recalc,
    test_hardware_spojnice,
    test_hardware_sokla_klipse,
    # Edge cases
    test_edge_very_narrow_module,
    test_edge_very_wide_module,
    test_edge_single_module_only,
    test_edge_no_modules,
    test_edge_worktop_disabled,
    test_edge_tall_plus_wall_same_position,
]


def _p(text: str) -> None:
    """Print sa ASCII-safe fallbackom (Windows cp1252 konzola)."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def main():
    parser = argparse.ArgumentParser(description="KrojnaListaPRO - geometrijski testovi")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detaljan ispis (i PASS)")
    parser.add_argument("--fail-only", action="store_true", help="Prikazi samo padove")
    args = parser.parse_args()

    verbose = args.verbose
    fail_only = args.fail_only

    _p("=" * 68)
    _p("  KrojnaListaPRO - test_geometry.py")
    _p("=" * 68)

    t_start = time.time()
    for fn in ALL_TESTS:
        before = len(_results)
        try:
            fn()
        except Exception as ex:
            _log(False, fn.__name__, f"EXCEPTION: {ex}")
        after = len(_results)

        # Ispiši rezultate koje je ovaj test zabeležio
        for ok, name, msg in _results[before:after]:
            if fail_only and ok:
                continue
            if verbose or not ok:
                icon = "[PASS]" if ok else "[FAIL]"
                _p(f"  {icon} {name:<45} {msg}")

    elapsed = time.time() - t_start

    passed = sum(1 for ok, _, _ in _results if ok)
    failed = sum(1 for ok, _, _ in _results if not ok)
    total = len(_results)

    _p("")
    _p("=" * 68)
    if failed == 0:
        _p(f"  REZULTAT: {passed}/{total} PASS  ({elapsed:.1f}s)  *** SVE OK ***")
    else:
        _p(f"  REZULTAT: {passed}/{total} PASS | {failed} FAIL  ({elapsed:.1f}s)")
        _p("")
        _p("  PADOVI:")
        for ok, name, msg in _results:
            if not ok:
                _p(f"    [FAIL] {name}")
                _p(f"           {msg}")
    _p("=" * 68)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
