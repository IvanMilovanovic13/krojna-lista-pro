# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
# UI za korak 4 podešavanja prostorije, izdvojen iz ui_panels.py (bez promene ponašanja).
from i18n import (
    BTN_2D_POZICIONIRANJE,
    BTN_AZURIRAJ_PRIKAZ_DIM,
    BTN_DIJAGONALA,
    BTN_KRENI_SA_DIZAJNOM,
    BTN_POGLED_NAPRED,
    BTN_POGLED_ODOZGO,
    BTN_RESET_PRIKAZA,
    BTN_ROTIRAJ_DESNO,
    BTN_ROTIRAJ_LEVO,
    BTN_SLEDECI_ZID,
    BTN_ZID_A,
    BTN_ZID_B,
    BTN_ZID_C,
    SYM_MID_DOT,
    BTN_ZATVORI,
    LBL_ZID_KUHINJE,
    WIZ4_ACTIVE_WALL,
    WIZ4_BADGE_A,
    WIZ4_BADGE_B,
    WIZ4_BADGE_C,
    WIZ4_CLICK_HINT,
    WIZ4_COMPASS_A,
    WIZ4_COMPASS_B,
    WIZ4_COMPASS_C,
    WIZ4_DIMS_HINT,
    WIZ4_DIMS_TITLE,
    WIZ4_DRAWER_2D_TITLE,
    WIZ4_EDITING_AND_MAIN_FMT,
    WIZ4_EDITING_WALL_FMT,
    WIZ4_EXP_DIMS,
    WIZ4_EXP_WALL_PICK,
    WIZ4_FILTER_ALL,
    WIZ4_FILTER_DIMS,
    WIZ4_FILTER_OPENINGS,
    WIZ4_FILTER_PRO,
    WIZ4_FILTER_WALL,
    WIZ4_FOCUS_WALL_A,
    WIZ4_FOCUS_WALL_B,
    WIZ4_FOCUS_WALL_C,
    WIZ4_GUIDE_1,
    WIZ4_GUIDE_2,
    WIZ4_GUIDE_3,
    WIZ4_GUIDE_4,
    WIZ4_GUIDE_TITLE,
    WIZ4_NORMAL_VIEW,
    WIZ4_NOTIFY_BAD_DIMS,
    WIZ4_NOTIFY_COORDS_FMT,
    WIZ4_NOTIFY_OPENING_SELECTED,
    WIZ4_NOTIFY_PICK_KITCHEN_WALL,
    WIZ4_NOTIFY_PRO_REQUIRED,
    WIZ4_NOTIFY_ROOM_READY,
    WIZ4_ORIENT_A,
    WIZ4_ORIENT_B,
    WIZ4_ORIENT_C,
    WIZ4_PREV_WALL,
    WIZ4_PRO_MAIN_WALL_FMT,
    WIZ4_PRO_EMPTY,
    WIZ4_PRO_HINT1,
    WIZ4_PRO_HINT2,
    WIZ4_PRO_MEASURE_CEIL,
    WIZ4_PRO_MEASURE_CEIL_NOTE,
    WIZ4_PRO_MEASURE_FLOOR,
    WIZ4_PRO_MEASURE_FLOOR_NOTE,
    WIZ4_PRO_TITLE,
    WIZ4_PRO_SUMMARY_FMT,
    WIZ4_ROOM_HEIGHT,
    WIZ4_SCENE_TITLE,
    WIZ4_SELECT_WALL_HINT,
    WIZ4_STEP_TITLE,
    WIZ4_STEP_DIMS_FMT,
    WIZ4_STEP_MAIN_WALL_FMT,
    WIZ4_STEP_PRO_FMT,
    WIZ4_SETUP_ROOM_FMT,
    WIZ4_MAIN_WALL_FMT,
    WIZ4_MEASUREMENT_FMT,
    WIZ4_OFFSET_FROM_WALL_FMT,
    WIZ4_STEPS_FIXTURES,
    WIZ4_STEPS_FIXTURES_FMT,
    WIZ4_STEPS_OPENINGS,
    WIZ4_STEPS_OPENINGS_FMT,
    WIZ4_STEPS_TITLE,
    WIZ4_UPDATE_TOOLTIP,
    WIZ4_USER_ORIENTATION,
    WIZ4_WALL_A_LEN,
    WIZ4_WALL_B_LEN,
    WIZ4_WALL_C_LEN,
    WIZ4_ACTIVE_WALL_MARK,
)
from room_floorplan_editor import render_room_floorplan_editor
from render_3d import render_room_setup_scene_3d

_LOG = logging.getLogger(__name__)

def ensure_room_setup_drawer(ui):
    """Create per-client 2D drawer and reuse it only within that client/page context."""
    _client = ui.context.client
    _drawer = getattr(_client, "_room_setup_drawer_2d", None)
    _content = getattr(_client, "_room_setup_drawer_2d_content", None)
    if _drawer is None or _content is None:
        _drawer = ui.right_drawer().classes('bg-white').props('width=420 bordered overlay')
        with _drawer:
            _content = ui.column().classes('w-full h-full p-3 gap-2')
        setattr(_client, "_room_setup_drawer_2d", _drawer)
        setattr(_client, "_room_setup_drawer_2d_content", _content)
    return _drawer, _content


