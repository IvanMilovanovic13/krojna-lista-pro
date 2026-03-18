# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    BTN_OTKAZI,
    GRAIN_HORZ,
    GRAIN_NONE,
    GRAIN_VERT,
    PARAMS_ADD_OK_FMT,
    PARAMS_DEPTH_DIALOG_TITLE_FMT,
    PARAMS_DEPTH_INDEPENDENT_FMT,
    PARAMS_DEPTH_ONLY_THIS_FMT,
    PARAMS_DEPTH_SET_OK_FMT,
    PARAMS_DEPTH_SET_STD_FMT,
    PARAMS_DEPTH_STANDARD_FMT,
    PARAMS_DOOR_H_LABEL,
    PARAMS_DOOR_DRAWER,
    PARAMS_DRAWERS_TITLE,
    PARAMS_DRAWERS_COUNT,
    PARAMS_DRAWER_H_FMT,
    PARAMS_DRAWER_LABEL_FMT,
    PARAMS_DRAWER_MIN_WARN_FMT,
    PARAMS_DRAWER_OK_FMT,
    PARAMS_DRAWER_REMAINING_FMT,
    PARAMS_DRAWER_TOO_SMALL_FMT,
    PARAMS_ERR_FMT,
    PARAMS_INNER_H_FMT,
    PARAMS_MAX_H_FMT,
    PARAMS_OVEN_DRAWER_TITLE,
    PARAMS_OVEN_STD_H_FMT,
    PARAMS_RECALC,
    PARAMS_RECALC_BTN,
    PARAMS_SHELVES,
    PARAMS_SHELVES_COUNT,
    PARAMS_SHELVES_SPACING_FMT,
    PARAMS_SHELVES_SUGGEST_FMT,
    PARAMS_WHAT_TO_DO,
)
from ui_panels_helpers import format_user_error

