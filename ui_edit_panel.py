# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    BTN_OBRISI_ELEMENT,
    BTN_OTKAZI,
    BTN_PRIMENI,
    EDIT_BTN_ADD_UPPER_ABOVE,
    EDIT_BTN_ONLY_THIS_CUSTOM,
    EDIT_BTN_SET_NEW_STD_FMT,
    EDIT_BTN_DUPLICATE,
    EDIT_BTN_SWAP_POS,
    EDIT_DEPTH_ASK,
    EDIT_DEPTH_DIALOG_TITLE_FMT,
    EDIT_DRAWERS_TITLE,
    EDIT_LABEL_DRAWER_COUNT,
    EDIT_LABEL_DOOR_H,
    EDIT_LABEL_GAP_MM,
    EDIT_LABEL_HANDLE,
    EDIT_LABEL_MAX_H_FMT,
    EDIT_LABEL_NAME,
    EDIT_LABEL_SWAP,
    EDIT_LABEL_X_MM,
    EDIT_NOTIFY_HEIGHT_LIMIT_FMT,
    EDIT_NOTIFY_DEPTH_STD_SET_FMT,
    EDIT_NOTIFY_SAVED,
    EDIT_NOTIFY_SAVED_DRAWERS_FMT,
    EDIT_NOTIFY_SWAP_OK_FMT,
    EDIT_SECTION_TOP_ELEMENT,
    EDIT_SECTION_SECOND_ROW,
    LBL_DODAJ_IZNAD_VISOKOG,
    LBL_DUBINA_MM,
    LBL_ELEMENT_NA_ZIDU,
    LBL_SIRINA_MM,
    SYM_BLACK_SQUARE,
    SYM_RECALC,
    MSG_ELEMENT_NIJE_PRONADJEN,
    MSG_ELEMENT_OBRISAN,
    MSG_GRESKA_PREFIX,
    MSG_NEMA_ELEMENATA_NA_ZIDU,
)
from ui_panels_helpers import format_user_error

