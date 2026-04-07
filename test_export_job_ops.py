# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from project_store import (
    cleanup_export_jobs,
    create_export_job,
    create_user_record,
    get_export_job_summary,
    init_project_store,
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


def run_export_job_ops_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("export_job_ops")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="export-ops@example.com",
            display_name="Export Ops",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        queued = create_export_job(user_id=int(user.id), project_id=0, job_type="pdf", request_payload_json="{}")
        running = create_export_job(user_id=int(user.id), project_id=0, job_type="excel", request_payload_json="{}")
        done = create_export_job(user_id=int(user.id), project_id=0, job_type="csv", request_payload_json="{}")
        failed = create_export_job(user_id=int(user.id), project_id=0, job_type="csv", request_payload_json="{}")
        update_export_job_status(int(running.id), status="running")
        update_export_job_status(int(done.id), status="done")
        update_export_job_status(int(failed.id), status="failed", error_message="boom")

        summary = get_export_job_summary()
        expected = {
            "total": 4,
            "queued": 1,
            "running": 1,
            "done": 1,
            "failed": 1,
        }
        for key, value in expected.items():
            if int(summary.get(key, -1)) != value:
                return False, f"FAIL_export_job_summary_{key}:{summary.get(key)}"

        cleanup = cleanup_export_jobs(keep_done_days=1, keep_failed_days=1, keep_canceled_days=1)
        if int(cleanup.get("pruned_export_jobs", -1)) != 0:
            return False, f"FAIL_export_job_cleanup_pruned:{cleanup}"
        if int(cleanup.get("remaining_export_jobs", -1)) != 4:
            return False, f"FAIL_export_job_cleanup_remaining:{cleanup}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