def render_params_panel(
    *,
    ui,
    state,
    templates,
    logger,
    is_independent_depth,
    get_zone_depth_standard,
    max_allowed_h_for_zone,
    set_zone_depth_standard,
    suggest_corner_neighbor_guidance,
    find_first_free_x,
    add_module_instance_local,
    nacrt_refresh,
    sidebar_refresh,
    set_sidebar_primary_action,
    params_panel_refresh,
    l_odaberi_element,
    l_sirina_mm,
    l_visina_mm,
    l_dubina_mm,
    l_smer_goda,
    l_naziv,
    l_strana_rucke,
    l_iznad_kog_gornjeg,
    m_nema_gornjih_1_red,
    b_dodaj_na_zid,
) -> None:
    if not state.selected_tid:
        set_sidebar_primary_action(None)
        with ui.column().classes('w-full items-center py-6 gap-2'):
            ui.icon('touch_app').classes('text-3xl text-gray-200')
            ui.label(l_odaberi_element).classes(
                'text-xs text-gray-400 text-center'
            )
        return

    tmpl = templates.get(state.selected_tid, {})
    # get_templates() vraća flatten strukturu — w_mm/h_mm/d_mm su top-level ključevi,
    # a ne unutar "defaults" pod-dikt-a. Rekonstruišemo defaults za uniforman pristup.
    defaults = {
        'w_mm': int(tmpl.get('w_mm', 600)),
        'h_mm': int(tmpl.get('h_mm', 720)),
        'd_mm': int(tmpl.get('d_mm', 560)),
    }
    label = tmpl.get("label", state.selected_tid)
    zone = str(tmpl.get("zone", "base"))
    tid = str(state.selected_tid or "").upper()
    _active_wall = str((getattr(state, 'room', {}) or {}).get('active_wall', 'A') or 'A').upper()
    _corner_guidance = suggest_corner_neighbor_guidance(zone, _active_wall, tid)

    # ── Separator + "Dodaj" section header ───────────────────────────────────
    ui.separator().classes('my-1')
    with ui.element('div').classes('px-2 pt-2 pb-0.5'):
        ui.label(label).classes('text-[11px] font-bold text-gray-700')

    with ui.element('div').classes('px-2 pb-2'):

        # ── Depth standard logika ─────────────────────────────────────────────
        _is_indep = is_independent_depth(state.selected_tid)
        _zone_std_d = get_zone_depth_standard(zone)

        _zd = state.zone_defaults.get(zone, {})
        _h_val = _zd.get('h_mm', defaults.get('h_mm', 720)) if zone not in ('tall', 'tall_top') else defaults.get('h_mm', 2100)
        if _is_indep:
            _d_val = defaults.get('d_mm', 560)
        elif zone not in ('tall', 'tall_top'):
            _d_val = _zone_std_d
        else:
            _d_val = defaults.get('d_mm', 560)

        _max_h = max_allowed_h_for_zone(zone)

        # ── Mutable tracker za dimenzije (zaštita od NiceGUI async desync) ────
        # Problem: korisnik unese vrednost u browser, klikne dugme, ali Python-side
        # .value još uvek ima staru vrednost (WebSocket kasnjenje ili stale closure).
        # Rešenje: eksplicitno pratimo vrednost kroz on_change i čuvamo u _dim dict-u.
        _dim = {
            'w': int(defaults.get('w_mm', 600)),
            'h': int(min(_h_val, _max_h)),
            'd': int(_d_val),
        }

        def _on_w_change(e):
            try:
                _dim['w'] = max(100, min(3000, int(float(e.value))))
            except Exception:
                pass

        def _on_h_change(e):
            try:
                _dim['h'] = max(100, min(_max_h, int(float(e.value))))
            except Exception:
                pass

        def _on_d_change(e):
            try:
                _dim['d'] = max(100, min(2000, int(float(e.value))))
            except Exception:
                pass

        # ── Dimension inputs (pregledno, bez sečenja labela) ──────────────────
        with ui.column().classes('w-full gap-1 mt-1'):
            with ui.row().classes('w-full gap-1'):
                w = ui.number(
                    label=l_sirina_mm, value=defaults.get('w_mm', 600),
                    min=100, max=3000, step=10,
                    on_change=_on_w_change,
                ).props('dense outlined').classes('flex-1 min-w-0')
                h = ui.number(
                    label=l_visina_mm, value=min(_h_val, _max_h),
                    min=100, max=_max_h, step=10,
                    on_change=_on_h_change,
                ).props('dense outlined').classes('flex-1 min-w-0')
            d = ui.number(
                label=l_dubina_mm, value=_d_val,
                min=100, max=2000, step=10,
                on_change=_on_d_change,
            ).props('dense outlined').classes('w-full')
            ui.label(PARAMS_MAX_H_FMT.format(h=_max_h)).classes(
                'text-[10px] text-gray-500'
            )

        # ── Depth status badge ────────────────────────────────────────────────
        if _is_indep:
            _depth_badge_txt = PARAMS_DEPTH_INDEPENDENT_FMT.format(d=_d_val)
            _depth_badge_cls = 'text-[10px] text-gray-700 bg-gray-50 border border-gray-300 px-2 py-0.5 rounded mt-1'
        else:
            _depth_badge_txt = PARAMS_DEPTH_STANDARD_FMT.format(d=_zone_std_d)
            _depth_badge_cls = 'text-[10px] text-gray-700 bg-gray-50 border border-gray-300 px-2 py-0.5 rounded mt-1'
        _depth_status_lbl = ui.label(_depth_badge_txt).classes(_depth_badge_cls)
        if _corner_guidance.get('active'):
            ui.label(str(_corner_guidance.get('message', ''))).classes(
                'text-[10px] text-amber-800 bg-amber-50 border border-amber-200 px-2 py-1 rounded mt-1'
            )

        # ── Smer goda ─────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-2 mt-1'):
            ui.label(l_smer_goda).classes('text-[10px] text-gray-500 shrink-0')
            grain_sel_add = ui.select(
                {'V': GRAIN_VERT, 'H': GRAIN_HORZ, 'N': GRAIN_NONE},
                value='V'
            ).classes('flex-1').props('dense outlined')

        # ── Fioke / Police panel ──────────────────────────────────────────
        features = tmpl.get("features", {})
        has_drawers = features.get("drawers", False)
        has_shelves = features.get("open", False) or features.get("pantry", False)
        has_oven = features.get("oven", False)
        has_door_and_drawer = features.get("doors", False) and features.get("drawers", False)
        has_wardrobe = bool(features.get("wardrobe", False))

        # Konstante
        carcass_thk = float(state.kitchen.get("materials", {}).get("carcass_thk", 18))
        edge_thk = float(state.kitchen.get("materials", {}).get("edge_abs_thk", 2))
        OVEN_H = 595  # standardna visina rerne
        OVEN_D = 550  # standardna dubina rerne
        MIN_DRAWER_H = 80  # minimalna visina fioke
        SHELF_STEP = 250  # jedna polica na svakih 250mm

        def _inner_h(corp_h: float) -> float:
            """Unutrašnja visina korpusa (oduzmi dno i plafon)."""
            return corp_h - 2 * carcass_thk

        def _distribute(total: float, n: int, locked: dict) -> list:
            """
            Ravnomerno rasporedi visinu na n fioka.
            locked = {index: visina} — zaključane fioke
            Slobodan prostor ide na nezaključane.
            """
            locked_sum = sum(locked.values())
            free = total - locked_sum
            unlocked = [i for i in range(n) if i not in locked]
            if not unlocked:
                return [locked.get(i, free/n) for i in range(n)]
            per = free / len(unlocked)
            return [locked.get(i, per) for i in range(n)]

        # state holders for dodaj()
        drawer_heights_state = None
        door_h_inp = None
        n_shelves = None
        fioka_h = None
        wardrobe_front_style = None
        wardrobe_door_mode = None
        wardrobe_n_shelves = None
        wardrobe_n_shelves_slider = None
        wardrobe_n_drawers = None
        wardrobe_n_drawers_slider = None
        wardrobe_hanger_sections = None
        wardrobe_hanger_sections_slider = None
        wardrobe_to_ceiling = None

        if has_oven and not has_door_and_drawer:
            # Rerna + fioka: rerna je fiksna, ostatak je fioka
            corp_h = float(_dim['h'])
            inner = _inner_h(corp_h)
            fioka_h = max(MIN_DRAWER_H, inner - OVEN_H)
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(PARAMS_OVEN_DRAWER_TITLE).classes('font-bold text-xs mb-0')
                ui.label(PARAMS_OVEN_STD_H_FMT.format(h=OVEN_H)).classes('text-xs text-gray-500')
                ui.label(PARAMS_DRAWER_REMAINING_FMT.format(h=fioka_h)).classes('text-xs text-gray-700 font-bold')
                if fioka_h < MIN_DRAWER_H:
                    ui.label(PARAMS_DRAWER_MIN_WARN_FMT.format(h=MIN_DRAWER_H)).classes('text-xs text-red-500')

        elif has_drawers and not has_door_and_drawer:
            # Čiste fioke — nova logika bez locked/distribute
            n_drawers_default = features.get("n_drawers", 3)

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(PARAMS_DRAWERS_TITLE).classes('font-bold text-xs mb-0')

                # State: samo lista visina i inputi — bez locked
                drawer_heights_state = {'n': n_drawers_default, 'heights': [], 'inputs': {}}
                fioka_container = ui.column().classes('w-full gap-1')
                _p_valid_lbl  = [None]
                _p_prop_html  = [None]   # ref na ui.html za proportion bars
                _P_COLORS = ['#111111', '#2f2f2f', '#4b4b4b',
                             '#676767', '#838383', '#9f9f9f']

                def _p_get_total():
                    return _inner_h(float(_dim['h']))

                def _p_refresh_valid():
                    total = _p_get_total()
                    zbir = sum(drawer_heights_state['heights'])
                    diff = abs(zbir - total)
                    if _p_valid_lbl[0] is not None:
                        if diff < 1:
                            _p_valid_lbl[0].set_text(f'✅ {zbir:.0f} = {total:.0f}mm')
                            _p_valid_lbl[0].classes(remove='text-red-500', add='text-gray-700')
                        else:
                            _p_valid_lbl[0].set_text(f'⚠️ {zbir:.0f} ≠ {total:.0f}mm — klikni ↺')
                            _p_valid_lbl[0].classes(remove='text-gray-700', add='text-red-500')

                def _p_update_prop_bars():
                    """Instant CSS proportion preview u panelu za dodavanje."""
                    if _p_prop_html[0] is None:
                        return
                    heights = drawer_heights_state['heights']
                    if not heights:
                        return
                    total_h = max(1.0, sum(heights))
                    parts = [
                        '<div style="display:flex;flex-direction:column;gap:2px;'
                        'width:100%;height:72px;border-radius:4px;overflow:hidden;">'
                    ]
                    for i, hv in enumerate(heights):
                        grow = max(1, int(hv / total_h * 1000))
                        col  = _P_COLORS[i % len(_P_COLORS)]
                        parts.append(
                            f'<div style="flex-grow:{grow};background:{col};'
                            f'display:flex;align-items:center;padding:0 5px;'
                            f'color:#fff;font-size:9px;font-weight:600;'
                            f'overflow:hidden;white-space:nowrap;">'
                            f'F{i+1}&nbsp;{int(hv)}mm</div>'
                        )
                    parts.append('</div>')
                    _p_prop_html[0].set_content(''.join(parts))

                def _p_auto_redistribute(idx, new_val, heights, total, n):
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
                    # Fix rounding on last other drawer
                    if others:
                        fix = others[-1]
                        heights[fix] = max(MIN_DRAWER_H,
                                           remaining - sum(heights[j] for j in others if j != fix))
                    heights[idx] = new_val
                    return heights

                def _p_build(n, init_list=None):
                    fioka_container.clear()
                    drawer_heights_state['inputs'].clear()
                    total = _p_get_total()
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
                        # F1 = top drawer (index 0) shown at top; F(n) = bottom
                        for i in range(n):
                            with ui.row().classes('w-full items-center gap-1 p-1'):
                                ui.label(PARAMS_DRAWER_LABEL_FMT.format(i=i+1)).classes('text-[6px] text-gray-500 w-8')
                                def _on_change(e, idx=i):
                                    try:
                                        h_state = drawer_heights_state['heights']
                                        _n = drawer_heights_state['n']
                                        _total = _p_get_total()
                                        _p_auto_redistribute(idx, float(e.value), h_state, _total, _n)
                                        drawer_heights_state['heights'] = h_state
                                        # Update other inputs to show new values
                                        for j, inp in drawer_heights_state['inputs'].items():
                                            if j != idx:
                                                try:
                                                    inp.set_value(round(h_state[j], 1))
                                                except Exception as ex:
                                                    logger.debug("Add drawer input sync failed: %s", ex)
                                        _p_refresh_valid()
                                        _p_update_prop_bars()  # ← instant vizuelni feedback
                                    except Exception as ex:
                                        logger.debug("Add drawer redistribute failed: %s", ex)
                                inp = ui.number(
                                    value=round(heights[i], 1),
                                    min=MIN_DRAWER_H, max=int(total),
                                    step=1, on_change=_on_change
                                ).props('outlined dense').classes('w-24')
                                drawer_heights_state['inputs'][i] = inp
                    _p_refresh_valid()
                    _p_update_prop_bars()

                def _p_recalc():
                    n = drawer_heights_state['n']
                    total = _p_get_total()
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
                        # Koriguj poslednji slobodni zbog zaokruživanja
                        rounding_adj = round(total - sum(heights), 1)
                        heights[free_indices[-1]] = round(heights[free_indices[-1]] + rounding_adj, 1)
                    else:
                        per = round(total / n, 1)
                        heights = [per] * (n - 1)
                        heights.append(round(total - sum(heights), 1))
                    drawer_heights_state['heights'] = heights
                    # Ažuriraj baseline za slobodne indekse
                    if 'original_heights' not in drawer_heights_state:
                        drawer_heights_state['original_heights'] = list(heights)
                    else:
                        for i in free_indices:
                            drawer_heights_state['original_heights'][i] = heights[i]
                    for idx, inp in drawer_heights_state['inputs'].items():
                        try:
                            inp.set_value(round(heights[idx], 1))
                        except Exception as ex:
                            logger.debug("Add drawer recalc input update failed: %s", ex)
                    _p_refresh_valid()
                    _p_update_prop_bars()

                def _on_n_change_p(e):
                    _p_build(int(float(e.value)))
                    _p_update_prop_bars()

                ui.number(PARAMS_DRAWERS_COUNT, value=n_drawers_default, min=1, max=6, step=1,
                          on_change=_on_n_change_p).props('dense').classes('w-full mt-1')

                with ui.row().classes('w-full items-center gap-2 mt-1'):
                    _p_valid_lbl[0] = ui.label('').classes('text-xs text-gray-700 flex-1')
                    ui.button(PARAMS_RECALC_BTN.format(label=PARAMS_RECALC), on_click=_p_recalc).props('flat dense').classes('text-xs text-gray-700 border border-gray-300')

                # ── Proportion bars — instant CSS preview ─────────────────────
                _p_prop_html[0] = ui.html('').classes('w-full mt-1')

                ui.timer(0.05, lambda: (_p_build(n_drawers_default), _p_update_prop_bars()), once=True)


        elif has_door_and_drawer:
            # Vrata + fioka kombinovano
            corp_h = float(_dim['h'])
            inner = _inner_h(corp_h)
            default_drawer_h = min(200.0, inner * 0.28)
            default_door_h = inner - default_drawer_h

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(PARAMS_DOOR_DRAWER).classes('font-bold text-xs mb-0')
                ui.label(PARAMS_INNER_H_FMT.format(h=inner)).classes('text-xs text-gray-500')

                door_h_inp = ui.number(
                    label=PARAMS_DOOR_H_LABEL,
                    value=round(default_door_h, 1),
                    min=100, max=int(inner - MIN_DRAWER_H), step=1
                ).props('dense').classes('w-full')

                drawer_h_lbl = ui.label(PARAMS_DRAWER_H_FMT.format(h=default_drawer_h)).classes('text-xs text-gray-700 font-bold mt-1')

                def _on_door_change(e):
                    dh = inner - float(e.value)
                    if dh < MIN_DRAWER_H:
                        drawer_h_lbl.set_text(PARAMS_DRAWER_TOO_SMALL_FMT.format(h=dh, min_h=MIN_DRAWER_H))
                    else:
                        drawer_h_lbl.set_text(PARAMS_DRAWER_OK_FMT.format(h=dh))

                door_h_inp.on('change', _on_door_change)

        elif has_shelves:
            # Police
            corp_h = float(_dim['h'])
            inner = _inner_h(corp_h)
            default_n_shelves = max(1, int(inner / SHELF_STEP))

            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label(PARAMS_SHELVES).classes('font-bold text-xs mb-0')
                ui.label(PARAMS_SHELVES_SUGGEST_FMT.format(n=default_n_shelves)).classes('text-xs text-gray-500')
                n_shelves = ui.number(PARAMS_SHELVES_COUNT, value=default_n_shelves, min=0, max=10, step=1).props('dense').classes('w-full')
                shelf_h_lbl = ui.label(PARAMS_SHELVES_SPACING_FMT.format(h=inner/(default_n_shelves+1))).classes('text-xs text-gray-700')

                def _on_shelves_change(e):
                    n = max(1, int(e.value))
                    spacing = inner / (n + 1)
                    shelf_h_lbl.set_text(PARAMS_SHELVES_SPACING_FMT.format(h=spacing))

                n_shelves.on('change', _on_shelves_change)


        if has_wardrobe:
            _s_min, _s_max = (0, 12)
            _d_min, _d_max = (0, 8)
            _h_min, _h_max = (0, 3)
            with ui.card().classes('w-full p-2 bg-gray-50 border border-gray-300 mt-1'):
                ui.label('Orman: unutrasnji raspored').classes('font-bold text-xs mb-0')
                _front_default = 'inside' if bool(features.get('interior_only', False)) else 'both'
                wardrobe_front_style = ui.select(
                    {
                        'doors': 'Spolja (vrata)',
                        'inside': 'Unutra (bez vrata)',
                        'both': 'Oba prikaza',
                    },
                    value=_front_default,
                    label='Sta zelis da vidis na frontu?',
                ).props('dense outlined').classes('w-full')
                _default_door_mode = 'sliding' if bool(features.get('sliding', False)) else str(getattr(state, 'wardrobe_door_mode', 'hinged') or 'hinged')
                wardrobe_door_mode = ui.select(
                    {'hinged': 'Krilna vrata', 'sliding': 'Klizna vrata'},
                    value=_default_door_mode if _default_door_mode in ('hinged', 'sliding') else 'hinged',
                    label='Tip vrata',
                ).props('dense outlined').classes('w-full')
                _ws = int(features.get('n_shelves', 4))
                _wd = int(features.get('n_drawers', 2))
                _wh = int(features.get('hanger_sections', 1))
                wardrobe_n_shelves = ui.number('Broj polica', value=_ws, min=_s_min, max=_s_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_n_shelves_slider = ui.slider(min=_s_min, max=_s_max, value=_ws, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_n_drawers = ui.number('Broj fioka', value=_wd, min=_d_min, max=_d_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_n_drawers_slider = ui.slider(min=_d_min, max=_d_max, value=_wd, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_hanger_sections = ui.number('Broj zona za kacenje', value=_wh, min=_h_min, max=_h_max, step=1).props('dense outlined').classes('w-full')
                wardrobe_hanger_sections_slider = ui.slider(min=_h_min, max=_h_max, value=_wh, step=1).props('label-always').classes('w-full -mt-1')
                wardrobe_to_ceiling = ui.switch('Do plafona', value=bool(getattr(state, 'wardrobe_to_ceiling', True))).classes('mt-1')

                def _sync_num_to_slider(num_el, slider_el):
                    def _h(e):
                        try:
                            slider_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    return _h

                def _sync_slider_to_num(slider_el, num_el):
                    def _h(e):
                        try:
                            num_el.set_value(int(float(e.value)))
                        except Exception:
                            pass
                    return _h

                wardrobe_n_shelves.on('change', _sync_num_to_slider(wardrobe_n_shelves, wardrobe_n_shelves_slider))
                wardrobe_n_shelves_slider.on('change', _sync_slider_to_num(wardrobe_n_shelves_slider, wardrobe_n_shelves))
                wardrobe_n_drawers.on('change', _sync_num_to_slider(wardrobe_n_drawers, wardrobe_n_drawers_slider))
                wardrobe_n_drawers_slider.on('change', _sync_slider_to_num(wardrobe_n_drawers_slider, wardrobe_n_drawers))
                wardrobe_hanger_sections.on('change', _sync_num_to_slider(wardrobe_hanger_sections, wardrobe_hanger_sections_slider))
                wardrobe_hanger_sections_slider.on('change', _sync_slider_to_num(wardrobe_hanger_sections_slider, wardrobe_hanger_sections))


        name = ui.input(l_naziv, value=label).props('dense').classes('w-full mt-1')
        handle_side_sel = None
        if "1DOOR" in tid and zone in ("base", "wall", "tall"):
            _default_handle_side = str(_corner_guidance.get('recommended_handle_side') or "right")
            handle_side_sel = ui.select(["left", "right"], value=_default_handle_side, label=l_strana_rucke).props('dense').classes('w-full')

        wall_upper_x = None
        if zone == "wall_upper":
            _active_wk = str(
                (getattr(state, "room", {}) or {}).get("active_wall",
                    (getattr(state, "room", {}) or {}).get("kitchen_wall", "A")) or "A"
            ).upper()
            wall_mods = [m for m in (state.kitchen.get("modules", []) or [])
                         if str(m.get("zone", "")).lower() == "wall"
                         and str(m.get("wall_key", "A")).upper() == _active_wk]
            options = [(f"#{m.get('id')} {m.get('label','')}", int(m.get("x_mm", 0))) for m in wall_mods]
            if options:
                def _wu_change(e):
                    try:
                        state.wall_upper_target_x = int(e.value[1])
                    except Exception as ex:
                        logger.debug("Wall-upper target change parse failed: %s", ex)
                        state.wall_upper_target_x = -1

                sel = ui.select(options, value=options[0], label=l_iznad_kog_gornjeg, on_change=_wu_change).props('dense').classes('w-full')
                wall_upper_x = sel
                try:
                    state.wall_upper_target_x = int(sel.value[1])
                except Exception as ex:
                    logger.debug("Wall-upper initial target parse failed: %s", ex)
                    state.wall_upper_target_x = -1
            else:
                ui.label(m_nema_gornjih_1_red).classes('text-xs text-gray-500')
                state.wall_upper_target_x = -1

        def _do_dodaj(use_d_mm: int, override_as_new_standard: bool = False) -> None:
            """Interni helper — stvarno dodaje element."""
            try:
                _h_for_add = int(_dim['h'])
                if has_wardrobe and wardrobe_to_ceiling is not None and bool(wardrobe_to_ceiling.value):
                    _h_for_add = int(_max_h)

                # Ažuriraj zone_defaults (samo za base/wall/wall_upper)
                if zone not in ('tall', 'tall_top'):
                    state.zone_defaults[zone]['h_mm'] = _h_for_add
                    if not _is_indep:
                        state.zone_defaults[zone]['d_mm'] = int(use_d_mm)

                # Ako korisnik bira da postavi novu zone dubinu kao standard
                if override_as_new_standard and not _is_indep:
                    set_zone_depth_standard(zone, use_d_mm, update_existing=False)

                # Skupi params za fioke/police
                _extra_params = {}
                try:
                    if has_drawers and not has_door_and_drawer and drawer_heights_state:
                        n_cur = int(drawer_heights_state.get('n', 3))
                        heights = drawer_heights_state.get('heights', [])
                        if not heights or len(heights) != n_cur:
                            total = _inner_h(float(_dim['h']))
                            per = round(total / n_cur, 1)
                            heights = [per] * (n_cur - 1)
                            heights.append(round(total - sum(heights), 1))
                        _extra_params['drawer_heights'] = [round(x, 1) for x in heights]
                        _extra_params['n_drawers'] = n_cur
                    if has_door_and_drawer and door_h_inp is not None:
                        _door_h = float(door_h_inp.value)
                        _drawer_h = _inner_h(float(_dim['h'])) - _door_h
                        _extra_params['door_height'] = _door_h
                        _extra_params['drawer_heights'] = [_drawer_h]
                        _extra_params['n_drawers'] = 1
                    if has_shelves and n_shelves is not None:
                        _extra_params['n_shelves'] = int(n_shelves.value)
                    if has_oven and fioka_h is not None:
                        _extra_params['drawer_heights'] = [fioka_h]
                        _extra_params['n_drawers'] = 1
                        _extra_params['oven_h'] = OVEN_H
                    if has_wardrobe:
                        _extra_params['wardrobe'] = True
                        if wardrobe_front_style is not None:
                            _extra_params['front_style'] = str(wardrobe_front_style.value or 'both')
                        if wardrobe_door_mode is not None:
                            _extra_params['door_mode'] = str(wardrobe_door_mode.value or 'hinged')
                        if wardrobe_n_shelves is not None:
                            _extra_params['n_shelves'] = int(wardrobe_n_shelves.value)
                        if wardrobe_n_drawers is not None:
                            _extra_params['n_drawers'] = int(wardrobe_n_drawers.value)
                        if wardrobe_hanger_sections is not None:
                            _extra_params['hanger_sections'] = int(wardrobe_hanger_sections.value)
                        if wardrobe_to_ceiling is not None:
                            _extra_params['to_ceiling'] = bool(wardrobe_to_ceiling.value)
                        if 'AMERICAN' in tid:
                            _extra_params['american_sections'] = {
                                'left_pct': 33,
                                'center_pct': 34,
                                'right_pct': 33,
                                'top_h_mm': 420,
                                'left': {
                                    'shelves': int(_extra_params.get('n_shelves', 4)),
                                    'drawers': max(0, int(_extra_params.get('n_drawers', 2)) // 2),
                                    'hangers': 0,
                                },
                                'center': {
                                    'shelves': 1,
                                    'drawers': 0,
                                    'hangers': max(1, int(_extra_params.get('hanger_sections', 1))),
                                },
                                'right': {
                                    'shelves': max(1, int(_extra_params.get('n_shelves', 4)) // 2),
                                    'drawers': max(0, int(_extra_params.get('n_drawers', 2))),
                                    'hangers': max(0, int(_extra_params.get('hanger_sections', 1)) - 1),
                                },
                                'top': {
                                    'shelves': 2,
                                    'drawers': 0,
                                    'hangers': 0,
                                },
                                'locked': False,
                            }
                except Exception as ex:
                    logger.debug("Add element extra params collection failed: %s", ex)

                _room_for_add = getattr(state, 'room', None)
                _kwall_key    = str(
                    (_room_for_add or {}).get('active_wall',
                        (_room_for_add or {}).get('kitchen_wall', 'A')) or 'A'
                ).upper()
                x_use = int(find_first_free_x(state.kitchen, zone, _dim['w'], wall_key=_kwall_key))
                if zone == "wall_upper" and wall_upper_x is not None:
                    x_use = int(wall_upper_x.value[1])
                if handle_side_sel is not None:
                    _extra_params["handle_side"] = str(handle_side_sel.value)

                # ── Smer goda ─────────────────────────────────────────────────
                _extra_params["grain_dir"] = str(grain_sel_add.value or "V")

                new_mod = add_module_instance_local(
                    template_id=state.selected_tid,
                    zone=zone,
                    x_mm=int(x_use),
                    w_mm=_dim['w'],
                    h_mm=_h_for_add,
                    d_mm=int(use_d_mm),
                    gap_after_mm=0,
                    label=name.value,
                    params=_extra_params,
                    room=_room_for_add,
                    wall_key=_kwall_key,
                )
                # Ako je CUSTOM (korisnik uneo drugačiju d od standarda), označi
                if not _is_indep and int(use_d_mm) != get_zone_depth_standard(zone):
                    new_mod["depth_mode"] = "CUSTOM"
                ui.notify(PARAMS_ADD_OK_FMT.format(label=label), type='positive')
                nacrt_refresh()
                sidebar_refresh()
            except Exception as e:
                ui.notify(PARAMS_ERR_FMT.format(err=format_user_error(e)), type='negative')

        def dodaj() -> None:
            entered_d = _dim['d']
            zone_std = get_zone_depth_standard(zone)

            # Aparat — direktno dodaj, bez pitanja
            if _is_indep:
                _do_dodaj(entered_d)
                return

            # Korisnik uneo d_mm različit od zone standarda → pitaj
            if entered_d != zone_std:
                zone_label = zone.upper()
                with ui.dialog() as _dlg_override:
                    with ui.card().classes('p-4 gap-2 min-w-72'):
                        ui.label(PARAMS_DEPTH_DIALOG_TITLE_FMT.format(entered=entered_d, zone=zone_label, std=zone_std)).classes('font-bold text-sm')
                        ui.label(PARAMS_WHAT_TO_DO).classes('text-sm text-gray-600')
                        with ui.column().classes('w-full gap-2 mt-2'):
                            def _set_as_std():
                                _dlg_override.close()
                                _do_dodaj(entered_d, override_as_new_standard=True)
                                ui.notify(PARAMS_DEPTH_SET_OK_FMT.format(zone=zone_label, d=entered_d), type='info')
                                params_panel_refresh()
                            def _keep_custom():
                                _dlg_override.close()
                                _do_dodaj(entered_d, override_as_new_standard=False)
                            def _cancel():
                                _dlg_override.close()

                            ui.button(
                                PARAMS_DEPTH_SET_STD_FMT.format(d=entered_d, zone=zone_label),
                                on_click=_set_as_std
                            ).classes('w-full bg-white text-[#111] border border-[#111] text-xs')
                            ui.button(
                                PARAMS_DEPTH_ONLY_THIS_FMT.format(std=zone_std),
                                on_click=_keep_custom
                            ).classes('w-full bg-gray-100 text-xs')
                            ui.button(BTN_OTKAZI, on_click=_cancel).classes('w-full text-xs')
                _dlg_override.open()
            else:
                _do_dodaj(entered_d)

        set_sidebar_primary_action(dodaj, b_dodaj_na_zid)

