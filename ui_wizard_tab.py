# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    LBL_USKORO,
    SYM_CHEVRON,
    WIZ_BACK,
    WIZ_BTN_LOAD_PROJECT,
    WIZ_CONTINUE_EXISTING,
    WIZ_LAYOUT_GALLEY,
    WIZ_LAYOUT_GALLEY_DESC,
    WIZ_LAYOUT_ISLAND,
    WIZ_LAYOUT_ISLAND_DESC,
    WIZ_LAYOUT_L_RIGHT,
    WIZ_LAYOUT_L_RIGHT_DESC,
    WIZ_LAYOUT_L_LEFT,
    WIZ_LAYOUT_L_LEFT_DESC,
    WIZ_LAYOUT_ONE_WALL,
    WIZ_LAYOUT_ONE_WALL_DESC,
    WIZ_LAYOUT_U,
    WIZ_LAYOUT_U_DESC,
    WIZ_MODE_PRO,
    WIZ_MODE_PRO_DESC1,
    WIZ_MODE_PRO_DESC2,
    WIZ_MODE_STANDARD,
    WIZ_MODE_STANDARD_DESC1,
    WIZ_MODE_STANDARD_DESC2,
    WIZ_STEP_LAYOUT,
    WIZ_STEP_MODE,
    WIZ_STEP_TYPE,
    WIZ_SUB_PICK_LAYOUT,
    WIZ_SUB_PICK_MODE,
    WIZ_TITLE_APP,
    WIZ_TITLE_PICK_LAYOUT,
    WIZ_TITLE_PICK_MODE,
    WIZ_TITLE_PICK_TYPE,
    WIZ_TYPE_KITCHEN,
    WIZ_TYPE_KITCHEN_DESC,
)


def render_wizard_tab(
    ui,
    state,
    main_content,
    main_content_refresh,
    switch_tab,
    render_room_setup_step3,
    plt,
    ensure_room_walls,
    get_room_wall,
    set_wall_length,
    set_wall_height,
    room_opening_types,
    room_fixture_types,
) -> None:
    with ui.column().classes('w-full h-[calc(100vh-48px)] overflow-hidden'):
        _render_wizard(
            ui=ui,
            state=state,
            main_content_refresh=main_content_refresh,
            switch_tab=switch_tab,
            render_room_setup_step3=render_room_setup_step3,
            plt=plt,
            ensure_room_walls=ensure_room_walls,
            get_room_wall=get_room_wall,
            set_wall_length=set_wall_length,
            set_wall_height=set_wall_height,
            room_opening_types=room_opening_types,
            room_fixture_types=room_fixture_types,
            main_content=main_content,
        )


def _render_wizard(
    ui,
    state,
    main_content_refresh,
    switch_tab,
    render_room_setup_step3,
    plt,
    ensure_room_walls,
    get_room_wall,
    set_wall_length,
    set_wall_height,
    room_opening_types,
    room_fixture_types,
    main_content,
) -> None:
    # Kitchen-only profil: svaki projekat se tretira kao kuhinja.
    if str(getattr(state, 'project_type', 'kitchen')).lower() != 'kitchen':
        state.project_type = 'kitchen'
        state.kitchen["project_type"] = 'kitchen'
        state.furniture_type = 'kuhinja'
        if state.wizard_step > 3:
            state.wizard_step = 3

    if state.wizard_step == 1:
        _render_wizard_step1(ui, state, main_content_refresh, switch_tab)
    elif state.wizard_step == 2:
        _render_wizard_step2_measurement(ui, state, main_content_refresh)
    elif state.wizard_step == 3:
        _render_wizard_step3_layout(ui, state, main_content_refresh)
    else:
        render_room_setup_step3(
            state,
            ui=ui,
            plt=plt,
            _ensure_room_walls=ensure_room_walls,
            _get_room_wall=get_room_wall,
            _set_wall_length=set_wall_length,
            _set_wall_height=set_wall_height,
            main_content=main_content,
            ROOM_OPENING_TYPES=room_opening_types,
            ROOM_FIXTURE_TYPES=room_fixture_types,
        )


