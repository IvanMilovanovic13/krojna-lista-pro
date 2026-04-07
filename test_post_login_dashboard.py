# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_post_login_dashboard_contract_check() -> tuple[bool, str]:
    state_logic = Path(__file__).with_name("state_logic.py").read_text(encoding="utf-8")
    nova_tab = Path(__file__).with_name("ui_nova_tab.py").read_text(encoding="utf-8")
    main_content = Path(__file__).with_name("ui_main_content.py").read_text(encoding="utf-8")

    required_state_logic = [
        'if str(getattr(state, "active_tab", "") or "").strip() in ("wizard", "nalog", ""):',
        'state.active_tab = "nova"',
        'event_type="auth.login_success"',
        'event_type="auth.register_trial"',
    ]
    missing_state_logic = [item for item in required_state_logic if item not in state_logic]
    if missing_state_logic:
        return False, f"FAIL_post_login_dashboard_state_logic:{', '.join(missing_state_logic)}"

    required_nova = [
        "is_authenticated = bool(str(getattr(state, 'current_user_email', '') or '').strip())",
        "if not is_authenticated:",
        "if is_authenticated:",
        "ui.label('krojna lista PRO')",
        "ui.label('Dashboard / Projekti')",
        "billing_title, billing_desc, show_checkout, show_portal = _dashboard_billing_copy(billing)",
        "primary_title, primary_desc, primary_btn, primary_mode = _dashboard_primary_action_copy(billing)",
        "if _show_paid_success_card(billing):",
        "tr_fn('nova.paid_success_title')",
        "ok, msg = build_checkout_start_message()",
        "ok, msg = build_customer_portal_message()",
        "ui.label(\n                            tr_fn(\n                                'nova.billing_status_fmt',",
        "tr_fn('nova.primary_action_start_title')",
        "tr_fn('nova.primary_action_upgrade_title')",
        "ui.label('Nastavi rad')",
        "tr_fn('nova.dashboard_account_btn')",
        "tr_fn('nova.auth_logout_btn')",
        "ui.button(primary_btn, on_click=_run_primary_action).classes(",
        "if autosave_info and not is_authenticated:",
        "with ui.card().classes('w-full p-6 bg-[#f8fafc] border border-gray-200'):",
        "ui.button(tr_fn('nova.user_projects_open'), on_click=_open_user_project).classes(",
        "ui.button(tr_fn('nova.recent_open'), on_click=_open_recent).classes(",
    ]
    missing_nova = [item for item in required_nova if item not in nova_tab]
    if missing_nova:
        return False, f"FAIL_post_login_dashboard_nova:{', '.join(missing_nova)}"

    required_main = [
        "render_toolbar_refresh,",
        "render_nova_panel()",
    ]
    missing_main = [item for item in required_main if item not in main_content]
    if missing_main:
        return False, f"FAIL_post_login_dashboard_main_content:{', '.join(missing_main)}"
    return True, "OK"
