# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import tr
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
    _lang = str(getattr(state, "language", "sr") or "sr").lower().strip()
    def _t(sr: str, en: str) -> str:
        return en if _lang == "en" else sr

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
                {
                    'A': _t("Zid A (zadnji)", "Wall A (back)"),
                    'B': _t("Zid B (levi)", "Wall B (left)"),
                    'C': _t("Zid C (desni)", "Wall C (right)"),
                },
                value=_fixture_wall_choice['value'],
                label=_t("Zid instalacije", "Fixture wall"),
            ).props('dense outlined').classes('w-full')
            inst_wall_sel.on(
                'update:model-value',
                lambda e: _fixture_wall_choice.__setitem__('value', str(e.value or 'A').upper())
            )
            ui.label(_t("Brzi unos", "Quick input")).classes('text-xs text-gray-500 mt-1')
            with ui.expansion(_t("Napredno (ručni unos X/Y)", "Advanced (manual X/Y input)"), value=False).classes('w-full mt-1'):
                with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
                    with ui.column().classes('gap-0'):
                        ui.label(_t("Od leve ivice (X)", "From left edge (X)")).classes('text-xs text-gray-500')
                        fx_inp = ui.number(value=500, min=0, max=10000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                        _refs['fx_inp'] = fx_inp
                    with ui.column().classes('gap-0'):
                        ui.label(_t("Od poda (Y)", "From floor (Y)")).classes('text-xs text-gray-500')
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
                    ui.notify(_t("Instalacija izlazi van zida. Proveri X/Y.", "The fixture is outside the wall. Check X/Y."), type='negative')
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

            ui.button(f'+ {_t("Dodaj instalaciju", "Add fixture")}', on_click=_add_fixture).classes(
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
            _t("Režim: Dodaj vrata", "Mode: Add door") if _sel_opening_type.get('value') == 'vrata' else _t("Režim: Dodaj prozor", "Mode: Add window")
        ).classes('text-xs font-semibold text-gray-700')

        opening_wall_sel = ui.select(
            {
                'A': _t("Zid A (zadnji)", "Wall A (back)"),
                'B': _t("Zid B (levi)", "Wall B (left)"),
                'C': _t("Zid C (desni)", "Wall C (right)"),
            },
            value=_opening_wall_choice['value'],
            label=_t("Zid otvora", "Opening wall"),
        ).props('dense outlined').classes('w-full')
        opening_wall_sel.on(
            'update:model-value',
            lambda e: _opening_wall_choice.__setitem__('value', str(e.value or 'A').upper())
        )
        ui.label().bind_text_from(
            _opening_wall_choice,
            'value',
            backward=lambda v: _t("Dodavanje ide na zid: {wall}", "Adding to wall: {wall}").format(wall=str(v or "A").upper()),
        ).classes('text-xs text-gray-600')
        ui.label(_t("Brzi unos", "Quick input")).classes('text-xs text-gray-500 mt-1')
        with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
            with ui.column().classes('gap-0'):
                ui.label(_t("Širina otvora", "Opening width")).classes('text-xs text-gray-500')
                ow_inp = ui.number(value=800, min=100, max=4000, step=50, suffix='mm').props('dense outlined').classes('w-full')
            with ui.column().classes('gap-0'):
                ui.label(_t("Visina otvora", "Opening height")).classes('text-xs text-gray-500')
                oh_inp = ui.number(value=1200, min=100, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')

        with ui.row().classes('w-full gap-2 mt-1'):
            with ui.column().classes('flex-1 gap-0'):
                ui.label(_t("Donja ivica od poda (Y)", "Bottom edge from floor (Y)")).classes('text-xs text-gray-500')
                oy_quick = ui.number(value=0, min=0, max=3000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                _refs['oy_quick'] = oy_quick
            with ui.column().classes('w-[140px] gap-0'):
                ui.label(_t("Ručni X/Y", "Manual X/Y")).classes('text-xs text-gray-500')
                ui.checkbox(
                    _t("Ručni unos", "Manual input"),
                    value=False,
                    on_change=lambda e: _use_manual_xy.__setitem__('value', bool(e.value)),
                ).props('dense')

        with ui.expansion(_t("Napredno (ručni unos X/Y)", "Advanced (manual X/Y input)"), value=False).classes('w-full mt-1'):
            with ui.grid(columns=2).classes('w-full gap-x-3 gap-y-1'):
                with ui.column().classes('gap-0'):
                    ui.label(_t("Od leve ivice (X)", "From left edge (X)")).classes('text-xs text-gray-500')
                    ox_inp = ui.number(value=500, min=0, max=10000, step=50, suffix='mm').props('dense outlined').classes('w-full')
                    _refs['ox_inp'] = ox_inp
                with ui.column().classes('gap-0'):
                    ui.label(_t("Od poda (Y)", "From floor (Y)")).classes('text-xs text-gray-500')
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
                    ui.notify(_t("Klikni na zid da postaviš X poziciju.", "Click the wall to set the X position."), type='negative')
                    return
                _y = int((oy_quick.value if _refs.get('oy_quick') is not None else (_refs['click_y_mm'][0] or 0)) or 0)
            if str(_sel_opening_type.get('value', 'prozor')) == 'vrata':
                _y = 0  # vrata su vezana za pod
            _w = int(ow_inp.value or 800)
            _h = int(oh_inp.value or 1200)
            if _x + _w > _wl or _y + _h > _wh:
                ui.notify(_t("Otvor izlazi van zida. Proveri X/Y i dimenzije.", "The opening is outside the wall. Check X/Y and dimensions."), type='negative')
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
            ui.notify(_t("Prozor dodat. Prevuci ga mišem na željenu poziciju u 2D prikazu.", "Window added. Drag it to the desired position in the 2D view."), timeout=2200)

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
            ui.notify(_t("Vrata dodata. Prevuci ih mišem na željenu poziciju u 2D prikazu.", "Door added. Drag it to the desired position in the 2D view."), timeout=2200)

        if _sel_opening_type.get('value') == 'vrata':
            ui.button(_t("Ubaci vrata i prevuci", "Insert door and drag"), on_click=_add_door_drag_ready).props('dense outlined').classes('w-full text-xs')
        else:
            ui.button(_t("Ubaci prozor i prevuci", "Insert window and drag"), on_click=_add_window_drag_ready).props('dense outlined').classes('w-full text-xs')
        _add_label = f' + {_t("Dodaj vrata", "Add door")}' if _sel_opening_type.get('value') == 'vrata' else f'+ {_t("Dodaj prozor", "Add window")}'
        ui.button(_add_label, on_click=_add_opening).classes('w-full font-semibold text-sm').props('dense')

    @ui.refreshable
    def openings_list():
        ops = _get_active_wall().get('openings', [])
        if not ops:
            ui.label(_t("Još nema otvora.", "There are no openings yet.")).classes('text-xs text-gray-300 italic text-center py-2')
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
                        _t(
                            "x={x}  {w}x{h}mm  +{y}mm od poda",
                            "x={x}  {w}x{h}mm  +{y}mm from floor",
                        ).format(
                            x=op["x_mm"],
                            w=op["width_mm"],
                            h=op["height_mm"],
                            y=op["y_mm"],
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
                            ui.label(_t("Izmena otvora", "Edit opening")).classes('font-bold text-sm')
                            wall_sel = ui.select(
                                {'A': _t("Zid A", "Wall A"), 'B': _t("Zid B", "Wall B"), 'C': _t("Zid C", "Wall C")},
                                value=cur_wall_key, label=_t("Zid", "Wall")
                            ).props('dense outlined').classes('w-full')
                            w_in = ui.number(value=int(_op.get('width_mm', 800)), label=_t("Širina [mm]", "Width [mm]")).props('dense outlined').classes('w-full')
                            h_in = ui.number(value=int(_op.get('height_mm', 1200)), label=_t("Visina [mm]", "Height [mm]")).props('dense outlined').classes('w-full')
                            x_in = ui.number(value=int(_op.get('x_mm', 0)), label=_t("X od levog ugla [mm]", "X from left corner [mm]")).props('dense outlined').classes('w-full')
                            y_in = ui.number(value=int(_op.get('y_mm', 0)), label=_t("Y od poda [mm]", "Y from floor [mm]")).props('dense outlined').classes('w-full')

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
                                ui.button(_t("Sačuvaj", "Save"), on_click=_save_edit).classes('flex-1')
                                ui.button(_t("Zatvori", "Close"), on_click=dlg.close).classes('flex-1')
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
            ui.label(_t("Klikni prozor/vrata u 2D prikazu za detalje.", "Click a window/door in the 2D view for details.")).classes('text-xs text-gray-500')
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
            ui.label(_t("Detalji izabranog otvora", "Selected opening details")).classes('text-xs font-bold text-gray-700')
            ui.label(_t("X od levog zida: {x} mm", "X from left wall: {x} mm").format(x=_x)).classes('text-xs')
            ui.label(_t("X od desnog zida: {x} mm", "X from right wall: {x} mm").format(x=_right)).classes('text-xs')
            ui.label(_t("Y od poda: {y} mm", "Y from floor: {y} mm").format(y=_y)).classes('text-xs')
            ui.label(_t("Dimenzije: {w} × {h} mm", "Dimensions: {w} × {h} mm").format(w=_w, h=_h)).classes('text-xs')
            with ui.grid(columns=2).classes('w-full gap-x-2 gap-y-1 mt-1'):
                ed_x = ui.number(value=_x, label="X [mm]").props('dense outlined').classes('w-full')
                ed_y = ui.number(value=_y, label="Y [mm]").props('dense outlined').classes('w-full')
                ed_w = ui.number(value=_w, label=_t("Širina [mm]", "Width [mm]")).props('dense outlined').classes('w-full')
                ed_h = ui.number(value=_h, label=_t("Visina [mm]", "Height [mm]")).props('dense outlined').classes('w-full')

            def _apply_selected():
                if _idx is None or not (0 <= _idx < len(_ops)):
                    return
                _nx = int(ed_x.value or 0)
                _ny = int(ed_y.value or 0)
                _nw = int(ed_w.value or 0)
                _nh = int(ed_h.value or 0)
                if _nw <= 0 or _nh <= 0:
                    ui.notify(_t("Dimenzije moraju biti veće od nule.", "Dimensions must be greater than zero."), type='negative')
                    return
                if _nx < 0 or _ny < 0 or (_nx + _nw) > _wl or (_ny + _nh) > _wh:
                    ui.notify(_t("Otvor izlazi van zida. Proveri X/Y/Š/V.", "The opening is outside the wall. Check X/Y/W/H."), type='negative')
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
                ui.button(_t("Primeni", "Apply"), on_click=_apply_selected).props('dense').classes('flex-1')
                ui.button(_t("Obriši", "Delete"), on_click=_delete_selected).props('dense outlined').classes('flex-1')

    @ui.refreshable
    def fixtures_list():
        ops = _get_active_wall().get('fixtures', [])
        if not ops:
            ui.label(_t("Još nema instalacija.", "There are no fixtures yet.")).classes('text-xs text-gray-300 italic text-center py-2')
            return
        for i, op in enumerate(ops):
            fi_ic, fnm, fcl = FIXTURE_TYPES.get(op['type'], ('?', op['type'], '#ccc'))
            with ui.row().classes('w-full items-center gap-1 py-1.5 px-2 rounded hover:bg-gray-50').style(f'border-left:3px solid {fcl};'):
                ui.label(f'{fi_ic}').classes('text-base shrink-0')
                with ui.column().classes('flex-1 gap-0'):
                    ui.label(fnm).classes('text-xs font-semibold text-gray-700')
                ui.label(
                    _t("x={x} mm  y={y} mm", "x={x} mm  y={y} mm").format(
                        x=op["x_mm"],
                        y=op["y_mm"],
                    )
                ).classes('text-xs text-gray-400')

    @ui.refreshable
    def openings_list_all():
        _all = []
        for _wk in ('A', 'B', 'C'):
            _w = _get_wall_by_key(_wk)
            for _idx, _op in enumerate(_w.get('openings', [])):
                _all.append((_wk, _idx, _op))
        if not _all:
            ui.label(_t("Nema otvora ni na jednom zidu.", "There are no openings on any wall.")).classes('text-xs text-gray-400')
            return
        for _wk, _idx, _op in _all:
            _lbl = _t("Zid {wall} · {type} · x={x} y={y}", "Wall {wall} · {type} · x={x} y={y}").format(
                wall=_wk,
                type=_t("vrata", "door") if str(_op.get("type", "otvor")) == "vrata" else _t("prozor", "window"),
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
        with ui.expansion(_t("4. Otvori / instalacije", "4. Openings / fixtures"), value=True).classes('w-full bg-white border border-gray-100'):
            with ui.column().classes('w-full p-3 gap-2'):
                with ui.row().classes('items-center gap-2 mb-0'):
                    ui.icon('door_front').classes('text-gray-700')
                    ui.label(_t("Otvori / Instalacije", "Openings / Fixtures")).classes('font-bold text-gray-800 text-sm')
                with ui.row().classes('items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-2 py-1'):
                    ui.icon('touch_app').classes('text-gray-600 shrink-0 text-sm')
                    ui.label(_t("Klikni direktno na zid (desno) da automatski postavi X/Y poziciju!", "Click directly on the wall (right) to set X/Y automatically.")).classes('text-xs text-gray-700')
                with ui.row().classes('w-full gap-2'):
                    def _set_tab(v):
                        _oi_tab['value'] = v
                        _oi_body.refresh()
                    ui.button(_t("Otvori", "Openings"), on_click=lambda: _set_tab('otvori')).props('dense outlined').classes('text-xs')
                    ui.button(_t("Instalacije", "Fixtures"), on_click=lambda: _set_tab('inst')).props('dense outlined').classes('text-xs')
            _oi_body()

    if _panel_mode['value'] in ('all', 'openings'):
        with ui.expansion(_t("5. Lista dodatih", "5. Added items"), value=True).classes('w-full bg-white border border-gray-100'):
            with ui.column().classes('w-full p-3 gap-2'):
                ui.label(_t("Otvori (aktivni zid)", "Openings (active wall)")).classes('text-xs font-semibold text-gray-600')
                openings_list()
                opening_selected_info()
                ui.separator()
                ui.label(_t("Instalacije (aktivni zid)", "Fixtures (active wall)")).classes('text-xs font-semibold text-gray-600')
                fixtures_list()
                ui.separator()
                ui.label(_t("Svi otvori (A/B/C)", "All openings (A/B/C)")).classes('text-xs font-semibold text-gray-600')
                openings_list_all()

    return {
        'oi_body': _oi_body,
        'openings_list': openings_list,
        'fixtures_list': fixtures_list,
        'opening_selected_info': opening_selected_info,
    }

