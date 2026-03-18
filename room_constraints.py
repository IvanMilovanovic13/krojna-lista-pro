# -*- coding: utf-8 -*-
"""
Konvertuje podatke prostorije (otvori, instalacije) u constraints za layout engine.

Koristi se pri:
  - dodavanju elemenata (add_module_instance_local)
  - auto-pronalasku slobodnog X (find_first_free_x)
  - audit-u layouta
  - 2D prikazu (zabranjene zone u boji)
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


# ── Tip constraint-a ──────────────────────────────────────────────────────────
# {
#   'x_start'      : int   — mm od lijevog kraja zida
#   'x_end'        : int   — mm od lijevog kraja zida
#   'blocked_zones': list  — podskup ['base','wall','wall_upper','tall','tall_top']
#   'type'         : str   — 'vrata' | 'prozor' | 'voda' | 'struja' | 'gas'
#   'label'        : str   — human-readable naziv za poruku greške/upozorenja
#   'y_mm'         : int   — Y od poda (parapetna visina za prozor / visina inst.)
#   'is_hard'      : bool  — True=blokira (ValueError), False=upozorenje
# }


def get_wall_constraints(
    room: dict,
    wall_key: str,
    kitchen: dict,
) -> List[Dict[str, Any]]:
    """
    Vraća listu constraint-a za dati zid prostorije.

    Otvori (vrata, prozori) → hard constraint (blokira postavljanje elementa).
    Instalacije (voda, struja, gas) → soft constraint (samo upozorenje).
    """
    if not room:
        return []
    try:
        from ui_room_helpers import get_room_wall, ensure_room_walls
        ensure_room_walls(room)
        wall = get_room_wall(room, wall_key)
    except Exception:
        return []

    base_h   = int(kitchen.get('base_korpus_h_mm', 720))
    foot_h   = int(kitchen.get('foot_height_mm', 100))
    korpus_h = base_h + foot_h   # gornja ivica baze od poda

    constraints: List[Dict[str, Any]] = []

    # ── Otvori (prozori, vrata) ───────────────────────────────────────────────
    for op in (wall.get('openings') or []):
        x = int(op.get('x_mm', 0))
        w = int(op.get('width_mm', 0))
        if w <= 0:
            continue
        op_type = str(op.get('type', '')).lower()
        y = int(op.get('y_mm', 0))   # parapetna visina za prozor, 0 za vrata
        h = int(op.get('height_mm', 0))

        if op_type == 'vrata':
            # Vrata blokiraju SVE zone u tom X rasponu
            constraints.append({
                'x_start': x, 'x_end': x + w,
                'blocked_zones': ['base', 'wall', 'wall_upper', 'tall', 'tall_top'],
                'type': 'vrata',
                'label': f'Vrata (širina {w}mm)',
                'y_mm': 0, 'is_hard': True,
            })

        elif op_type == 'prozor':
            # Prozor uvijek blokira gornje zone (wall, wall_upper)
            constraints.append({
                'x_start': x, 'x_end': x + w,
                'blocked_zones': ['wall', 'wall_upper'],
                'type': 'prozor',
                'label': f'Prozor (parap. {y}mm)',
                'y_mm': y, 'is_hard': True,
            })
            # Ako prozor seže ispod vrha baze → blokira i base zonu
            if y < korpus_h:
                constraints.append({
                    'x_start': x, 'x_end': x + w,
                    'blocked_zones': ['base'],
                    'type': 'prozor_niska',
                    'label': f'Prozor nizak (parap. {y}mm < visina baze {korpus_h}mm)',
                    'y_mm': y, 'is_hard': True,
                })

    # ── Instalacije (voda, struja, gas) — soft constraints ───────────────────
    _labels = {'voda': 'Voda/odvod', 'struja': 'Struja', 'gas': 'Gas', 'ventilacija': 'Ventilacija'}
    for fx in (wall.get('fixtures') or []):
        x  = int(fx.get('x_mm', 0))
        y  = int(fx.get('y_mm', 0))
        fx_type = str(fx.get('type', '')).lower()
        label   = _labels.get(fx_type, fx_type)
        constraints.append({
            'x_start': x, 'x_end': x,   # tačka, ne raspon
            'blocked_zones': [],          # ne blokira hard
            'type': fx_type,
            'label': label,
            'y_mm': y, 'is_hard': False,
        })

    return constraints


def get_hard_blocked_spans(
    constraints: List[Dict[str, Any]],
    zone: str,
) -> List[Tuple[int, int]]:
    """
    Iz liste constraint-a vraća X-rasponove koji HARD-blokiraju datu zonu.
    Vraća [(x_start, x_end), ...].
    """
    return [
        (int(c['x_start']), int(c['x_end']))
        for c in constraints
        if c.get('is_hard') and zone in c.get('blocked_zones', [])
    ]


def check_module_against_constraints(
    constraints: List[Dict[str, Any]],
    zone: str,
    x_mm: int,
    w_mm: int,
) -> Tuple[bool, str]:
    """
    Provjeri kolidira li modul sa nekim hard constraint-om.
    Vraća (True, '') ako je OK, ili (False, poruka_greške).
    """
    x_end = x_mm + w_mm
    for c in constraints:
        if not c.get('is_hard'):
            continue
        if zone not in c.get('blocked_zones', []):
            continue
        cs = int(c['x_start'])
        ce = int(c['x_end'])
        if x_mm < ce and cs < x_end:
            return False, (
                f"Element kolidira sa: {c['label']} "
                f"(X={cs}–{ce}mm na zidu). "
                f"Pomjeri element ili ukloni prepreku."
            )
    return True, ''


def get_installation_warnings(
    constraints: List[Dict[str, Any]],
    x_mm: int,
    w_mm: int,
) -> List[str]:
    """
    Vraća lista upozorenja za soft constraints (instalacije) unutar X raspona modula.
    """
    x_end = x_mm + w_mm
    warnings = []
    for c in constraints:
        if c.get('is_hard'):
            continue
        cx = int(c.get('x_start', 0))
        if x_mm <= cx <= x_end:
            warnings.append(
                f"⚠️ {c['label']} na X={cx}mm (visina={c.get('y_mm', 0)}mm) "
                f"je unutar ovog elementa — provjeri pristup instalaciji."
            )
    return warnings


def constraints_to_color_bands(
    constraints: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Za 2D prikaz: pretvori constraints u liste obojenih pravougaonika.
    Vraća [{x_start, x_end, color, alpha, label, zones}, ...].
    """
    _colors = {
        'vrata':        '#EF4444',   # crvena
        'prozor':       '#F97316',   # narandžasta
        'prozor_niska': '#FB923C',   # svjetlija narandžasta
        'voda':         '#22D3EE',   # cyan
        'struja':       '#FACC15',   # žuta
        'gas':          '#F87171',   # roza-crvena
        'ventilacija':  '#A3E635',   # zelenkasta
    }
    bands = []
    for c in constraints:
        if not c.get('is_hard') or int(c['x_end']) <= int(c['x_start']):
            continue
        bands.append({
            'x_start': int(c['x_start']),
            'x_end':   int(c['x_end']),
            'color':   _colors.get(c['type'], '#CBD5E1'),
            'alpha':   0.25,
            'label':   c['label'],
            'zones':   c.get('blocked_zones', []),
        })
    return bands
