# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_internal_auth_autofill_check() -> tuple[bool, str]:
    auth_tab = Path(__file__).with_name("ui_auth_tab.py").read_text(encoding="utf-8")
    nova_tab = Path(__file__).with_name("ui_nova_tab.py").read_text(encoding="utf-8")

    required_auth = [
        "async def _resolve_input_value(",
        "id=account-login-email autocomplete=username",
        "id=account-login-password autocomplete=current-password",
        "await _resolve_input_value('account-login-email', str(login_email.value or ''))",
        "await _resolve_input_value('account-login-password', str(login_password.value or ''))",
        "id=account-register-email autocomplete=email",
    ]
    missing_auth = [item for item in required_auth if item not in auth_tab]
    if missing_auth:
        return False, f"FAIL_internal_auth_autofill_auth_tab:{', '.join(missing_auth)}"

    required_nova = [
        "async def _resolve_input_value(",
        "id=nova-login-email autocomplete=username",
        "id=nova-login-password autocomplete=current-password",
        "await _resolve_input_value('nova-login-email', str(login_email.value or ''))",
        "await _resolve_input_value('nova-login-password', str(login_password.value or ''))",
        "id=nova-register-email autocomplete=email",
    ]
    missing_nova = [item for item in required_nova if item not in nova_tab]
    if missing_nova:
        return False, f"FAIL_internal_auth_autofill_nova_tab:{', '.join(missing_nova)}"

    return True, "OK"
