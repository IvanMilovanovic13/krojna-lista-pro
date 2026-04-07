# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from project_store import (
    create_export_job,
    create_user_record,
    get_export_job,
    init_project_store,
    list_export_jobs_for_user,
    update_export_job_status,
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


def run_export_job_store_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("export_job_store")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="export-job@example.com",
            display_name="Export Job",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )

        job = create_export_job(
            user_id=int(user.id),
            project_id=17,
            job_type="pdf",
            request_payload_json='{"lang":"sr"}',
        )
        if str(job.status) != "queued":
            return False, f"FAIL_initial_status:{job.status}"

        running = update_export_job_status(int(job.id), status="running")
        if running is None or str(running.status) != "running" or not str(running.started_at or ""):
            return False, f"FAIL_running_transition:{running}"

        done = update_export_job_status(
            int(job.id),
            status="done",
            result_ref="exports/job_17.pdf",
        )
        if done is None:
            return False, "FAIL_done_transition_missing"
        if str(done.status) != "done":
            return False, f"FAIL_done_status:{done.status}"
        if str(done.result_ref) != "exports/job_17.pdf":
            return False, f"FAIL_done_result_ref:{done.result_ref}"
        if not str(done.finished_at or ""):
            return False, "FAIL_done_finished_at_empty"

        fetched = get_export_job(int(job.id))
        listed = list_export_jobs_for_user(int(user.id), limit=5)
        if fetched is None or int(fetched.id) != int(job.id):
            return False, "FAIL_fetch_job"
        if not listed or int(listed[0].id) != int(job.id):
            return False, f"FAIL_list_jobs:{listed}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)


def run_export_job_user_isolation_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("export_job_user_isolation")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        owner = create_user_record(
            email="export-owner@example.com",
            display_name="Export Owner",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        other = create_user_record(
            email="export-other@example.com",
            display_name="Export Other",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        job = create_export_job(
            user_id=int(owner.id),
            project_id=17,
            job_type="pdf",
            request_payload_json='{"lang":"sr"}',
        )
        owner_job = get_export_job(int(job.id), user_id=int(owner.id))
        other_job = get_export_job(int(job.id), user_id=int(other.id))
        if owner_job is None or int(owner_job.user_id) != int(owner.id):
            return False, "FAIL_owner_export_job_missing"
        if other_job is not None:
            return False, "FAIL_cross_user_export_job_visible"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
