# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable

from auth_models import ensure_local_session
from i18n import SYM_CHEVRON


def render_wizard_tab(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content: Any,
    main_content_refresh: Callable[[], None],
    switch_tab: Callable[[str], None],
    render_room_setup_step3: Callable[..., None],
    plt: Any,
    ensure_room_walls: Callable[..., Any],
    get_room_wall: Callable[..., Any],
    set_wall_length: Callable[[int], None],
    set_wall_height: Callable[[int], None],
    room_opening_types: Any,
    room_fixture_types: Any,
) -> None:
    with ui.column().classes('w-full h-[calc(100vh-48px)] overflow-hidden'):
        _render_wizard(
            ui=ui,
            state=state,
            tr_fn=tr_fn,
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
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
    switch_tab: Callable[[str], None],
    render_room_setup_step3: Callable[..., None],
    plt: Any,
    ensure_room_walls: Callable[..., Any],
    get_room_wall: Callable[..., Any],
    set_wall_length: Callable[[int], None],
    set_wall_height: Callable[[int], None],
    room_opening_types: Any,
    room_fixture_types: Any,
    main_content: Any,
) -> None:
    state.project_type = 'kitchen'
    state.kitchen['project_type'] = 'kitchen'
    state.kitchen_layout = 'jedan_zid'
    state.kitchen['layout'] = 'jedan_zid'

    if state.wizard_step == 3:
        state.wizard_step = 4

    _auth_mode = str(getattr(state, 'current_auth_mode', '') or '').strip().lower()
    if state.wizard_step == 1 and not _auth_mode:
        _render_wizard_auth_gate(ui, state, tr_fn, main_content_refresh, switch_tab)
        return

    if state.wizard_step == 1:
        _render_wizard_step1(ui, state, tr_fn, main_content_refresh, switch_tab)
    elif state.wizard_step == 2:
        _render_wizard_step2_measurement(ui, state, tr_fn, main_content_refresh)
    else:
        render_room_setup_step3(
            state,
            ui=ui,
            tr_fn=tr_fn,
            plt=plt,
            _ensure_room_walls=ensure_room_walls,
            _get_room_wall=get_room_wall,
            _set_wall_length=set_wall_length,
            _set_wall_height=set_wall_height,
            main_content=main_content,
            ROOM_OPENING_TYPES=room_opening_types,
            ROOM_FIXTURE_TYPES=room_fixture_types,
        )


def _render_wizard_auth_gate(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
    switch_tab: Callable[[str], None],
) -> None:
    def _continue_local() -> None:
        session = ensure_local_session()
        state.current_user_id = int(session.user.user_id)
        state.current_user_email = str(session.user.email)
        state.current_user_display = str(session.user.display_name)
        state.current_auth_mode = "local"
        state.current_access_tier = str(session.user.access_tier or "local_beta")
        state.current_subscription_status = str(session.user.subscription_status or "local_active")
        state.current_gate_reason = str(session.gate_reason or "")
        state.current_can_access_app = bool(session.can_access_app)
        main_content_refresh()

    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-5'):
        with ui.card().classes('w-full max-w-2xl p-8 bg-white border border-gray-200'):
            ui.label(tr_fn('wizard.auth_gate_title')).classes('text-3xl font-bold text-gray-900')
            ui.label(tr_fn('wizard.auth_gate_desc')).classes('text-base text-gray-600')
            with ui.column().classes('w-full gap-3 mt-4'):
                ui.button(
                    tr_fn('wizard.auth_gate_create_btn'),
                    on_click=lambda: switch_tab('nalog'),
                ).classes('w-full bg-[#111] text-white')
                ui.button(
                    tr_fn('wizard.auth_gate_login_btn'),
                    on_click=lambda: switch_tab('nalog'),
                ).classes('w-full bg-white text-[#111] border border-[#111]')
            ui.link(
                tr_fn('wizard.auth_gate_local_link'),
                _continue_local,
            ).classes('text-sm text-gray-500 mt-4')