from ui_color_picker import render_color_picker
from ui_catalog_config import _FRONT_COLOR_PRESETS


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
        ui.label(MSG_NEMA_ELEMENATA_NA_ZIDU).classes('text-gray-400 text-sm p-4')
        return

    # Kratak format da ne širi sidebar
    _ZONE_SHORT = {'base': 'D', 'wall': 'G', 'wall_upper': 'G2',
                   'tall': 'V', 'tall_top': 'VT'}
    labels = [
        f"#{m.get('id')} [{_ZONE_SHORT.get(str(m.get('zone','')).lower(), '?')}] "
        f"{m.get('label','')[:18]} {m.get('w_mm','')}mm"
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

    ui.select(labels, value=current_label, label=LBL_ELEMENT_NA_ZIDU,
              on_change=_on_select).classes('w-full')

    # Uvek uzmi svez m iz kitchen po ID-u
    current_id = int(state.selected_edit_id)
    m = next((mod for mod in mods if int(mod.get('id', -1)) == current_id), None)
    if not m:
        ui.label(MSG_ELEMENT_NIJE_PRONADJEN).classes('text-red-500 text-sm p-2')
        return

    cur_tid = str(m.get("template_id", "")).upper()
    zone_m = str(m.get("zone", "base")).lower()
    # Za wall_upper: postavi target_x da funkcija nađe pravi wall element ispod
    # i izračuna tačan max (do plafona, od gornje ivice elementa ispod)
    if zone_m == 'wall_upper':
        state.wall_upper_target_x = int(m.get('x_mm', -1))
    max_h = max_allowed_h_for_zone(zone_m)

    _OPEN_TIDS = {'BASE_OPEN', 'WALL_OPEN', 'TALL_OPEN', 'TALL_TOP_OPEN', 'WALL_UPPER_OPEN'}
    _is_open = cur_tid in _OPEN_TIDS
    _open_color_ref = {'value': str((m.get('params') or {}).get('front_color') or '')}

    with ui.card().classes('w-full p-2 mt-1'):
        # ── Header ───────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center justify-between mb-1'):
            ui.label(f"#{m.get('id')}  {m.get('label','')}").classes('font-bold text-sm')
            _zc = {'base': 'bg-gray-100 text-gray-800',
                   'wall': 'bg-gray-100 text-gray-800',
                   'tall': 'bg-gray-100 text-gray-800'}.get(zone_m, 'bg-gray-100 text-gray-700')
            ui.label(zone_m.upper()).classes(f'text-xs px-1.5 py-0.5 rounded font-mono {_zc}')
        ui.separator().classes('mb-1')

        # ── Kompaktna grid forma — 2 polja po redu ──────────────────────────────
        def _lbl(txt: str):
            ui.label(txt).classes('text-xs text-gray-400 leading-none mb-0.5')

        def _col():
            return ui.column().classes('flex-1 gap-0 min-w-0')

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(EDIT_LABEL_X_MM)
                x = ui.number(value=int(m.get('x_mm', 0)), min=0, max=20000, step=5).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(LBL_SIRINA_MM)
                w = ui.number(value=int(m.get('w_mm', 0)), min=100, max=3000, step=10).props(
                    'dense outlined').classes('w-full')

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(EDIT_LABEL_MAX_H_FMT.format(max_h=max_h))
                h = ui.number(value=min(int(m.get('h_mm', 0)), max_h), min=100, max=max_h, step=10).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(LBL_DUBINA_MM)
                d = ui.number(value=int(m.get('d_mm', 0)), min=100, max=2000, step=10).props(
                    'dense outlined').classes('w-full')

        # ── Depth mode badge ──────────────────────────────────────────────────
        _dm = get_depth_mode(m)
        _dm_zone_std = get_zone_depth_standard(zone_m)
        if _dm == "INDEPENDENT":
            _dm_txt = f'🔧 Nezavisna dubina ({int(m.get("d_mm", 0))} mm)'
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        elif _dm == "CUSTOM":
            _dm_txt = f'✏️ Prilagođeno ({int(m.get("d_mm", 0))} mm) — zonski standard: {_dm_zone_std} mm'
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        else:  # STANDARD
            _dm_txt = f'📐 Standardna dubina ({_dm_zone_std} mm)'
            _dm_cls = 'text-xs px-2 py-0.5 rounded bg-gray-50 text-gray-700 border border-gray-300 mb-1'
        ui.label(_dm_txt).classes(_dm_cls)

        with ui.row().classes('w-full gap-1'):
            with _col():
                _lbl(EDIT_LABEL_GAP_MM)
                g = ui.number(value=int(m.get('gap_after_mm', 0)), min=0, max=500, step=1).props(
                    'dense outlined').classes('w-full')
            with _col():
                _lbl(EDIT_LABEL_NAME)
                name_inp = ui.input(value=str(m.get('label', ''))).props(
                    'dense outlined').classes('w-full')

        handle_side_sel = None
        _no_handle_side = any(k in cur_tid for k in (
            '2DOOR', 'DRAWERS', 'OPEN', 'SINK', 'FRIDGE', 'FREEZER', 'OVEN', 'HOB',
            'DISHWASHER', 'LIFTUP', 'CORNER', 'GLASS',
        ))
        _has_handle_side = (
            zone_m in ('base', 'wall', 'tall', 'wall_upper') and not _no_handle_side
        )
        if _has_handle_side:
            cur_side = str((m.get("params") or {}).get("handle_side", "right"))
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(EDIT_LABEL_HANDLE).classes('text-xs text-gray-500 w-14 shrink-0')
                handle_side_sel = ui.select(
                    {"left": "◀ Lijevo", "right": "Desno ▶"},
                    value=cur_side,
                ).props('dense outlined').classes('flex-1')

        # Fioke / vrata+fioka / police u edit panelu
        features = templates.get(cur_tid, {}).get("features", {}) if cur_tid in templates else {}
        has_drawers = features.get("drawers", False)
        has_door_and_drawer = features.get("doors", False) and features.get("drawers", False)
        # Police: zatvoreni elementi s vratima koji NISU fioke ni aparati
        _NO_SHELF_EDIT = ("FRIDGE", "DISHWASHER", "COOKING_UNIT", "OVEN_HOB",
                          "OVEN", "SINK", "HOOD", "GLASS",
                          "NARROW", "DRAWER", "LIFTUP")
        has_shelves_edit = (
            (features.get("doors", False) or features.get("open", False) or features.get("pantry", False))
            and not has_drawers
            and not any(_k in cur_tid.upper() for _k in _NO_SHELF_EDIT)
        )
        carcass_thk = float(state.kitchen.get("materials", {}).get("carcass_thk", 18))
        MIN_DRAWER_H = 80
        SHELF_STEP = 250  # mm — preporučeni razmak između polica

        def _inner_h(corp_h: float) -> float:
            return corp_h - 2 * carcass_thk

        drawer_heights_state = None
        door_h_inp = None

        if has_drawers and not has_door_and_drawer:
            n_drawers_default = int((m.get('params') or {}).get('n_drawers', features.get('n_drawers', 3)))
            existing_heights = list((m.get('params') or {}).get('drawer_heights', []))

            ui.separator().classes('mt-1 mb-0.5')
            ui.label(f'🗂 {EDIT_DRAWERS_TITLE}').classes('text-xs font-bold text-gray-700')

            # State: samo lista visina i inputi — bez locked
            drawer_heights_state = {'n': n_drawers_default, 'heights': [], 'inputs': {}}
            fioka_container = ui.column().classes('w-full gap-0.5')
            _e_valid_lbl = [None]
            _e_prop_html  = [None]   # ref na ui.html za proportion bars
            _e_autosave_t = [None]   # ref na debounce timer

            # ── Boje traka (gornja = F1 = plava, itd.) ────────────────────────
            _E_COLORS = ['#111111', '#2f2f2f', '#4b4b4b',
                         '#676767', '#838383', '#9f9f9f']

            def _e_get_total():
                return _inner_h(float(h.value) if hasattr(h, 'value') else int(m.get('h_mm', 720)))

            def _e_refresh_valid():
                total = _e_get_total()
                zbir = sum(drawer_heights_state['heights'])
                diff = abs(zbir - total)
                if _e_valid_lbl[0] is not None:
                    if diff < 1:
                        _e_valid_lbl[0].set_text(f'✅ {zbir:.0f} = {total:.0f}mm')
                        _e_valid_lbl[0].classes(remove='text-red-500', add='text-gray-700')
                    else:
                        _e_valid_lbl[0].set_text(f'⚠️ {zbir:.0f} ≠ {total:.0f}mm — klikni ↺')
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
                max_val = total - (n - 1) * MIN_DRAWER_H
                new_val = max(float(MIN_DRAWER_H), min(float(new_val), float(max_val)))
                others = [j for j in range(n) if j != idx]
                remaining = total - new_val
                other_sum = sum(heights[j] for j in others)
                if other_sum > 0:
                    for j in others:
                        heights[j] = remaining * heights[j] / other_sum
                elif others:
                    per = remaining / len(others)
                    for j in others:
                        heights[j] = per
                if others:
                    fix = others[-1]
                    heights[fix] = max(MIN_DRAWER_H,
                                       remaining - sum(heights[j] for j in others if j != fix))
                heights[idx] = new_val
                return heights

            def _e_do_autosave():
                """Sprema drawer_heights u state i osvježava nacrt (bez edit_panel.refresh)."""
                try:
                    if drawer_heights_state is None:
                        return
                    n_cur = int(drawer_heights_state.get('n', 0))
                    cur_h = drawer_heights_state.get('heights', [])
                    if n_cur == 0 or len(cur_h) != n_cur:
                        return
                    fresh_mods = state.kitchen.get('modules', []) or []
                    fresh_m = next(
                        (mm for mm in fresh_mods if int(mm.get('id', -1)) == _frozen_id), None)
                    if not fresh_m:
                        return
                    new_params = dict(fresh_m.get('params') or {})
                    new_params['drawer_heights'] = [round(hh, 1) for hh in cur_h]
                    new_params['n_drawers'] = n_cur
                    update_module_local(
                        _frozen_id,
                        x_mm=int(x.value), w_mm=int(w.value),
                        h_mm=int(h.value), d_mm=int(d.value),
                        gap_after_mm=int(g.value),
                        label=str(name_inp.value),
                        template_id=_frozen_tid,
                        params=new_params,
                    )
                    try:
                        solve_layout(state.kitchen, zone=_frozen_zone, mode="pack", wall_key=_frozen_wk)
                    except Exception as ex:
                        logger.debug("Edit autosave solve_layout failed: %s", ex)
                    nacrt_refresh()
                except Exception as ex:
                    logger.debug("Edit autosave failed: %s", ex)

            def _e_schedule_autosave():
                """Debounced auto-save: 800ms nakon zadnje izmjene."""
                if _e_autosave_t[0] is not None:
                    try:
                        _e_autosave_t[0].active = False
                    except Exception as ex:
                        logger.debug("Edit autosave timer deactivate failed: %s", ex)
                _e_autosave_t[0] = ui.timer(0.8, _e_do_autosave, once=True)

            def _e_build(n, init_list=None):
                fioka_container.clear()
                drawer_heights_state['inputs'].clear()
                total = _e_get_total()
                if init_list and len(init_list) == n:
                    heights = [float(x) for x in init_list]
                else:
                    per = round(total / n, 1)
                    heights = [per] * (n - 1)
                    heights.append(round(total - sum(heights), 1))
                drawer_heights_state['heights'] = heights
                drawer_heights_state['original_heights'] = list(heights)
                drawer_heights_state['n'] = n
                with fioka_container:
                    # Horizontalni prikaz: F1 (lijevo) = gornja fioka (index 0)
                    with ui.row().classes('w-full gap-1'):
                        for i in range(n):
                            with ui.column().classes('flex-1 gap-0 min-w-0'):
                                ui.label(f'F{i+1}').classes('text-[6px] text-center text-gray-400')
                                def _on_change(e, idx=i):
                                    try:
                                        h_state = drawer_heights_state['heights']
                                        _n = drawer_heights_state['n']
                                        _total = _e_get_total()
                                        _e_auto_redistribute(idx, float(e.value), h_state, _total, _n)
                                        drawer_heights_state['heights'] = h_state
                                        for j, inp in drawer_heights_state['inputs'].items():
                                            if j != idx:
                                                try:
                                                    inp.set_value(round(h_state[j], 1))
                                                except Exception as ex:
                                                    logger.debug("Edit drawer input sync failed: %s", ex)
                                        _e_refresh_valid()
                                        _e_update_prop_bars()   # ← instant vizuelni feedback
                                        _e_schedule_autosave()  # ← auto-save za 800ms
                                    except Exception as ex:
                                        logger.debug("Edit drawer redistribute failed: %s", ex)
                                inp = ui.number(
                                    value=round(heights[i], 1),
                                    min=MIN_DRAWER_H, max=int(total),
                                    step=1, on_change=_on_change
                                ).props('outlined dense').classes('w-full')
                                drawer_heights_state['inputs'][i] = inp
                _e_refresh_valid()
                _e_update_prop_bars()

            def _e_recalc():
                n = drawer_heights_state['n']
                total = _e_get_total()
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
                fixed_sum = sum(current[i] for i in modified)
                heights = list(current)
                if free_indices:
                    remaining = total - fixed_sum
                    per = remaining / len(free_indices)
                    for i in free_indices:
                        heights[i] = round(per, 1)
                    rounding_adj = round(total - sum(heights), 1)
                    heights[free_indices[-1]] = round(heights[free_indices[-1]] + rounding_adj, 1)
                else:
                    per = round(total / n, 1)
                    heights = [per] * (n - 1)
                    heights.append(round(total - sum(heights), 1))
                drawer_heights_state['heights'] = heights
                if 'original_heights' not in drawer_heights_state:
                    drawer_heights_state['original_heights'] = list(heights)
                else:
                    for i in free_indices:
                        drawer_heights_state['original_heights'][i] = heights[i]
                for idx, inp in drawer_heights_state['inputs'].items():
                    try:
                        inp.set_value(round(heights[idx], 1))
                    except Exception as ex:
                        logger.debug("Edit drawer recalc UI sync failed: %s", ex)
                _e_refresh_valid()
                _e_update_prop_bars()
                _e_schedule_autosave()

            def _on_n_change_e(e):
                _e_build(int(float(e.value)))
                _e_update_prop_bars()

            with ui.row().classes('w-full items-center gap-1 mt-0.5'):
                ui.label(EDIT_LABEL_DRAWER_COUNT).classes('text-xs text-gray-500 w-14 shrink-0')
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
            inner = _inner_h(corp_h)
            default_drawer_h = min(200.0, inner * 0.28)
            default_door_h = inner - default_drawer_h
            ui.separator().classes('mt-1 mb-0.5')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label(EDIT_LABEL_DOOR_H).classes('text-xs text-gray-500 w-14 shrink-0')
                door_h_inp = ui.number(value=round(default_door_h, 1), min=100,
                                       max=int(inner - MIN_DRAWER_H), step=1).props(
                    'dense outlined suffix=mm').classes('flex-1')
        # ── Police (n_shelves) za zatvorene elemente s vratima ──────────────
        n_shelves_inp = None
        if has_shelves_edit:
            _cur_n_sh = int((m.get('params') or {}).get('n_shelves', 0) or 0)
            _corp_h_sh = float(m.get('h_mm', 720))
            _inner_h_sh = _corp_h_sh - 2 * carcass_thk
            _default_n_sh = max(0, int(_inner_h_sh / SHELF_STEP) - 1)
            if _cur_n_sh == 0:
                _cur_n_sh = _default_n_sh
            ui.separator().classes('mt-1 mb-0.5')
            ui.label('📦 Police').classes('text-xs font-bold text-gray-700')
            with ui.row().classes('w-full items-center gap-1 py-0.5'):
                ui.label('Broj polica').classes('text-xs text-gray-500 w-20 shrink-0')
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
                        _sp_lbl.set_text(f'razmak ≈ {_sp:.0f}mm')
                    else:
                        _sp_lbl.set_text('bez polica')
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
                title='🎨 Boja materijala',
                columns=4,
                swatch_h=28,
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
                ui.label(EDIT_LABEL_SWAP).classes('text-xs text-gray-500 w-14 shrink-0')
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
                    ui.notify(f'⚠️ {MSG_ELEMENT_NIJE_PRONADJEN}', type='negative')
                    return
                new_h = int(h.value)
                if new_h > max_h:
                    ui.notify(
                        f'⚠️ {EDIT_NOTIFY_HEIGHT_LIMIT_FMT.format(h=new_h, max_h=max_h)}',
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
                    )
                    try:
                        solve_layout(state.kitchen, zone=_frozen_zone, mode="pack", wall_key=_frozen_wk)
                    except Exception as ex:
                        logger.debug("Edit drawer recalc input update failed: %s", ex)
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
                            f'✅ {EDIT_NOTIFY_SAVED_DRAWERS_FMT.format(n=n_cur_e, heights=heights_e)}',
                            type='positive'
                        )
                    else:
                        ui.notify(f'✅ {EDIT_NOTIFY_SAVED}', type='positive')
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
                            p['drawer_heights'] = [round(hv, 1) for hv in current_heights_e]
                        else:
                            locked_e = drawer_heights_state.get('locked', {})
                            p['drawer_heights'] = [round(locked_e.get(i, per_e), 1) for i in range(n_cur_e)]
                        p['n_drawers'] = n_cur_e
                    if door_h_inp is not None:
                        dh_e = float(door_h_inp.value)
                        fioka_e = (new_h - 2 * carcass_thk) - dh_e
                        p['door_height'] = dh_e
                        p['drawer_heights'] = [round(fioka_e, 1)]
                        p['n_drawers'] = 1
                    # Sačuvaj broj polica za zatvorene elemente s vratima
                    if n_shelves_inp is not None:
                        p['n_shelves'] = int(n_shelves_inp.value or 0)
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
                                f'🔔 {EDIT_DEPTH_DIALOG_TITLE_FMT.format(new_d=new_d, zone=_frozen_zone.upper(), std_d=_zone_std_d)}'
                            ).classes('font-bold text-sm')
                            ui.label(EDIT_DEPTH_ASK).classes('text-sm text-gray-600')
                            with ui.column().classes('w-full gap-2 mt-2'):
                                def _set_as_std_edit(dlg=_dlg_edit_d, nd=new_d, fzone=_frozen_zone, fm=fresh_m):
                                    dlg.close()
                                    set_zone_depth_standard(fzone, nd, update_existing=False)
                                    _apply_inner(fm, nd, "STANDARD")
                                    ui.notify(
                                        f'📐 {EDIT_NOTIFY_DEPTH_STD_SET_FMT.format(zone=fzone.upper(), depth=nd)}',
                                        type='info'
                                    )
                                def _keep_custom_edit(dlg=_dlg_edit_d, nd=new_d, fm=fresh_m):
                                    dlg.close()
                                    _apply_inner(fm, nd, "CUSTOM")
                                def _cancel_edit(dlg=_dlg_edit_d):
                                    dlg.close()
                                ui.button(
                                    f'📐 {EDIT_BTN_SET_NEW_STD_FMT.format(depth=new_d, zone=_frozen_zone.upper())}',
                                    on_click=_set_as_std_edit
                                ).classes('w-full bg-white text-[#111] border border-[#111] text-xs')
                                ui.button(
                                    f'✏️ {EDIT_BTN_ONLY_THIS_CUSTOM}',
                                    on_click=_keep_custom_edit
                                ).classes('w-full bg-gray-100 text-xs')
                                ui.button(BTN_OTKAZI, on_click=_cancel_edit).classes('w-full text-xs')
                    _dlg_edit_d.open()
                    return

                # d_mm se vratio na standard
                if new_d == _zone_std_d and _cur_dm == "CUSTOM":
                    _apply_inner(fresh_m, new_d, "STANDARD")
                    return

                # Nema promene u depth_mode → standardan put (koristi _apply_inner)
                _apply_inner(fresh_m, new_d)
            except Exception as e:
                ui.notify(f'{MSG_GRESKA_PREFIX}: {format_user_error(e)}', type='negative')

        def _delete():
            delete_module_local(_frozen_id)
            state.selected_edit_id = 0
            state.mode = "add"
            ui.notify(MSG_ELEMENT_OBRISAN, type='warning')
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
                        EDIT_NOTIFY_SWAP_OK_FMT.format(id_a=mod_a["id"], id_b=mod_b["id"]),
                        type='positive'
                    )
                    nacrt_refresh()
                    edit_panel_refresh()
            except Exception as e:
                ui.notify(f'{MSG_GRESKA_PREFIX} pri zameni: {format_user_error(e)}', type='negative')

        def _duplicate():
            try:
                fresh_mods = state.kitchen.get("modules", []) or []
                src = next((mm for mm in fresh_mods if int(mm.get("id", -1)) == _frozen_id), None)
                if not src:
                    ui.notify(MSG_ELEMENT_NIJE_PRONADJEN, type='negative')
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
                ui.notify('Element je kopiran.', type='positive')
                nacrt_refresh()
                edit_panel_refresh()
            except Exception as e:
                ui.notify(f'{MSG_GRESKA_PREFIX} pri dupliranju: {format_user_error(e)}', type='negative')

        ui.separator().classes('mt-1 mb-0.5')
        with ui.row().classes('w-full gap-1 mt-1'):
            ui.button(BTN_PRIMENI, on_click=_apply).props('dense').classes(
                'flex-1 text-xs font-bold btn-wrap')
            ui.button(EDIT_BTN_DUPLICATE, on_click=_duplicate).props('dense').classes(
                'flex-1 text-xs btn-wrap')
            ui.button(BTN_OBRISI_ELEMENT, on_click=_delete).props('dense').classes(
                'flex-1 text-xs btn-wrap')
        if swap_sel:
            ui.button(EDIT_BTN_SWAP_POS, on_click=_swap).props('dense').classes(
                'w-full text-xs mt-0.5 btn-wrap')

        # ── Dodaj red iznad — wall zona → wall_upper ─────────────────────────
        if _frozen_zone == 'wall':
            ui.separator().classes('mt-2 mb-1')
            ui.label(EDIT_SECTION_SECOND_ROW).classes(
                'text-[10px] font-semibold uppercase tracking-wider text-gray-400')
            ui.button(
                EDIT_BTN_ADD_UPPER_ABOVE,
                on_click=lambda: open_add_above_dialog(_frozen_id)
            ).props('dense').classes('w-full text-xs mt-0.5 btn-wrap')

        # ── Dodaj nadstrešni — tall zona → tall_top ──────────────────────────
        if _frozen_zone == 'tall':
            ui.separator().classes('mt-2 mb-1')
            ui.label(EDIT_SECTION_TOP_ELEMENT).classes(
                'text-[10px] font-semibold uppercase tracking-wider text-gray-400')
            ui.button(
                LBL_DODAJ_IZNAD_VISOKOG,
                on_click=lambda: open_add_above_tall_dialog(_frozen_id)
            ).props('dense').classes('w-full text-xs mt-0.5 btn-wrap')



