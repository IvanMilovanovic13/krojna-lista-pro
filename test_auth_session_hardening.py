# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from project_store import (
    cleanup_auth_artifacts,
    create_auth_session,
    create_password_reset_token,
    create_user_record,
    get_auth_session,
    get_password_reset_token,
    hash_password,
    init_project_store,
    record_login_attempt,
    use_password_reset_token,
)
from storage_backend import get_store_backend


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


def run_auth_session_hardening_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("auth_session_hardening")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()

        user = create_user_record(
            email="session-hardening@example.com",
            display_name="Session Hardening",
            password_hash=hash_password("old-password"),
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        session_a = create_auth_session(user_id=int(user.id))
        session_b = create_auth_session(user_id=int(user.id))
        reset = create_password_reset_token(email=str(user.email), expires_in_minutes=30)
        if reset is None:
            return False, "FAIL_missing_reset_token"

        updated_user = use_password_reset_token(
            reset_token=str(reset.reset_token),
            new_password_hash=hash_password("new-password"),
        )
        if updated_user is None:
            return False, "FAIL_password_reset_not_applied"

        session_a_after = get_auth_session(str(session_a.session_token))
        session_b_after = get_auth_session(str(session_b.session_token))
        reset_after = get_password_reset_token(str(reset.reset_token))
        if session_a_after is None or session_b_after is None or reset_after is None:
            return False, "FAIL_missing_auth_artifacts_after_reset"
        if str(session_a_after.status) != "revoked" or str(session_b_after.status) != "revoked":
            return False, f"FAIL_sessions_not_revoked:{session_a_after.status}/{session_b_after.status}"
        if str(reset_after.status) != "used":
            return False, f"FAIL_reset_token_not_used:{reset_after.status}"

        active_session = create_auth_session(user_id=int(user.id))
        stale_reset = create_password_reset_token(email=str(user.email), expires_in_minutes=30)
        expired_reset = create_password_reset_token(email=str(user.email), expires_in_minutes=30)
        if expired_reset is None or stale_reset is None:
            return False, "FAIL_missing_cleanup_tokens"
        stale_session = create_auth_session(user_id=int(user.id))
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=45)).replace(microsecond=0).isoformat()
        expired_timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).replace(microsecond=0).isoformat()

        record_login_attempt(email=str(user.email), success=False)

        with get_store_backend().connect() as conn:
            conn.execute(
                "UPDATE auth_sessions SET expires_at = ? WHERE session_token = ?",
                (expired_timestamp, str(active_session.session_token)),
            )
            conn.execute(
                """
                UPDATE auth_sessions
                SET status = 'revoked',
                    revoked_at = ?,
                    updated_at = ?
                WHERE session_token = ?
                """,
                (old_timestamp, old_timestamp, str(stale_session.session_token)),
            )
            conn.execute(
                "UPDATE password_reset_tokens SET expires_at = ? WHERE reset_token = ?",
                (expired_timestamp, str(expired_reset.reset_token)),
            )
            conn.execute(
                """
                UPDATE password_reset_tokens
                SET status = 'used',
                    used_at = ?,
                    created_at = ?
                WHERE reset_token = ?
                """,
                (old_timestamp, old_timestamp, str(stale_reset.reset_token)),
            )
            conn.execute(
                "UPDATE login_attempts SET attempted_at = ? WHERE email = ?",
                (old_timestamp, str(user.email)),
            )

        result = cleanup_auth_artifacts(
            keep_login_attempts_days=30,
            keep_reset_tokens_days=7,
            keep_revoked_sessions_days=30,
        )
        if int(result.get("expired_sessions", 0)) < 1:
            return False, f"FAIL_expired_sessions_count:{result}"
        if int(result.get("expired_reset_tokens", 0)) < 1:
            return False, f"FAIL_expired_reset_tokens_count:{result}"
        if int(result.get("pruned_login_attempts", 0)) < 1:
            return False, f"FAIL_pruned_login_attempts_count:{result}"
        if int(result.get("pruned_sessions", 0)) < 1:
            return False, f"FAIL_pruned_sessions_count:{result}"
        if int(result.get("pruned_reset_tokens", 0)) < 1:
            return False, f"FAIL_pruned_reset_tokens_count:{result}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
