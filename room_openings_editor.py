# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    BTN_DODAJ_INSTALACIJU,
    BTN_DODAJ_PROZOR,
    BTN_DODAJ_VRATA,
    BTN_UBACI_PROZOR_PREVUCI,
    BTN_UBACI_VRATA_PREVUCI,
    ROE_ADV_MANUAL_XY,
    ROE_ALL_OPENINGS_FMT,
    ROE_APPLY,
    ROE_CLICK_OPENING_FOR_DETAILS,
    ROE_CLICK_WALL_HINT,
    ROE_DELETE,
    ROE_DIMENSIONS_FMT,
    ROE_EDIT_OPENING,
    ROE_EXP_ADDED_LIST,
    ROE_EXP_OPENINGS_INSTALL,
    ROE_FIXTURE_INFO_FMT,
    ROE_LABEL_BOTTOM_EDGE_Y,
    ROE_LABEL_FLOOR_Y,
    ROE_LABEL_HEIGHT_MM,
    ROE_LABEL_INSTALL_WALL,
    ROE_LABEL_LEFT_EDGE_X,
    ROE_LABEL_MANUAL_INPUT,
    ROE_LABEL_MANUAL_XY,
    ROE_LABEL_OPENING_HEIGHT,
    ROE_LABEL_OPENING_WALL,
    ROE_LABEL_OPENING_WIDTH,
    ROE_LABEL_WIDTH_MM,
    ROE_LABEL_X_MM,
    ROE_LABEL_Y_MM,
    ROE_LABEL_X_FROM_LEFT_MM,
    ROE_LABEL_Y_FROM_FLOOR_MM,
    ROE_LIST_FIXTURES_ACTIVE,
    ROE_LIST_OPENINGS_ACTIVE,
    ROE_LIST_OPENINGS_ALL,
    ROE_MODE_ADD_DOOR,
    ROE_MODE_ADD_WINDOW,
    ROE_NO_FIXTURES,
    ROE_NO_OPENINGS,
    ROE_NO_OPENINGS_ANY,
    ROE_NOTIFY_CLICK_WALL_FOR_X,
    ROE_NOTIFY_DIM_POSITIVE,
    ROE_NOTIFY_DOOR_ADDED_DRAG,
    ROE_NOTIFY_FIXTURE_OUT,
    ROE_NOTIFY_OPENING_OUT,
    ROE_NOTIFY_OPENING_OUT_SHORT,
    ROE_NOTIFY_WINDOW_ADDED_DRAG,
    ROE_OPENING_ADDING_ON_WALL_FMT,
    ROE_OPENING_INFO_FMT,
    ROE_QUICK_INPUT,
    ROE_SAVE,
    ROE_SELECTED_OPENING_DETAILS,
    ROE_TAB_FIXTURES,
    ROE_TAB_OPENINGS,
    ROE_TITLE_OPENINGS_INSTALL,
    ROE_WALL,
    ROE_WALL_A,
    ROE_WALL_A_BACK,
    ROE_WALL_B,
    ROE_WALL_B_LEFT,
    ROE_WALL_C,
    ROE_WALL_C_RIGHT,
    ROE_X_FROM_LEFT_FMT,
    ROE_X_FROM_RIGHT_FMT,
    ROE_Y_FROM_FLOOR_FMT,
)


