# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_auth_tab_wiring_check() -> tuple[bool, str]:
    path = Path(__file__).with_name("ui_main_content.py")
    text = path.read_text(encoding="utf-8")
    required = [
        'elif state.active_tab == "nalog":',
        'render_auth_tab(',
        'reset_password_with_token=reset_password_with_token',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_auth_tab_wiring_missing:{', '.join(missing)}"
    return True, "OK"
