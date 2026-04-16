# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from auth_models import build_session_from_user
from project_store import UserRecord


def run_access_gate_billing_check() -> tuple[bool, str]:
    inactive_user = UserRecord(
        id=1,
        email="inactive@example.com",
        username="inactive-user",
        display_name="Inactive User",
        auth_mode="password",
        access_tier="blocked",
        status="inactive",
        email_verified=True,
        created_at="2026-03-26T10:00:00+00:00",
        updated_at="2026-03-26T10:00:00+00:00",
    )
    trial_user = UserRecord(
        id=2,
        email="trial@example.com",
        username="trial-user",
        display_name="Trial User",
        auth_mode="password",
        access_tier="trial",
        status="trial_active",
        email_verified=True,
        created_at="2026-03-26T10:00:00+00:00",
        updated_at="2026-03-26T10:00:00+00:00",
    )
    paid_user = UserRecord(
        id=3,
        email="paid@example.com",
        username="paid-user",
        display_name="Paid User",
        auth_mode="password",
        access_tier="paid",
        status="paid_active",
        email_verified=True,
        created_at="2026-03-26T10:00:00+00:00",
        updated_at="2026-03-26T10:00:00+00:00",
    )

    inactive_session = build_session_from_user(inactive_user)
    if inactive_session.can_access_app:
        return False, "FAIL_inactive_user_should_be_blocked"
    if "Aktiviraj PRO" not in str(inactive_session.gate_reason) and "Pretplata nije aktivna" not in str(inactive_session.gate_reason):
        return False, f"FAIL_inactive_gate_reason:{inactive_session.gate_reason}"

    if not build_session_from_user(trial_user).can_access_app:
        return False, "FAIL_trial_user_should_have_access"
    if not build_session_from_user(paid_user).can_access_app:
        return False, "FAIL_paid_user_should_have_access"

    access_gate = Path(__file__).with_name("ui_access_gate.py").read_text(encoding="utf-8")
    main_content = Path(__file__).with_name("ui_main_content.py").read_text(encoding="utf-8")
    i18n = Path(__file__).with_name("i18n.py").read_text(encoding="utf-8")

    required_gate = [
        "get_current_billing_summary: Callable[[], dict[str, Any] | None]",
        "build_checkout_start_message: Callable[[], tuple[bool, str]]",
        "build_customer_portal_message: Callable[[], tuple[bool, str]]",
        "tr_fn('gate.billing_title')",
        "tr_fn('gate.checkout_btn')",
        "tr_fn('gate.portal_btn')",
    ]
    missing_gate = [item for item in required_gate if item not in access_gate]
    if missing_gate:
        return False, f"FAIL_access_gate_ui:{', '.join(missing_gate)}"

    required_main = [
        "get_current_billing_summary=get_current_billing_summary",
        "build_checkout_start_message=build_checkout_start_message",
        "build_customer_portal_message=build_customer_portal_message",
    ]
    missing_main = [item for item in required_main if item not in main_content]
    if missing_main:
        return False, f"FAIL_access_gate_wiring:{', '.join(missing_main)}"

    required_i18n = [
        '"gate.checkout_btn": "Aktiviraj PRO"',
        '"gate.portal_btn": "Otvori naplatu"',
        '"gate.checkout_btn": "Activate PRO"',
        '"gate.portal_btn": "Open billing"',
    ]
    missing_i18n = [item for item in required_i18n if item not in i18n]
    if missing_i18n:
        return False, f"FAIL_access_gate_i18n:{', '.join(missing_i18n)}"

    return True, "OK"