def _render_wizard_step1(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
    switch_tab: Callable[[str], None],
) -> None:
    def _start_new_kitchen() -> None:
        state.project_type = 'kitchen'
        state.kitchen['project_type'] = 'kitchen'
        state.furniture_type = 'kuhinja'
        state.kitchen_layout = 'jedan_zid'
        state.kitchen['layout'] = 'jedan_zid'
        state.active_group = 'donji'
        state.measurement_mode = ''
        state.wizard_step = 2
        main_content_refresh()

    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        ui.label(tr_fn('wizard.title_app')).classes('text-4xl font-bold text-gray-800')
        ui.label(tr_fn('wizard.title_pick_type')).classes('text-lg text-gray-500 mb-2')

        with ui.row().classes('flex-wrap justify-center items-stretch gap-4 max-w-5xl w-full'):
            with ui.card().classes(
                'w-[320px] cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 '
                'flex flex-col gap-3 p-6 bg-white'
            ).on('click', _start_new_kitchen):
                ui.label(tr_fn('wizard.start_recommended')).classes(
                    'self-start text-xs font-semibold uppercase tracking-wide text-green-700 '
                    'bg-green-100 px-3 py-1 rounded-full'
                )
                ui.label(tr_fn('wizard.type_kitchen')).classes('text-2xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.start_new')).classes('text-xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.start_new_desc')).classes('text-sm text-gray-500')
                ui.separator()
                ui.label(tr_fn('wizard.type_kitchen_desc')).classes('text-sm text-gray-500')
                ui.button(tr_fn('wizard.start_new'), on_click=_start_new_kitchen).classes(
                    'mt-auto bg-[#111] text-white'
                )

            with ui.card().classes(
                'w-[320px] border border-gray-200 flex flex-col gap-3 p-6 bg-white'
            ):
                ui.label(tr_fn('wizard.type_json')).classes('text-2xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.start_load')).classes('text-xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.start_load_desc')).classes('text-sm text-gray-500')
                ui.separator()
                ui.label(tr_fn('wizard.continue_existing')).classes('text-sm text-gray-400')
                ui.button(tr_fn('wizard.load_project'), on_click=lambda: switch_tab('nova')).classes(
                    'mt-auto bg-white text-[#111] border border-[#111]'
                ).props('flat')

            with ui.card().classes(
                'w-[320px] border border-[#d4a017] flex flex-col gap-3 p-6 bg-[#fff7d6]'
            ):
                ui.label(tr_fn('wizard.type_account')).classes('text-2xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.account_title')).classes('text-xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.account_desc')).classes('text-sm text-gray-500')
                ui.separator()
                ui.label(tr_fn('wizard.account_hint')).classes('text-sm text-gray-400')
                ui.button(tr_fn('wizard.account_open'), on_click=lambda: switch_tab('nalog')).classes(
                    'mt-auto bg-[#111] text-white'
                )

            with ui.card().classes('w-[320px] border border-gray-200 flex flex-col gap-3 p-6 bg-[#f7f5ef]'):
                ui.label(tr_fn('wizard.start_next_title')).classes('text-xl font-bold text-gray-800')
                ui.label(tr_fn('wizard.start_next_1')).classes('text-sm text-gray-600')
                ui.label(tr_fn('wizard.start_next_2')).classes('text-sm text-gray-600')
                ui.label(tr_fn('wizard.start_next_3')).classes('text-sm text-gray-600')


def _render_wizard_step2_measurement(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
) -> None:
    with ui.column().classes('w-full h-full overflow-auto bg-gray-50 items-center justify-center p-8 gap-6'):
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.button(f'← {tr_fn("wizard.back")}', on_click=lambda: (
                setattr(state, 'wizard_step', 1), main_content_refresh()
            )).props('flat dense')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(tr_fn('wizard.step_type')).classes('text-sm text-gray-400')
            ui.label(SYM_CHEVRON).classes('text-gray-300')
            ui.label(tr_fn('wizard.step_mode')).classes('text-sm font-semibold text-gray-700')

        ui.label(tr_fn('wizard.title_pick_mode')).classes('text-3xl font-bold text-gray-800')
        ui.label(tr_fn('wizard.sub_pick_mode')).classes('text-gray-400 mb-2')

        with ui.row().classes('flex-wrap justify-center gap-5 max-w-4xl'):
            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'standard'),
                setattr(
                    state,
                    'room',
                    {
                        **getattr(state, 'room', {}),
                        'active_wall': 'A',
                        'kitchen_wall': 'A',
                        'setup_panel_mode': 'walls',
                    },
                ),
                setattr(state, 'wizard_step', 4),
                main_content_refresh()
            )):
                ui.label(tr_fn('wizard.mode_standard_badge')).classes(
                    'self-start text-xs font-semibold uppercase tracking-wide text-green-700 '
                    'bg-green-100 px-3 py-1 rounded-full mb-1'
                )
                ui.label(tr_fn('wizard.mode_standard')).classes('font-bold text-gray-800 text-lg')
                ui.label(tr_fn('wizard.mode_standard_desc1')).classes('text-sm text-gray-500')
                ui.label(tr_fn('wizard.mode_standard_desc2')).classes('text-xs text-gray-400')
                ui.label(tr_fn('wizard.mode_standard_desc3')).classes('text-xs text-gray-500')

            with ui.card().classes(
                'w-80 cursor-pointer hover:shadow-xl hover:border-gray-500 '
                'border-2 border-transparent transition-all duration-200 p-5 gap-2'
            ).on('click', lambda: (
                setattr(state, 'measurement_mode', 'pro'),
                setattr(
                    state,
                    'room',
                    {
                        **getattr(state, 'room', {}),
                        'active_wall': 'A',
                        'kitchen_wall': 'A',
                        'setup_panel_mode': 'walls',
                    },
                ),
                setattr(state, 'wizard_step', 4),
                main_content_refresh()
            )):
                ui.label(tr_fn('wizard.mode_pro_badge')).classes(
                    'self-start text-xs font-semibold uppercase tracking-wide text-amber-700 '
                    'bg-amber-100 px-3 py-1 rounded-full mb-1'
                )
                ui.label(tr_fn('wizard.mode_pro')).classes('font-bold text-gray-800 text-lg')
                ui.label(tr_fn('wizard.mode_pro_desc1')).classes('text-sm text-gray-500')
                ui.label(tr_fn('wizard.mode_pro_desc2')).classes('text-xs text-gray-400')
                ui.label(tr_fn('wizard.mode_pro_desc3')).classes('text-xs text-gray-500')