def _render_wizard_step1(ui, state, main_content_refresh, switch_tab) -> None:
    furniture_types = [
        ('kuhinja', '🍴', WIZ_TYPE_KITCHEN, WIZ_TYPE_KITCHEN_DESC, True),
    ]

    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        ui.label(WIZ_TITLE_APP).classes('text-4xl font-bold text-gray-800')
        ui.label(WIZ_TITLE_PICK_TYPE).classes('text-lg text-gray-500 mb-2')

        with ui.row().classes('flex-wrap justify-center gap-4 max-w-4xl'):
            for ftype, icon, naziv, opis, aktivan in furniture_types:
                if aktivan:

                    def _klik(ft=ftype):
                        state.project_type = 'kitchen'
                        state.kitchen["project_type"] = state.project_type
                        state.furniture_type = ft
                        state.active_group = 'donji'
                        state.measurement_mode = ''
                        state.wizard_step = 2
                        main_content_refresh()

                    with ui.card().classes(
                        'w-48 h-44 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                        'border-2 border-transparent transition-all duration-200 '
                        'flex flex-col items-center justify-center gap-2 p-4'
                    ).on('click', _klik):
                        ui.label(icon).classes('text-5xl')
                        ui.label(naziv).classes('text-base font-bold text-gray-800')
                        ui.label(opis).classes('text-xs text-gray-400 text-center')

        ui.separator().classes('max-w-4xl w-full')
        ui.label(WIZ_CONTINUE_EXISTING).classes('text-sm text-gray-400')
        ui.button(WIZ_BTN_LOAD_PROJECT, on_click=lambda: switch_tab('nova')).classes(
            'bg-white text-[#111] border border-[#111]'
        ).props('flat')


def _render_wizard_step2_measurement(ui, state, main_content_refresh) -> None:
    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.button(icon='arrow_back', on_click=lambda: (
                setattr(state, 'wizard_step', 1), main_content_refresh()
            )).props('flat round dense')
            ui.label(WIZ_BACK).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(WIZ_STEP_TYPE).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(WIZ_STEP_MODE).classes('text-sm font-semibold text-gray-700')

        ui.label(WIZ_TITLE_PICK_MODE).classes('text-3xl font-bold text-gray-800')
        ui.label(WIZ_SUB_PICK_MODE).classes('text-gray-400 mb-2')

        with ui.row().classes('flex-wrap justify-center gap-5 max-w-4xl'):
            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'standard'),
                setattr(state, 'wizard_step', 3),
                main_content_refresh()
            )):
                ui.label(WIZ_MODE_STANDARD).classes('font-bold text-gray-800 text-lg')
                ui.label(WIZ_MODE_STANDARD_DESC1).classes('text-sm text-gray-500')
                ui.label(WIZ_MODE_STANDARD_DESC2).classes('text-xs text-gray-400')

            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'pro'),
                setattr(state, 'wizard_step', 3),
                main_content_refresh()
            )):
                ui.label(WIZ_MODE_PRO).classes('font-bold text-gray-800 text-lg')
                ui.label(WIZ_MODE_PRO_DESC1).classes('text-sm text-gray-500')
                ui.label(WIZ_MODE_PRO_DESC2).classes('text-xs text-gray-400')


