# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

import project_store as ps
from export_jobs import enqueue_export_job
from project_store import create_export_job, create_user_record, get_export_job, init_project_store, update_export_job_status


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


def run_export_job_stale_cleanup_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("export_job_stale_cleanup")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="export-stale@example.com",
            display_name="Export Stale",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        kitchen = {
            "language": "sr",
            "wall": {"length_mm": 3000, "height_mm": 2600},
            "modules": [
                {"id": 1, "template_id": "BASE_2DOOR", "zone": "base", "x_mm": 0, "w_mm": 800, "h_mm": 720, "d_mm": 560, "label": "Donji 2V", "params": {}, "wall_key": "A", "gap_after_mm": 0},
            ],
        }
        payload = json.dumps(
            {"job_type": "csv", "lang": "sr", "project_title": "Krojna lista PRO", "kitchen": kitchen},
            ensure_ascii=False,
        )

        queued = create_export_job(user_id=int(user.id), project_id=0, job_type="csv", request_payload_json=payload)
        running = create_export_job(user_id=int(user.id), project_id=0, job_type="csv", request_payload_json=payload)
        update_export_job_status(int(running.id), status="running")

        with ps._connect() as conn:
            conn.execute(
                """
                UPDATE export_jobs
                SET updated_at = ?, created_at = ?, started_at = CASE WHEN id = ? THEN ? ELSE started_at END
                WHERE id IN (?, ?)
                """,
                (
                    "2026-01-01T00:00:00+00:00",
                    "2026-01-01T00:00:00+00:00",
                    int(running.id),
                    "2026-01-01T00:00:00+00:00",
                    int(queued.id),
                    int(running.id),
                ),
            )

        job_id = enqueue_export_job(
            user_id=int(user.id),
            project_id=0,
            kitchen=kitchen,
            job_type="csv",
            lang="sr",
            project_title="Krojna lista PRO",
        )
        if int(job_id) <= 0:
            return False, f"FAIL_enqueue_after_stale_cleanup:{job_id}"

        queued_after = get_export_job(int(queued.id))
        running_after = get_export_job(int(running.id))
        if queued_after is None or str(queued_after.status) != "failed" or "predugo ostao na cekanju" not in str(queued_after.error_message):
            return False, f"FAIL_stale_queued_not_failed:{queued_after}"
        if running_after is None or str(running_after.status) != "failed" or "predugo ostao u obradi" not in str(running_after.error_message):
            return False, f"FAIL_stale_running_not_failed:{running_after}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
