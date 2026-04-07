# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_billing_state_ux_check() -> tuple[bool, str]:
    auth_tab = Path(__file__).with_name("ui_auth_tab.py").read_text(encoding="utf-8")
    i18n = Path(__file__).with_name("i18n.py").read_text(encoding="utf-8")

    required_auth = [
        "def _billing_state_copy(billing: dict[str, Any])",
        "nova.billing_state_trial_title",
        "nova.billing_state_paid_title",
        "nova.billing_state_past_due_title",
        "nova.billing_state_inactive_title",
        "nova.billing_state_admin_title",
        "nova.billing_features_title",
        "if show_checkout:",
        "if show_portal:",
    ]
    missing_auth = [item for item in required_auth if item not in auth_tab]
    if missing_auth:
        return False, f"FAIL_billing_state_ux_auth:{', '.join(missing_auth)}"

    required_i18n = [
        '"nova.billing_state_trial_title": "Trenutno si na probnom pristupu."',
        '"nova.billing_state_paid_title": "Tvoj PRO pristup je aktivan."',
        '"nova.billing_state_past_due_title": "Naplata zahteva paznju."',
        '"nova.billing_state_inactive_title": "Pretplata nije aktivna."',
        '"nova.billing_state_admin_title": "Admin pristup je aktivan."',
        '"nova.billing_state_trial_title": "You are currently on trial access."',
        '"nova.billing_state_paid_title": "Your PRO access is active."',
        '"nova.billing_state_past_due_title": "Billing needs attention."',
        '"nova.billing_state_inactive_title": "The subscription is not active."',
        '"nova.billing_state_admin_title": "Admin access is active."',
    ]
    missing_i18n = [item for item in required_i18n if item not in i18n]
    if missing_i18n:
        return False, f"FAIL_billing_state_ux_i18n:{', '.join(missing_i18n)}"

    return True, "OK"
