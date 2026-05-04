# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from cutlist import MANUFACTURING_PROFILES


# ---------------------------------------------------------
# Clearance / wall helpers
# ---------------------------------------------------------
def _profile_clearance_mm(kitchen: Dict[str, Any]) -> Tuple[int, int]:
    """
    Vraća (left, right) u mm.
    """
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
        total = int(prof.get("mounting_tolerance_total_mm", left + right))
        left = total // 2
        right = total - left

    if ("mounting_tolerance_total_mm" in mfg) and (
        ("mounting_tolerance_left_mm" not in mfg) and ("mounting_tolerance_right_mm" not in mfg)
    ):
        total = int(mfg.get("mounting_tolerance_total_mm", left + right))
        left = total // 2
        right = total - left

    return left, right


def _wall_len(kitchen: Dict[str, Any], wall_key: str | None = None) -> int:
    wk = str(wall_key or kitchen.get("active_wall_key", "A") or "A").upper()
    wall_map = kitchen.get("wall_lengths_mm", {}) or {}
    if wk in wall_map:
        return int(wall_map[wk])
    wall = kitchen.get("wall", {}) or {}
    return int(wall.get("length_mm", 3000))


def _wall_height(kitchen: Dict[str, Any], wall_key: str | None = None) -> int:
    wk = str(wall_key or kitchen.get("active_wall_key", "A") or "A").upper()
    wall_map = kitchen.get("wall_heights_mm", {}) or {}
    if wk in wall_map:
        return int(wall_map[wk])
    wall = kitchen.get("wall", {}) or {}
    return int(wall.get("height_mm", 2600))


def _get_zone(m: Dict[str, Any]) -> str:
    return str(m.get("zone", "base")).lower().strip()


def _get_wall_key(m: Dict[str, Any]) -> str:
    return str(m.get("wall_key", "A") or "A").upper()


def _wall_match(m: Dict[str, Any], wall_key: str | None) -> bool:
    if wall_key is None:
        return True
    return _get_wall_key(m) == str(wall_key or "A").upper()


def _is_tall_top(m: Dict[str, Any]) -> bool:
    return _get_zone(m) == "tall_top"


def _is_wall_upper(m: Dict[str, Any]) -> bool:
    return _get_zone(m) == "wall_upper"


def _is_fridge_tall(m: Dict[str, Any]) -> bool:
    tid = str(m.get("template_id", "")).upper()
    # Robust: any tall fridge template contains FRIDGE
    if "FRIDGE" in tid:
        return True
    # Optional explicit flag (if you ever add it)
    p = m.get("params", {}) or {}
    return bool(p.get("fridge", False) or p.get("is_fridge", False))


def _tall_base_y_mm(kitchen: Dict[str, Any], tall_mod: Dict[str, Any]) -> int:
    """Y baseline for tall module. Default is foot height, but fridges stand on floor."""
    foot_mm = int(kitchen.get("foot_height_mm", 0) or 0)
    if foot_mm <= 0:
        foot_mm = int(round(float(kitchen.get("foot_height", 10.0)) * 10.0))
    return 0 if _is_fridge_tall(tall_mod) else int(foot_mm)


def _span_x(m: Dict[str, Any]) -> Tuple[int, int]:
    x = int(m.get("x_mm", 0))
    w = int(m.get("w_mm", 0))
    return (x, x + w)