def render_room_setup_step3(
    state,
    *,
    ui,
    plt,
    _ensure_room_walls,
    _get_room_wall,
    _set_wall_length,
    _set_wall_height,
    main_content,
    ROOM_OPENING_TYPES,
    ROOM_FIXTURE_TYPES,
) -> None:
    """Korak 3 — Prostorija: dimenzije, otvori i 3D preview (interaktivni)."""
    import io as _io
    import base64 as _b64
    import matplotlib as _mpl
    _mpl.use('Agg')
    import matplotlib.pyplot as _plt
    import matplotlib.patches as _mpatches

    room = state.room
    _layout_key = str(getattr(state, 'kitchen_layout', '') or '').lower().strip()
    _is_l_layout    = (_layout_key == 'l_oblik')
    _is_jedan_zid   = (_layout_key in ('jedan_zid', ''))
    type_icons = {"kuhinja": "🍴", "orman": "🚪", "ormani": "🚪", "americki_orman": "🧥", "tv_zona": "📺",
                  "hodnik": "👟", "kupatilo": "🚿", "kancelarija": "💼"}
    OPENING_TYPES = ROOM_OPENING_TYPES
    FIXTURE_TYPES = ROOM_FIXTURE_TYPES

    # Shared mutable refs — accessible in all nested closures
    _refs: dict = {
        'ox_inp':     None,    # ui.number for X position of new opening
        'oy_inp':     None,    # ui.number for Y position of new opening
        'oy_quick':   None,    # ui.number for quick Y (bottom) input
        'fx_inp':     None,    # ui.number for X position of new fixture
        'fy_inp':     None,    # ui.number for Y position of new fixture
        'wall_t':     None,    # transform dict for click-to-mm mapping
        'click_x_mm': [None],  # last clicked X (list for mutability)
        'click_y_mm': [None],  # last clicked Y (list for mutability)
        'drag_open_idx': [None],   # opening index currently dragged in active wall
        'drag_dx_mm': [0],         # pointer offset within opening (x)
        'drag_dy_mm': [0],         # pointer offset within opening (y)
        'is_dragging_open': [False],
        'selected_open_idx': [None],
    }
    _dim_refs: dict = {'wl': None, 'wh': None}
    _sel_opening_type = {'value': 'prozor'}
    _sel_fixture_type = {'value': 'voda'}
    _opening_wall_choice = {'value': str(room.get("active_wall", room.get("kitchen_wall", "A"))).upper()}
    _fixture_wall_choice = {'value': str(room.get("active_wall", room.get("kitchen_wall", "A"))).upper()}
    _use_manual_xy = {'value': False}
    _camera_view = {'value': 'front'}  # front | top | A | B | C | diag
    _diag_yaw = {'value': 45}  # degrees around room center for diagonal view
    # Jednostavan vodjeni tok za laike: 1) zid, 2) dimenzije, 3) otvori/instalacije.
    _panel_mode = {'value': str(room.get('setup_panel_mode', 'walls') or 'walls')}  # walls | dims | openings | all | pro

    _ensure_room_walls(room)
    room.setdefault("kitchen_wall", "A")
    room.setdefault("pro_measurements", {})

    class _NoopRefresh:
        def refresh(self):
            return None
    class _RefreshProxy:
        def __init__(self):
            self._target = None
        def set_target(self, target):
            self._target = target
        def refresh(self):
            try:
                if self._target is not None:
                    self._target.refresh()
            except Exception as ex:
                _LOG.debug("Ignored proxy refresh error in room wizard: %s", ex)
                return None

    _oi_body = _NoopRefresh()
    openings_list = _NoopRefresh()
    fixtures_list = _NoopRefresh()
    opening_selected_info = _NoopRefresh()
    wall_preview = _NoopRefresh()
    scene_container = _NoopRefresh()
    _wall_preview_proxy = _RefreshProxy()
    _scene_container_proxy = _RefreshProxy()
    _wall_headline_proxy = _RefreshProxy()
    _wall_compass_proxy = _RefreshProxy()

    def _get_active_wall() -> dict:
        return _get_room_wall(room, room.get("active_wall", "A"))

    def _wall_name(k: str) -> str:
        ku = str(k or "A").upper()
        return "ZADNJI" if ku == "A" else ("LEVI" if ku == "B" else "DESNI")

    def _get_wall_by_key(k: str) -> dict:
        return _get_room_wall(room, str(k or "A").upper())

    def _ensure_pro_wall_measurements(wkey: str):
        wkey = str(wkey or "A").upper()
        room.setdefault("pro_measurements", {})
        pm = room["pro_measurements"]
        if wkey not in pm:
            pm[wkey] = {}
        _base_len = int((_get_wall_by_key(wkey) or {}).get('length_mm', room.get('wall_length_mm', 3000)) or 3000)
        for _off in (0, 300, 600):
            _row = pm[wkey].setdefault(str(_off), {"0": None, "1000": None, "2000": None, "2500": None})
            for _h in ("0", "1000", "2000", "2500"):
                if _row.get(_h) is None:
                    _row[_h] = _base_len
        return pm[wkey]

    def _pro_values_flat(wkey: str):
        wm = _ensure_pro_wall_measurements(wkey)
        vals = []
        for _off in ("0", "300", "600"):
            row = wm.get(_off, {})
            for _h in ("0", "1000", "2000", "2500"):
                v = row.get(_h)
                if isinstance(v, (int, float)) and v > 0:
                    vals.append(float(v))
        return vals

    def _pro_summary(wkey: str):
        vals = _pro_values_flat(wkey)
        if not vals:
            return None
        mn = min(vals)
        mx = max(vals)
        dev = mx - mn
        if dev <= 5:
            rec = "Odstupanje malo: 5-8 mm tolerancije je dovoljno."
        elif dev <= 12:
            rec = "Srednje odstupanje: planiraj toleranciju 10-15 mm."
        else:
            rec = "Veliko odstupanje: preporuka filer/lajsna 20+ mm ili podela elemenata."
        return {"min": mn, "max": mx, "dev": dev, "rec": rec}

    # ── Wall Preview image constants ─────────────────────────────────────────
    # Fixed canvas: 950 × 300 px at dpi=100 — no bbox_inches='tight' so coords are exact
    _WP_W_IN = 9.5
    _WP_H_IN = 3.0
    _WP_DPI  = 100
    _WP_W_PX = _WP_W_IN * _WP_DPI   # 950
    _WP_H_PX = _WP_H_IN * _WP_DPI   # 300

    with ui.row().classes('w-full h-full gap-0 overflow-hidden bg-gray-100'):

        # ══════════════════════════════════════════════════════════════════════
        # LEVI PANEL
        # ══════════════════════════════════════════════════════════════════════
        with ui.column().classes(
            'w-[420px] shrink-0 bg-white border-r border-gray-200 h-full '
            'overflow-y-auto flex flex-col shadow-sm'
        ):
            # ── Header ────────────────────────────────────────────────────────
            with ui.element('div').classes('bg-white px-3 py-3 shrink-0 border-b border-gray-300'):
                with ui.row().classes('items-center gap-2'):
                    ui.button(icon='arrow_back', on_click=lambda: (
                        setattr(state, 'wizard_step', 3), main_content.refresh()
                    )).props('flat round dense')
                    ui.label(
                        WIZ4_SETUP_ROOM_FMT.format(icon=type_icons.get(state.furniture_type, "🏠"))
                    ).classes('text-xl font-bold text-gray-900')
                with ui.row().classes('items-center gap-2 mt-1'):
                    ui.label(f'{LBL_ZID_KUHINJE}:').classes('text-gray-600 text-xs')
                    ui.label(str(room.get("kitchen_wall", "A")).upper()).classes(
                        'text-xs font-bold text-gray-900 border border-gray-900 px-2 py-0.5 rounded'
                    )
                with ui.row().classes('items-center gap-2 mt-0.5'):
                    ui.label(WIZ4_STEP_TITLE).classes('text-gray-600 text-xs')
                    ui.label(SYM_MID_DOT).classes('text-gray-400')
                    ui.label(
                        f'📐 {state.kitchen_layout.replace("_", " ").title()}'
                    ).classes('text-gray-600 text-xs')
                    _mm = 'PRO' if str(getattr(state, 'measurement_mode', '')).lower() == 'pro' else 'STANDARD'
                    ui.label(SYM_MID_DOT).classes('text-gray-400')
                    ui.label(WIZ4_MEASUREMENT_FMT.format(mode=_mm)).classes('text-gray-600 text-xs')

            with ui.column().classes('flex-1 p-4 gap-3 overflow-y-auto'):
                # ── Workflow progress ───────────────────────────────────────
                _kw = str(room.get("kitchen_wall", "") or "").upper()
                _dims_ok = all(int((_get_wall_by_key(k) or {}).get('length_mm', 0)) > 0 for k in ("A", "B", "C"))
                _pro_mode = str(getattr(state, "measurement_mode", "standard")).lower() == "pro"
                _pro_ok = (not _pro_mode) or bool(_pro_summary(_kw))
                # Broji otvore i instalacije na svim zidovima
                _walls_all = _ensure_room_walls(room)
                _total_openings = sum(len(w.get("openings", [])) for w in _walls_all)
                _total_fixtures = sum(len(w.get("fixtures", [])) for w in _walls_all)
                _open_mark = f"✅ ({_total_openings})" if _total_openings > 0 else "• (opciono)"
                _fix_mark  = f"✅ ({_total_fixtures})" if _total_fixtures > 0 else "• (opciono)"

                def _step_cls(done: bool) -> str:
                    return 'text-xs text-green-700 font-semibold' if done else 'text-xs text-gray-500'

                with ui.card().classes('w-full p-2 border border-gray-200'):
                    ui.label(WIZ4_STEPS_TITLE).classes('text-xs font-bold text-gray-700 mb-1')
                    _wall_done  = _kw in ("A", "B", "C")
                    _pro_show   = _pro_mode  # ako je PRO mode, pokazuje se korak
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('check_circle' if _wall_done else 'radio_button_unchecked').classes(
                            'text-green-600 text-base' if _wall_done else 'text-gray-400 text-base')
                        ui.label(WIZ4_STEP_MAIN_WALL_FMT.format(mark=("✅" if _wall_done else "•"))).classes(
                            _step_cls(_wall_done))
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('check_circle' if _dims_ok else 'radio_button_unchecked').classes(
                            'text-green-600 text-base' if _dims_ok else 'text-gray-400 text-base')
                        ui.label(WIZ4_STEP_DIMS_FMT.format(mark=("✅" if _dims_ok else "•"))).classes(
                            _step_cls(_dims_ok))
                    if _pro_show:
                        with ui.row().classes('items-center gap-1'):
                            ui.icon('check_circle' if _pro_ok else 'radio_button_unchecked').classes(
                                'text-green-600 text-base' if _pro_ok else 'text-gray-400 text-base')
                            ui.label(WIZ4_STEP_PRO_FMT.format(mark=("✅" if _pro_ok else "•"))).classes(
                                _step_cls(_pro_ok))
                    with ui.row().classes('items-center gap-1'):
                        _op_done = _total_openings > 0
                        ui.icon('check_circle' if _op_done else 'radio_button_unchecked').classes(
                            'text-green-600 text-base' if _op_done else 'text-gray-300 text-base')
                        ui.label(WIZ4_STEPS_OPENINGS_FMT.format(mark=_open_mark)).classes(
                            _step_cls(_op_done))
                    with ui.row().classes('items-center gap-1'):
                        _fx_done = _total_fixtures > 0
                        ui.icon('check_circle' if _fx_done else 'radio_button_unchecked').classes(
                            'text-green-600 text-base' if _fx_done else 'text-gray-300 text-base')
                        ui.label(WIZ4_STEPS_FIXTURES_FMT.format(mark=_fix_mark)).classes(
                            _step_cls(_fx_done))
                with ui.card().classes('w-full p-2'):
                    ui.label(WIZ4_GUIDE_TITLE).classes('text-xs font-bold text-gray-700')
                    ui.label(WIZ4_GUIDE_1).classes('text-xs')
                    ui.label(WIZ4_GUIDE_2).classes('text-xs')
                    ui.label(WIZ4_GUIDE_3).classes('text-xs')
                    ui.label(WIZ4_GUIDE_4).classes('text-xs')

                with ui.row().classes('w-full gap-1 flex-wrap'):
                    def _set_panel_mode(m: str):
                        _panel_mode['value'] = m
                        room['setup_panel_mode'] = m
                        main_content.refresh()
                    _pm = str(_panel_mode.get('value', 'walls'))
                    _is_pro = str(getattr(state, "measurement_mode", "standard")).lower() == "pro"

                    def _step_cls(key: str) -> str:
                        if _pm == key:
                            return 'bg-white text-gray-900 border-2 border-gray-900'
                        return 'bg-white text-gray-700 border border-gray-300'

                    ui.button('1) Zid', on_click=lambda: _set_panel_mode('walls')).props('dense').classes(f'text-xs {_step_cls("walls")}')
                    ui.button('2) Dimenzije', on_click=lambda: _set_panel_mode('dims')).props('dense').classes(f'text-xs {_step_cls("dims")}')
                    ui.button('3) Otvori i instalacije', on_click=lambda: _set_panel_mode('openings')).props('dense').classes(f'text-xs {_step_cls("openings")}')

                    # Napredne opcije ostaju dostupne, ali nisu podrazumevane.
                    with ui.expansion('Napredno').classes('w-full mt-1'):
                        with ui.row().classes('w-full gap-1 flex-wrap'):
                            ui.button(WIZ4_FILTER_ALL, on_click=lambda: _set_panel_mode('all')).props('dense outlined').classes('text-xs')
                            ui.button(WIZ4_FILTER_WALL, on_click=lambda: _set_panel_mode('walls')).props('dense outlined').classes('text-xs')
                            ui.button(WIZ4_FILTER_DIMS, on_click=lambda: _set_panel_mode('dims')).props('dense outlined').classes('text-xs')
                            if _is_pro:
                                ui.button(WIZ4_FILTER_PRO, on_click=lambda: _set_panel_mode('pro')).props('dense outlined').classes('text-xs')
                            ui.button(WIZ4_FILTER_OPENINGS, on_click=lambda: _set_panel_mode('openings')).props('dense outlined').classes('text-xs')

                # ── 1. Izbor zida ─────────────────────────────────────────────
                if _panel_mode['value'] in ('all', 'walls'):
                    with ui.expansion(WIZ4_EXP_WALL_PICK, value=True).classes('w-full bg-white border border-gray-100'):
                        with ui.column().classes('w-full p-3 gap-2'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('wallpaper').classes('text-gray-700')
                                ui.label(WIZ4_SELECT_WALL_HINT).classes('font-bold text-gray-800 text-sm')
                            if _is_l_layout:
                                _l_side = str((state.kitchen or {}).get('l_corner_side', getattr(state, 'l_corner_side', 'right')) or 'right')
                                _side_txt = 'desni ugao' if _l_side == 'right' else 'levi ugao'
                                ui.label(f'L-oblik ({_side_txt}): fokus na zid A (glavni) i zid B (bočni).')
                                ui.label('Zid C se automatski usklađuje sa dubinom zida B.').classes('text-xs text-gray-500')
                            elif _is_jedan_zid:
                                ui.label('Jedan zid: svi elementi idu na Zid A.').classes('text-xs text-gray-500')

                            with ui.row().classes('w-full gap-2 flex-wrap'):
                                for _w in _ensure_room_walls(room):
                                    _wk = str(_w.get("key", "A"))
                                    # Za jedan_zid prikazujemo samo Zid A
                                    if _is_jedan_zid and _wk != "A":
                                        continue
                                    _lbl = f'Zid {_wk} ({_wall_name(_wk)})'
                                    _is_kitchen = (room.get("kitchen_wall", "A") == _wk)
                                    _cls = 'bg-white text-gray-900 border border-gray-900' if _is_kitchen else 'bg-gray-100 text-gray-700 border border-gray-300'

                                    def _set_kitchen_wall(k=_wk):
                                        room["kitchen_wall"] = k
                                        wall_preview.refresh()
                                        scene_container.refresh()

                                    ui.button(_lbl, on_click=_set_kitchen_wall).classes(
                                        f'px-3 py-1 rounded text-xs font-semibold {_cls}'
                                    ).props('dense')
                            _kw = str(room.get("kitchen_wall", "A")).upper()
                            ui.label(WIZ4_MAIN_WALL_FMT.format(wall=_kw, name=_wall_name(_kw))).classes(
                                'text-xs font-bold text-gray-700'
                            )

                            # Wall-by-wall nav + active wall header — skriveno za jedan zid
                            if not _is_jedan_zid:
                                with ui.row().classes('w-full items-center justify-between mt-1'):
                                    def _prev_wall():
                                        order = ["A", "B", "C"]
                                        cur = str(room.get("active_wall", "A")).upper()
                                        idx = max(0, order.index(cur) - 1)
                                        room["active_wall"] = order[idx]
                                        _w = _get_room_wall(room, order[idx])
                                        if _dim_refs.get('wl') is not None:
                                            _dim_refs['wl'].set_value(int(_w.get('length_mm', 3000)))
                                        if _dim_refs.get('wh') is not None:
                                            _dim_refs['wh'].set_value(int(_w.get('height_mm', 2600)))
                                        wall_preview.refresh()
                                        _oi_body.refresh()
                                        openings_list.refresh()
                                        fixtures_list.refresh()
                                        wall_headline.refresh()
                                        wall_compass.refresh()
                                        scene_container.refresh()

                                    def _next_wall():
                                        order = ["A", "B", "C"]
                                        cur = str(room.get("active_wall", "A")).upper()
                                        idx = min(len(order) - 1, order.index(cur) + 1)
                                        room["active_wall"] = order[idx]
                                        _w = _get_room_wall(room, order[idx])
                                        if _dim_refs.get('wl') is not None:
                                            _dim_refs['wl'].set_value(int(_w.get('length_mm', 3000)))
                                        if _dim_refs.get('wh') is not None:
                                            _dim_refs['wh'].set_value(int(_w.get('height_mm', 2600)))
                                        wall_preview.refresh()
                                        _oi_body.refresh()
                                        openings_list.refresh()
                                        fixtures_list.refresh()
                                        wall_headline.refresh()
                                        wall_compass.refresh()
                                        scene_container.refresh()

                                    ui.button(WIZ4_PREV_WALL, on_click=_prev_wall).props('dense outlined').classes('text-xs')
                                    _aw = str(room.get("active_wall", "A")).upper()
                                    _aw_lbl = "ZADNJI" if _aw == "A" else ("LEVI" if _aw == "B" else "DESNI")
                                    ui.label(WIZ4_EDITING_WALL_FMT.format(wall=_aw, name=_aw_lbl)).classes('text-xs font-bold text-gray-800')
                                    ui.button(BTN_SLEDECI_ZID, on_click=_next_wall).props('dense outlined').classes('text-xs')

                # ── 2. Dimenzije ──────────────────────────────────────────────
                if _panel_mode['value'] in ('all', 'dims'):
                    with ui.expansion(WIZ4_EXP_DIMS, value=True).classes('w-full bg-white border border-gray-100'):
                        with ui.column().classes('w-full p-3 gap-3'):
                            with ui.row().classes('items-center gap-2 mb-0'):
                                ui.icon('straighten').classes('text-gray-700')
                                ui.label(WIZ4_DIMS_TITLE).classes('font-bold text-gray-800 text-sm')
                            ui.label(
                                WIZ4_DIMS_HINT
                            ).classes('text-xs text-gray-500')

                            wall_a = _get_wall_by_key("A")
                            wall_b = _get_wall_by_key("B")
                            wall_c = _get_wall_by_key("C")

                            def _focus_wall(k: str):
                                room["active_wall"] = str(k or "A").upper()
                                wall_headline.refresh()
                                wall_compass.refresh()
                                wall_preview.refresh()
                                scene_container.refresh()

                            # 1) Visina prostorije
                            with ui.card().classes('w-full p-3 border border-gray-200'):
                                ui.label(WIZ4_ROOM_HEIGHT).classes('text-xs font-semibold text-gray-700')
                                wh_inp = ui.number(
                                    value=int(room.get('wall_height_mm', 2600)),
                                    min=2000, max=4000, step=50, suffix='mm'
                                ).props('outlined dense').classes('w-full')

                            # 2) Zid A
                            with ui.card().classes('w-full p-3 border border-gray-200'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    ui.label(WIZ4_WALL_A_LEN).classes('text-xs font-semibold text-gray-700')
                                    ui.button(f'🧭 {WIZ4_FOCUS_WALL_A}', on_click=lambda: _focus_wall("A")).props('dense outlined').classes('text-xs')
                                wa_inp = ui.number(
                                    value=int(wall_a.get('length_mm', room.get('wall_length_mm', 3000))),
                                    min=500, max=12000, step=50, suffix='mm'
                                ).props('outlined dense').classes('w-full')

                            if _is_jedan_zid:
                                # Jedan zid: samo dubina prostorije (B=C=ta vrednost)
                                with ui.card().classes('w-full p-3 border border-gray-200'):
                                    ui.label('3) Dubina prostorije').classes('text-xs font-semibold text-gray-700')
                                    ui.label('Rastojanje od kuhinjskog zida do suprotnog zida.').classes('text-xs text-gray-400')
                                    wb_inp = ui.number(
                                        value=int(wall_b.get('length_mm', room.get('room_depth_mm', 3000))),
                                        min=500, max=12000, step=50, suffix='mm'
                                    ).props('outlined dense').classes('w-full')
                                wc_inp = None  # Za jedan_zid: C = B, automatski
                            else:
                                # 3) Zid B (L-oblik, U-oblik, galija)
                                with ui.card().classes('w-full p-3 border border-gray-200'):
                                    with ui.row().classes('w-full items-center justify-between'):
                                        ui.label(WIZ4_WALL_B_LEN).classes('text-xs font-semibold text-gray-700')
                                        ui.button(f'🧭 {WIZ4_FOCUS_WALL_B}', on_click=lambda: _focus_wall("B")).props('dense outlined').classes('text-xs')
                                    wb_inp = ui.number(
                                        value=int(wall_b.get('length_mm', room.get('room_depth_mm', 3000))),
                                        min=500, max=12000, step=50, suffix='mm'
                                    ).props('outlined dense').classes('w-full')

                                if not _is_l_layout:
                                    # 4) Zid C (ostali multi-wall režimi)
                                    with ui.card().classes('w-full p-3 border border-gray-200'):
                                        with ui.row().classes('w-full items-center justify-between'):
                                            ui.label(WIZ4_WALL_C_LEN).classes('text-xs font-semibold text-gray-700')
                                            ui.button(f'🧭 {WIZ4_FOCUS_WALL_C}', on_click=lambda: _focus_wall("C")).props('dense outlined').classes('text-xs')
                                        wc_inp = ui.number(
                                            value=int(wall_c.get('length_mm', room.get('room_depth_mm', 3000))),
                                            min=500, max=12000, step=50, suffix='mm'
                                        ).props('outlined dense').classes('w-full')
                                else:
                                    # L-oblik: zid C = dubina zida B (read-only info)
                                    wc_inp = None
                                    with ui.card().classes('w-full p-3 border border-gray-100 bg-gray-50'):
                                        ui.label('Zid C (auto)').classes('text-xs font-semibold text-gray-600')
                                        ui.label('Automatski = dužina zida B (dubina prostorije).').classes('text-xs text-gray-500')

                            def _update_preview():
                                _h = int(wh_inp.value or 2600)
                                _wa = int(wa_inp.value or 3000)
                                _wb = int(wb_inp.value or 3000)
                                _wc = int(_wb if (_is_l_layout or _is_jedan_zid) else int(wc_inp.value or 3000))
                                _get_wall_by_key("A")['length_mm'] = _wa
                                _get_wall_by_key("B")['length_mm'] = _wb
                                _get_wall_by_key("C")['length_mm'] = _wc
                                _get_wall_by_key("A")['height_mm'] = _h
                                _get_wall_by_key("B")['height_mm'] = _h
                                _get_wall_by_key("C")['height_mm'] = _h
                                room['wall_length_mm'] = _wa
                                room['wall_height_mm'] = _h
                                room['room_depth_mm']  = max(_wb, _wc)
                                wall_preview.refresh()
                                scene_container.refresh()

                            ui.button(BTN_AZURIRAJ_PRIKAZ_DIM, on_click=_update_preview).props(
                                'unelevated'
                            ).classes('w-full text-sm font-bold py-2').tooltip(WIZ4_UPDATE_TOOLTIP)

                # ── 3. PRO merenje glavnog zida ─────────────────────────────
                if str(getattr(state, "measurement_mode", "standard")).lower() == "pro" and _panel_mode['value'] in ('all', 'pro'):
                    with ui.expansion(WIZ4_PRO_TITLE, value=True).classes(
                        'w-full bg-white border border-gray-100'
                    ):
                        with ui.column().classes('w-full p-3 gap-3'):
                            kw = str(room.get("kitchen_wall", "A")).upper()
                            with ui.card().classes('w-full p-3 border border-gray-200 bg-gray-50'):
                                ui.label(WIZ4_PRO_MAIN_WALL_FMT.format(wall=kw, name=_wall_name(kw))).classes(
                                    'text-sm font-bold text-gray-800'
                                )
                                ui.label(WIZ4_PRO_HINT1).classes('text-xs text-gray-600')
                                ui.label(WIZ4_PRO_HINT2).classes('text-xs text-gray-500')
                                with ui.row().classes('w-full gap-2 mt-1'):
                                    ui.button(WIZ4_PRO_MEASURE_FLOOR, on_click=lambda: ui.notify(
                                        WIZ4_PRO_MEASURE_FLOOR_NOTE, timeout=1800
                                    )).props('dense outlined').classes('text-xs')
                                    ui.button(WIZ4_PRO_MEASURE_CEIL, on_click=lambda: ui.notify(
                                        WIZ4_PRO_MEASURE_CEIL_NOTE, timeout=1800
                                    )).props('dense outlined').classes('text-xs')
                            wm = _ensure_pro_wall_measurements(kw)
                            _kw_wall_len = int(_get_wall_by_key(kw).get('length_mm', 3000) or 3000)
                            for _off in ("0", "300", "600"):
                                with ui.card().classes('w-full p-3 border border-gray-200'):
                                    ui.label(WIZ4_OFFSET_FROM_WALL_FMT.format(offset=_off)).classes('text-xs font-bold text-gray-700')
                                    with ui.grid(columns=2).classes('w-full gap-2'):
                                        for _h in ("0", "1000", "2000", "2500"):
                                            _init = wm.get(_off, {}).get(_h)
                                            _inp = ui.number(
                                                value=_init if _init else _kw_wall_len, min=100, max=20000, step=1
                                            ).props('dense outlined').classes('w-full')
                                            _inp.style('min-width: 120px;')
                                            _inp.props(f'label="{_h} mm"')
                                            def _save(v_inp=_inp, off=_off, hh=_h):
                                                try:
                                                    v = int(v_inp.value or 0)
                                                    wm[off][hh] = v if v > 0 else None
                                                    scene_container.refresh()
                                                except Exception as ex:
                                                    _LOG.debug("Invalid PRO input (%s/%s): %s", off, hh, ex)
                                                    wm[off][hh] = None
                                            _inp.on('change', lambda e, _s=_save: _s())
                            _sum = _pro_summary(kw)
                            if _sum:
                                with ui.card().classes('w-full p-2 border border-gray-200'):
                                    ui.label(
                                        WIZ4_PRO_SUMMARY_FMT.format(
                                            min_v=int(_sum["min"]),
                                            max_v=int(_sum["max"]),
                                            dev=int(_sum["dev"]),
                                        )
                                    ).classes('text-xs font-bold text-gray-700')
                                    ui.label(_sum["rec"]).classes('text-xs text-gray-600')
                            else:
                                ui.label(WIZ4_PRO_EMPTY).classes('text-xs text-gray-400')

                # Jednostavni režim: dodavanje/provera otvora i instalacija radi se kroz jedan centralni editor.
                # Napredni panel ostaje isključen da UI ne bude prenatrpan.

            # ── Nastavi dugme (sticky bottom) ──────────────────────────────────
            with ui.element('div').classes('p-4 border-t border-gray-200 bg-white shrink-0 sticky bottom-0'):
                def _nastavi():
                    _kw = str(room.get("kitchen_wall", "") or "").upper()
                    if _kw not in ("A", "B", "C"):
                        ui.notify(f'❌ {WIZ4_NOTIFY_PICK_KITCHEN_WALL}', type='negative')
                        return
                    _wa = int((_get_wall_by_key("A") or {}).get('length_mm', 0))
                    _wb = int((_get_wall_by_key("B") or {}).get('length_mm', 0))
                    _wc = int((_get_wall_by_key("C") or {}).get('length_mm', 0))
                    if _is_l_layout or _is_jedan_zid:
                        _wc = _wb
                        _get_wall_by_key("C")['length_mm'] = _wc
                    _wh = int((_get_wall_by_key("A") or {}).get('height_mm', room.get('wall_height_mm', 2600)))
                    if _wa <= 0 or _wb <= 0 or _wc <= 0 or _wh <= 0:
                        ui.notify(f'❌ {WIZ4_NOTIFY_BAD_DIMS}', type='negative')
                        return
                    # ── PRO mode: koristi MIN izmjerenu vrijednost za kuhinjski zid ──
                    _final_wall_len = _wa  # default: ručno unesena vrijednost
                    if str(getattr(state, "measurement_mode", "standard")).lower() == "pro":
                        _sum = _pro_summary(_kw)
                        if not _sum:
                            ui.notify(f'❌ {WIZ4_NOTIFY_PRO_REQUIRED}', type='negative')
                            return
                        _final_wall_len = int(_sum["min"])
                        # Ažuriraj i wall zapis da se poklapa s PRO MIN vrijednošću
                        _kw_wall = _get_wall_by_key(_kw)
                        if _kw_wall:
                            _kw_wall['length_mm'] = _final_wall_len
                        if _sum["dev"] > 0:
                            ui.notify(
                                f'📐 PRO: koristi se MIN {_final_wall_len} mm '
                                f'(odstupanje {int(_sum["dev"])} mm)',
                                type='info', timeout=4000
                            )
                    _set_wall_length(_final_wall_len)
                    _set_wall_height(_wh)
                    room['wall_length_mm'] = _final_wall_len
                    room['wall_height_mm'] = _wh
                    room['room_depth_mm']  = max(_wb, _wc)
                    state.room_setup_done = True
                    state.active_tab = 'elementi'
                    main_content.refresh()
                    ui.notify(f'✅ {WIZ4_NOTIFY_ROOM_READY}', type='positive')

                ui.button(
                    f'➡️ {BTN_KRENI_SA_DIZAJNOM}',
                    on_click=_nastavi
                ).classes('w-full font-bold text-base py-3 rounded-lg shadow')

        # ══════════════════════════════════════════════════════════════════════
        # DESNI PANEL — 2D + 3D preview
        # ══════════════════════════════════════════════════════════════════════
        with ui.column().classes('flex-1 h-full bg-transparent gap-3 overflow-y-auto pr-1'):

            @ui.refreshable
            def wall_headline():
                _aw = str(room.get("active_wall", "A")).upper()
                _aw_lbl = "ZADNJI" if _aw == "A" else ("LEVI" if _aw == "B" else "DESNI")
                _kw = str(room.get("kitchen_wall", "A")).upper()
                ui.label(WIZ4_EDITING_AND_MAIN_FMT.format(wall=_aw, name=_aw_lbl, main=_kw)).classes(
                    'text-sm font-bold text-gray-800'
                )
            _wall_headline_proxy.set_target(wall_headline)

            @ui.refreshable
            def wall_compass():
                _aw = str(room.get("active_wall", "A")).upper()
                def _cls(k: str) -> str:
                    return 'bg-white text-gray-900 border-gray-900' if _aw == k else 'bg-gray-100 text-gray-500 border-gray-200'
                with ui.element('div').classes('inline-grid gap-1').style('grid-template-columns: 56px 56px;'):
                    ui.label(WIZ4_COMPASS_B).classes(f'px-2 py-1 text-xs text-center rounded border {_cls("B")}')
                    ui.label(WIZ4_COMPASS_C).classes(f'px-2 py-1 text-xs text-center rounded border {_cls("C")}')
            _wall_compass_proxy.set_target(wall_compass)

            with ui.row().classes('items-center justify-between'):
                wall_headline()
                with ui.row().classes('items-center gap-2'):
                    wall_compass()

            def _open_3d_fullscreen():
                with ui.dialog().props('maximized') as _dlg_3d:
                    with ui.card().classes('w-full h-full p-3 gap-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label('3D prikaz prostorije').classes('text-base font-bold')
                            ui.button(BTN_ZATVORI, on_click=_dlg_3d.close).props('dense outlined')

                        _tool = {'value': 'prozor'}
                        _fs_camera = {'value': 'diag'}
                        _refs.setdefault('scene_pick', {'wall': str(room.get('active_wall', 'A')).upper(), 'x_mm': 0})

                        @ui.refreshable
                        def _wall_badge():
                            _aw = str(room.get("active_wall", "A")).upper()
                            ui.label(f'Aktivan zid: {_aw}').classes('text-xs text-gray-600')
                            _sp = _refs.get('scene_pick', {}) or {}
                            ui.label(
                                f'3D pozicija: zid {str(_sp.get("wall", _aw)).upper()}  ·  X={int(_sp.get("x_mm", 0))} mm'
                            ).classes('text-xs text-gray-600')

                        @ui.refreshable
                        def _wall_picker():
                            _aw = str(room.get("active_wall", "A")).upper()
                            with ui.row().classes('w-full gap-2 items-center flex-wrap'):
                                ui.label('Izaberi zid:').classes('text-xs text-gray-600')
                                for _k, _label in (('A', 'Zid A'), ('B', 'Zid B'), ('C', 'Zid C')):
                                    _active = (_aw == _k)
                                    _cls = (
                                        'bg-white text-gray-900 border-2 border-gray-900'
                                        if _active else
                                        'bg-white text-gray-700 border border-gray-300'
                                    )
                                    def _pick_wall(k=_k):
                                        room["active_wall"] = k
                                        _wk = _get_room_wall(room, k)
                                        _wlen = int(_wk.get('length_mm', room.get('wall_length_mm', 3000)))
                                        _refs['scene_pick'] = {'wall': k, 'x_mm': int(_wlen / 2)}
                                        _fs_camera['value'] = k
                                        _wall_badge.refresh()
                                        openings_list.refresh()
                                        opening_selected_info.refresh()
                                        _wall_preview_proxy.refresh()
                                        _scene_container_proxy.refresh()
                                        _scene_full.refresh()
                                        wall_headline.refresh()
                                        wall_compass.refresh()
                                    ui.button(_label, on_click=_pick_wall).props('dense').classes(f'text-xs {_cls}')
                                ui.button('Diag', on_click=lambda: (_fs_camera.__setitem__('value', 'diag'), _scene_full.refresh())).props('dense outlined').classes('text-xs')

                        with ui.row().classes('w-full gap-2 items-end flex-wrap'):
                            _tool_sel = ui.select(
                                {
                                    'prozor': '🪟 Prozor',
                                    'vrata': '🚪 Vrata',
                                    'struja': '⚡ Utičnica',
                                    'voda': '💧 Voda',
                                    'gas': '🔥 Gas',
                                },
                                value='prozor',
                                label='Šta dodaješ',
                            ).props('dense outlined').classes('w-44')
                            _w_in = ui.number(value=900, min=100, max=4000, step=10, label='Širina [mm]').props(
                                'dense outlined'
                            ).classes('w-36')
                            _h_in = ui.number(value=1200, min=100, max=3000, step=10, label='Visina [mm]').props(
                                'dense outlined'
                            ).classes('w-36')
                            _y_in = ui.number(value=0, min=0, max=3000, step=10, label='Y od poda [mm]').props(
                                'dense outlined'
                            ).classes('w-36')

                            def _add_from_3d():
                                _tool['value'] = str(_tool_sel.value or 'prozor')
                                _sp = _refs.get('scene_pick', {}) or {}
                                _wk = str(_sp.get("wall", room.get("active_wall", "A"))).upper()
                                _wobj = _get_room_wall(room, _wk)
                                _wlen = int(_wobj.get('length_mm', room.get('wall_length_mm', 3000)))
                                _x_pick = int(_sp.get("x_mm", int(_wlen / 2)))
                                if _tool['value'] in ('prozor', 'vrata'):
                                    _ww = int(_w_in.value or 900)
                                    _hh = int(_h_in.value or 1200)
                                    _yy = int(_y_in.value or 0)
                                    if _tool['value'] == 'vrata':
                                        _yy = 0
                                    _x = int(max(0, min(max(0, _wlen - _ww), _x_pick)))
                                    _wobj.setdefault('openings', []).append(
                                        {
                                            'type': _tool['value'],
                                            'wall': _wk,
                                            'x_mm': _x,
                                            'width_mm': _ww,
                                            'height_mm': _hh,
                                            'y_mm': _yy,
                                        }
                                    )
                                else:
                                    _yy = int(_y_in.value or 300)
                                    _x = int(max(0, min(_wlen, _x_pick)))
                                    _wobj.setdefault('fixtures', []).append(
                                        {
                                            'type': _tool['value'],
                                            'wall': _wk,
                                            'x_mm': _x,
                                            'y_mm': _yy,
                                        }
                                    )
                                openings_list.refresh()
                                fixtures_list.refresh()
                                opening_selected_info.refresh()
                                _wall_preview_proxy.refresh()
                                _scene_container_proxy.refresh()
                                _scene_full.refresh()
                                _wall_badge.refresh()

                            ui.button('➕ Dodaj na aktivan zid', on_click=_add_from_3d).props('dense').classes(
                                'text-xs'
                            )

                        _wall_badge()
                        _wall_picker()
                        ui.label('Klikni tačno na zid u 3D: bira se zid i X pozicija, pa klikni Dodaj.').classes(
                            'text-xs text-gray-500'
                        )

                        @ui.refreshable
                        def _scene_full():
                            render_room_setup_scene_3d(
                                ui=ui,
                                state=state,
                                room=room,
                                ensure_room_walls=_ensure_room_walls,
                                get_room_wall=_get_room_wall,
                                camera_view=_fs_camera,
                                diag_yaw=_diag_yaw,
                                refs=_refs,
                                openings_list_refresh=openings_list.refresh,
                                opening_selected_info_refresh=opening_selected_info.refresh,
                                wall_headline_refresh=lambda: (wall_headline.refresh(), _wall_badge.refresh(), _wall_picker.refresh()),
                                wall_compass_refresh=lambda: (wall_compass.refresh(), _wall_badge.refresh(), _wall_picker.refresh()),
                                wall_preview_refresh=_wall_preview_proxy.refresh,
                                scene_refresh=_scene_full.refresh,
                            )

                        with ui.element('div').classes('w-full').style('height: calc(100vh - 170px);'):
                            _scene_full()

                    _dlg_3d.open()

            render_room_floorplan_editor(
                ui=ui,
                room=room,
                state=state,
                ensure_room_walls=_ensure_room_walls,
                get_room_wall=_get_room_wall,
                refs=_refs,
                opening_types=OPENING_TYPES,
                fixture_types=FIXTURE_TYPES,
                wall_headline_refresh=wall_headline.refresh,
                wall_compass_refresh=wall_compass.refresh,
                wall_preview_refresh=_wall_preview_proxy.refresh,
                scene_refresh=_scene_container_proxy.refresh,
                openings_list_refresh=openings_list.refresh,
                fixtures_list_refresh=fixtures_list.refresh,
                opening_selected_info_refresh=opening_selected_info.refresh,
                on_show_3d=_open_3d_fullscreen,
            )

            with ui.card().props('id=room-scene-card').classes('w-full p-3 bg-white border border-gray-200 shadow-sm'):
                ui.label('3D prikaz je sada samo preko celog ekrana.').classes('text-xs text-gray-600')
                ui.label('Dodavanje i pomeranje radi se na 2D planu iznad, na jednom mestu.').classes('text-xs text-gray-600')
                ui.button('Otvori 3D preko celog ekrana', on_click=_open_3d_fullscreen).props('unelevated').classes(
                    'text-xs mt-1'
                )
