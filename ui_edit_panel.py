# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import tr
from i18n import SYM_BLACK_SQUARE, SYM_RECALC
from ui_panels_helpers import format_user_error
from module_rules import (
    default_shelf_count,
    dishwasher_installation_metrics,
    module_supports_adjustable_shelves,
)
from drawer_logic import rebalance_drawers_proportional, redistribute_drawers_proportional

from ui_color_picker import render_color_picker
from ui_catalog_config import _FRONT_COLOR_PRESETS, translate_template_label

_FREESTANDING_TIDS = {
    "BASE_DISHWASHER_FREESTANDING",
    "BASE_OVEN_HOB_FREESTANDING",
    "TALL_FRIDGE_FREESTANDING",
}


def render_edit_panel(
    *,
    ui,
    state,
    templates,
    max_allowed_h_for_zone,
    get_depth_mode,
    get_zone_depth_standard,
    is_independent_depth,
    update_module_local,
    solve_layout,
    set_zone_depth_standard,
    delete_module_local,
    nacrt_refresh,
    edit_panel_refresh,
    open_add_above_dialog,
    open_add_above_tall_dialog,
    duplicate_module_local,
    logger,
) -> None:
    _lang = str(getattr(state, 'language', 'sr') or 'sr').lower().strip()
    def _t(key: str, **fmt: object) -> str:
        return tr(key, _lang, **fmt)
    def _display_label(raw: object) -> str:
        return translate_template_label(str(raw or ""), _lang)

    k = state.kitchen
    _active_wk = str(
        (getattr(state, "room", {}) or {}).get("active_wall",
            (getattr(state, "room", {}) or {}).get("kitchen_wall", "A")) or "A"
    ).upper()
    mods = [
        m for m in (k.get("modules", []) or [])
        if str(m.get("wall_key", "A")).upper() == _active_wk
    ]
    if not mods:
        ui.label(_t('edit.no_elements_on_wall')).classes('text-gray-400 text-sm p-4')
        return

    # Kratak format da ne širi sidebar
    _ZONE_SHORT = (
        {'base': 'B', 'wall': 'W', 'wall_upper': 'W2', 'tall': 'T', 'tall_top': 'TT'}
        if _lang == 'en'
        else {'base': 'D', 'wall': 'G', 'wall_upper': 'G2', 'tall': 'V', 'tall_top': 'VT'}
    )
    labels = [
        f"#{m.get('id')} [{_ZONE_SHORT.get(str(m.get('zone','')).lower(), '?')}] "
        f"{_display_label(m.get('label',''))[:18]} {m.get('w_mm','')}mm"
        for m in mods
    ]
    id_list = [int(m.get('id', 0)) for m in mods]

    # Ako selected_edit_id nije validan, uzmi prvi
    if state.selected_edit_id not in id_list:
        state.selected_edit_id = id_list[0]

    current_index = id_list.index(state.selected_edit_id)
    current_label = labels[current_index]

    def _on_select(e):
        # Nadji ID po label-u direktno iz sveze liste
        val = str(e.value)
        for i, lbl in enumerate(labels):
            if lbl == val:
                state.selected_edit_id = id_list[i]
                break
        edit_panel_refresh()

    ui.select(labels, value=current_label, label=_t('edit.element_on_wall'),
              on_change=_on_select).classes('w-full')

    # Uvek uzmi svez m iz kitchen po ID-u
    current_id = int(state.selected_edit_id)
    m = next((mod for mod in mods if int(mod.get('id', -1)) == current_id), None)
    if not m:
        ui.label(_t('edit.element_not_found')).classes('text-red-500 text-sm p-2')
        return

    cur_tid = str(m.get("template_id", "")).upper()
    zone_m = str(m.get("zone", "base")).lower()
    # Za wall_upper: postavi target_x da funkcija nađe pravi wall element ispod
    # i izračuna tačan max (do plafona, od gornje ivice elementa ispod)
    if zone_m == 'wall_upper':
        state.wall_upper_target_x = int(m.get('x_mm', -1))
    max_h = max_allowed_h_for_zone(zone_m, cur_tid)
    if cur_tid in _FREESTANDING_TIDS:
        max_h = max(max_h, 3000)

    _OPEN_TIDS = {'BASE_OPEN', 'WALL_OPEN', 'TALL_OPEN', 'TALL_TOP_OPEN', 'WALL_UPPER_OPEN'}
    _is_open = cur_tid in _OPEN_TIDS
    _open_color_ref = {'value': str((m.get('params') or {}).get('front_color') or '')}

    with ui.card().classes('w-full p-2 mt-1'):
        # ── Header ───────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center justify-between mb-1'):
            ui.label(f"#{m.get('id')}  {_display_label(m.get('label',''))}").classes('font-bold text-sm')
            _zc = {'base': 'bg-gray-100 text-gray-800',
                   'wall': 'bg-gray-100 text-gray-800',
                   'tall': 'bg-gray-100 text-gray-800'}.get(zone_m, 'bg-gray-100 text-gray-700')
            _zone_badge = {
                'base': 'BASE',
                'wall': 'WALL',
                'wall_upper': 'WALL+',
                'tall': 'TALL',
                'tall_top': 'TALL+',
            }.get(zone_m, zone_m.upper()) if _lang == 'en' else zone_m.upper()
            ui.label(_zone_badge).classes(f'text-xs px-1.5 py-0.5 rounded font-mono {_zc}')
        ui.separator().classes('mb-1')

        # ── Kompaktna grid forma — 2 polja po redu ──────────────────────────────
        def _lbl(txt: str):
            ui.label(txt).classes('text-xs text-gray-400 leading-none mb-0.5')

        def _col():
            return ui.column().classes('flex-1 gap-0 min-w-0')

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(_t('edit.x_mm'))
                x = ui.number(value=int(m.get('x_mm', 0)), min=0, max=20000, step=5).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(_t('params.width_mm'))
                w = ui.number(value=int(m.get('w_mm', 0)), min=100, max=3000, step=10).props(
                    'dense outlined').classes('w-full')

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(_t('edit.height_max_fmt', max_h=max_h))
                h = ui.number(value=min(int(m.get('h_mm', 0)), max_h), min=100, max=max_h, step=10).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(_t('params.depth_mm'))
                d = ui.number(value=int(m.get('d_mm', 0)), min=100, max=2000, step=10).props(
                    'dense outlined').classes('w-full')

        # ── Depth mode badge ──────────────────────────────────────────────────
        _dm = get_depth_mode(m)
        _dm_zone_std = get_zone_depth_standard(zone_m)
        if _dm == "INDEPENDENT":
            _dm_txt = _t('edit.depth_independent_fmt', depth=int(m.get("d_mm", 0)))
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        elif _dm == "CUSTOM":
            _dm_txt = _t('edit.depth_custom_fmt', depth=int(m.get("d_mm", 0)), std=_dm_zone_std)
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        else:  # STANDARD
            _dm_txt = _t('edit.depth_standard_fmt', std=_dm_zone_std)
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        ui.label(_dm_txt).classes(_dm_cls)

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(_t('edit.gap_mm'))
                g = ui.number(value=int(m.get('gap_after_mm', 0)), min=0, max=500, step=1).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(_t('params.name'))
                name_inp = ui.input(value=_display_label(m.get('label', ''))).props(
                    'dense outlined').classes('w-full')

        handle_side_sel = None
        _no_handle_side = any(k in cur_tid for k in (
            '2DOOR', 'DRAWERS', 'DOOR_DRAWER', 'OPEN', 'SINK', 'FRIDGE', 'FREEZER', 'OVEN', 'HOB', 'COOKING_UNIT',
            'DISHWASHER', 'LIFTUP', 'CORNER', 'GLASS',
        ))
        _has_handle_side = (
            zone_m in ('base', 'wall', 'tall', 'wall_upper') and not _no_handle_side
        )
        if _has_handle_side:
            cur_side = str((m.get("params") or {}).get("handle_side", "right"))
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(_t('edit.handle')).classes('text-xs text-gray-500 w-14 shrink-0')
                handle_side_sel = ui.select(
                    {"left": _t('edit.handle_left'), "right": _t('edit.handle_right')},
                    value=cur_side,
                ).props('dense outlined').classes('flex-1')

        if cur_tid in {"BASE_COOKING_UNIT", "OVEN_HOB"}:
            _params = dict(m.get("params", {}) or {})
            _oven_h_info = float(_params.get("oven_h", 595) or 595)
            _drawer_list = list(_params.get("drawer_heights", []) or [])
            _drawer_h_info = float(_drawer_list[0]) if _drawer_list else max(
                80.0, float(m.get('h_mm', 720)) - 2.0 * float(state.kitchen.get("materials", {}).get("carcass_thk", 18)) - _oven_h_info
            )
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                _cook_title = _t('edit.cooking_unit_title')
                _oven_h_txt = _t('edit.cooking_unit_oven_height_fmt', value=f'{_oven_h_info:.0f}')
                _drawer_h_txt = _t('edit.cooking_unit_drawer_height_fmt', value=f'{_drawer_h_info:.0f}')
                _oven_handle_note = _t('edit.cooking_unit_oven_handle_note')
                ui.label(_cook_title).classes('text-xs font-bold text-gray-700')
                ui.label(_oven_h_txt).classes('text-[11px] text-gray-600')
                ui.label(_drawer_h_txt).classes('text-[11px] font-semibold text-gray-700')
                ui.label(_oven_handle_note).classes('text-[10px] text-gray-500')

        # Fioke / vrata+fioka / police u edit panelu
        features = templates.get(cur_tid, {}).get("features", {}) if cur_tid in templates else {}
        has_drawers = features.get("drawers", False)
        has_door_and_drawer = features.get("doors", False) and features.get("drawers", False)
        has_shelves_edit = (
            not has_drawers
            and module_supports_adjustable_shelves(cur_tid, features=features)
        )
        carcass_thk = float(state.kitchen.get("materials", {}).get("carcass_thk", 18))
        MIN_DRAWER_H = 80
        SHELF_STEP = 250  # mm — preporučeni razmak između polica

        def _inner_h(corp_h: float) -> float:
            return corp_h - 2 * carcass_thk

        drawer_heights_state = None
        door_h_inp = None
        drawer_h_inp = None
        sink_cutout_x = None
        sink_cutout_w = None
        sink_cutout_d = None
        hob_cutout_x = None
        hob_cutout_w = None
        hob_cutout_d = None

        if cur_tid == "SINK_BASE":
            _params = dict(m.get("params", {}) or {})
            _default_cut_w = int(_params.get("sink_cutout_width_mm", max(400, min(int(m.get('w_mm', 800)) - 80, 500))) or max(400, min(int(m.get('w_mm', 800)) - 80, 500)))
            _default_cut_d = int(_params.get("sink_cutout_depth_mm", max(400, min(int(m.get('d_mm', 560)) - 40, 480))) or max(400, min(int(m.get('d_mm', 560)) - 40, 480)))
            _default_cut_x = int(_params.get("sink_cutout_x_mm", max(0, int((int(m.get('w_mm', 800)) - _default_cut_w) / 2))) or max(0, int((int(m.get('w_mm', 800)) - _default_cut_w) / 2)))
            _sink_title = _t('edit.sink_cutout_title')
            _sink_x_lbl = _t('edit.cutout_x_label')
            _sink_w_lbl = _t('edit.cutout_w_label')
            _sink_d_lbl = _t('edit.cutout_d_label')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_sink_title).classes('text-xs font-bold text-gray-700')
                sink_cutout_x = ui.number(value=_default_cut_x, min=0, max=max(0, int(m.get('w_mm', 800)) - 200), step=5, label=_sink_x_lbl).props('dense outlined').classes('w-full')
                sink_cutout_w = ui.number(value=_default_cut_w, min=300, max=max(300, int(m.get('w_mm', 800)) - 40), step=5, label=_sink_w_lbl).props('dense outlined').classes('w-full')
                sink_cutout_d = ui.number(value=_default_cut_d, min=300, max=max(300, int(m.get('d_mm', 560)) - 20), step=5, label=_sink_d_lbl).props('dense outlined').classes('w-full')

        if cur_tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
            _params = dict(m.get("params", {}) or {})
            _default_hob_w = int(_params.get("hob_cutout_width_mm", max(450, min(int(m.get('w_mm', 600)) - 60, 560))) or max(450, min(int(m.get('w_mm', 600)) - 60, 560)))
            _default_hob_d = int(_params.get("hob_cutout_depth_mm", max(400, min(int(m.get('d_mm', 560)) - 40, 490))) or max(400, min(int(m.get('d_mm', 560)) - 40, 490)))
            _default_hob_x = int(_params.get("hob_cutout_x_mm", max(0, int((int(m.get('w_mm', 600)) - _default_hob_w) / 2))) or max(0, int((int(m.get('w_mm', 600)) - _default_hob_w) / 2)))
            _hob_title = _t('edit.hob_cutout_title')
            _hob_x_lbl = _t('edit.cutout_x_label')
            _hob_w_lbl = _t('edit.cutout_w_label')
            _hob_d_lbl = _t('edit.cutout_d_label')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_hob_title).classes('text-xs font-bold text-gray-700')
                hob_cutout_x = ui.number(value=_default_hob_x, min=0, max=max(0, int(m.get('w_mm', 600)) - 200), step=5, label=_hob_x_lbl).props('dense outlined').classes('w-full')
                hob_cutout_w = ui.number(value=_default_hob_w, min=350, max=max(350, int(m.get('w_mm', 600)) - 40), step=5, label=_hob_w_lbl).props('dense outlined').classes('w-full')
                hob_cutout_d = ui.number(value=_default_hob_d, min=300, max=max(300, int(m.get('d_mm', 560)) - 20), step=5, label=_hob_d_lbl).props('dense outlined').classes('w-full')

        if cur_tid == "BASE_DISHWASHER":
            _dish = dishwasher_installation_metrics(state.kitchen, m)
            _dish_title = _t('edit.dishwasher_title')
            _dish_l1 = _t('edit.dishwasher_l1')
            _dish_l2 = _t('edit.dishwasher_l2')
            _dish_l3 = _t('edit.dishwasher_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_dish_title).classes('text-xs font-bold text-gray-700')
                ui.label(_dish_l1).classes('text-[10px] text-gray-600')
                ui.label(_dish_l2).classes('text-[10px] text-gray-600')
                ui.label(_dish_l3).classes('text-[10px] text-gray-500')
                ui.label(_t('edit.dishwasher_available_fmt', value=_dish['dishwasher_available_height_under_worktop'])).classes('text-[10px] text-gray-600')
                ui.label(_t('edit.dishwasher_front_fmt', value=_dish['dishwasher_front_height'])).classes('text-[10px] text-gray-600')
                if _dish["dishwasher_raised_mode"]:
                    ui.label(_t(
                        'edit.dishwasher_raised_fmt',
                        platform=_dish['dishwasher_platform_height'],
                        filler=_dish['dishwasher_lower_filler_height'],
                    )).classes('text-[10px] font-semibold text-gray-700')

        if cur_tid == "BASE_TRASH":
            _trash_title = _t('edit.trash_title')
            _trash_l1 = _t('edit.trash_l1')
            _trash_l2 = _t('edit.trash_l2')
            _trash_l3 = _t('edit.trash_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_trash_title).classes('text-xs font-bold text-gray-700')
                ui.label(_trash_l1).classes('text-[10px] text-gray-600')
                ui.label(_trash_l2).classes('text-[10px] text-gray-600')
                ui.label(_trash_l3).classes('text-[10px] text-gray-500')

        if cur_tid == "BASE_CORNER":
            _corner_title = _t('edit.corner_title')
            _corner_l1 = _t('edit.corner_l1')
            _corner_l2 = _t('edit.corner_l2')
            _corner_l3 = _t('edit.corner_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_corner_title).classes('text-xs font-bold text-gray-700')
                ui.label(_corner_l1).classes('text-[10px] text-gray-600')
                ui.label(_corner_l2).classes('text-[10px] text-gray-600')
                ui.label(_corner_l3).classes('text-[10px] text-gray-500')

        if cur_tid == "END_PANEL":
            _end_title = _t('edit.end_panel_title')
            _end_l1 = _t('edit.end_panel_l1')
            _end_l2 = _t('edit.end_panel_l2')
            _end_l3 = _t('edit.end_panel_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_end_title).classes('text-xs font-bold text-gray-700')
                ui.label(_end_l1).classes('text-[10px] text-gray-600')
                ui.label(_end_l2).classes('text-[10px] text-gray-600')
                ui.label(_end_l3).classes('text-[10px] text-gray-500')

        if cur_tid == "FILLER_PANEL":
            _filler_title = _t('edit.filler_title')
            _filler_l1 = _t('edit.filler_l1')
            _filler_l2 = _t('edit.filler_l2')
            _filler_l3 = _t('edit.filler_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_filler_title).classes('text-xs font-bold text-gray-700')
                ui.label(_filler_l1).classes('text-[10px] text-gray-600')
                ui.label(_filler_l2).classes('text-[10px] text-gray-600')
                ui.label(_filler_l3).classes('text-[10px] text-gray-500')

        if cur_tid in {"TALL_FRIDGE", "TALL_FRIDGE_FREEZER", "TALL_FRIDGE_FREESTANDING"}:
            _fridge_title = _t('edit.fridge_title')
            _fridge_l1 = _t('edit.fridge_l1')
            _fridge_l2 = _t('edit.fridge_l2')
            _fridge_l3 = _t('edit.fridge_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_fridge_title).classes('text-xs font-bold text-gray-700')
                ui.label(_fridge_l1).classes('text-[10px] text-gray-600')
                ui.label(_fridge_l2).classes('text-[10px] text-gray-600')
                ui.label(_fridge_l3).classes('text-[10px] text-gray-500')

        if cur_tid in {"TALL_OVEN", "TALL_OVEN_MICRO"}:
            _is_combo = cur_tid == "TALL_OVEN_MICRO"
            _title = _t('edit.tall_appliance_title')
            _l1 = _t('edit.tall_appliance_l1')
            _l2 = _t('edit.tall_appliance_l2_combo' if _is_combo else 'edit.tall_appliance_l2_single')
            _l3 = _t('edit.tall_appliance_l3')
            with ui.card().classes('w-full p-2 mt-1 bg-gray-50 border border-gray-300'):
                ui.label(_title).classes('text-xs font-bold text-gray-700')
                ui.label(_l1).classes('text-[10px] text-gray-600')
                ui.label(_l2).classes('text-[10px] text-gray-600')
                ui.label(_l3).classes('text-[10px] text-gray-500')

        if has_drawers and not has_door_and_drawer:
            n_drawers_default = int((m.get('params') or {}).get('n_drawers', features.get('n_drawers', 3)))
            existing_heights = list((m.get('params') or {}).get('drawer_heights', []))

            ui.separator().classes('mt-1 mb-0.5')
            ui.label(f'🗂 {_t("edit.drawers_title")}').classes('text-xs font-bold text-gray-700')

            # State: samo lista visina i inputi — bez locked
            drawer_heights_state = {'n': n_drawers_default, 'heights': [], 'inputs': {}}
            fioka_container = ui.column().classes('w-full gap-0.5')
            _e_valid_lbl = [None]
            _e_prop_html  = [None]   # ref na ui.html za proportion bars
            # ── Boje traka (gornja = F1 = plava, itd.) ────────────────────────
            _E_COLORS = ['#111111', '#2f2f2f', '#4b4b4b',
                         '#676767', '#838383', '#9f9f9f']

            def _e_get_total():
                return _inner_h(float(h.value) if hasattr(h, 'value') else int(m.get('h_mm', 720)))

            def _e_distribute_equal_int(total_mm, count):
                total_i = int(round(total_mm))
                count_i = max(1, int(count))
                base = total_i // count_i
                rem = total_i - (base * count_i)
                vals = [base] * count_i
                vals[0] += rem
                return vals

            def _e_refresh_valid():
                total = int(round(_e_get_total()))
                zbir = sum(drawer_heights_state['heights'])
                diff = abs(zbir - total)
                if _e_valid_lbl[0] is not None:
                    if diff < 1:
                        _e_valid_lbl[0].set_text(f'✅ {zbir:.0f} = {total:.0f}mm')
                        _e_valid_lbl[0].classes(remove='text-red-500', add='text-gray-700')
                    else:
                        _warn_hint = _t('edit.drawer_warn_click_recalc')
                        _e_valid_lbl[0].set_text(f'⚠️ {zbir:.0f} ≠ {total:.0f}mm — {_warn_hint}')
                        _e_valid_lbl[0].classes(remove='text-gray-700', add='text-red-500')

            def _e_update_prop_bars():
                """Instant CSS proportion preview — bez matplotlib, nula lag-a."""
                if _e_prop_html[0] is None:
                    return
                heights = drawer_heights_state['heights']
                if not heights:
                    return
                total_h = max(1.0, sum(heights))
                parts = [
                    '<div style="display:flex;flex-direction:column;gap:2px;'
                    'width:100%;height:80px;border-radius:4px;overflow:hidden;">'
                ]
                for i, hv in enumerate(heights):
                    grow = max(1, int(hv / total_h * 1000))
                    col  = _E_COLORS[i % len(_E_COLORS)]
                    parts.append(
                        f'<div style="flex-grow:{grow};background:{col};'
                        f'display:flex;align-items:center;padding:0 6px;'
                        f'color:#fff;font-size:10px;font-weight:600;'
                        f'overflow:hidden;white-space:nowrap;">'
                        f'F{i+1}&nbsp;·&nbsp;{int(hv)}mm</div>'
                    )
                parts.append('</div>')
                _e_prop_html[0].set_content(''.join(parts))

            def _e_auto_redistribute(idx, new_val, heights, total, n):
                """Set heights[idx]=new_val, redistribute remaining proportionally."""
                redistributed = redistribute_drawers_proportional(
                    heights,
                    changed_idx=idx,
                    requested_height=new_val,
                    total_target=total,
                    min_h=MIN_DRAWER_H,
                    step=1,
                )
                for pos in range(min(n, len(redistributed))):
                    heights[pos] = int(redistributed[pos])
                return heights

            def _e_build(n, init_list=None):
                fioka_container.clear()
                drawer_heights_state['inputs'].clear()
                total = int(round(_e_get_total()))
                if init_list and len(init_list) == n:
                    heights = [int(round(float(x))) for x in init_list]
                else:
                    heights = _e_distribute_equal_int(total, n)
                drawer_heights_state['heights'] = heights
                drawer_heights_state['original_heights'] = list(heights)
                drawer_heights_state['n'] = n
                with fioka_container:
                    # Horizontalni prikaz: F1 (lijevo) = gornja fioka (index 0)
                    with ui.grid().classes('w-full grid-cols-2 gap-2 lg:grid-cols-4'):
                        for i in range(n):
                            with ui.column().classes('w-full gap-0 min-w-0'):
                                ui.label(f'F{i+1}').classes('text-[10px] text-center text-gray-500')
                                def _on_change(e, idx=i):
                                    try:
                                        logger.info(
                                            "DRAWER_EDIT change start idx=%s raw=%r heights_before=%s",
                                            idx,
                                            getattr(e, 'value', None),
                                            drawer_heights_state.get('heights', []),
                                        )
                                        h_state = list(drawer_heights_state['heights'])
                                        _n = drawer_heights_state['n']
                                        _total = _e_get_total()
                                        _e_auto_redistribute(idx, float(e.value), h_state, _total, _n)
                                        drawer_heights_state['heights'] = h_state
                                        logger.info(
                                            "DRAWER_EDIT change applied idx=%s heights_after=%s",
                                            idx,
                                            h_state,
                                        )
                                        for j, inp in drawer_heights_state['inputs'].items():
                                            if j != idx:
                                                try:
                                                    inp.set_value(int(h_state[j]))
                                                except Exception as ex:
                                                    logger.debug("Edit drawer input sync failed: %s", ex)
                                        _e_refresh_valid()
                                        _e_update_prop_bars()   # ← instant vizuelni feedback
                                    except Exception as ex:
                                        logger.exception("DRAWER_EDIT change failed idx=%s", idx)
                                        logger.debug("Edit drawer redistribute failed: %s", ex)
                                inp = ui.number(
                                    value=int(heights[i]),
                                    min=MIN_DRAWER_H, max=int(total),
                                    step=1, on_change=_on_change
                                ).props('outlined dense').classes('w-full min-w-[110px]')
                                inp.on('update:model-value', _on_change)
                                drawer_heights_state['inputs'][i] = inp
                _e_refresh_valid()
                _e_update_prop_bars()

            def _e_recalc():
                n = drawer_heights_state['n']
                total = int(round(_e_get_total()))
                current = list(drawer_heights_state['heights'])
                original = drawer_heights_state.get('original_heights', [])
                THRESHOLD = 1.0
                if original and len(original) == n:
                    modified = {i for i in range(n) if abs(current[i] - original[i]) > THRESHOLD}
                else:
                    orig_per = total / n
                    modified = {i for i in range(n) if abs(current[i] - orig_per) > THRESHOLD}
                # Ako su sve izmenjene — zadrži sve osim prve, preračunaj prvu
                if len(modified) == n:
                    modified = set(range(1, n))
                free_indices = [i for i in range(n) if i not in modified]
                heights = rebalance_drawers_proportional(
                    current,
                    fixed_indices=modified,
                    total_target=total,
                    min_h=MIN_DRAWER_H,
                    step=1,
                    basis_heights=original if original and len(original) == n else current,
                )
                drawer_heights_state['heights'] = heights
                if 'original_heights' not in drawer_heights_state:
                    drawer_heights_state['original_heights'] = list(heights)
                else:
                    for i in free_indices:
                        drawer_heights_state['original_heights'][i] = heights[i]
                for idx, inp in drawer_heights_state['inputs'].items():
                    try:
                        inp.set_value(int(heights[idx]))
                    except Exception as ex:
                        logger.debug("Edit drawer recalc UI sync failed: %s", ex)
                _e_refresh_valid()
                _e_update_prop_bars()

            def _on_n_change_e(e):
                _e_build(int(float(e.value)))
                _e_update_prop_bars()

            with ui.row().classes('w-full items-center gap-1 mt-0.5'):
                ui.label(_t('edit.drawer_count')).classes('text-xs text-gray-500 w-14 shrink-0')
                ui.number(value=n_drawers_default, min=1, max=6, step=1,
                          on_change=_on_n_change_e).props('dense outlined').classes('w-14')
                ui.button(SYM_RECALC, on_click=_e_recalc).props('flat dense').classes(
                    'text-xs text-gray-700 border border-gray-300 px-1')
                _e_valid_lbl[0] = ui.label('').classes('text-xs text-gray-700 flex-1 text-right')

            # ── Proportion bars — instant CSS preview ─────────────────────────
            with ui.row().classes('w-full items-center gap-1 mt-1'):
                ui.label(SYM_BLACK_SQUARE).classes('text-[9px] text-gray-400 shrink-0')
                _e_prop_html[0] = ui.html('').classes('flex-1')

            _e_build(n_drawers_default, existing_heights)
            _e_update_prop_bars()  # initial render
        elif has_door_and_drawer:
            corp_h = float(h.value) if hasattr(h, 'value') else int(m.get('h_mm', 720))
            _params_dd = dict(m.get("params", {}) or {})
            _drawer_list_dd = list(_params_dd.get("drawer_heights", []) or [])
            default_drawer_h = float(_drawer_list_dd[0]) if _drawer_list_dd else 170.0
            default_door_h = float(_params_dd.get("door_height", corp_h - default_drawer_h) or (corp_h - default_drawer_h))
            default_drawer_h = max(float(MIN_DRAWER_H), min(default_drawer_h, corp_h - 180.0))
            default_door_h = max(180.0, min(default_door_h, corp_h - float(MIN_DRAWER_H)))
            ui.separator().classes('mt-1 mb-0.5')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(_t('edit.door_height')).classes('text-xs text-gray-500 w-14 shrink-0')
                door_h_inp = ui.number(value=round(default_door_h, 1), min=100,
                                       max=int(corp_h - MIN_DRAWER_H), step=1).props(
                    'dense outlined suffix=mm').classes('flex-1')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(_t('edit.drawer_height')).classes('text-xs text-gray-500 w-14 shrink-0')
                drawer_h_inp = ui.number(value=round(default_drawer_h, 1), min=MIN_DRAWER_H,
                                         max=int(corp_h - 180), step=1).props(
                    'dense outlined suffix=mm').classes('flex-1')
            _dd_sum_lbl = ui.label('').classes('text-xs text-gray-600')
            _door_drawer_syncing = {'value': False}

            def _update_dd_sum_hint():
                try:
                    door_val = float(door_h_inp.value or 0)
                    drawer_val = float(drawer_h_inp.value or 0)
                    remaining = corp_h - door_val - drawer_val
                    if remaining < 0:
                        _dd_sum_lbl.set_text(_t('elements.door_drawer_sum_too_high', total=door_val + drawer_val, h=corp_h))
                    else:
                        _dd_sum_lbl.set_text(_t('elements.door_drawer_sum_ok', total=door_val + drawer_val, reserve=remaining))
                except Exception:
                    pass

            def _on_door_change(e=None):
                if _door_drawer_syncing['value']:
                    return
                try:
                    _door_drawer_syncing['value'] = True
                    door_val = max(180.0, min(float(door_h_inp.value or 0), corp_h - float(MIN_DRAWER_H)))
                    drawer_h_inp.set_value(max(float(MIN_DRAWER_H), corp_h - door_val))
                finally:
                    _door_drawer_syncing['value'] = False
                _update_dd_sum_hint()

            def _on_drawer_change(e=None):
                if _door_drawer_syncing['value']:
                    return
                try:
                    _door_drawer_syncing['value'] = True
                    drawer_val = max(float(MIN_DRAWER_H), min(float(drawer_h_inp.value or 0), corp_h - 180.0))
                    door_h_inp.set_value(max(180.0, corp_h - drawer_val))
                finally:
                    _door_drawer_syncing['value'] = False
                _update_dd_sum_hint()

            door_h_inp.on('change', _on_door_change)
            drawer_h_inp.on('change', _on_drawer_change)
            _update_dd_sum_hint()
        # ── Police (n_shelves) za zatvorene elemente s vratima ──────────────
        n_shelves_inp = None
        if has_shelves_edit:
            _cur_n_sh = default_shelf_count(
                cur_tid,
                zone=zone_m,
                h_mm=float(m.get('h_mm', 720) or 720),
                params=(m.get('params') or {}),
                features=features,
            )
            _corp_h_sh = float(m.get('h_mm', 720))
            _inner_h_sh = _corp_h_sh - 2 * carcass_thk
            ui.separator().classes('mt-1 mb-0.5')
            ui.label(f'📦 {_t("elements.panel_shelves")}').classes('text-xs font-bold text-gray-700')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(_t('elements.panel_shelf_count')).classes('text-xs text-gray-500 w-20 shrink-0')
                n_shelves_inp = ui.number(
                    value=_cur_n_sh, min=0, max=12, step=1,
                ).props('dense outlined').classes('w-16')
                _sp_lbl = ui.label('').classes('text-xs text-gray-400 flex-1')

            def _update_shelf_spacing(e=None):
                try:
                    n = int(n_shelves_inp.value or 0)
                    _h_val = float(h.value) if hasattr(h, 'value') else _corp_h_sh
                    _inn = _h_val - 2 * carcass_thk
                    if n > 0:
                        _sp = _inn / (n + 1)
                        _sp_lbl.set_text(_t('elements.panel_spacing', val=f'{_sp:.0f}'))
                    else:
                        _sp_lbl.set_text(_t('elements.panel_no_shelves'))
                except Exception:
                    pass

            n_shelves_inp.on('update:model-value', _update_shelf_spacing)
            _update_shelf_spacing()

        # ── Boja materijala (samo za OPEN elemente) ──────────────────────────
        if _is_open:
            ui.separator().classes('mt-1 mb-0.5')
            render_color_picker(
                ui=ui,
                presets=_FRONT_COLOR_PRESETS,
                color_ref=_open_color_ref,
                title=f'🎨 {_t("elements.material_color")}',
                columns=4,
                swatch_h=28,
                lang=_lang,
            )

        same_zone_mods = [
            mm for mm in mods
            if str(mm.get("zone", "")).lower() == zone_m
            and int(mm.get("id", -1)) != current_id
        ]
        swap_sel = None
        if same_zone_mods:
            swap_options = [
                (f"#{mm.get('id')} {mm.get('label','')} X={mm.get('x_mm')}mm", int(mm.get("id", 0)))
                for mm in same_zone_mods
            ]
            ui.separator().classes('mt-1 mb-0.5')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(_t('edit.swap_with')).classes('text-xs text-gray-500 w-14 shrink-0')
                swap_sel = ui.select(
                    swap_options,
                    value=swap_options[0],
                ).props('dense outlined').classes('flex-1')

        # Zamrzni ID za closures
        _frozen_id = current_id
        _frozen_zone = zone_m
        _frozen_tid = cur_tid
        _frozen_wk = str(m.get("wall_key", "A") or "A").upper()
        def _apply():
            try:
                # Uzmi svež m po frozen ID
                fresh_mods = state.kitchen.get("modules", []) or []
                fresh_m = next((mm for mm in fresh_mods if int(mm.get('id', -1)) == _frozen_id), None)
                if not fresh_m:
                    ui.notify(_t('edit.element_not_found'), type='negative')
                    return
                new_h = int(h.value)
                if new_h > max_h:
                    ui.notify(
                        f'⚠️ {_t("edit.height_limit_exceeded_fmt", value=new_h, max_h=max_h)}',
                        type='negative'
                    )
                    return

                # ── Depth mode logika pri editovanju ──────────────────────────
                new_d = int(d.value)
                _cur_dm = get_depth_mode(fresh_m)
                _zone_std_d = get_zone_depth_standard(_frozen_zone)
                _is_indep_edit = is_independent_depth(_frozen_tid)

                def _do_apply_with_depth(use_d: int, new_dm: str = None):
                    _apply_inner(fresh_m, use_d, new_dm)

                def _apply_inner(fm, use_d: int, new_dm: str = None):
                    nonlocal new_params_ref
                    new_params_ref = dict(fm.get("params") or {})
                    if handle_side_sel is not None:
                        new_params_ref["handle_side"] = str(handle_side_sel.value)
                    _collect_drawer_params(new_params_ref)
                    _manual_x = int(x.value) != int(fm.get("x_mm", 0))
                    update_module_local(
                        _frozen_id,
                        x_mm=int(x.value),
                        w_mm=int(w.value),
                        h_mm=new_h,
                        d_mm=use_d,
                        gap_after_mm=int(g.value),
                        label=str(name_inp.value),
                        template_id=_frozen_tid,
                        params=new_params_ref,
                        manual_x=_manual_x or bool(fm.get("manual_x", False)),
                    )
                    # Ažuriraj depth_mode na modulu direktno
                    upd_mods = state.kitchen.get("modules", []) or []
                    upd_m = next((mm for mm in upd_mods if int(mm.get('id', -1)) == _frozen_id), None)
                    if upd_m is not None:
                        if _is_indep_edit:
                            upd_m["depth_mode"] = "INDEPENDENT"
                        elif new_dm:
                            upd_m["depth_mode"] = new_dm
                        elif use_d != _zone_std_d and _cur_dm != "INDEPENDENT":
                            upd_m["depth_mode"] = "CUSTOM"
                        elif use_d == _zone_std_d:
                            upd_m["depth_mode"] = "STANDARD"
                    if drawer_heights_state is not None:
                        n_cur_e = int(drawer_heights_state.get('n', 3))
                        heights_e = new_params_ref.get('drawer_heights', [])
                        ui.notify(
                            f'✅ {_t("edit.saved_drawers_fmt", n=n_cur_e, heights=heights_e)}',
                            type='positive'
                        )
                    else:
                        ui.notify(_t('edit.saved'), type='positive')
                    nacrt_refresh()
                    edit_panel_refresh()

                new_params_ref = {}

                def _collect_drawer_params(p: dict):
                    if drawer_heights_state is not None:
                        n_cur_e = int(drawer_heights_state.get('n', 3))
                        current_heights_e = drawer_heights_state.get('heights', [])
                        inner_e = new_h - 2 * carcass_thk
                        per_e = inner_e / n_cur_e if n_cur_e > 0 else inner_e
                        if len(current_heights_e) == n_cur_e:
                            p['drawer_heights'] = [int(round(hv)) for hv in current_heights_e]
                        else:
                            locked_e = drawer_heights_state.get('locked', {})
                            p['drawer_heights'] = [int(round(locked_e.get(i, per_e))) for i in range(n_cur_e)]
                        p['n_drawers'] = n_cur_e
                    if door_h_inp is not None:
                        dh_e = float(door_h_inp.value)
                        fioka_e = float(drawer_h_inp.value) if drawer_h_inp is not None else (new_h - dh_e)
                        if dh_e + fioka_e > float(new_h):
                            raise ValueError(
                                _t('elements.door_drawer_sum_too_high', total=dh_e + fioka_e, h=float(new_h))
                            )
                        p['door_height'] = dh_e
                        p['drawer_heights'] = [int(round(fioka_e))]
                        p['n_drawers'] = 1
                    # Sačuvaj broj polica za zatvorene elemente s vratima
                    if n_shelves_inp is not None:
                        p['n_shelves'] = int(n_shelves_inp.value or 0)
                    if cur_tid == "SINK_BASE":
                        if sink_cutout_x is not None:
                            p['sink_cutout_x_mm'] = int(float(sink_cutout_x.value or 0))
                        if sink_cutout_w is not None:
                            p['sink_cutout_width_mm'] = int(float(sink_cutout_w.value or 0))
                        if sink_cutout_d is not None:
                            p['sink_cutout_depth_mm'] = int(float(sink_cutout_d.value or 0))
                    if cur_tid in {"BASE_COOKING_UNIT", "BASE_HOB"}:
                        if hob_cutout_x is not None:
                            p['hob_cutout_x_mm'] = int(float(hob_cutout_x.value or 0))
                        if hob_cutout_w is not None:
                            p['hob_cutout_width_mm'] = int(float(hob_cutout_w.value or 0))
                        if hob_cutout_d is not None:
                            p['hob_cutout_depth_mm'] = int(float(hob_cutout_d.value or 0))
                    # Sačuvaj boju materijala za OPEN elemente
                    if _is_open and _open_color_ref.get('value'):
                        p['front_color'] = _open_color_ref['value']

                # Aparat → direktno, bez pitanja
                if _is_indep_edit:
                    _apply_inner(fresh_m, new_d, "INDEPENDENT")
                    return

                # d_mm se promenio od zone standarda → pitaj korisnika
                if new_d != _zone_std_d and _cur_dm != "CUSTOM":
                    with ui.dialog() as _dlg_edit_d:
                        with ui.card().classes('p-4 gap-2 min-w-72'):
                            ui.label(
                                _t(
                                    'edit.depth_dialog_title_fmt',
                                    new_d=new_d,
                                    zone=_frozen_zone.upper(),
                                    std_d=_zone_std_d,
                                )
                            ).classes('font-bold text-sm')
                            ui.label(_t('edit.depth_dialog_ask')).classes('text-sm text-gray-600')
                            with ui.column().classes('w-full gap-2 mt-2'):
                                def _set_as_std_edit(dlg=_dlg_edit_d, nd=new_d, fzone=_frozen_zone, fm=fresh_m):
                                    dlg.close()
                                    set_zone_depth_standard(fzone, nd, update_existing=False)
                                    _apply_inner(fm, nd, "STANDARD")
                                    ui.notify(
                                        f'📐 {_t("edit.depth_std_set_fmt", zone=fzone.upper(), depth=nd)}',
                                        type='info'
                                    )
                                def _keep_custom_edit(dlg=_dlg_edit_d, nd=new_d, fm=fresh_m):
                                    dlg.close()
                                    _apply_inner(fm, nd, "CUSTOM")
                                def _cancel_edit(dlg=_dlg_edit_d):
                                    dlg.close()
                                ui.button(
                                    f'📐 {_t("edit.set_new_std_fmt", depth=new_d, zone=_frozen_zone.upper())}',
                                    on_click=_set_as_std_edit
                                ).classes('w-full bg-white text-[#111] border border-[#111] text-xs')
                                ui.button(
                                    _t('edit.only_this_custom'),
                                    on_click=_keep_custom_edit
                                ).classes('w-full bg-gray-100 text-xs')
                                ui.button(_t('common.cancel'), on_click=_cancel_edit).classes('w-full text-xs')
                    _dlg_edit_d.open()
                    return

                # d_mm se vratio na standard
                if new_d == _zone_std_d and _cur_dm == "CUSTOM":
                    _apply_inner(fresh_m, new_d, "STANDARD")
                    return

                # Nema promene u depth_mode → standardan put (koristi _apply_inner)
                _apply_inner(fresh_m, new_d)
            except Exception as e:
                ui.notify(format_user_error(e, getattr(state, 'language', 'sr')), type='negative')

        def _delete():
            delete_module_local(_frozen_id)
            state.selected_edit_id = 0
            state.mode = "add"
            ui.notify(_t('edit.element_deleted'), type='warning')
            nacrt_refresh()
            edit_panel_refresh()

        def _swap():
            if swap_sel is None:
                return
            try:
                other_id = int(swap_sel.value[1])
                fresh_mods = state.kitchen.get("modules", []) or []
                mod_a = next((mm for mm in fresh_mods if int(mm.get("id", -1)) == _frozen_id), None)
                mod_b = next((mm for mm in fresh_mods if int(mm.get("id", -1)) == other_id), None)
                if mod_a and mod_b:
                    x_a = int(mod_a.get("x_mm", 0))
                    x_b = int(mod_b.get("x_mm", 0))
                    mod_a["x_mm"] = x_b
                    mod_b["x_mm"] = x_a
                    solve_layout(state.kitchen, zone=_frozen_zone, mode="pack", wall_key=_frozen_wk)
                    ui.notify(
                        _t('edit.swap_ok_fmt', id_a=mod_a["id"], id_b=mod_b["id"]),
                        type='positive'
                    )
                    nacrt_refresh()
                    edit_panel_refresh()
            except Exception as e:
                ui.notify(_t('elements.error_swap', err=format_user_error(e, getattr(state, 'language', 'sr'))), type='negative')

        def _duplicate():
            try:
                fresh_mods = state.kitchen.get("modules", []) or []
                src = next((mm for mm in fresh_mods if int(mm.get("id", -1)) == _frozen_id), None)
                if not src:
                    ui.notify(_t('edit.element_not_found'), type='negative')
                    return

                _new_x = int(src.get("x_mm", 0)) + int(src.get("w_mm", 0)) + int(src.get("gap_after_mm", 0))
                _new_label = str(src.get('label', 'Element')).strip() or 'Element'
                _new_mod = duplicate_module_local(
                    template_id=str(src.get("template_id", _frozen_tid)),
                    zone=_frozen_zone,
                    x_mm=_new_x,
                    w_mm=int(src.get("w_mm", 600)),
                    h_mm=int(src.get("h_mm", 720)),
                    d_mm=int(src.get("d_mm", 560)),
                    gap_after_mm=int(src.get("gap_after_mm", 0)),
                    label=_new_label,
                    params=dict(src.get("params", {}) or {}),
                )
                state.selected_edit_id = int((_new_mod or {}).get("id", 0))
                state.mode = "edit"
                ui.notify(_t('elements.duplicate_ok'), type='positive')
                nacrt_refresh()
                edit_panel_refresh()
            except Exception as e:
                ui.notify(_t('elements.error_duplicate', err=format_user_error(e, getattr(state, 'language', 'sr'))), type='negative')

        ui.separator().classes('mt-1 mb-0.5')
        with ui.row().classes('w-full gap-1 mt-1'):
            ui.button(_t('edit.apply'), on_click=_apply).props('dense').classes(
                'flex-1 text-xs font-bold btn-wrap')
            ui.button(_t('edit.duplicate'), on_click=_duplicate).props('dense').classes(
                'flex-1 text-xs btn-wrap')
            ui.button(_t('edit.delete'), on_click=_delete).props('dense').classes(
                'flex-1 text-xs btn-wrap')
        if swap_sel:
            ui.button(_t('edit.swap_positions'), on_click=_swap).props('dense').classes(
                'w-full text-xs mt-0.5 btn-wrap')

        # ── Dodaj red iznad — wall zona → wall_upper ─────────────────────────
        if _frozen_zone == 'wall':
            ui.separator().classes('mt-2 mb-1')
            ui.label(_t('edit.second_row')).classes(
                'text-[10px] font-semibold uppercase tracking-wider text-gray-400')
            ui.button(
                _t('edit.add_upper_above'),
                on_click=lambda: open_add_above_dialog(_frozen_id)
            ).props('dense').classes('w-full text-xs mt-0.5 btn-wrap')

        # ── Dodaj nadstrešni — tall zona → tall_top ──────────────────────────
        if _frozen_zone == 'tall':
            ui.separator().classes('mt-2 mb-1')
            ui.label(_t('edit.top_element')).classes(
                'text-[10px] font-semibold uppercase tracking-wider text-gray-400')
            ui.button(
                _t('edit.add_above_tall'),
                on_click=lambda: open_add_above_tall_dialog(_frozen_id)
            ).props('dense').classes('w-full text-xs mt-0.5 btn-wrap')



