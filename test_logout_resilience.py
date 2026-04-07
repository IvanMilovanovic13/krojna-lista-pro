# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl
import project_store as ps


def run_logout_resilience_check() -> tuple[bool, str]:
    original_revoke = ps.revoke_auth_session
    original_audit = ps.append_audit_log
    original_storage_getter = sl._get_user_storage
    original_init_local_session_state = sl.init_local_session_state
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_session_token = str(getattr(sl.state, "current_session_token", "") or "")
    original_session_expires_at = str(getattr(sl.state, "current_session_expires_at", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    storage: dict[str, str] = {}

    def _fake_storage():
        return storage

    def _fake_init_local_session_state() -> None:
        sl.state.current_user_id = 0
        sl.state.current_user_email = "local@offline"
        sl.state.current_access_tier = "local_beta"
        sl.state.current_session_token = ""
        sl.state.current_session_expires_at = ""

    def _raise_revoke(_session_token: str):
        raise RuntimeError("db unavailable")

    try:
        sl._get_user_storage = _fake_storage
        sl.init_local_session_state = _fake_init_local_session_state
        ps.revoke_auth_session = _raise_revoke
        ps.append_audit_log = lambda **kwargs: None

        storage["auth_session_token"] = "persisted-token"
        storage["auth_session_expires_at"] = "2099-01-01T00:00:00+00:00"
        sl.state.current_user_id = 17
        sl.state.current_user_email = "logout@example.com"
        sl.state.current_access_tier = "trial"
        sl.state.current_session_token = "persisted-token"
        sl.state.current_session_expires_at = "2099-01-01T00:00:00+00:00"

        ok, err = sl.logout_current_session()
        if not ok:
            return False, f"FAIL_logout_returned_error:{err}"
        if str(storage.get("auth_session_token", "") or "").strip():
            return False, f"FAIL_persisted_token_not_cleared:{storage}"
        if str(getattr(sl.state, "current_session_token", "") or "").strip():
            return False, f"FAIL_runtime_token_not_cleared:{sl.state.current_session_token}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_local_fallback_not_applied:{sl.state.current_user_email}"
        return True, "OK"
    finally:
        ps.revoke_auth_session = original_revoke
        ps.append_audit_log = original_audit
        sl._get_user_storage = original_storage_getter
        sl.init_local_session_state = original_init_local_session_state
        sl.state.current_user_id = original_user_id
        sl.state.current_user_email = original_user_email
        sl.state.current_session_token = original_session_token
        sl.state.current_session_expires_at = original_session_expires_at
        sl.state.current_access_tier = original_access_tier
