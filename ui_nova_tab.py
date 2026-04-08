# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Callable

from i18n import (
    ERR_LOAD_PREFIX,
    MSG_SAVE_OK,
)

_LOG = logging.getLogger(__name__)


def render_nova_tab(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
    render_toolbar_refresh: Callable[[], None],
    switch_tab: Callable[[str], None],
    clear_all_local: Callable[[], None],
    save_project_json: Callable[[], bytes],
    load_project_json: Callable[[bytes], tuple[bool, str]],
    build_demo_project_json: Callable[[], bytes],
    save_local_recent_project: Callable[..., str],
    list_recent_projects: Callable[[], list[dict[str, str]]],
    load_recent_project: Callable[[str], tuple[bool, str]],
    list_user_store_projects: Callable[[], list[dict[str, str]]],
    load_project_from_store: Callable[[int], tuple[bool, str]],
    get_autosave_info: Callable[[], dict[str, str] | None],
    load_autosave_project: Callable[[], tuple[bool, str]],
    login_user_session: Callable[[str, str], tuple[bool, str]],
    register_trial_user_session: Callable[[str, str, str], tuple[bool, str]],
    restore_local_session_state: Callable[[], tuple[bool, str]],
    logout_current_session: Callable[[], tuple[bool, str]],
    build_forgot_password_message: Callable[[str], tuple[bool, str]],
    reset_password_with_token: Callable[[str, str], tuple[bool, str]],
    get_current_billing_summary: Callable[[], dict[str, Any] | None],
    build_checkout_start_message: Callable[[], tuple[bool, str]],
    build_customer_portal_message: Callable[[], tuple[bool, str]],
) -> None:
    is_authenticated = bool(str(getattr(state, 'current_user_email', '') or '').strip())
    billing = get_current_billing_summary()

    async def _resolve_input_value(element_id: str, fallback: str = "") -> str:
        try:
            value = await ui.run_javascript(
                f"""
                (() => {{
                    const root = document.getElementById('{element_id}');
                    if (!root) return '';
                    const input = root.querySelector('input');
                    return input ? (input.value || '') : '';
                }})()
                """
            )
            clean = str(value or "").strip()
            return clean if clean else str(fallback or "").strip()
        except Exception:
            return str(fallback or "").strip()

    def _dashboard_billing_copy(payload: dict[str, str] | None) -> tuple[str, str, bool, bool]:
        if not payload:
            return "", "", False, False
        account_status = str(payload.get('account_status', '') or '').strip().lower()
        billing_status = str(payload.get('billing_status', '') or '').strip().lower()
        access_tier = str(payload.get('access_tier', '') or '').strip().lower()
        stripe_ready = bool(payload.get('stripe_ready', False))
        if account_status == 'admin_active' or access_tier == 'admin':
            return (
                tr_fn('nova.billing_state_admin_title'),
                tr_fn('nova.billing_state_admin_desc'),
                False,
                False,
            )
        if account_status == 'paid_active' or billing_status in ('active', 'paid'):
            return (
                tr_fn('nova.billing_state_paid_title'),
                tr_fn('nova.billing_state_paid_desc'),
                False,
                stripe_ready and bool(payload.get('has_portal', False)),
            )
        if billing_status == 'past_due':
            return (
                tr_fn('nova.billing_state_past_due_title'),
                tr_fn('nova.billing_state_past_due_desc'),
                stripe_ready,
                stripe_ready,
            )
        if account_status == 'trial_active' or access_tier == 'trial' or billing_status in ('trial', 'trialing'):
            return (
                tr_fn('nova.billing_state_trial_title'),
                tr_fn('nova.billing_state_trial_desc'),
                stripe_ready,
                False,
            )
        return (
            tr_fn('nova.billing_state_inactive_title'),
            tr_fn('nova.billing_state_inactive_desc'),
            stripe_ready,
            stripe_ready and bool(payload.get('has_portal', False)),
        )

    def _dashboard_primary_action_copy(payload: dict[str, Any] | None) -> tuple[str, str, str, str]:
        if not payload:
            return (
                tr_fn('nova.primary_action_start_title'),
                tr_fn('nova.primary_action_start_desc'),
                tr_fn('nova.primary_action_start_btn'),
                'project',
            )
        account_status = str(payload.get('account_status', '') or '').strip().lower()
        billing_status = str(payload.get('billing_status', '') or '').strip().lower()
        access_tier = str(payload.get('access_tier', '') or '').strip().lower()
        stripe_ready = bool(payload.get('stripe_ready', False))
        if account_status == 'admin_active' or access_tier == 'admin':
            return (
                tr_fn('nova.primary_action_start_title'),
                tr_fn('nova.primary_action_start_desc'),
                tr_fn('nova.primary_action_start_btn'),
                'project',
            )
        if account_status == 'paid_active' or billing_status in ('active', 'paid'):
            return (
                tr_fn('nova.primary_action_start_title'),
                tr_fn('nova.primary_action_paid_desc'),
                tr_fn('nova.primary_action_start_btn'),
                'project',
            )
        if account_status == 'trial_active' or access_tier == 'trial' or billing_status in ('trial', 'trialing'):
            return (
                tr_fn('nova.primary_action_trial_title'),
                tr_fn('nova.primary_action_trial_desc'),
                tr_fn('nova.primary_action_start_btn'),
                'project',
            )
        if billing_status == 'past_due':
            if not stripe_ready:
                return (
                    tr_fn('nova.primary_action_upgrade_title'),
                    tr_fn('nova.primary_action_past_due_desc'),
                    '',
                    'none',
                )
            return (
                tr_fn('nova.primary_action_upgrade_title'),
                tr_fn('nova.primary_action_past_due_desc'),
                tr_fn('nova.billing_checkout_btn'),
                'checkout',
            )
        if not stripe_ready:
            return (
                tr_fn('nova.primary_action_upgrade_title'),
                tr_fn('nova.primary_action_upgrade_desc'),
                '',
                'none',
            )
        return (
            tr_fn('nova.primary_action_upgrade_title'),
            tr_fn('nova.primary_action_upgrade_desc'),
            tr_fn('nova.billing_checkout_btn'),
            'checkout',
        )

    def _show_paid_success_card(payload: dict[str, Any] | None) -> bool:
        if not payload:
            return False
        account_status = str(payload.get('account_status', '') or '').strip().lower()
        billing_status = str(payload.get('billing_status', '') or '').strip().lower()
        access_tier = str(payload.get('access_tier', '') or '').strip().lower()
        return (
            account_status in ('paid_active', 'admin_active')
            or billing_status in ('active', 'paid')
            or access_tier == 'admin'
        )

    with ui.column().classes('w-full max-w-2xl mx-auto gap-6 py-8'):
        if not is_authenticated:
            with ui.card().classes('w-full p-6 bg-[#fff7d6] border-2 border-[#d4a017] shadow-sm'):
                ui.label(tr_fn('nova.auth_title')).classes('text-lg font-bold mb-1')
                ui.label(tr_fn('nova.auth_desc')).classes('text-sm text-gray-600 mb-4')

                login_email = ui.input(
                    label=tr_fn('nova.auth_login_email'),
                    value=str(getattr(state, 'current_user_email', '') or ''),
                ).props('id=nova-login-email autocomplete=username').classes('w-full')
                login_password = ui.input(
                    label=tr_fn('nova.auth_login_password'),
                    password=True,
                    password_toggle_button=True,
                ).props('id=nova-login-password autocomplete=current-password').classes('w-full')

                async def _login_existing() -> None:
                    email_value = await _resolve_input_value('nova-login-email', str(login_email.value or ''))
                    password_value = await _resolve_input_value('nova-login-password', str(login_password.value or ''))
                    ok, err = login_user_session(
                        email_value,
                        password_value,
                    )
                    if ok:
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_login_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_login_btn'), on_click=_login_existing).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )

                ui.separator().classes('my-4')

                register_name = ui.input(label=tr_fn('nova.auth_register_name')).props(
                    'id=nova-register-name autocomplete=name'
                ).classes('w-full')
                register_email = ui.input(label=tr_fn('nova.auth_register_email')).props(
                    'id=nova-register-email autocomplete=email'
                ).classes('w-full')
                register_password = ui.input(
                    label=tr_fn('nova.auth_register_password'),
                    password=True,
                    password_toggle_button=True,
                ).props('id=nova-register-password autocomplete=new-password').classes('w-full')

                async def _register_trial() -> None:
                    register_name_value = await _resolve_input_value('nova-register-name', str(register_name.value or ''))
                    register_email_value = await _resolve_input_value('nova-register-email', str(register_email.value or ''))
                    register_password_value = await _resolve_input_value('nova-register-password', str(register_password.value or ''))
                    ok, err = register_trial_user_session(
                        register_email_value,
                        register_name_value,
                        register_password_value,
                    )
                    if ok:
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_register_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_register_btn'), on_click=_register_trial).classes(
                    'w-full bg-[#111] text-white mt-2'
                )

                ui.separator().classes('my-4')

                forgot_email = ui.input(label=tr_fn('nova.auth_forgot_email')).props(
                    'id=nova-forgot-email autocomplete=email'
                ).classes('w-full')

                async def _forgot_password() -> None:
                    forgot_value = await _resolve_input_value('nova-forgot-email', str(forgot_email.value or ''))
                    ok, msg = build_forgot_password_message(forgot_value)
                    if ok:
                        ui.notify(msg, type='info', timeout=5000)
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=msg), type='negative', timeout=5000)

                def _restore_local() -> None:
                    ok, err = restore_local_session_state()
                    if ok:
                        render_toolbar_refresh()
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_local_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_forgot_btn'), on_click=_forgot_password).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )
                ui.button(tr_fn('nova.auth_local_btn'), on_click=_restore_local).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )

        if is_authenticated:
            _current_tier = str(getattr(state, 'current_access_tier', '') or '').strip().lower()
            billing_title, billing_desc, show_checkout, show_portal = _dashboard_billing_copy(billing)
            primary_title, primary_desc, primary_btn, primary_mode = _dashboard_primary_action_copy(billing)
            _show_plan_cards = _current_tier in {'trial', 'local', 'local_beta', ''}

            with ui.card().classes('w-full p-6 bg-[#f7f5ef] border border-gray-200'):
                ui.label('krojna lista PRO').classes('text-3xl font-bold text-gray-900')
                ui.label('Dashboard / Projekti').classes('text-xs font-semibold uppercase tracking-[0.18em] text-gray-400')
                if _show_plan_cards:
                    ui.label(tr_fn('nova.plan_choose_title')).classes('text-lg text-gray-700')
                    ui.label(tr_fn('nova.plan_choose_desc')).classes('text-sm text-gray-500')
                else:
                    ui.label(tr_fn('nova.projects_heading')).classes('text-lg text-gray-700')
                    ui.label(tr_fn('nova.projects_subheading')).classes('text-sm text-gray-500')

            def _start_fresh_project() -> None:
                clear_all_local()
                state.active_tab = "elementi"
                main_content_refresh()
                ui.notify(tr_fn('nova.created_ok'), type='positive')

            def _continue_current_project() -> None:
                state.active_tab = "elementi"
                main_content_refresh()

            def _start_paid_checkout(plan_code: str) -> None:
                ok, msg = build_checkout_start_message(plan_code)
                if ok and str(msg or '').startswith(('http://', 'https://')):
                    ui.navigate.to(str(msg), new_tab=True)
                    ui.notify(tr_fn('nova.billing_checkout_redirect'), type='positive', timeout=4000)
                else:
                    ui.notify(msg or tr_fn('nova.billing_checkout_btn'), type='info' if ok else 'negative', timeout=5000)

            def _open_portal_dashboard() -> None:
                ok, msg = build_customer_portal_message()
                if ok and str(msg or '').startswith(('http://', 'https://')):
                    ui.navigate.to(str(msg), new_tab=True)
                    ui.notify(tr_fn('nova.billing_portal_redirect'), type='positive', timeout=4000)
                else:
                    ui.notify(msg or tr_fn('nova.billing_portal_btn'), type='info' if ok else 'negative', timeout=5000)

            def _run_primary_action() -> None:
                if primary_mode == 'checkout':
                    ok, msg = build_checkout_start_message()
                    if ok and str(msg or '').startswith(('http://', 'https://')):
                        ui.navigate.to(str(msg), new_tab=True)
                        ui.notify(tr_fn('nova.billing_checkout_redirect'), type='positive', timeout=4000)
                    else:
                        ui.notify(msg or tr_fn('nova.billing_checkout_btn'), type='info' if ok else 'negative', timeout=5000)
                    return
                if primary_mode == 'project':
                    _start_fresh_project()

            autosave_info = get_autosave_info()
            if _show_paid_success_card(billing):
                with ui.card().classes('w-full p-5 bg-[#eefbf3] border border-[#b7e4c7]'):
                    ui.label(tr_fn('nova.paid_success_title')).classes('text-base font-bold text-[#166534]')
                    ui.label(tr_fn('nova.billing_state_paid_desc')).classes('text-sm text-[#166534]')

            if _show_plan_cards:
                with ui.row().classes('w-full gap-4 max-md:flex-col'):
                    with ui.card().classes('flex-1 p-5 bg-white border border-gray-200'):
                        ui.label(tr_fn('nova.plan_weekly_title')).classes('text-base font-bold text-gray-900')
                        ui.label(tr_fn('nova.plan_weekly_desc')).classes('text-sm text-gray-600')
                        ui.button(
                            tr_fn('nova.plan_weekly_btn'),
                            on_click=lambda: _start_paid_checkout('pro_weekly'),
                        ).classes('w-full mt-4 bg-[#111] text-white')
                    with ui.card().classes('flex-1 p-5 bg-white border border-gray-200'):
                        ui.label(tr_fn('nova.plan_monthly_title')).classes('text-base font-bold text-gray-900')
                        ui.label(tr_fn('nova.plan_monthly_desc')).classes('text-sm text-gray-600')
                        ui.button(
                            tr_fn('nova.plan_monthly_btn'),
                            on_click=lambda: _start_paid_checkout('pro_monthly'),
                        ).classes('w-full mt-4 bg-[#111] text-white')

            if billing_title or billing_desc:
                with ui.card().classes('w-full p-5 bg-[#f8fafc] border border-gray-200'):
                    ui.label(billing_title).classes('text-base font-bold text-gray-900')
                    ui.label(billing_desc).classes('text-sm text-gray-600')
                    ui.label(
                            tr_fn(
                                'nova.billing_status_fmt',
                                plan=str((billing or {}).get('plan_code', '-') or '-'),
                                billing_status=str((billing or {}).get('billing_status', '-') or '-'),
                                access_tier=str((billing or {}).get('access_tier', '-') or '-'),
                            )
                    ).classes('text-sm text-gray-600')
                    with ui.row().classes('w-full gap-3 mt-3 max-md:flex-col'):
                        if show_checkout:
                            ui.button(tr_fn('nova.billing_checkout_btn'), on_click=lambda: _start_paid_checkout('pro_monthly')).classes(
                                'flex-1 bg-[#111] text-white'
                            )
                        if show_portal:
                            ui.button(tr_fn('nova.billing_portal_btn'), on_click=_open_portal_dashboard).classes(
                                'flex-1 bg-white text-[#111] border border-[#111]'
                            )

            with ui.card().classes('w-full p-5 bg-white border border-gray-200'):
                ui.label(primary_title).classes('text-base font-bold text-gray-900')
                ui.label(primary_desc).classes('text-sm text-gray-600')
                ui.label('Nastavi rad').classes('text-xs font-semibold uppercase tracking-[0.18em] text-gray-400')
                if primary_mode != 'none' and str(primary_btn or '').strip():
                    ui.button(primary_btn, on_click=_run_primary_action).classes(
                        'w-full bg-white text-[#111] border border-[#111] mt-3'
                    )

            with ui.card().classes('w-full p-4 bg-white border border-gray-200'):
                ui.label(tr_fn('nova.account_card_title')).classes('text-sm font-bold text-gray-800')
                ui.label(str(getattr(state, 'current_user_email', '') or '')).classes('text-base text-gray-900')
                ui.label(
                    tr_fn(
                        'nova.session_meta',
                        access_tier=str(getattr(state, 'current_access_tier', '') or 'local_beta'),
                        auth_mode=str(getattr(state, 'current_auth_mode', '') or 'local'),
                        status=str(getattr(state, 'current_subscription_status', '') or 'local_active'),
                    )
                ).classes('text-xs text-gray-500')
                if not bool(getattr(state, 'current_can_access_app', True)):
                    ui.label(str(getattr(state, 'current_gate_reason', '') or tr_fn('nova.session_blocked'))).classes(
                        'text-xs text-red-600 mt-1'
                    )
                with ui.row().classes('w-full gap-2 mt-3 max-md:flex-col'):
                    ui.button(
                        tr_fn('nova.dashboard_account_btn'),
                        on_click=lambda: switch_tab('nalog'),
                    ).classes('flex-1 bg-white text-[#111] border border-[#111]')

                    def _logout_dashboard() -> None:
                        ok, err = logout_current_session()
                        if ok:
                            render_toolbar_refresh()
                            main_content_refresh()
                            ui.notify(tr_fn('nova.auth_logout_ok'), type='positive')
                            ui.navigate.to('/login')
                        else:
                            ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                    ui.button(tr_fn('nova.auth_logout_btn'), on_click=_logout_dashboard).classes(
                        'flex-1 bg-white text-[#111] border border-[#111]'
                    )

        if int(getattr(state, 'current_project_id', 0) or 0):
            with ui.card().classes('w-full p-4 bg-[#f7f5ef] border border-gray-200'):
                ui.label(tr_fn('nova.current_project_title')).classes('text-sm font-bold text-gray-800')
                ui.label(str(getattr(state, 'current_project_name', '') or tr_fn('nova.current_project_unknown'))).classes(
                    'text-base text-gray-900'
                )
                ui.label(
                    tr_fn(
                        'nova.current_project_meta',
                        project_id=int(getattr(state, 'current_project_id', 0) or 0),
                        source=str(getattr(state, 'current_project_source', '') or 'local'),
                    )
                ).classes('text-xs text-gray-500')

        if not is_authenticated:
            with ui.card().classes('w-full p-8 text-center'):
                ui.label(tr_fn('nova.title')).classes('text-2xl font-bold mb-2')
                ui.label(tr_fn('nova.warn_clear')).classes('text-gray-500 mb-6')

                def _potvrdi():
                    clear_all_local()
                    state.active_tab = "elementi"
                    main_content_refresh()
                    ui.notify(tr_fn('nova.created_ok'), type='positive')

                ui.button(tr_fn('nova.confirm'), on_click=_potvrdi).classes(
                    'bg-white text-[#111] border border-[#111] w-full'
                )
                ui.button(tr_fn('nova.cancel'), on_click=lambda: switch_tab('elementi')).classes('w-full mt-2')

        if not is_authenticated:
            with ui.card().classes('w-full p-6'):
                ui.label(tr_fn('nova.save_load_title')).classes('text-lg font-bold mb-4')

                autosave_info = get_autosave_info()
                if autosave_info and not is_authenticated:
                    def _open_autosave() -> None:
                        ok, err = load_autosave_project()
                        if ok:
                            state.room_setup_done = True
                            state.active_tab = "elementi"
                            main_content_refresh()
                            ui.notify(tr_fn('nova.autosave_open_ok'), type='positive')
                        else:
                            ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                    with ui.card().classes('w-full p-4 mb-4 bg-[#eef6ff] border border-[#c7ddff]'):
                        ui.label(tr_fn('nova.autosave_title')).classes('text-base font-bold mb-1')
                        if autosave_info.get('saved_at'):
                            ui.label(
                                tr_fn('nova.autosave_saved_at', saved_at=str(autosave_info.get('saved_at', '')))
                            ).classes('text-sm text-gray-700 mb-1')
                        ui.label(tr_fn('nova.autosave_desc')).classes('text-sm text-gray-600 mb-3')
                        ui.button(tr_fn('nova.autosave_open'), on_click=_open_autosave).classes(
                            'w-full bg-white text-[#111] border border-[#111]'
                        )

                def _load_demo() -> None:
                    ok, err = load_project_json(build_demo_project_json())
                    if ok:
                        save_local_recent_project(label=tr_fn('nova.demo_title'))
                        state.room_setup_done = True
                        state.active_tab = "elementi"
                        main_content_refresh()
                        ui.notify(tr_fn('nova.demo_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                with ui.card().classes('w-full p-4 mb-4 bg-[#f7f5ef] border border-gray-200'):
                    ui.label(tr_fn('nova.demo_title')).classes('text-base font-bold mb-1')
                    ui.label(tr_fn('nova.demo_desc')).classes('text-sm text-gray-600 mb-3')
                    ui.button(tr_fn('nova.demo_open'), on_click=_load_demo).classes(
                        'w-full bg-[#111] text-white'
                    )

                def _nova_save():
                    from datetime import datetime as _dt
                    filename = f"kuhinja_{_dt.now().strftime('%Y%m%d_%H%M%S')}.json"
                    data = save_project_json()
                    ui.download(data, filename, "application/json")
                    save_local_recent_project(label=filename.replace('.json', ''))
                    ui.notify(MSG_SAVE_OK.format(filename=filename), type='positive', timeout=3000)

                ui.button(tr_fn('nova.save_json'), on_click=_nova_save).classes(
                    'w-full bg-white text-[#111] border border-[#111] mb-4'
                )

                ui.label(tr_fn('nova.load_from_file')).classes('text-sm text-gray-600 mb-2')
                _nova_status = ui.label('').classes('text-sm mb-2')
                _pending_raw = [b'']

                async def _extract_raw_upload(e) -> bytes:
                    _raw = b''
                    try:
                        _file = getattr(e, 'file', None)
                        if _file is not None and hasattr(_file, 'read'):
                            _raw = await _file.read()
                            if _raw:
                                return _raw
                        _content = getattr(e, 'content', None)
                        if hasattr(_content, 'read'):
                            _raw = _content.read()
                            if not _raw and hasattr(_content, 'seek'):
                                _content.seek(0)
                                _raw = _content.read()
                        elif isinstance(_content, (bytes, bytearray)):
                            _raw = bytes(_content)
                        elif isinstance(getattr(e, 'content', None), str):
                            _raw = str(e.content).encode('utf-8')
                        if not _raw:
                            _data = getattr(e, 'data', None)
                            if isinstance(_data, (bytes, bytearray)):
                                _raw = bytes(_data)
                    except Exception as ex:
                        _LOG.debug("Nova upload read failed: %s", ex)
                        _raw = b''
                    return _raw

                async def _nova_upload(e) -> None:
                    _raw = await _extract_raw_upload(e)
                    if not _raw:
                        _nova_status.set_text(tr_fn('nova.no_file_content'))
                        _nova_status.classes('text-red-600', remove='text-gray-800')
                        ui.notify(tr_fn('nova.load_empty_fail'), type='negative')
                        return
                    _pending_raw[0] = _raw
                    _nova_status.set_text(tr_fn('nova.file_selected'))
                    _nova_status.classes('text-gray-800', remove='text-red-600')

                def _nova_load_selected() -> None:
                    _raw = _pending_raw[0]
                    if not _raw:
                        _nova_status.set_text(tr_fn('nova.no_file_content'))
                        _nova_status.classes('text-red-600', remove='text-gray-800')
                        ui.notify(tr_fn('nova.load_empty_fail'), type='negative')
                        return
                    ok, err = load_project_json(_raw)
                    if ok:
                        save_local_recent_project(label='Ucitan lokalni fajl')
                        _nova_status.set_text(tr_fn('nova.load_ok'))
                        _nova_status.classes('text-gray-800 font-semibold', remove='text-red-600')
                        ui.notify(tr_fn('nova.load_ok'), type='positive')
                        state.room_setup_done = True
                        main_content_refresh()
                    else:
                        _nova_status.set_text(ERR_LOAD_PREFIX.format(err=err))
                        _nova_status.classes('text-red-600', remove='text-gray-800')
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                _nova_uploader = ui.upload(
                    on_upload=_nova_upload,
                    auto_upload=True,
                ).props(f'accept=".json" label="{tr_fn("nova.upload_label")}"').classes('w-full')
                ui.button(tr_fn('nova.load_selected'), on_click=_nova_load_selected).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )

        if is_authenticated:
            with ui.card().classes('w-full p-6 bg-[#f8fafc] border border-gray-200'):
                ui.label(tr_fn('nova.user_projects_title')).classes('text-lg font-bold mb-4')
                user_projects = list_user_store_projects()
                if not user_projects:
                    ui.label(tr_fn('nova.user_projects_empty')).classes('text-sm text-gray-500')
                else:
                    for item in user_projects:
                        project_id = int(item.get('project_id', 0) or 0)
                        name = str(item.get('name', '') or tr_fn('nova.current_project_unknown'))
                        updated_at = str(item.get('updated_at', '') or item.get('last_opened_at', '') or '')
                        source = str(item.get('source', '') or 'local')

                        def _open_user_project(pid=project_id) -> None:
                            ok, err = load_project_from_store(pid)
                            if ok:
                                state.room_setup_done = True
                                state.active_tab = "elementi"
                                main_content_refresh()
                                ui.notify(tr_fn('nova.user_projects_open_ok'), type='positive')
                            else:
                                ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                        with ui.card().classes('w-full p-4 mb-3 border border-gray-200 bg-white shadow-sm'):
                            with ui.row().classes('w-full items-start justify-between gap-3 max-md:flex-col'):
                                with ui.column().classes('gap-1'):
                                    ui.label(name).classes('text-sm font-bold text-gray-800')
                                    if updated_at:
                                        ui.label(updated_at).classes('text-xs text-gray-500')
                                    ui.label(
                                        tr_fn('nova.user_projects_meta', project_id=project_id, source=source)
                                    ).classes('text-xs text-gray-500')
                                ui.button(tr_fn('nova.user_projects_open'), on_click=_open_user_project).classes(
                                    'bg-white text-[#111] border border-[#111] min-w-[150px]'
                                )

        if not is_authenticated:
            with ui.card().classes('w-full p-6 bg-[#f8fafc] border border-gray-200'):
                ui.label(tr_fn('nova.recent_title')).classes('text-lg font-bold mb-4')
                recent_items = list_recent_projects()
                if not recent_items:
                    ui.label(tr_fn('nova.recent_empty')).classes('text-sm text-gray-500')
                else:
                    for item in recent_items:
                        label = str(item.get('label', '') or 'Projekat')
                        path = str(item.get('path', '') or '')
                        saved_at = str(item.get('saved_at', '') or '')
                        store_project_id = int(item.get('store_project_id', 0) or 0)

                        def _open_recent(project_path=path, project_store_id=store_project_id) -> None:
                            if project_store_id > 0:
                                ok, err = load_project_from_store(project_store_id)
                            else:
                                ok, err = load_recent_project(project_path)
                            if ok:
                                state.room_setup_done = True
                                state.active_tab = "elementi"
                                main_content_refresh()
                                ui.notify(tr_fn('nova.recent_open_ok'), type='positive')
                            else:
                                ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                        with ui.card().classes('w-full p-4 border border-gray-200 bg-white shadow-sm'):
                            with ui.row().classes('w-full items-start justify-between gap-3 max-md:flex-col'):
                                with ui.column().classes('gap-1'):
                                    ui.label(label).classes('text-sm font-bold text-gray-800')
                                    if saved_at:
                                        ui.label(saved_at).classes('text-xs text-gray-500')
                                    if store_project_id > 0:
                                        ui.label(tr_fn('nova.current_project_store_id', project_id=store_project_id)).classes('text-xs text-gray-500')
                                    _path_label = "Centralni storage zapis" if path.startswith('store://') else path
                                    ui.label(_path_label).classes('text-xs text-gray-400 break-all')
                                ui.button(tr_fn('nova.recent_open'), on_click=_open_recent).classes(
                                    'bg-white text-[#111] border border-[#111] min-w-[170px]'
                                )
