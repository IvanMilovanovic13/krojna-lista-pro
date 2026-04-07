# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_session_restore_resilience_check() -> tuple[bool, str]:
    original_load_token = sl._load_persisted_session_token
    original_init_local_session_state = sl.init_local_session_state
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_session_token = str(getattr(sl.state, "current_session_token", "") or "")
    original_session_expires_at = str(getattr(sl.state, "current_session_expires_at", "") or "")

    def _fake_load_token() -> str:
        raise RuntimeError("storage unavailable")

    def _fake_init_local_session_state() -> None:
        sl.state.current_user_email = "local@offline"
        sl.state.current_access_tier = "local_beta"
        sl.state.current_session_token = ""
        sl.state.current_session_expires_at = ""

    try:
        sl._load_persisted_session_token = _fake_load_token
        sl.init_local_session_state = _fake_init_local_session_state
        sl.state.current_user_email = ""
        sl.state.current_access_tier = ""
        sl.state.current_session_token = "stale-token"
        sl.state.current_session_expires_at = "2099-01-01T00:00:00+00:00"

        sl.ensure_runtime_state_initialized(allow_local_fallback=True)
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_local_fallback_not_applied:{sl.state.current_user_email}"
        if str(getattr(sl.state, "current_access_tier", "") or "") != "local_beta":
            return False, f"FAIL_local_access_tier_not_restored:{sl.state.current_access_tier}"
        if str(getattr(sl.state, "current_session_token", "") or "").strip():
            return False, f"FAIL_session_token_not_cleared:{sl.state.current_session_token}"
        return True, "OK"
    finally:
        sl._load_persisted_session_token = original_load_token
        sl.init_local_session_state = original_init_local_session_state
        sl.state.current_user_email = original_user_email
        sl.state.current_access_tier = original_access_tier
        sl.state.current_session_token = original_session_token
        sl.state.current_session_expires_at = original_session_expires_at
