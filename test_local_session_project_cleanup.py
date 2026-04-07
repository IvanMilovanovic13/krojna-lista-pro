# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_local_session_project_cleanup_check() -> tuple[bool, str]:
    original_ensure_local_session = None
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_session_token = str(getattr(sl.state, "current_session_token", "") or "")
    original_session_expires_at = str(getattr(sl.state, "current_session_expires_at", "") or "")
    original_project_id = int(getattr(sl.state, "current_project_id", 0) or 0)
    original_project_name = str(getattr(sl.state, "current_project_name", "") or "")
    original_project_source = str(getattr(sl.state, "current_project_source", "") or "")
    try:
        import auth_models

        original_ensure_local_session = auth_models.ensure_local_session

        class _FakeUser:
            user_id = 0
            email = "local@offline"
            auth_mode = "local"
            access_tier = "local_beta"
            subscription_status = "local_active"
            display_name = "Local User"

        class _FakeSession:
            user = _FakeUser()
            can_access_app = True
            gate_reason = ""

        auth_models.ensure_local_session = lambda: _FakeSession()

        sl.state.current_user_id = 17
        sl.state.current_user_email = "paid@example.com"
        sl.state.current_access_tier = "paid"
        sl.state.current_session_token = "persisted-token"
        sl.state.current_session_expires_at = "2099-01-01T00:00:00+00:00"
        sl.state.current_project_id = 321
        sl.state.current_project_name = "Private Store Project"
        sl.state.current_project_source = "local_recent"

        sl.init_local_session_state()

        if int(getattr(sl.state, "current_project_id", 0) or 0) != 0:
            return False, f"FAIL_project_id_not_cleared:{sl.state.current_project_id}"
        if str(getattr(sl.state, "current_project_name", "") or ""):
            return False, f"FAIL_project_name_not_cleared:{sl.state.current_project_name}"
        if str(getattr(sl.state, "current_project_source", "") or ""):
            return False, f"FAIL_project_source_not_cleared:{sl.state.current_project_source}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_local_user_not_restored:{sl.state.current_user_email}"
        return True, "OK"
    finally:
        if original_ensure_local_session is not None:
            import auth_models
            auth_models.ensure_local_session = original_ensure_local_session
        sl.state.current_user_id = original_user_id
        sl.state.current_user_email = original_user_email
        sl.state.current_access_tier = original_access_tier
        sl.state.current_session_token = original_session_token
        sl.state.current_session_expires_at = original_session_expires_at
        sl.state.current_project_id = original_project_id
        sl.state.current_project_name = original_project_name
        sl.state.current_project_source = original_project_source