def render_room_openings_editor(
    *,
    ui,
    room,
    state,
    _panel_mode,
    OPENING_TYPES,
    FIXTURE_TYPES,
    _refs,
    _sel_opening_type,
    _sel_fixture_type,
    _opening_wall_choice,
    _fixture_wall_choice,
    _use_manual_xy,
    _get_wall_by_key,
    _get_active_wall,
    wall_preview,
    scene_container,
    wall_headline,
    wall_compass,
    BTN_ZATVORI,
):
    # Stabilni podrazumevani parametri prostorije
    for _k in ('A', 'B', 'C'):
        _w = _get_wall_by_key(_k)
        if int(_w.get('length_mm', 0) or 0) <= 0:
            _w['length_mm'] = 3000
        if int(_w.get('height_mm', 0) or 0) <= 0:
            _w['height_mm'] = int(room.get('wall_height_mm', 2600) or 2600)
    room['wall_height_mm'] = int(room.get('wall_height_mm', 2600) or 2600)
    room['wall_length_mm'] = int(room.get('wall_length_mm', 3000) or 3000)
    room['room_depth_mm'] = int(room.get('room_depth_mm', 3000) or 3000)

    _oi_tab = {'value': 'otvori'}

    @ui.refreshable
    def _oi_body():
        if _oi_tab['value'] == 'inst':
            _fix_btns: list = []
            with ui.row().classes('w-full gap-1 flex-wrap'):
                for ft, (fi, fnm, fcl) in FIXTURE_TYPES.items():
                    def _sel_f(t=ft):
                        _sel_fixture_type['value'] = t
                        for _idx2, _btn2 in enumerate(_fix_btns):
                            _kt2 = list(FIXTURE_TYPES.keys())[_idx2]
                            _btn2.style('opacity:1.0;' if _kt2 == t else 'opacity:0.35;')

                    _b = ui.button(f'{fi} {fnm}', on_click=_sel_f).props('dense').style(
                        f'background:#F8FAFC;border:2px solid {fcl};'
                        f'color:#374151;border-radius:6px;font-size:0.7rem;'
                    )
                    _fix_btns.append(_b)

            inst_wall_sel = ui.select(
                {'A': ROE_WALL_A_BACK, 'B': ROE_WALL_B_LEFT, 'C': ROE_WALL_C_RIGHT},
                value=_fixture_wall_choice['value'],
                label=ROE_LABEL_INSTALL_WALL,
            ).props('dense outlined').classes('w-full')
            inst_wall_sel.on(
                'update:model-value',
                lambda e: _fixture_wall_choice.__setitem__('value', str(e.value or 'A').upper())
            )
            ui.label(ROE_QUICK_INPUT).classes('text-xs text-gray-500 mt-1')
            with ui.expansion(ROE_ADV_MANUAL_XY, value=False).classes('w-full mt-1'):
                with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
                    with ui.column().classes('gap-0'):
                        ui.label(ROE_LABEL_LEFT_EDGE_X).classes('text-xs text-gray-500')
                        fx_inp = ui.number(value=500, min=0, max=10000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                        _refs['fx_inp'] = fx_inp
                    with ui.column().classes('gap-0'):
                        ui.label(ROE_LABEL_FLOOR_Y).classes('text-xs text-gray-500')
                        fy_inp = ui.number(value=300, min=0, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                        _refs['fy_inp'] = fy_inp

            def _add_fixture():
                _wall_key = str(inst_wall_sel.value or _fixture_wall_choice['value'] or "A").upper()
                _wall = _get_wall_by_key(_wall_key)
                _wl = int(_wall.get('length_mm', 3000))
                _wh = int(_wall.get('height_mm', 2600))
                _x = int((fx_inp.value if _refs.get('fx_inp') is not None else (_refs['click_x_mm'][0] or 0)) or 0)
                _y = int((fy_inp.value if _refs.get('fy_inp') is not None else (_refs['click_y_mm'][0] or 0)) or 0)
                if _x > _wl or _y > _wh:
                    ui.notify(ROE_NOTIFY_FIXTURE_OUT, type='negative')
                    return
                _wall.setdefault('fixtures', []).append({
                    'type': _sel_fixture_type['value'],
                    'wall': _wall_key,
                    'x_mm': _x,
                    'y_mm': _y,
                })
                room["active_wall"] = _wall_key
                fixtures_list.refresh()
                wall_preview.refresh()
                scene_container.refresh()

            ui.button(f'+ {BTN_DODAJ_INSTALACIJU}', on_click=_add_fixture).classes(
                'w-full font-semibold text-sm'
            ).props('dense')
            return

        _type_btns: list = []
        with ui.row().classes('w-full gap-1 flex-wrap'):
            for ot, (oi, onm, ocl) in OPENING_TYPES.items():
                def _sel_t(t=ot):
                    _sel_opening_type['value'] = t
                    _oi_body.refresh()

                _active = (_sel_opening_type.get('value') == ot)
                _b = ui.button(f'{oi} {onm}', on_click=_sel_t).props('dense').style(
                    f'background:{"#EEF2FF" if _active else "#F8FAFC"};'
                    f'border:{"2px solid #111111" if _active else f"2px solid {ocl}"};'
                    f'color:#111111;border-radius:6px;font-size:0.7rem;'
                    f'opacity:{1.0 if _active else 0.7};'
                )
                _type_btns.append(_b)
        ui.label(
            ROE_MODE_ADD_DOOR if _sel_opening_type.get('value') == 'vrata' else ROE_MODE_ADD_WINDOW
        ).classes('text-xs font-semibold text-gray-700')

        opening_wall_sel = ui.select(
            {'A': ROE_WALL_A_BACK, 'B': ROE_WALL_B_LEFT, 'C': ROE_WALL_C_RIGHT},
            value=_opening_wall_choice['value'],
            label=ROE_LABEL_OPENING_WALL,
        ).props('dense outlined').classes('w-full')
        opening_wall_sel.on(
            'update:model-value',
            lambda e: _opening_wall_choice.__setitem__('value', str(e.value or 'A').upper())
        )
        ui.label().bind_text_from(
            _opening_wall_choice,
            'value',
            backward=lambda v: ROE_OPENING_ADDING_ON_WALL_FMT.format(wall=str(v or "A").upper()),
        ).classes('text-xs text-gray-600')
        ui.label(ROE_QUICK_INPUT).classes('text-xs text-gray-500 mt-1')
        with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
            with ui.column().classes('gap-0'):
                ui.label(ROE_LABEL_OPENING_WIDTH).classes('text-xs text-gray-500')
                ow_inp = ui.number(value=800, min=100, max=4000, step=50, suffix='mm').props('dense outlined').classes('w-full')
            with ui.column().classes('gap-0'):
                ui.label(ROE_LABEL_OPENING_HEIGHT).classes('text-xs text-gray-500')
                oh_inp = ui.number(value=1200, min=100, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')

        with ui.row().classes('w-full gap-2 mt-1'):
            with ui.column().classes('flex-1 gap-0'):
                ui.label(ROE_LABEL_BOTTOM_EDGE_Y).classes('text-xs text-gray-500')
                oy_quick = ui.number(value=0, min=0, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                _refs['oy_quick'] = oy_quick
            with ui.column().classes('w-[140px] gap-0'):
                ui.label(ROE_LABEL_MANUAL_XY).classes('text-xs text-gray-500')
                ui.checkbox(
                    ROE_LABEL_MANUAL_INPUT,
                    value=False,
                    on_change=lambda e: _use_manual_xy.__setitem__('value', bool(e.value)),
                ).props('dense')

        with ui.expansion(ROE_ADV_MANUAL_XY, value=False).classes('w-full mt-1'):
            with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
                with ui.column().classes('gap-0'):
                    ui.label(ROE_LABEL_LEFT_EDGE_X).classes('text-xs text-gray-500')
                    ox_inp = ui.number(value=500, min=0, max=10000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                    _refs['ox_inp'] = ox_inp
                with ui.column().classes('gap-0'):
                    ui.label(ROE_LABEL_FLOOR_Y).classes('text-xs text-gray-500')
                    oy_inp = ui.number(value=800, min=0, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                    _refs['oy_inp'] = oy_inp

        def _add_opening():
            _wall_key = str(opening_wall_sel.value or _opening_wall_choice['value'] or "A").upper()
            _wall = _get_wall_by_key(_wall_key)
            _wl = int(_wall.get('length_mm', 3000))
            _wh = int(_wall.get('height_mm', 2600))
            if _use_manual_xy['value']:
                _x = int((ox_inp.value if _refs.get('ox_inp') is not None else 0) or 0)
                _y = int((oy_inp.value if _refs.get('oy_inp') is not None else 0) or 0)
            else:
                _x = int((_refs['click_x_mm'][0] if _refs['click_x_mm'][0] is not None else -1))
                if _x < 0:
                    ui.notify(ROE_NOTIFY_CLICK_WALL_FOR_X, type='negative')
                    return
                _y = int((oy_quick.value if _refs.get('oy_quick') is not None else (_refs['click_y_mm'][0] or 0)) or 0)
            if str(_sel_opening_type.get('value', 'prozor')) == 'vrata':
                _y = 0  # vrata su vezana za pod
            _w = int(ow_inp.value or 800)
            _h = int(oh_inp.value or 1200)
            if _x + _w > _wl or _y + _h > _wh:
                ui.notify(ROE_NOTIFY_OPENING_OUT, type='negative')
                return
            _wall.setdefault('openings', []).append({
                'type': _sel_opening_type['value'],
                'wall': _wall_key,
                'x_mm': _x,
                'width_mm': _w,
                'height_mm': _h,
                'y_mm': _y,
            })
            room["active_wall"] = _wall_key
            _refs['click_x_mm'][0] = None
            _refs['selected_open_idx'][0] = len(_wall.get('openings', [])) - 1
            openings_list.refresh()
            opening_selected_info.refresh()
            wall_headline.refresh()
            wall_compass.refresh()
            wall_preview.refresh()
            scene_container.refresh()

        def _add_window_drag_ready():
            _wall_key = str(opening_wall_sel.value or _opening_wall_choice['value'] or "A").upper()
            _wall = _get_wall_by_key(_wall_key)
            _wl = int(_wall.get('length_mm', 3000))
            _wh = int(_wall.get('height_mm', 2600))
            _w = int(ow_inp.value or 800)
            _h = int(oh_inp.value or 1200)
            _x = max(0, min(_wl - _w, int(_wl * 0.35)))
            _y = max(0, min(_wh - _h, int((oy_quick.value or 0) or 0)))
            _wall.setdefault('openings', []).append({
                'type': 'prozor',
                'wall': _wall_key,
                'x_mm': _x,
                'width_mm': _w,
                'height_mm': _h,
                'y_mm': _y,
            })
            room["active_wall"] = _wall_key
            _refs['selected_open_idx'][0] = len(_wall.get('openings', [])) - 1
            openings_list.refresh()
            opening_selected_info.refresh()
            wall_headline.refresh()
            wall_compass.refresh()
            wall_preview.refresh()
            scene_container.refresh()
            ui.notify(ROE_NOTIFY_WINDOW_ADDED_DRAG, timeout=2200)

        def _add_door_drag_ready():
            _wall_key = str(opening_wall_sel.value or _opening_wall_choice['value'] or "A").upper()
            _wall = _get_wall_by_key(_wall_key)
            _wl = int(_wall.get('length_mm', 3000))
            _wh = int(_wall.get('height_mm', 2600))
            _w = int(ow_inp.value or 900)
            _h = int(oh_inp.value or 2100)
            _x = max(0, min(_wl - _w, int(_wl * 0.35)))
            _y = 0
            if _y + _h > _wh:
                _h = max(100, _wh)
            _wall.setdefault('openings', []).append({
                'type': 'vrata',
                'wall': _wall_key,
                'x_mm': _x,
                'width_mm': _w,
                'height_mm': _h,
                'y_mm': _y,
            })
            room["active_wall"] = _wall_key
            _refs['selected_open_idx'][0] = len(_wall.get('openings', [])) - 1
            openings_list.refresh()
            opening_selected_info.refresh()
            wall_headline.refresh()
            wall_compass.refresh()
            wall_preview.refresh()
            scene_container.refresh()
            ui.notify(ROE_NOTIFY_DOOR_ADDED_DRAG, timeout=2200)

        if _sel_opening_type.get('value') == 'vrata':
            ui.button(f'{BTN_UBACI_VRATA_PREVUCI}', on_click=_add_door_drag_ready).props('dense outlined').classes('w-full text-xs')
        else:
            ui.button(f'{BTN_UBACI_PROZOR_PREVUCI}', on_click=_add_window_drag_ready).props('dense outlined').classes('w-full text-xs')
        _add_label = f' + {BTN_DODAJ_VRATA}' if _sel_opening_type.get('value') == 'vrata' else f'+ {BTN_DODAJ_PROZOR}'
        ui.button(_add_label, on_click=_add_opening).classes('w-full font-semibold text-sm').props('dense')

    @ui.refreshable
    def openings_list():
        ops = _get_active_wall().get('openings', [])
        if not ops:
            ui.label(ROE_NO_OPENINGS).classes('text-xs text-gray-300 italic text-center py-2')
            return
        for i, op in enumerate(ops):
            oi_ic, onm, ocl = OPENING_TYPES.get(op['type'], ('?', op['type'], '#ccc'))
            _sel = (_refs['selected_open_idx'][0] == i)
            _row = ui.row().classes('w-full items-center gap-1 py-1.5 px-2 rounded hover:bg-gray-50 cursor-pointer').style(
                f'border-left:3px solid {ocl};' + ('border:1px solid #111;' if _sel else '')
            )
            with _row:
                ui.label(f'{oi_ic}').classes('text-base shrink-0')
                with ui.column().classes('flex-1 gap-0'):
                    ui.label(onm).classes('text-xs font-semibold text-gray-700')
                    ui.label(
                        ROE_OPENING_INFO_FMT.format(
                            x=op["x_mm"], w=op["width_mm"], h=op["height_mm"], y=op["y_mm"]
                        )
                    ).classes('text-xs text-gray-400')

                def _select_opening_from_list(idx=i):
                    _refs['selected_open_idx'][0] = idx
                    openings_list.refresh()
                    opening_selected_info.refresh()
                    wall_preview.refresh()

                def _edit(idx=i):
                    cur_wall_key = str(room.get("active_wall", "A")).upper()
                    _op = dict(_get_wall_by_key(cur_wall_key).get('openings', [])[idx])
                    with ui.dialog() as dlg:
                        with ui.card().classes('p-4 min-w-80 gap-2'):
                            ui.label(ROE_EDIT_OPENING).classes('font-bold text-sm')
                            wall_sel = ui.select(
                                {'A': ROE_WALL_A, 'B': ROE_WALL_B, 'C': ROE_WALL_C},
                                value=cur_wall_key, label=ROE_WALL
                            ).props('dense outlined').classes('w-full')
                            w_in = ui.number(value=int(_op.get('width_mm', 800)), label=ROE_LABEL_WIDTH_MM).props('dense outlined').classes('w-full')
                            h_in = ui.number(value=int(_op.get('height_mm', 1200)), label=ROE_LABEL_HEIGHT_MM).props('dense outlined').classes('w-full')
                            x_in = ui.number(value=int(_op.get('x_mm', 0)), label=ROE_LABEL_X_FROM_LEFT_MM).props('dense outlined').classes('w-full')
                            y_in = ui.number(value=int(_op.get('y_mm', 0)), label=ROE_LABEL_Y_FROM_FLOOR_MM).props('dense outlined').classes('w-full')

                            def _save_edit():
                                src_wall = _get_wall_by_key(cur_wall_key)
                                dst_wall = _get_wall_by_key(wall_sel.value)
                                src_wall.get('openings', []).pop(idx)
                                dst_wall.setdefault('openings', []).append({
                                    'type': _op.get('type', 'prozor'),
                                    'wall': str(wall_sel.value or "A").upper(),
                                    'x_mm': int(x_in.value or 0),
                                    'y_mm': int(y_in.value or 0),
                                    'width_mm': int(w_in.value or 0),
                                    'height_mm': int(h_in.value or 0),
                                })
                                dlg.close()
                                openings_list.refresh()
                                opening_selected_info.refresh()
                                fixtures_list.refresh()
                                wall_preview.refresh()
                                scene_container.refresh()

                            with ui.row().classes('w-full gap-2'):
                                ui.button(ROE_SAVE, on_click=_save_edit).classes('flex-1')
                                ui.button(BTN_ZATVORI, on_click=dlg.close).classes('flex-1')
                    dlg.open()

                def _rm(idx=i):
                    _get_active_wall().get('openings', []).pop(idx)
                    _refs['selected_open_idx'][0] = None
                    openings_list.refresh()
                    opening_selected_info.refresh()
                    wall_preview.refresh()
                    scene_container.refresh()

                ui.button(icon='edit', on_click=_edit).props('flat round dense').classes('text-gray-500 shrink-0')
                ui.button(icon='close', on_click=_rm).props('flat round dense').classes('text-red-400 shrink-0')
            _row.on('click', lambda e, _s=_select_opening_from_list: _s())

    @ui.refreshable
    def opening_selected_info():
        _ops = _get_active_wall().get('openings', [])
        _idx = _refs['selected_open_idx'][0]
        if _idx is None or not (0 <= _idx < len(_ops)):
            ui.label(ROE_CLICK_OPENING_FOR_DETAILS).classes('text-xs text-gray-500')
            return
        _op = _ops[_idx]
        _wl = int(_get_active_wall().get('length_mm', room.get('wall_length_mm', 3000)))
        _wh = int(_get_active_wall().get('height_mm', room.get('wall_height_mm', 2600)))
        _x = int(_op.get('x_mm', 0))
        _y = int(_op.get('y_mm', 0))
        _w = int(_op.get('width_mm', 0))
        _h = int(_op.get('height_mm', 0))
        _right = max(0, _wl - (_x + _w))
        with ui.card().classes('w-full p-2 border border-gray-300'):
            ui.label(ROE_SELECTED_OPENING_DETAILS).classes('text-xs font-bold text-gray-700')
            ui.label(ROE_X_FROM_LEFT_FMT.format(x=_x)).classes('text-xs')
            ui.label(ROE_X_FROM_RIGHT_FMT.format(x=_right)).classes('text-xs')
            ui.label(ROE_Y_FROM_FLOOR_FMT.format(y=_y)).classes('text-xs')
            ui.label(ROE_DIMENSIONS_FMT.format(w=_w, h=_h)).classes('text-xs')
            with ui.grid(columns=2).classes('w-full gap-x-2 gap-y-1 mt-1'):
                ed_x = ui.number(value=_x, label=ROE_LABEL_X_MM).props('dense outlined').classes('w-full')
                ed_y = ui.number(value=_y, label=ROE_LABEL_Y_MM).props('dense outlined').classes('w-full')
                ed_w = ui.number(value=_w, label=ROE_LABEL_WIDTH_MM).props('dense outlined').classes('w-full')
                ed_h = ui.number(value=_h, label=ROE_LABEL_HEIGHT_MM).props('dense outlined').classes('w-full')

            def _apply_selected():
                if _idx is None or not (0 <= _idx < len(_ops)):
                    return
                _nx = int(ed_x.value or 0)
                _ny = int(ed_y.value or 0)
                _nw = int(ed_w.value or 0)
                _nh = int(ed_h.value or 0)
                if _nw <= 0 or _nh <= 0:
                    ui.notify(ROE_NOTIFY_DIM_POSITIVE, type='negative')
                    return
                if _nx < 0 or _ny < 0 or (_nx + _nw) > _wl or (_ny + _nh) > _wh:
                    ui.notify(ROE_NOTIFY_OPENING_OUT_SHORT, type='negative')
                    return
                _ops[_idx]['x_mm'] = _nx
                _ops[_idx]['y_mm'] = _ny
                _ops[_idx]['width_mm'] = _nw
                _ops[_idx]['height_mm'] = _nh
                _refs['click_x_mm'][0] = _nx
                _refs['click_y_mm'][0] = _ny
                openings_list.refresh()
                opening_selected_info.refresh()
                wall_preview.refresh()
                scene_container.refresh()

            def _delete_selected():
                if _idx is None or not (0 <= _idx < len(_ops)):
                    return
                _ops.pop(_idx)
                _refs['selected_open_idx'][0] = None
                openings_list.refresh()
                opening_selected_info.refresh()
                wall_preview.refresh()
                scene_container.refresh()

            with ui.row().classes('w-full gap-2 mt-1'):
                ui.button(ROE_APPLY, on_click=_apply_selected).props('dense').classes('flex-1')
                ui.button(ROE_DELETE, on_click=_delete_selected).props('dense outlined').classes('flex-1')

    @ui.refreshable
    def fixtures_list():
        ops = _get_active_wall().get('fixtures', [])
        if not ops:
            ui.label(ROE_NO_FIXTURES).classes('text-xs text-gray-300 italic text-center py-2')
            return
        for i, op in enumerate(ops):
            fi_ic, fnm, fcl = FIXTURE_TYPES.get(op['type'], ('?', op['type'], '#ccc'))
            with ui.row().classes('w-full items-center gap-1 py-1.5 px-2 rounded hover:bg-gray-50').style(f'border-left:3px solid {fcl};'):
                ui.label(f'{fi_ic}').classes('text-base shrink-0')
                with ui.column().classes('flex-1 gap-0'):
                    ui.label(fnm).classes('text-xs font-semibold text-gray-700')
                ui.label(ROE_FIXTURE_INFO_FMT.format(x=op["x_mm"], y=op["y_mm"])).classes('text-xs text-gray-400')

    @ui.refreshable
    def openings_list_all():
        _all = []
        for _wk in ('A', 'B', 'C'):
            _w = _get_wall_by_key(_wk)
            for _idx, _op in enumerate(_w.get('openings', [])):
                _all.append((_wk, _idx, _op))
        if not _all:
            ui.label(ROE_NO_OPENINGS_ANY).classes('text-xs text-gray-400')
            return
        for _wk, _idx, _op in _all:
            _lbl = ROE_ALL_OPENINGS_FMT.format(
                wall=_wk,
                type=_op.get("type", "otvor"),
                x=int(_op.get("x_mm", 0)),
                y=int(_op.get("y_mm", 0)),
            )
            _row = ui.row().classes('w-full items-center justify-between px-2 py-1 rounded hover:bg-gray-50 cursor-pointer border border-gray-200')
            with _row:
                ui.label(_lbl).classes('text-xs')
            def _go(wk=_wk, idx=_idx):
                room["active_wall"] = wk
                _refs['selected_open_idx'][0] = idx
                openings_list.refresh()
                opening_selected_info.refresh()
                wall_headline.refresh()
                wall_compass.refresh()
                wall_preview.refresh()
                scene_container.refresh()
            _row.on('click', lambda e, _s=_go: _s())

    if _panel_mode['value'] in ('all', 'openings'):
        with ui.expansion(ROE_EXP_OPENINGS_INSTALL, value=True).classes('w-full bg-white border border-gray-100'):
            with ui.column().classes('w-full p-3 gap-2'):
                with ui.row().classes('items-center gap-2 mb-0'):
                    ui.icon('door_front').classes('text-gray-700')
                    ui.label(ROE_TITLE_OPENINGS_INSTALL).classes('font-bold text-gray-800 text-sm')
                with ui.row().classes('items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-2 py-1'):
                    ui.icon('touch_app').classes('text-gray-600 shrink-0 text-sm')
                    ui.label(ROE_CLICK_WALL_HINT).classes('text-xs text-gray-700')
                with ui.row().classes('w-full gap-2'):
                    def _set_tab(v):
                        _oi_tab['value'] = v
                        _oi_body.refresh()
                    ui.button(ROE_TAB_OPENINGS, on_click=lambda: _set_tab('otvori')).props('dense outlined').classes('text-xs')
                    ui.button(ROE_TAB_FIXTURES, on_click=lambda: _set_tab('inst')).props('dense outlined').classes('text-xs')
            _oi_body()

    if _panel_mode['value'] in ('all', 'openings'):
        with ui.expansion(ROE_EXP_ADDED_LIST, value=True).classes('w-full bg-white border border-gray-100'):
            with ui.column().classes('w-full p-3 gap-2'):
                ui.label(ROE_LIST_OPENINGS_ACTIVE).classes('text-xs font-semibold text-gray-600')
                openings_list()
                opening_selected_info()
                ui.separator()
                ui.label(ROE_LIST_FIXTURES_ACTIVE).classes('text-xs font-semibold text-gray-600')
                fixtures_list()
                ui.separator()
                ui.label(ROE_LIST_OPENINGS_ALL).classes('text-xs font-semibold text-gray-600')
                openings_list_all()

    return {
        'oi_body': _oi_body,
        'openings_list': openings_list,
        'fixtures_list': fixtures_list,
        'opening_selected_info': opening_selected_info,
    }

