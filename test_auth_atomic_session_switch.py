# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import state_logic as sl
import project_store as ps


def _test_db_path(prefix: str) -> Path:
    data_dir = Path(__file__).with_name("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / f"{prefix}_{uuid4().hex}.db"


def _cleanup_sqlite_family(db_path: Path) -> None:
    for suffix in ("", "-wal", "-shm"):
        target = Path(f"{db_path}{suffix}")
        try:
            if target.exists():
                target.unlink()
        except Exception:
            pass


def run_auth_atomic_session_switch_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    original_create_auth_session = ps.create_auth_session
    original_storage_getter = sl._get_user_storage
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_user_display = str(getattr(sl.state, "current_user_display", "") or "")
    original_auth_mode = str(getattr(sl.state, "current_auth_mode", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_subscription_status = str(getattr(sl.state, "current_subscription_status", "") or "")
    original_gate_reason = str(getattr(sl.state, "current_gate_reason", "") or "")
    original_can_access = bool(getattr(sl.state, "current_can_access_app", True))
    original_session_token = str(getattr(sl.state, "current_session_token", "") or "")
    original_session_expires_at = str(getattr(sl.state, "current_session_expires_at", "") or "")
    db_path = _test_db_path("auth_atomic_session_switch")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        ps.init_project_store()
        user = ps.create_user_record(
            email="atomic-login@example.com",
            username="atomic-login",
            display_name="Atomic Login",
            password_hash=ps.hash_password("secret123"),
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
            email_verified=True,
        )

        sl.state.current_user_id = 777
        sl.state.current_user_email = "local@offline"
        sl.state.current_user_display = "Local User"
        sl.state.current_auth_mode = "local"
        sl.state.current_access_tier = "local_beta"
        sl.state.current_subscription_status = "local_active"
        sl.state.current_gate_reason = ""
        sl.state.current_can_access_app = True
        sl.state.current_session_token = ""
        sl.state.current_session_expires_at = ""

        def _raise_create_auth_session(*args, **kwargs):
            raise RuntimeError("session storage unavailable")

        ps.create_auth_session = _raise_create_auth_session
        ok, err = sl.login_user_session("atomic-login@example.com", "secret123")
        if ok:
            return False, "FAIL_login_unexpected_success"
        if "session storage unavailable" not in str(err):
            return False, f"FAIL_unexpected_login_error:{err}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_login_state_switched_without_session:{sl.state.current_user_email}"
        if str(getattr(sl.state, "current_auth_mode", "") or "") != "local":
            return False, f"FAIL_login_auth_mode_switched_without_session:{sl.state.current_auth_mode}"
        if str(getattr(sl.state, "current_session_token", "") or "").strip():
            return False, f"FAIL_login_session_token_present:{sl.state.current_session_token}"

        ps.create_auth_session = _raise_create_auth_session
        ok_reg, err_reg = sl.register_trial_user_session(
            "atomic-register@example.com",
            "Atomic Register",
            "secret123",
            "atomic-register",
        )
        if not ok_reg:
            return False, f"FAIL_register_unexpected_error:{err_reg}"
        if "Potvrdi email" not in str(err_reg):
            return False, f"FAIL_register_missing_verification_copy:{err_reg}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_register_state_switched_without_session:{sl.state.current_user_email}"
        if str(getattr(sl.state, "current_auth_mode", "") or "") != "local":
            return False, f"FAIL_register_auth_mode_switched_without_session:{sl.state.current_auth_mode}"

        class _BrokenStorage(dict):
            def __setitem__(self, key, value):
                raise RuntimeError("persist unavailable")

        sl._get_user_storage = lambda: _BrokenStorage()
        ps.create_auth_session = original_create_auth_session

        ok_persist, err_persist = sl.login_user_session("atomic-login@example.com", "secret123")
        if ok_persist:
            return False, "FAIL_login_persist_unexpected_success"
        if "persist unavailable" not in str(err_persist):
            return False, f"FAIL_unexpected_persist_error:{err_persist}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "local@offline":
            return False, f"FAIL_persist_failure_state_switched:{sl.state.current_user_email}"
        with ps.get_store_backend().connect() as conn:
            row = conn.execute(
                "SELECT session_token FROM auth_sessions ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is not None:
            latest_token = str(row["session_token"] or "")
            latest_record = ps.get_auth_session(latest_token)
            if latest_record is not None and str(latest_record.status or "") != "revoked":
                return False, f"FAIL_persist_failure_session_not_revoked:{latest_record.status}"
        return True, "OK"
    finally:
        ps.create_auth_session = original_create_auth_session
        sl._get_user_storage = original_storage_getter
        sl.state.current_user_id = original_user_id
        sl.state.current_user_email = original_user_email
        sl.state.current_user_display = original_user_display
        sl.state.current_auth_mode = original_auth_mode
        sl.state.current_access_tier = original_access_tier
        sl.state.current_subscription_status = original_subscription_status
        sl.state.current_gate_reason = original_gate_reason
        sl.state.current_can_access_app = original_can_access
        sl.state.current_session_token = original_session_token
        sl.state.current_session_expires_at = original_session_expires_at
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