def _render_wizard_step3_layout(ui, state, main_content_refresh) -> None:
    layouts = [
        ('jedan_zid', WIZ_LAYOUT_ONE_WALL, True, WIZ_LAYOUT_ONE_WALL_DESC, None),
        ('l_oblik_desni', WIZ_LAYOUT_L_RIGHT, False, WIZ_LAYOUT_L_RIGHT_DESC, 'right'),
        ('l_oblik_levi', WIZ_LAYOUT_L_LEFT, False, WIZ_LAYOUT_L_LEFT_DESC, 'left'),
        ('u_oblik', WIZ_LAYOUT_U, False, WIZ_LAYOUT_U_DESC, None),
        ('galija', WIZ_LAYOUT_GALLEY, False, WIZ_LAYOUT_GALLEY_DESC, None),
        ('ostrvo', WIZ_LAYOUT_ISLAND, False, WIZ_LAYOUT_ISLAND_DESC, None),
    ]

    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.button(icon='arrow_back', on_click=lambda: (
                setattr(state, 'wizard_step', 2), main_content_refresh()
            )).props('flat round dense')
            ui.label(WIZ_BACK).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(WIZ_STEP_TYPE).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(WIZ_STEP_MODE).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(WIZ_STEP_LAYOUT).classes('text-sm font-semibold text-gray-700')

        ui.label(WIZ_TITLE_PICK_LAYOUT).classes('text-3xl font-bold text-gray-800')
        ui.label(WIZ_SUB_PICK_LAYOUT).classes('text-gray-400 mb-2')

        with ui.row().classes('flex-wrap justify-center gap-5 max-w-4xl'):
            for ltype, naziv, aktivan, opis, l_corner_side in layouts:
                if aktivan:

                    def _klik(lt=ltype, _lcs=l_corner_side):
                        state.kitchen_layout = 'l_oblik' if str(lt).startswith('l_oblik') else lt
                        state.kitchen['layout'] = state.kitchen_layout
                        if state.kitchen_layout == 'l_oblik':
                            state.l_corner_side = str(_lcs or 'right')
                            state.kitchen['l_corner_side'] = state.l_corner_side
                        # Priprema room state-a po odabranom obliku (bez lomljenja one-wall toka).
                        _room = getattr(state, 'room', None) or {}
                        _walls = list(_room.get('walls', []) or [])
                        _wa = next((w for w in _walls if str(w.get('key', '')).upper() == 'A'), None)
                        _wb = next((w for w in _walls if str(w.get('key', '')).upper() == 'B'), None)
                        _wc = next((w for w in _walls if str(w.get('key', '')).upper() == 'C'), None)
                        _wl = int((_wa or {}).get('length_mm', _room.get('wall_length_mm', 3000)) or 3000)
                        _rd = int(_room.get('room_depth_mm', (_wb or {}).get('length_mm', 3000)) or 3000)

                        if state.kitchen_layout == 'l_oblik':
                            # L osnova: aktivan kuhinjski zid je A, bočni B je spreman za nastavak.
                            _room['active_wall'] = 'A'
                            _room['kitchen_wall'] = 'A'
                            _room['room_depth_mm'] = max(1800, _rd)
                            _room['l_corner_side'] = str(_lcs or 'right')
                            # Sinkronizuj zidove ako postoje.
                            if _wa is not None:
                                _wa['length_mm'] = int(_wl)
                            if _wb is not None:
                                _wb['length_mm'] = int(_room['room_depth_mm'])
                            if _wc is not None:
                                _wc['length_mm'] = int(_room['room_depth_mm'])
                            _room['setup_panel_mode'] = 'walls'
                        else:
                            # Jedan zid: zadrži postojeći stabilni tok.
                            _room['active_wall'] = 'A'
                            _room['kitchen_wall'] = 'A'
                            _room['setup_panel_mode'] = 'walls'

                        state.wizard_step = 4
                        main_content_refresh()

                    with ui.card().classes(
                        'w-52 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                        'border-2 border-transparent transition-all duration-200 p-4 gap-2'
                    ).on('click', _klik):
                        ui.label(naziv).classes('font-bold text-gray-800 text-center text-sm')
                        ui.label(opis).classes('text-xs text-gray-400 text-center')
                else:
                    with ui.card().classes(
                        'w-52 border-2 border-dashed border-gray-200 p-4 gap-2 opacity-50'
                    ):
                        ui.label(naziv).classes('font-bold text-gray-400 text-center text-sm')
                        ui.label(opis).classes('text-xs text-gray-300 text-center')
                        ui.badge(LBL_USKORO).classes('bg-gray-100 text-gray-400 text-xs mx-auto')
