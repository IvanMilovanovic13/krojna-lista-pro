# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable

from i18n import ERR_LOAD_PREFIX


def render_auth_tab(
    ui: Any,
    state: Any,
    tr_fn: Callable[[str], str],
    main_content_refresh: Callable[[], None],
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

    def _billing_state_copy(billing: dict[str, Any]) -> tuple[str, str, list[str], bool, bool]:
        account_status = str(billing.get('account_status', '') or '').strip().lower()
        billing_status = str(billing.get('billing_status', '') or '').strip().lower()
        access_tier = str(billing.get('access_tier', '') or '').strip().lower()
        stripe_ready = bool(billing.get('stripe_ready', False))

        pro_features = [
            tr_fn('nova.billing_feature_projects'),
            tr_fn('nova.billing_feature_exports'),
            tr_fn('nova.billing_feature_account'),
        ]

        if account_status == 'admin_active' or access_tier == 'admin':
            return (
                tr_fn('nova.billing_state_admin_title'),
                tr_fn('nova.billing_state_admin_desc'),
                [],
                False,
                False,
            )
        if account_status == 'paid_active' or billing_status in ('active', 'paid'):
            return (
                tr_fn('nova.billing_state_paid_title'),
                tr_fn('nova.billing_state_paid_desc'),
                [],
                False,
                stripe_ready,
            )
        if billing_status == 'past_due':
            return (
                tr_fn('nova.billing_state_past_due_title'),
                tr_fn('nova.billing_state_past_due_desc'),
                pro_features,
                stripe_ready,
                stripe_ready,
            )
        if account_status == 'trial_active' or access_tier == 'trial' or billing_status in ('trial', 'trialing'):
            return (
                tr_fn('nova.billing_state_trial_title'),
                tr_fn('nova.billing_state_trial_desc'),
                pro_features,
                stripe_ready,
                False,
            )
        return (
            tr_fn('nova.billing_state_inactive_title'),
            tr_fn('nova.billing_state_inactive_desc'),
            pro_features,
            stripe_ready,
            stripe_ready and bool(billing.get('has_portal', False)),
        )

    with ui.column().classes('w-full max-w-2xl mx-auto gap-6 py-8'):
        is_authenticated = bool(str(getattr(state, 'current_user_email', '') or '').strip())
        _tier = str(getattr(state, 'current_access_tier', '') or '').strip().lower()
        _show_plan_cards = _tier in {'trial', 'local', 'local_beta', ''}
        billing = get_current_billing_summary()

        if is_authenticated:
            with ui.card().classes('w-full p-6 bg-[#f7f5ef] border border-gray-200'):
                ui.label(tr_fn('nova.account_page_title')).classes('text-2xl font-bold text-gray-900')
                ui.label(tr_fn('nova.account_page_desc')).classes(
                    'text-sm text-gray-600'
                )
                if bool(getattr(state, 'account_upgrade_focus', False)):
                    ui.label(tr_fn('nova.primary_action_upgrade_title')).classes('text-lg font-bold text-[#7a5d00] mt-2')
                    ui.label(tr_fn('nova.primary_action_upgrade_desc')).classes('text-sm text-[#7a5d00]')
        else:
            with ui.card().classes('w-full p-6 bg-[#fff7d6] border-2 border-[#d4a017] shadow-sm'):
                ui.label(tr_fn('nova.auth_title')).classes('text-xl font-bold mb-1')
                ui.label(tr_fn('nova.auth_desc')).classes('text-sm text-gray-600')
                ui.label(tr_fn('nova.auth_flow_hint')).classes('text-sm font-semibold text-[#7a5d00] mt-2')
                ui.separator().classes('my-3')
                ui.label(tr_fn('nova.auth_how_title')).classes('text-sm font-bold text-gray-800')
                ui.label(tr_fn('nova.auth_how_1')).classes('text-sm text-gray-700')
                ui.label(tr_fn('nova.auth_how_2')).classes('text-sm text-gray-700')
                ui.label(tr_fn('nova.auth_how_3')).classes('text-sm text-gray-700')

        def _start_checkout() -> None:
            ok, msg = build_checkout_start_message()
            if ok and str(msg or "").startswith(("http://", "https://")):
                ui.navigate.to(str(msg), new_tab=True)
                ui.notify(tr_fn('nova.billing_checkout_redirect'), type='positive', timeout=4000)
            else:
                ui.notify(msg, type='info' if ok else 'negative', timeout=5000)

        def _start_checkout_with_plan(plan_code: str) -> None:
            ok, msg = build_checkout_start_message(plan_code)
            if ok and str(msg or "").startswith(("http://", "https://")):
                ui.navigate.to(str(msg), new_tab=True)
                ui.notify(tr_fn('nova.billing_checkout_redirect'), type='positive', timeout=4000)
            else:
                ui.notify(msg, type='info' if ok else 'negative', timeout=5000)

        def _open_portal() -> None:
            ok, msg = build_customer_portal_message()
            if ok and str(msg or "").startswith(("http://", "https://")):
                ui.navigate.to(str(msg), new_tab=True)
                ui.notify(tr_fn('nova.billing_portal_redirect'), type='positive', timeout=4000)
            else:
                ui.notify(msg, type='info' if ok else 'negative', timeout=5000)

        if billing and _show_plan_cards:
            with ui.row().classes('w-full gap-4 max-md:flex-col'):
                with ui.card().classes('flex-1 p-5 bg-[#fff7d6] border-2 border-[#d4a017] shadow-sm'):
                    ui.label(tr_fn('nova.plan_weekly_title')).classes('text-base font-bold text-gray-900')
                    ui.label(tr_fn('nova.plan_weekly_desc')).classes('text-sm text-gray-600')
                    ui.button(
                        tr_fn('nova.plan_weekly_btn'),
                        on_click=lambda: _start_checkout_with_plan('pro_weekly'),
                    ).classes('w-full mt-4 bg-[#111] text-white')
                with ui.card().classes('flex-1 p-5 bg-white border-2 border-[#111] shadow-sm'):
                    ui.label(tr_fn('nova.plan_monthly_title')).classes('text-base font-bold text-gray-900')
                    ui.label(tr_fn('nova.plan_monthly_desc')).classes('text-sm text-gray-600')
                    ui.button(
                        tr_fn('nova.plan_monthly_btn'),
                        on_click=lambda: _start_checkout_with_plan('pro_monthly'),
                    ).classes('w-full mt-4 bg-[#111] text-white')

        if is_authenticated:
            with ui.card().classes('w-full p-4 bg-white border border-gray-200'):
                ui.label(tr_fn('nova.session_title')).classes('text-sm font-bold text-gray-800')
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

                def _logout() -> None:
                    ok, err = logout_current_session()
                    if ok:
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_logout_ok'), type='positive')
                        ui.navigate.to('/login')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_logout_btn'), on_click=_logout).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-3'
                )

        if billing:
            with ui.card().classes('w-full p-6 bg-[#eef6ff] border border-[#c7ddff]'):
                ui.label(tr_fn('nova.billing_title')).classes('text-lg font-bold mb-1')
                billing_title, billing_desc, pro_features, show_checkout, show_portal = _billing_state_copy(billing)
                ui.label(billing_title).classes('text-base font-bold text-slate-900')
                ui.label(billing_desc).classes('text-sm text-slate-700')
                ui.label(
                    tr_fn(
                        'nova.billing_status_fmt',
                        plan=str(billing.get('plan_code', '-') or '-'),
                        billing_status=str(billing.get('billing_status', '-') or '-'),
                        access_tier=str(billing.get('access_tier', '-') or '-'),
                    )
                ).classes('text-sm text-gray-700')
                if str(billing.get('current_period_end', '') or ''):
                    ui.label(
                        tr_fn('nova.billing_period_end', period_end=str(billing.get('current_period_end', '') or ''))
                    ).classes('text-sm text-gray-600')
                if pro_features:
                    ui.label(tr_fn('nova.billing_features_title')).classes('text-sm font-bold text-gray-800 mt-3')
                    for item in pro_features:
                        ui.label(f"- {item}").classes('text-sm text-gray-700')

                if show_checkout:
                    ui.button(tr_fn('nova.billing_checkout_btn'), on_click=_start_checkout).classes(
                        'w-full bg-white text-[#111] border border-[#111] mt-3'
                    )
                if show_portal:
                    ui.button(tr_fn('nova.billing_portal_btn'), on_click=_open_portal).classes(
                        'w-full bg-white text-[#111] border border-[#111] mt-2'
                    )

                if bool(getattr(state, 'account_upgrade_focus', False)):
                    ui.timer(0.05, lambda: ui.run_javascript('window.scrollTo({top: 0, behavior: "auto"})'), once=True)

        if not is_authenticated:
            with ui.card().classes('w-full p-6 bg-white border border-gray-200'):
                ui.label(tr_fn('nova.auth_login_title')).classes('text-lg font-bold mb-1')
                ui.label(tr_fn('nova.auth_login_desc')).classes('text-sm text-gray-600 mb-4')
                login_email = ui.input(
                    label=tr_fn('nova.auth_login_email'),
                ).props('id=account-login-email autocomplete=username').classes('w-full')
                login_email.value = str(getattr(state, 'current_user_email', '') or '')
                login_password = ui.input(
                    label=tr_fn('nova.auth_login_password'),
                    password=True,
                    password_toggle_button=True,
                ).props('id=account-login-password autocomplete=current-password').classes('w-full')

                async def _login_existing() -> None:
                    email_value = await _resolve_input_value('account-login-email', str(login_email.value or ''))
                    password_value = await _resolve_input_value('account-login-password', str(login_password.value or ''))
                    ok, err = login_user_session(
                        email_value,
                        password_value,
                    )
                    if ok:
                        state.active_tab = 'wizard'
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_login_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_login_btn'), on_click=_login_existing).classes(
                    'w-full bg-[#111] text-white mt-2'
                )

                forgot_email = ui.input(label=tr_fn('nova.auth_forgot_email')).props(
                    'id=account-forgot-email autocomplete=email'
                ).classes('w-full mt-4')

                async def _forgot_password() -> None:
                    forgot_value = await _resolve_input_value('account-forgot-email', str(forgot_email.value or ''))
                    ok, msg = build_forgot_password_message(forgot_value)
                    if ok:
                        ui.notify(msg, type='info', timeout=5000)
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=msg), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_forgot_btn'), on_click=_forgot_password).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )

            with ui.card().classes('w-full p-6 bg-white border border-gray-200'):
                ui.label(tr_fn('nova.auth_reset_title')).classes('text-lg font-bold mb-1')
                ui.label(tr_fn('nova.auth_reset_desc')).classes('text-sm text-gray-600 mb-4')
                reset_token = ui.input(label=tr_fn('nova.auth_reset_token')).classes('w-full')
                reset_password = ui.input(
                    label=tr_fn('nova.auth_reset_password'),
                    password=True,
                    password_toggle_button=True,
                ).classes('w-full')

                def _reset_password() -> None:
                    ok, msg = reset_password_with_token(
                        str(reset_token.value or ''),
                        str(reset_password.value or ''),
                    )
                    if ok:
                        ui.notify(msg, type='positive', timeout=5000)
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=msg), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_reset_btn'), on_click=_reset_password).classes(
                    'w-full bg-white text-[#111] border border-[#111] mt-2'
                )

            with ui.card().classes('w-full p-6 bg-white border border-gray-200'):
                ui.label(tr_fn('nova.auth_register_title')).classes('text-lg font-bold mb-1')
                ui.label(tr_fn('nova.auth_register_desc')).classes('text-sm text-gray-600 mb-4')
                register_name = ui.input(label=tr_fn('nova.auth_register_name')).props(
                    'id=account-register-name autocomplete=name'
                ).classes('w-full')
                register_email = ui.input(label=tr_fn('nova.auth_register_email')).props(
                    'id=account-register-email autocomplete=email'
                ).classes('w-full')
                register_password = ui.input(
                    label=tr_fn('nova.auth_register_password'),
                    password=True,
                    password_toggle_button=True,
                ).props('id=account-register-password autocomplete=new-password').classes('w-full')

                async def _register_trial() -> None:
                    register_name_value = await _resolve_input_value('account-register-name', str(register_name.value or ''))
                    register_email_value = await _resolve_input_value('account-register-email', str(register_email.value or ''))
                    register_password_value = await _resolve_input_value('account-register-password', str(register_password.value or ''))
                    ok, err = register_trial_user_session(
                        register_email_value,
                        register_name_value,
                        register_password_value,
                    )
                    if ok:
                        state.active_tab = 'wizard'
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_register_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_register_btn'), on_click=_register_trial).classes(
                    'w-full bg-[#111] text-white mt-2'
                )

            with ui.card().classes('w-full p-6 bg-[#f8fafc] border border-gray-200'):
                ui.label(tr_fn('nova.auth_local_title')).classes('text-lg font-bold mb-1')
                ui.label(tr_fn('nova.auth_local_desc')).classes('text-sm text-gray-600 mb-4')

                def _restore_local() -> None:
                    ok, err = restore_local_session_state()
                    if ok:
                        state.active_tab = 'wizard'
                        main_content_refresh()
                        ui.notify(tr_fn('nova.auth_local_ok'), type='positive')
                    else:
                        ui.notify(ERR_LOAD_PREFIX.format(err=err), type='negative', timeout=5000)

                ui.button(tr_fn('nova.auth_local_btn'), on_click=_restore_local).classes(
                    'w-full bg-white text-[#111] border border-[#111]'
                )
