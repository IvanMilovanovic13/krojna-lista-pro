# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import state_logic as sl
from project_store import append_audit_log, create_user_record, init_project_store


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


def run_audit_visibility_scope_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    db_path = _test_db_path("audit_visibility_scope")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        owner = create_user_record(
            email="audit-owner@example.com",
            display_name="Audit Owner",
            password_hash="hash",
            auth_mode="password",
            access_tier="local_beta",
            status="trial_active",
        )
        other = create_user_record(
            email="audit-other@example.com",
            display_name="Audit Other",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        append_audit_log(
            user_id=int(owner.id),
            event_type="owner_event",
            status="info",
            detail="owner detail",
        )
        append_audit_log(
            user_id=int(other.id),
            event_type="other_event",
            status="info",
            detail="other detail",
        )

        sl.state.current_user_id = int(owner.id)
        sl.state.current_access_tier = "local_beta"
        local_beta_rows = sl.get_visible_audit_logs(limit=10)
        local_beta_events = {str(row.get("event_type", "")) for row in local_beta_rows}
        if "owner_event" not in local_beta_events:
            return False, f"FAIL_local_beta_missing_own_event:{local_beta_rows}"
        if "other_event" in local_beta_events:
            return False, f"FAIL_local_beta_saw_other_event:{local_beta_rows}"

        sl.state.current_access_tier = "admin"
        admin_rows = sl.get_visible_audit_logs(limit=10)
        admin_events = {str(row.get("event_type", "")) for row in admin_rows}
        if "owner_event" not in admin_events or "other_event" not in admin_events:
            return False, f"FAIL_admin_missing_global_events:{admin_rows}"
        return True, "OK"
    finally:
        sl.state.current_user_id = original_user_id
        sl.state.current_access_tier = original_access_tier
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
