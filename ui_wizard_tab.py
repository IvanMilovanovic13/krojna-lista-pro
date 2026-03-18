# -*- coding: utf-8 -*-
from __future__ import annotations

from i18n import (
    SYM_CHEVRON,
    WIZ_BACK,
    WIZ_BTN_LOAD_PROJECT,
    WIZ_CONTINUE_EXISTING,
    WIZ_MODE_PRO,
    WIZ_MODE_PRO_DESC1,
    WIZ_MODE_PRO_DESC2,
    WIZ_MODE_STANDARD,
    WIZ_MODE_STANDARD_DESC1,
    WIZ_MODE_STANDARD_DESC2,
    WIZ_STEP_MODE,
    WIZ_STEP_TYPE,
    WIZ_SUB_PICK_MODE,
    WIZ_TITLE_APP,
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
    # Produkcija: jedan zid, projekat uvek kuhinja.
    state.project_type = 'kitchen'
    state.kitchen['project_type'] = 'kitchen'
    state.kitchen_layout = 'jedan_zid'
    state.kitchen['layout'] = 'jedan_zid'

    # Wizard ima 3 koraka: 1=tip, 2=rezim merenja, 4=prostorija (korak 3 nije u produkciji)
    if state.wizard_step == 3:
        state.wizard_step = 4

    if state.wizard_step == 1:
        _render_wizard_step1(ui, state, main_content_refresh, switch_tab)
    elif state.wizard_step == 2:
        _render_wizard_step2_measurement(ui, state, main_content_refresh)
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
    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        ui.label(WIZ_TITLE_APP).classes('text-4xl font-bold text-gray-800')
        ui.label(WIZ_TITLE_PICK_TYPE).classes('text-lg text-gray-500 mb-2')

        with ui.row().classes('flex-wrap justify-center gap-4 max-w-4xl'):
            def _klik():
                state.project_type = 'kitchen'
                state.kitchen['project_type'] = 'kitchen'
                state.furniture_type = 'kuhinja'
                state.kitchen_layout = 'jedan_zid'
                state.kitchen['layout'] = 'jedan_zid'
                state.active_group = 'donji'
                state.measurement_mode = ''
                state.wizard_step = 2
                main_content_refresh()

            with ui.card().classes(
                'w-48 h-44 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 '
                'flex flex-col items-center justify-center gap-2 p-4'
            ).on('click', _klik):
                ui.label('🍴').classes('text-5xl')
                ui.label(WIZ_TYPE_KITCHEN).classes('text-base font-bold text-gray-800')
                ui.label(WIZ_TYPE_KITCHEN_DESC).classes('text-xs text-gray-400 text-center')

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
            # Standard merenje -> direktno na korak 4 (prostorija)
            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'standard'),
                setattr(state, 'room', {**getattr(state, 'room', {}), 'active_wall': 'A', 'kitchen_wall': 'A', 'setup_panel_mode': 'walls'}),
                setattr(state, 'wizard_step', 4),
                main_content_refresh()
            )):
                ui.label(WIZ_MODE_STANDARD).classes('font-bold text-gray-800 text-lg')
                ui.label(WIZ_MODE_STANDARD_DESC1).classes('text-sm text-gray-500')
                ui.label(WIZ_MODE_STANDARD_DESC2).classes('text-xs text-gray-400')

            # PRO merenje -> direktno na korak 4 (prostorija)
            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'pro'),
                setattr(state, 'room', {**getattr(state, 'room', {}), 'active_wall': 'A', 'kitchen_wall': 'A', 'setup_panel_mode': 'walls'}),
                setattr(state, 'wizard_step', 4),
                main_content_refresh()
            )):
                ui.label(WIZ_MODE_PRO).classes('font-bold text-gray-800 text-lg')
                ui.label(WIZ_MODE_PRO_DESC1).classes('text-sm text-gray-500')
                ui.label(WIZ_MODE_PRO_DESC2).classes('text-xs text-gray-400')
