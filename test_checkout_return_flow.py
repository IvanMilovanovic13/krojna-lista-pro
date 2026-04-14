# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_checkout_return_flow_check() -> tuple[bool, str]:
    public_site = Path(__file__).with_name("ui_public_site.py").read_text(encoding="utf-8")
    app_py = Path(__file__).with_name("app.py").read_text(encoding="utf-8")

    required_public = [
        "def render_login_page(request: Request | None = None)",
        'request.query_params.get("checkout", "")',
        'if checkout_state == "success":',
        'elif checkout_state == "cancel":',
        'refresh_current_session_access()',
        'ui.button(_tr("nova.paid_success_continue_btn"), on_click=lambda: ui.navigate.to("/app"))',
        '_tr("public.checkout_success_title")',
        '_tr("public.checkout_cancel_title")',
    ]
    missing_public = [item for item in required_public if item not in public_site]
    if missing_public:
        return False, f"FAIL_checkout_return_public:{', '.join(missing_public)}"

    required_app = [
        "def index(request: Request) -> None:",
        "render_login_page(request)",
        "def login_page(request: Request) -> None:",
        "def account_compat_page(request: Request) -> None:",
    ]
    missing_app = [item for item in required_app if item not in app_py]
    if missing_app:
        return False, f"FAIL_checkout_return_app:{', '.join(missing_app)}"

    return True, "OK"
