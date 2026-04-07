# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import state_logic as sl
from project_store import (
    create_user_record,
    get_user_autosave_project,
    init_project_store,
    list_projects_for_user_by_source,
    save_payload_from_bytes,
    touch_project_opened,
)


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


def run_project_store_recent_autosave_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("project_store_recent_autosave")
    original_kitchen = None
    original_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="store-recent@example.com",
            display_name="Store Recent",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        original_kitchen = sl.state.kitchen
        sl.state.kitchen = sl._default_kitchen()
        sl.state.current_user_email = str(user.email)
        sl.state.current_user_id = int(user.id)

        recent_ref = sl.save_local_recent_project(label="Recent Snapshot")
        autosave_ref = sl.write_autosave_snapshot(reason="test")
        recent = list_projects_for_user_by_source(int(user.id), source="local_recent", limit=5)
        autosave = get_user_autosave_project(int(user.id))
        autosave_info = sl.get_autosave_info()
        recent_items = sl.list_recent_projects()

        if not str(recent_ref).startswith("store://"):
            return False, f"FAIL_recent_not_store_backed:{recent_ref}"
        if not str(autosave_ref).startswith("store://"):
            return False, f"FAIL_autosave_not_store_backed:{autosave_ref}"
        if not recent:
            return False, "FAIL_missing_recent_store_project"
        if autosave is None:
            return False, "FAIL_missing_autosave_store_project"
        if autosave_info is None or not str(autosave_info.get("path", "")).startswith("store://"):
            return False, f"FAIL_autosave_info_not_store_backed:{autosave_info}"
        if not recent_items or not int(recent_items[0].get("store_project_id", 0) or 0):
            return False, f"FAIL_recent_items_not_store_backed:{recent_items}"
        return True, "OK"
    finally:
        if original_kitchen is not None:
            sl.state.kitchen = original_kitchen
        sl.state.current_user_email = original_email
        sl.state.current_user_id = original_user_id
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)


def run_project_store_user_isolation_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("project_store_user_isolation")
    original_kitchen = None
    original_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_project_id = int(getattr(sl.state, "current_project_id", 0) or 0)
    original_project_name = str(getattr(sl.state, "current_project_name", "") or "")
    original_project_source = str(getattr(sl.state, "current_project_source", "") or "")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        owner = create_user_record(
            email="owner-isolation@example.com",
            display_name="Owner Isolation",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        other = create_user_record(
            email="other-isolation@example.com",
            display_name="Other Isolation",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        original_kitchen = sl.state.kitchen
        sl.state.kitchen = sl._default_kitchen()
        sl.state.current_user_email = str(owner.email)
        sl.state.current_user_id = int(owner.id)
        project_ref = sl.save_local_recent_project(label="Owner Only Project")
        if not str(project_ref).startswith("store://"):
            return False, f"FAIL_owner_project_not_store_backed:{project_ref}"
        project_id = int(str(project_ref).split("store://", 1)[-1] or 0)
        if project_id <= 0:
            return False, f"FAIL_invalid_project_ref:{project_ref}"

        sl.state.current_user_email = str(other.email)
        sl.state.current_user_id = int(other.id)
        ok, err = sl.load_project_from_store(project_id)
        if ok:
            return False, "FAIL_cross_user_project_load_allowed"
        if "ne pripada aktivnom korisniku" not in str(err):
            return False, f"FAIL_unexpected_cross_user_error:{err}"
        return True, "OK"
    finally:
        if original_kitchen is not None:
            sl.state.kitchen = original_kitchen
        sl.state.current_user_email = original_email
        sl.state.current_user_id = original_user_id
        sl.state.current_project_id = original_project_id
        sl.state.current_project_name = original_project_name
        sl.state.current_project_source = original_project_source
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)


def run_project_touch_user_isolation_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("project_touch_user_isolation")
    original_kitchen = None
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        owner = create_user_record(
            email="touch-owner@example.com",
            display_name="Touch Owner",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        other = create_user_record(
            email="touch-other@example.com",
            display_name="Touch Other",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        original_kitchen = sl.state.kitchen
        sl.state.kitchen = sl._default_kitchen()
        record = save_payload_from_bytes(
            user_id=int(owner.id),
            name="Touch Guard Project",
            payload_bytes=sl.save_project_json(),
            source="local_recent",
            is_demo=False,
            is_autosave=False,
        )
        other_touch = touch_project_opened(int(record.id), user_id=int(other.id))
        owner_touch = touch_project_opened(int(record.id), user_id=int(owner.id))
        if other_touch:
            return False, "FAIL_cross_user_touch_allowed"
        if not owner_touch:
            return False, "FAIL_owner_touch_blocked"
        return True, "OK"
    finally:
        if original_kitchen is not None:
            sl.state.kitchen = original_kitchen
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
