# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_public_auth_autofill_check() -> tuple[bool, str]:
    path = Path(__file__).with_name("ui_public_site.py")
    text = path.read_text(encoding="utf-8")

    required = [
        'id=public-login-email autocomplete=username',
        'id=public-login-password autocomplete=current-password',
        'async def _resolve_input_value(',
        'await _resolve_input_value("public-login-email", str(login_email.value or ""))',
        'await _resolve_input_value("public-login-password", str(login_password.value or ""))',
        "document.getElementById('public-register-email')",
        "document.getElementById('public-register-password')",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_public_auth_autofill_missing:{', '.join(missing)}"
    return True, "OK"
