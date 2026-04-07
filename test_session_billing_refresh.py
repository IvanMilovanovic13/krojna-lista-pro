# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_session_billing_refresh_check() -> tuple[bool, str]:
    state_logic = Path(__file__).with_name("state_logic.py").read_text(encoding="utf-8")
    app_py = Path(__file__).with_name("app.py").read_text(encoding="utf-8")

    required_state_logic = [
        "def refresh_current_session_access() -> None:",
        "from auth_models import build_session_from_user",
        "from project_store import get_user_by_email",
        "_apply_session_state(build_session_from_user(user))",
    ]
    missing_state_logic = [item for item in required_state_logic if item not in state_logic]
    if missing_state_logic:
        return False, f"FAIL_session_billing_refresh_state_logic:{', '.join(missing_state_logic)}"

    required_app = [
        "from state_logic import ensure_runtime_state_initialized, refresh_current_session_access, seed_demo_project_store, state",
        "refresh_current_session_access()",
    ]
    missing_app = [item for item in required_app if item not in app_py]
    if missing_app:
        return False, f"FAIL_session_billing_refresh_app:{', '.join(missing_app)}"

    return True, "OK"
