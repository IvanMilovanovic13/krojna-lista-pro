# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_nova_tab_wiring_check() -> tuple[bool, str]:
    path = Path(__file__).with_name("ui_nova_tab.py")
    text = path.read_text(encoding="utf-8")
    required = [
        "render_toolbar_refresh: Callable[[], None]",
        "logout_current_session: Callable[[], tuple[bool, str]]",
        "reset_password_with_token: Callable[[str, str], tuple[bool, str]]",
        "get_current_billing_summary: Callable[[], dict[str, Any] | None]",
        "build_checkout_start_message: Callable[[], tuple[bool, str]]",
        "build_customer_portal_message: Callable[[], tuple[bool, str]]",
        "render_toolbar_refresh()",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_nova_tab_wiring_missing:{', '.join(missing)}"
    return True, "OK"
