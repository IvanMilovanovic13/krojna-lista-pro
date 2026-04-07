# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_session_refresh_resilience_check() -> tuple[bool, str]:
    original_init_local_session_state = sl.init_local_session_state
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_subscription_status = str(getattr(sl.state, "current_subscription_status", "") or "")
    original_can_access = bool(getattr(sl.state, "current_can_access_app", True))
    original_gate_reason = str(getattr(sl.state, "current_gate_reason", "") or "")
    original_project_id = int(getattr(sl.state, "current_project_id", 0) or 0)
    original_project_name = str(getattr(sl.state, "current_project_name", "") or "")
    original_project_source = str(getattr(sl.state, "current_project_source", "") or "")
    try:
        def _fake_init_local_session_state() -> None:
            sl.state.current_user_id = 0
            sl.state.current_user_email = "local@offline"
            sl.state.current_access_tier = "local_beta"
            sl.state.current_subscription_status = "local_active"
            sl.state.current_can_access_app = True
            sl.state.current_gate_reason = ""
            sl.state.current_project_id = 0
            sl.state.current_project_name = ""
            sl.state.current_project_source = ""

        sl.init_local_session_state = _fake_init_local_session_state
        sl.state.current_user_id = 99
        sl.state.current_user_email = "stale@example.com"
        sl.state.current_access_tier = "paid"
        sl.state.current_subscription_status = "paid_active"
        sl.state.current_can_access_app = True
        sl.state.current_gate_reason = ""
        sl.state.current_project_id = 81
        sl.state.current_project_name = "Stale Session Project"
        sl.state.current_project_source = "store"

        import project_store
        original_get_user_by_email = project_store.get_user_by_email
        project_store.get_user_by_email = lambda _email: (_ for _ in ()).throw(RuntimeError("db unavailable"))
        try:
            sl.refresh_current_session_access()
        finally:
            project_store.get_user_by_email = original_get_user_by_email

        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_local_fallback_not_applied:{sl.state.current_user_email}"
        if str(getattr(sl.state, "current_access_tier", "") or "") != "local_beta":
            return False, f"FAIL_access_tier_not_reset:{sl.state.current_access_tier}"
        if int(getattr(sl.state, "current_project_id", 0) or 0) != 0:
            return False, f"FAIL_project_binding_not_cleared:{sl.state.current_project_id}"
        return True, "OK"
    finally:
        sl.init_local_session_state = original_init_local_session_state
        sl.state.current_user_id = original_user_id
        sl.state.current_user_email = original_user_email
        sl.state.current_access_tier = original_access_tier
        sl.state.current_subscription_status = original_subscription_status
        sl.state.current_can_access_app = original_can_access
        sl.state.current_gate_reason = original_gate_reason
        sl.state.current_project_id = original_project_id
        sl.state.current_project_name = original_project_name
        sl.state.current_project_source = original_project_source