def _overlaps(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def _is_corner_module(m: Dict[str, Any]) -> bool:
    return "CORNER" in str(m.get("template_id", "")).upper()


def _corner_anchor_side(wall_key: str, kitchen: Dict[str, Any]) -> str:
    wk = str(wall_key or "A").upper()
    side = str((kitchen or {}).get("l_corner_side", "right") or "right").lower()
    if side not in ("left", "right"):
        side = "right"
    if wk == "A":
        return side
    if wk in ("B", "C"):
        return "left" if side == "right" else "right"
    return side


def _l_corner_offsets_mm(
    kitchen: Dict[str, Any],
    wall_key: str | None = None,
) -> Tuple[int, int]:
    """
    Vraća (left_offset, right_offset) u mm za ugaonu zaštitu na Wall B/C.

    Problem koji rješava:
        Wall A korpusi imaju dubinu ~560mm koja fizički zauzima ugaoni prostor.
        Taj prostor na Wall B odgovara x=0..560mm (lijevi ugao) ili
        x=(wall_len-560)..wall_len (desni ugao).
        Regularni elementi na Wall B ne smiju ulaziti u tu zonu.

    Ugaoni moduli (CORNER u template_id) su izuzeti — oni se postavljaju
    direktno na anchor poziciju u state_logic.py i ne koriste find_first_free_x().

    Vraća (0, 0) za:
        - jednozidne kuhinje (nije l_oblik)
        - Wall A (referentni zid, bez offseta)

    Vraća (depth, 0) ili (0, depth) za Wall B ovisno o anchor strani.
    depth = d_mm ugaonog modula (ako postoji) ili zone_defaults['base']['d_mm'].
    """
    _kd = kitchen or {}
    _layout = str(_kd.get("layout", _kd.get("kitchen_layout", "")) or "").lower().strip()
    if _layout != "l_oblik":
        return 0, 0

    wk = str(wall_key or "A").upper()
    if wk == "A":
        return 0, 0

    anchor = _corner_anchor_side(wk, kitchen)

    # Dubina: uzmi d_mm corner modula ako postoji, inače zone_defaults baze
    corner_mod = next(
        (m for m in (kitchen.get("modules", []) or [])
         if "CORNER" in str(m.get("template_id", "")).upper()
         and str(m.get("wall_key", "A")).upper() == wk),
        None,
    )
    if corner_mod:
        depth = int(corner_mod.get("d_mm", 560) or 560)
    else:
        zd = (kitchen.get("zone_defaults", {}) or {})
        depth = int(((zd.get("base") or {}).get("d_mm", 560)) or 560)

    # Uzmi stvarni max d_mm svih Wall A baza modula — ako je neki modul
    # (npr. sudopera, aparat) dublji od zone_defaults, ugaona zaštita mora
    # biti bazirana na toj većoj dubini da se izbjegne 3D preklapanje.
    _wall_a_base = [
        m for m in (kitchen.get("modules", []) or [])
        if str(m.get("wall_key", "A")).upper() == "A"
        and str(m.get("zone", "")).lower().strip() in ("base",)
    ]
    _max_wall_a_d = max((int(m.get("d_mm", 0) or 0) for m in _wall_a_base), default=0)
    if _max_wall_a_d > depth:
        depth = _max_wall_a_d

    if anchor == "left":
        result = (depth, 0)   # ugao je lijevo → offset na lijevoj strani
    else:
        result = (0, depth)   # ugao je desno → offset na desnoj strani

    # Invarijanta: tačno jedan offset je > 0 za L-kuhinju, Zid B/C
    assert result[0] >= 0 and result[1] >= 0, (
        f"_l_corner_offsets_mm: negativan offset — wall_key={wk}, anchor={anchor}, depth={depth}"
    )
    assert not (result[0] > 0 and result[1] > 0), (
        f"_l_corner_offsets_mm: oba offseta su > 0 — wall_key={wk}, anchor={anchor}, depth={depth}. "
        "Ugao ne može biti istovremeno na levoj i desnoj strani."
    )
    return result


def _clamp_to_wall(kitchen: Dict[str, Any], m: Dict[str, Any]) -> None:
    wall_len = _wall_len(kitchen, wall_key=_get_wall_key(m))
    left, right = _profile_clearance_mm(kitchen)

    w = int(m.get("w_mm", 0))
    x = int(m.get("x_mm", 0))

    min_x = int(left)
    max_x = int(max(left, wall_len - right - w))
    x = max(min_x, min(x, max_x))
    m["x_mm"] = int(x)


# ---------------------------------------------------------
# Slobodan prostor u zoni
# ---------------------------------------------------------
def available_space_in_zone(kitchen: Dict[str, Any], zone: str, wall_key: str | None = None) -> int:
    """
    Koliko mm slobodnog prostora ima u zoni (uzimajući u obzir clearance i postojeće module).
    Za tall_top: gleda slobodne X pozicije koje IMAJU tall element ispod,
    ali NEMA tall_top element na istom X.
    """
    z = (zone or "base").lower().strip()
    wall_len = _wall_len(kitchen, wall_key=wall_key)
    left, right = _profile_clearance_mm(kitchen)
    usable = wall_len - left - right

    mods = [m for m in (kitchen.get("modules", []) or []) if _wall_match(m, wall_key)]

    if z == "tall_top":
        # Slobodan prostor = suma širina tall elemenata koji nemaju tall_top
        tall_mods = [m for m in mods if _get_zone(m) == "tall"]
        tall_top_mods = [m for m in mods if _get_zone(m) == "tall_top"]
        tt_spans = [_span_x(m) for m in tall_top_mods]
        free = 0
        for t in tall_mods:
            ts = _span_x(t)
            covered = any(_overlaps(ts, tts) for tts in tt_spans)
            if not covered:
                free += ts[1] - ts[0]
        return max(0, free)
    elif z == "wall_upper":
        # Slobodan prostor = suma širina wall elemenata koji nemaju wall_upper
        wall_mods = [m for m in mods if _get_zone(m) == "wall"]
        wall_upper_mods = [m for m in mods if _get_zone(m) == "wall_upper"]
        wu_spans = [_span_x(m) for m in wall_upper_mods]
        free = 0
        for w in wall_mods:
            ws = _span_x(w)
            covered = any(_overlaps(ws, wus) for wus in wu_spans)
            if not covered:
                free += ws[1] - ws[0]
        return max(0, free)
    elif z in ("base", "wall"):
        zone_mods = [m for m in mods if _get_zone(m) == z]
        tall_mods = [m for m in mods if _get_zone(m) == "tall"]
        used = sum(int(m.get("w_mm", 0)) + int(m.get("gap_after_mm", 0)) for m in zone_mods)
        tall_used = sum(int(m.get("w_mm", 0)) for m in tall_mods)
        return max(0, usable - used - tall_used)
    elif z == "tall":
        # Visoki elementi ne mogu biti na istom podu kao donji (base) elementi.
        # Slobodan prostor = ukupno - zauzeto tall elementima - zauzeto base elementima.
        tall_mods = [m for m in mods if _get_zone(m) == "tall"]
        base_mods = [m for m in mods if _get_zone(m) == "base"]
        tall_used = sum(int(m.get("w_mm", 0)) + int(m.get("gap_after_mm", 0)) for m in tall_mods)
        base_used = sum(int(m.get("w_mm", 0)) + int(m.get("gap_after_mm", 0)) for m in base_mods)
        return max(0, usable - tall_used - base_used)
    else:
        all_mods = [m for m in mods if _get_zone(m) == z]
        used = sum(int(m.get("w_mm", 0)) + int(m.get("gap_after_mm", 0)) for m in all_mods)
        return max(0, usable - used)


def suggest_tall_top_height(kitchen: Dict[str, Any], tall_id: int, wall_key: str | None = None) -> int:
    """
    Sugeriše visinu elementa iznad visokog (tall_top).
    = plafon - stopica - visina tall elementa - 50mm (min razmak do plafona)
    Vraća 0 ako nema prostora.
    """
    mods = [m for m in (kitchen.get("modules", []) or []) if _wall_match(m, wall_key)]
    tall = next((m for m in mods if int(m.get("id", -1)) == tall_id and _get_zone(m) == "tall"), None)
    if not tall:
        return 0

    wall_h = _wall_height(kitchen, wall_key=wall_key)
    foot_mm = int(round(float(kitchen.get("foot_height_mm", kitchen.get("foot_height", 10.0) * 10.0 if "foot_height_mm" not in kitchen else 0))))
    if "foot_height_mm" in kitchen:
        foot_mm = int(kitchen["foot_height_mm"])
    else:
        foot_mm = int(round(float(kitchen.get("foot_height", 10.0)) * 10.0))

    tall_h = int(tall.get("h_mm", 0))
    tall_top_y = _tall_base_y_mm(kitchen, tall) + tall_h  # Y gde počinje prostor iznad tall-a
    available = wall_h - tall_top_y - 50  # 50mm slobodno do plafona
    return max(0, available)


def suggest_wall_upper_height(kitchen: Dict[str, Any], wall_id: int, wall_key: str | None = None) -> int:
    """
    Sugeriše visinu wall_upper elementa iznad wall elementa.
    = plafon - (wall_gap + wall_h_elem) - 5mm tolerancija
    Vraća 0 ako nema prostora ili wall element nije pronađen.
    """
    mods = [m for m in (kitchen.get("modules", []) or []) if _wall_match(m, wall_key)]
    wall_mod = next(
        (m for m in mods if int(m.get("id", -1)) == wall_id and _get_zone(m) == "wall"),
        None,
    )
    if not wall_mod:
        return 0

    wall_h = _wall_height(kitchen, wall_key=wall_key)

    # Čitaj zones dict da nađemo wall_gap (isto kao _zone_baseline_and_height u visualization.py)
    zones = (kitchen.get("zones", {}) or {})
    wall_gap = int((zones.get("wall", {}) or {}).get("gap_from_base_mm", 0))
    if wall_gap == 0:
        # Fallback: izračunaj iz parametara kuhinje (isto kao _compute_zones u utils.py)
        if "foot_height_mm" in kitchen:
            foot_mm = int(kitchen["foot_height_mm"])
        else:
            foot_mm = int(round(float(kitchen.get("foot_height", 10.0)) * 10.0))
        base_h = int(kitchen.get("base_korpus_h_mm", 720))
        wt = kitchen.get("worktop", {}) or {}
        worktop_thk_mm = int(round(float(wt.get("thickness", 4.0)) * 10.0))
        if "vertical_gap_mm" in kitchen:
            vgap = int(kitchen["vertical_gap_mm"])
        else:
            vgap = int(round(float(kitchen.get("vertical_gap", 60.0)) * 10.0))
        wall_gap = foot_mm + base_h + worktop_thk_mm + vgap

    wall_h_elem = int(wall_mod.get("h_mm", 720))
    wall_upper_y_start = wall_gap + wall_h_elem
    available = wall_h - wall_upper_y_start - 5
    return max(0, available)


# ---------------------------------------------------------
# Zone pack (existing)
# ---------------------------------------------------------
def _reflow_zone_pack(kitchen: Dict[str, Any], zone: str, wall_key: str | None = None) -> None:
    """
    Pack unutar zone: slaže elemente sleva->desno bez preklapanja.
    Novi element koji je dodat ide na kraj ili slobodnu poziciju.
    """
    z = zone.lower().strip()
    if z not in ("base", "wall", "tall"):
        return

    mods = [
        m for m in (kitchen.get("modules", []) or [])
        if _get_zone(m) == z and _wall_match(m, wall_key)
    ]
    if not mods:
        return

    mods.sort(key=lambda m: int(m.get("x_mm", 0)))

    wall_len = _wall_len(kitchen, wall_key=wall_key)
    left, right = _profile_clearance_mm(kitchen)

    _manual_mods = [m for m in mods if bool(m.get("manual_x", False))]
    _regular_mods = [m for m in mods if not bool(m.get("manual_x", False))]
    _manual_spans = sorted(_span_x(m) for m in _manual_mods)

    def _overlaps_manual(x: int, w: int) -> Tuple[bool, int]:
        seg = (x, x + w)
        for (a, b) in _manual_spans:
            if _overlaps(seg, (a, b)):
                return True, int(b)
        return False, x

    cursor = int(left)
    for m in _regular_mods:
        w = int(m.get("w_mm", 0))
        gap = int(m.get("gap_after_mm", 0))

        x = int(m.get("x_mm", 0))
        x = max(x, cursor)
        while True:
            ov, jump_to = _overlaps_manual(x, w)
            if not ov:
                break
            x = int(jump_to)

        max_x = int(max(left, wall_len - right - w))
        if x > max_x:
            x = max_x

        m["x_mm"] = int(x)
        cursor = int(x + w + gap)

    for cur in mods:
        _clamp_to_wall(kitchen, cur)


# ---------------------------------------------------------
# Free-slot finder (used by suggest_next_x)
# ---------------------------------------------------------
def _effective_span_with_gap(m: Dict[str, Any]) -> Tuple[int, int]:
    x = int(m.get("x_mm", 0))
    w = int(m.get("w_mm", 0))
    gap = int(m.get("gap_after_mm", 0))
    return (x, x + w + gap)


def find_first_free_x(
    kitchen: Dict[str, Any],
    zone: str,
    w_mm: int,
    forbidden_spans: List[Tuple[int, int]] | None = None,
    start_x: int | None = None,
    wall_key: str | None = None,
) -> int:
    """
    Nalazi prvi slobodan X u mm (sa korakom 5mm).

    Za tall_top: mora da se poklapa sa X nekog tall elementa,
    i ne sme da se preklapa sa već postojećim tall_top elementima.
    Vraća -1 ako nema slobodnog mesta.

    forbidden_spans: lista (x_start, x_end) koja dolazi iz room_constraints
    (otvori, vrata, prozori) — auto-placement ih preskače.

    start_x: ako je zadano, skeniranje počinje od max(left, start_x).
             Korisno za click-to-place na canvasu — postavljanje blizu kliknutog mjesta.
    """
    z = (zone or "base").lower().strip()
    w = int(w_mm or 1)

    wall_len = _wall_len(kitchen, wall_key=wall_key)
    left, right = _profile_clearance_mm(kitchen)
    step = 5

    mods = [m for m in (kitchen.get("modules", []) or []) if _wall_match(m, wall_key)]

    # Zabranjeni X-rasponovi iz prostorije (prozori, vrata)
    _forbidden: List[Tuple[int, int]] = list(forbidden_spans or [])

    # Specijalna logika za tall_top
    if z == "tall_top":
        tall_mods = [m for m in mods if _get_zone(m) == "tall"]
        tall_top_mods = [m for m in mods if _get_zone(m) == "tall_top"]
        tt_spans = [_span_x(m) for m in tall_top_mods]

        # Traži tall element koji nema tall_top i čija širina >= w
        for t in sorted(tall_mods, key=lambda m: int(m.get("x_mm", 0))):
            ts = _span_x(t)
            tw = ts[1] - ts[0]
            if tw < w:
                continue
            # Proveri da li ima tall_top na ovom X
            covered = any(_overlaps(ts, tts) for tts in tt_spans)
            if not covered:
                # Provjeri i zabranjene rasponove
                if not any(_overlaps(ts, fb) for fb in _forbidden):
                    return ts[0]  # vrati X tall elementa
        return -1

    # Specijalna logika za wall_upper
    if z == "wall_upper":
        wall_mods = [m for m in mods if _get_zone(m) == "wall"]
        wall_upper_mods = [m for m in mods if _get_zone(m) == "wall_upper"]
        wu_spans = [_span_x(m) for m in wall_upper_mods]

        # Traži wall element koji nema wall_upper i čija širina >= w
        for wm in sorted(wall_mods, key=lambda m: int(m.get("x_mm", 0))):
            ws = _span_x(wm)
            tw = ws[1] - ws[0]
            if tw < w:
                continue
            # Proveri da li ima wall_upper na ovom X
            covered = any(_overlaps(ws, wus) for wus in wu_spans)
            if not covered:
                if not any(_overlaps(ws, fb) for fb in _forbidden):
                    return ws[0]  # vrati X wall elementa
        return -1

    tall_spans = [_span_x(m) for m in mods if _get_zone(m) == "tall"]

    if z == "tall":
        occ = [_effective_span_with_gap(m) for m in mods if _get_zone(m) != "tall_top"]
    else:
        occ = [_effective_span_with_gap(m) for m in mods if _get_zone(m) == z]
        occ = occ + [(a, b) for (a, b) in tall_spans]

    # Dodaj zabranjene rasponove iz prostorije u listu zauzetih
    occ = occ + _forbidden

    # Ugaoni offset za L-kuhinju: Wall B elementi ne smiju biti u ugaonoj zoni Wall A
    _left_off, _right_off = _l_corner_offsets_mm(kitchen, wall_key)
    _eff_left = max(int(left), _left_off)
    _eff_right = int(right) + _right_off

    def fits(x: int) -> bool:
        if x < _eff_left:
            return False
        if (x + w) > (wall_len - _eff_right):
            return False
        span = (x, x + w)
        for (a, b) in occ:
            if _overlaps(span, (a, b)):
                return False
        return True

    x = max(_eff_left, int(start_x)) if start_x is not None else _eff_left
    while x + w <= wall_len - _eff_right:
        if fits(x):
            return int(x)
        x += step

    return -1  # nema slobodnog mesta


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def solve_layout(
    kitchen: Dict[str, Any],
    zone: str | None = None,
    mode: str = "pack",
    wall_key: str | None = None,
) -> Dict[str, Any]:
    """
    mode:
      - "pack"  : slaganje bez praznina — base/wall koriste _compact_zone_skip_tall
                  (cursor-based, nema rupa, skače preko tall span-ova)
      - "insert": ne preslaže postojeće, samo clampuje sve
    """
    mode = (mode or "pack").lower().strip()

    mods = [m for m in (kitchen.get("modules", []) or []) if _wall_match(m, wall_key)]
    for m in mods:
        _clamp_to_wall(kitchen, m)

    if mode == "insert":
        return kitchen

    # pack (default) — base/wall koriste compact (bez praznina), tall koristi reflow
    tall_spans = _tall_anchor_spans(kitchen, wall_key=wall_key)
    if zone is None:
        for z in ("base", "wall"):
            _compact_zone_skip_tall(kitchen, z, tall_spans=tall_spans, wall_key=wall_key)
        _reflow_zone_pack(kitchen, "tall", wall_key=wall_key)
        # tall_top i wall_upper se ne preslaguju automatski (vezani su za parent element)
    else:
        z_norm = str(zone).lower().strip()
        if z_norm not in ("tall_top", "wall_upper"):
            if z_norm in ("base", "wall"):
                _compact_zone_skip_tall(kitchen, z_norm, tall_spans=tall_spans, wall_key=wall_key)
            else:
                _reflow_zone_pack(kitchen, z_norm, wall_key=wall_key)
        # tall_top / wall_upper: samo clamp (ne preslaži)

    return kitchen


# ---------------------------------------------------------
# Compact after swap/delete (only when explicitly called)
# ---------------------------------------------------------
def _compact_zone_skip_tall(
    kitchen: Dict[str, Any],
    zone: str,
    *,
    tall_spans: List[Tuple[int, int]],
    wall_key: str | None = None,
) -> None:
    """
    Kompaktno slaganje elemenata u zoni sleva->desno, BEZ praznih rupa osim gap_after_mm,
    uz zabranu ulaska u TALL span-ove.
    """
    z = (zone or "").lower().strip()
    if z not in ("base", "wall"):
        return

    mods = [
        m for m in (kitchen.get("modules", []) or [])
        if _get_zone(m) == z and _wall_match(m, wall_key)
    ]
    if not mods:
        return

    mods.sort(key=lambda m: int(m.get("x_mm", 0)))

    left, _ = _profile_clearance_mm(kitchen)

    # Ugaoni offset za L-kuhinju: Wall B regularni elementi ne smiju biti u ugaonoj zoni
    _left_off, _right_off = _l_corner_offsets_mm(kitchen, wall_key)

    # Ugaoni i ručno pozicionirani moduli ostaju na svojoj poziciji — odvajamo ih od regularnih modula.
    _corner_mods = [m for m in mods if _is_corner_module(m)]
    _manual_mods = [m for m in mods if bool(m.get("manual_x", False)) and not _is_corner_module(m)]
    _regular_mods = [m for m in mods if not _is_corner_module(m) and not bool(m.get("manual_x", False))]

    spans = [(int(a), int(b)) for (a, b) in (tall_spans or []) if int(b) > int(a)]
    # Ugaoni moduli kao prepreka za regularne module (ne preslagujemo ih)
    spans.extend(_span_x(cm) for cm in _corner_mods)
    # Ručno pozicionirani moduli kao prepreka za regularne module (poštujemo korisnikov X).
    spans.extend(_span_x(mm) for mm in _manual_mods)
    # Virtualna desna ugaona prepreka (bez corner modula, ali postoji desni offset)
    if _right_off > 0 and not _corner_mods:
        _wl = _wall_len(kitchen, wall_key=wall_key)
        _, _r = _profile_clearance_mm(kitchen)
        spans.append((_wl - int(_r) - _right_off, _wl))
    spans.sort(key=lambda p: p[0])

    def overlaps_any(x: int, w: int) -> Tuple[bool, int]:
        seg = (x, x + w)
        for (a, b) in spans:
            if _overlaps(seg, (a, b)):
                return True, int(b)
        return False, x

    # Kursor za regularne module kreće od lijevog ugaonog offseta (ili normalnog left)
    cursor = max(int(left), _left_off)
    for m in _regular_mods:
        w = int(m.get("w_mm", 0))
        gap = int(m.get("gap_after_mm", 0))

        while True:
            ov, jump_to = overlaps_any(cursor, w)
            if not ov:
                break
            cursor = int(jump_to)

        m["x_mm"] = int(cursor)
        cursor = int(cursor + w + gap)

    for m in mods:
        _clamp_to_wall(kitchen, m)


def _tall_anchor_spans(kitchen: Dict[str, Any], wall_key: str | None = None) -> List[Tuple[int, int]]:
    tall = [
        m for m in (kitchen.get("modules", []) or [])
        if _get_zone(m) == "tall" and _wall_match(m, wall_key)
    ]
    return [_span_x(t) for t in tall]


def _needs_left_right_by_side(mods_in_zone: List[Dict[str, Any]], tall_x: int) -> Tuple[int, int]:
    left_need = 0
    right_need = 0
    for m in mods_in_zone:
        x = int(m.get("x_mm", 0))
        w = int(m.get("w_mm", 0))
        gap = int(m.get("gap_after_mm", 0))
        if x < tall_x:
            left_need += w + gap
        else:
            right_need += w + gap
    return int(left_need), int(right_need)


def compact_after_swap_delete(
    kitchen: Dict[str, Any],
    *,
    zones: Tuple[str, ...] = ("base", "wall"),
    allow_tall_shift: bool = True,
    wall_key: str | None = None,
) -> Dict[str, Any]:
    """
    Specijalna logika za swap/delete: kompaktno slaganje bez rupa.
    """
    zones_norm = tuple((z or "").lower().strip() for z in zones if (z or "").lower().strip() in ("base", "wall"))
    if not zones_norm:
        return kitchen

    solve_layout(kitchen=kitchen, zone=None, mode="insert", wall_key=wall_key)

    tall_spans = _tall_anchor_spans(kitchen, wall_key=wall_key)
    for z in zones_norm:
        _compact_zone_skip_tall(kitchen, z, tall_spans=tall_spans, wall_key=wall_key)

    ok, _ = layout_audit(kitchen)
    if ok:
        return kitchen

    if not allow_tall_shift:
        return kitchen

    tall = [
        m for m in (kitchen.get("modules", []) or [])
        if _get_zone(m) == "tall" and _wall_match(m, wall_key)
    ]
    if len(tall) != 1:
        return kitchen

    t = tall[0]
    wall_len = _wall_len(kitchen, wall_key=wall_key)
    left_clear, right_clear = _profile_clearance_mm(kitchen)
    tw = int(t.get("w_mm", 0))
    cur_tx = int(t.get("x_mm", 0))

    left_need_max = 0
    right_need_max = 0
    for z in zones_norm:
        mods_z = [
            m for m in (kitchen.get("modules", []) or [])
            if _get_zone(m) == z and _wall_match(m, wall_key)
        ]
        ln, rn = _needs_left_right_by_side(mods_z, cur_tx)
        left_need_max = max(left_need_max, ln)
        right_need_max = max(right_need_max, rn)

    min_tx = int(left_clear + left_need_max)
    max_tx = int(wall_len - right_clear - tw - right_need_max)

    if min_tx > max_tx:
        return kitchen

    new_tx = int(min(max(cur_tx, min_tx), max_tx))
    t["x_mm"] = int(new_tx)
    _clamp_to_wall(kitchen, t)

    solve_layout(kitchen=kitchen, zone=None, mode="insert", wall_key=wall_key)
    tall_spans = _tall_anchor_spans(kitchen, wall_key=wall_key)
    for z in zones_norm:
        _compact_zone_skip_tall(kitchen, z, tall_spans=tall_spans, wall_key=wall_key)

    return kitchen


def suggest_next_x(kitchen: Dict[str, Any], zone: str, w_mm: int | None = None, wall_key: str | None = None) -> int:
    """
    AUTO X: nalazi prvi slobodan X.
    Ako nema slobodnog mesta, vraća left clearance (korisnik će dobiti grešku iz audit-a).
    """
    z = (zone or "base").lower().strip()
    w = int(w_mm) if w_mm is not None else 1
    result = find_first_free_x(kitchen=kitchen, zone=z, w_mm=w, wall_key=wall_key)
    if result < 0:
        # Nema slobodnog mesta — vrati left da audit uhvati overlap i da korisnik vidi jasnu poruku
        left, _ = _profile_clearance_mm(kitchen)
        return int(left)
    return int(result)


def layout_audit(kitchen: Dict[str, Any]) -> tuple[bool, str]:
    """
    Provera:
      - nema out-of-bounds (uz clearance)
      - nema overlap unutar iste zone
      - TALL ne sme da preklapa BASE/WALL po X
      - TALL_TOP mora biti tačno iznad TALL elementa (isti X span ili manji)
      - TALL_TOP h_mm ne sme prekoračiti slobodan prostor iznad TALL-a
    """
    try:
        left, right = _profile_clearance_mm(kitchen)

        mods = kitchen.get("modules", []) or []
        walls = sorted({_get_wall_key(m) for m in mods}) or ["A"]

        # Foot mm
        if "foot_height_mm" in kitchen:
            foot_mm = int(kitchen["foot_height_mm"])
        else:
            foot_mm = int(round(float(kitchen.get("foot_height", 10.0)) * 10.0))

        # bounds — tall_top i wall_upper nisu ograničeni na wall clearance L/R već na parent span
        for wk in walls:
            wall_len = _wall_len(kitchen, wall_key=wk)
            mods_w = [m for m in mods if _get_wall_key(m) == wk]
            for m in mods_w:
                z = _get_zone(m)
                x = int(m.get("x_mm", 0))
                w = int(m.get("w_mm", 0))
                if z in ("tall_top", "wall_upper"):
                    continue  # bounds za tall_top/wall_upper se proveravaju posebno
                if x < left or (x + w) > (wall_len - right):
                    return (False, f"Out-of-bounds: wall={wk} id={m.get('id')} span=({x}..{x+w}) wall=({left}..{wall_len-right})")

        # Ugaona zona zaštita za L-kuhinju (Wall B/C regularni elementi)
        _kd_audit = kitchen or {}
        _layout_audit = str(_kd_audit.get("layout", _kd_audit.get("kitchen_layout", "")) or "").lower().strip()
        if _layout_audit == "l_oblik":
            for wk in walls:
                if wk == "A":
                    continue
                _wl = _wall_len(kitchen, wall_key=wk)
                _lo, _ro = _l_corner_offsets_mm(kitchen, wk)
                mods_wk = [m for m in mods if _get_wall_key(m) == wk]
                for m in mods_wk:
                    if _is_corner_module(m):
                        continue
                    _x = int(m.get("x_mm", 0))
                    _w = int(m.get("w_mm", 0))
                    if _lo > 0 and _x < _lo:
                        return (
                            False,
                            f"Corner offset Wall {wk}: id={m.get('id')} x={_x} < left_offset={_lo}mm. "
                            f"Baza Zida A zauzima ugaoni prostor ({_lo}mm dubine)."
                        )
                    if _ro > 0 and (_x + _w) > (_wl - right - _ro):
                        return (
                            False,
                            f"Corner offset Wall {wk}: id={m.get('id')} kraj={_x + _w} > granica={_wl - right - _ro}mm. "
                            f"Baza Zida A zauzima ugaoni prostor ({_ro}mm dubine)."
                        )

        def spans(lst):
            return [(m, _span_x(m)) for m in lst]

        def any_overlap(pairs):
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    if _overlaps(pairs[i][1], pairs[j][1]):
                        return (pairs[i][0], pairs[j][0])
            return None

        for wk in walls:
            wall_h = _wall_height(kitchen, wall_key=wk)
            wall_len = _wall_len(kitchen, wall_key=wk)
            mods_w = [m for m in mods if _get_wall_key(m) == wk]
            base = [m for m in mods_w if _get_zone(m) == "base"]
            wall_mods = [m for m in mods_w if _get_zone(m) == "wall"]
            tall = [m for m in mods_w if _get_zone(m) == "tall"]
            tall_top = [m for m in mods_w if _get_zone(m) == "tall_top"]
            wall_upper = [m for m in mods_w if _get_zone(m) == "wall_upper"]

            ov = any_overlap(spans(base))
            if ov:
                return (False, f"Overlap BASE ({wk}): id={ov[0].get('id')} & id={ov[1].get('id')}")
            ov = any_overlap(spans(wall_mods))
            if ov:
                return (False, f"Overlap WALL ({wk}): id={ov[0].get('id')} & id={ov[1].get('id')}")
            ov = any_overlap(spans(tall))
            if ov:
                return (False, f"Overlap TALL ({wk}): id={ov[0].get('id')} & id={ov[1].get('id')}")
            ov = any_overlap(spans(tall_top))
            if ov:
                return (False, f"Overlap TALL_TOP ({wk}): id={ov[0].get('id')} & id={ov[1].get('id')}")
            ov = any_overlap(spans(wall_upper))
            if ov:
                return (False, f"Overlap WALL_UPPER ({wk}): id={ov[0].get('id')} & id={ov[1].get('id')}")

            for _zone_name, _zone_mods in (("BASE", base), ("WALL", wall_mods)):
                _corners = [m for m in _zone_mods if _is_corner_module(m)]
                if len(_corners) > 1:
                    return (False, f"{_zone_name} ({wk}) ima vise ugaonih elemenata u istom kraku.")
                if not _corners:
                    continue
                _corner = _corners[0]
                _x0, _x1 = _span_x(_corner)
                _anchor = _corner_anchor_side(wk, kitchen)
                if _anchor == "right":
                    if abs((wall_len - right) - _x1) > 5:
                        return (False, f"{_zone_name}_CORNER ({wk}) id={_corner.get('id')} mora biti naslonjen na unutrasnji ugao desno.")
                    if any(int(m.get("x_mm", 0)) > _x0 for m in _zone_mods if int(m.get("id", -1)) != int(_corner.get("id", -1))):
                        return (False, f"{_zone_name}_CORNER ({wk}) id={_corner.get('id')} mora biti poslednji element na kraku.")
                else:
                    if abs(_x0 - left) > 5:
                        return (False, f"{_zone_name}_CORNER ({wk}) id={_corner.get('id')} mora biti naslonjen na unutrasnji ugao levo.")
                    if any((int(m.get("x_mm", 0)) + int(m.get("w_mm", 0))) < _x1 for m in _zone_mods if int(m.get("id", -1)) != int(_corner.get("id", -1))):
                        return (False, f"{_zone_name}_CORNER ({wk}) id={_corner.get('id')} mora biti prvi element na kraku.")

            # TALL vs BASE/WALL
            for t in tall:
                ts = _span_x(t)
                for b in base:
                    if _overlaps(ts, _span_x(b)):
                        return (False, f"TALL overlaps BASE ({wk}): tall id={t.get('id')} & base id={b.get('id')}")
                for wm in wall_mods:
                    if _overlaps(ts, _span_x(wm)):
                        return (False, f"TALL overlaps WALL ({wk}): tall id={t.get('id')} & wall id={wm.get('id')}")

            # TALL_TOP: mora biti unutar X spana nekog TALL elementa,
            #           i visina ne sme prekoračiti slobodan prostor iznad tog TALL-a
            for tt in tall_top:
                tt_span = _span_x(tt)
                tt_h = int(tt.get("h_mm", 0))
                # Nađi tall ispod
                parent_tall = None
                for t in tall:
                    ts = _span_x(t)
                    if ts[0] <= tt_span[0] and ts[1] >= tt_span[1]:
                        parent_tall = t
                        break
                if parent_tall is None:
                    return (False, f"TALL_TOP ({wk}) id={tt.get('id')} nema pun oslonac na TALL elementu ispod.")

                tall_h = int(parent_tall.get("h_mm", 0))
                # Y odakle počinje prostor iznad tall-a
                tall_top_y_start = _tall_base_y_mm(kitchen, parent_tall) + tall_h
                # Slobodan prostor do plafona (minus 5mm tolerancija)
                available_h = wall_h - tall_top_y_start - 5
                if tt_h > available_h:
                    return (
                        False,
                        f"TALL_TOP ({wk}) id={tt.get('id')} visina {tt_h}mm prekoracuje slobodan prostor "
                        f"iznad visokog elementa ({available_h}mm). "
                        f"Smanji visinu na max {available_h}mm."
                    )

        # WALL_UPPER: mora biti iznad WALL elementa,
        #             i visina ne sme prekoračiti slobodan prostor do plafona
        zones = (kitchen.get("zones", {}) or {})
        wall_gap = int((zones.get("wall", {}) or {}).get("gap_from_base_mm", 0))
        if wall_gap == 0:
            if "foot_height_mm" in kitchen:
                _foot = int(kitchen["foot_height_mm"])
            else:
                _foot = int(round(float(kitchen.get("foot_height", 10.0)) * 10.0))
            _base_h = int(kitchen.get("base_korpus_h_mm", 720))
            _wt = kitchen.get("worktop", {}) or {}
            _wt_thk = int(round(float(_wt.get("thickness", 4.0)) * 10.0))
            if "vertical_gap_mm" in kitchen:
                _vgap = int(kitchen["vertical_gap_mm"])
            else:
                _vgap = int(round(float(kitchen.get("vertical_gap", 60.0)) * 10.0))
            wall_gap = _foot + _base_h + _wt_thk + _vgap

        for wk in walls:
            mods_w = [m for m in mods if _get_wall_key(m) == wk]
            wall_mods = [m for m in mods_w if _get_zone(m) == "wall"]
            wall_upper = [m for m in mods_w if _get_zone(m) == "wall_upper"]
            for wu in wall_upper:
                wu_span = _span_x(wu)
                wu_h = int(wu.get("h_mm", 0))
                # Nađi wall element ispod
                parent_wall = None
                for wm in wall_mods:
                    ws = _span_x(wm)
                    if ws[0] <= wu_span[0] and ws[1] >= wu_span[1]:
                        parent_wall = wm
                        break
                if parent_wall is None:
                    return (False, f"WALL_UPPER ({wk}) id={wu.get('id')} nema pun oslonac na WALL elementu ispod.")

                wall_h_elem = int(parent_wall.get("h_mm", 720))
                wu_y_start = wall_gap + wall_h_elem
                available_h = wall_h - wu_y_start - 5
                if wu_h > available_h:
                    return (
                        False,
                        f"WALL_UPPER ({wk}) id={wu.get('id')} visina {wu_h}mm prekoracuje slobodan prostor "
                        f"iznad gornjeg elementa ({available_h}mm). "
                        f"Smanji visinu na max {available_h}mm."
                    )

        return (True, "OK")

    except Exception as e:
        return (False, f"Audit exception: {e}")

