# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from export_jobs import (
    EXPORT_WORKER_HEARTBEAT_PATH,
    enqueue_export_job,
    get_export_runtime_summary,
    run_export_worker_once,
)
from project_store import create_user_record, get_export_job, init_project_store


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


def run_export_worker_mode_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    original_worker_mode = os.environ.get("EXPORT_WORKER_MODE")
    original_poll = os.environ.get("EXPORT_WORKER_POLL_SECONDS")
    db_path = _test_db_path("export_worker_mode")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        os.environ["EXPORT_WORKER_MODE"] = "dedicated_process"
        os.environ["EXPORT_WORKER_POLL_SECONDS"] = "2"
        init_project_store()
        user = create_user_record(
            email="export-worker@example.com",
            display_name="Export Worker",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        kitchen = {
            "language": "sr",
            "wall": {"length_mm": 3000, "height_mm": 2600},
            "materials": {
                "carcass_material": "Iver 18mm",
                "carcass_thk": 18,
                "front_material": "MDF 19mm",
                "front_thk": 19,
                "back_material": "Iver 8mm",
                "back_thk": 8,
                "edge_abs_thk": 2.0,
            },
            "modules": [
                {"id": 1, "template_id": "BASE_2DOOR", "zone": "base", "x_mm": 0, "w_mm": 800, "h_mm": 720, "d_mm": 560, "label": "Donji 2V", "params": {}, "wall_key": "A", "gap_after_mm": 0},
            ],
        }
        job_id = enqueue_export_job(
            user_id=int(user.id),
            project_id=0,
            kitchen=kitchen,
            job_type="csv",
            lang="sr",
            project_title="Krojna lista PRO",
        )
        before = get_export_job(int(job_id))
        if before is None or str(before.status) != "queued":
            return False, f"FAIL_export_worker_dedicated_not_queued:{before.status if before else 'missing'}"
        processed = run_export_worker_once()
        if processed != 1:
            return False, f"FAIL_export_worker_once_processed:{processed}"
        after = get_export_job(int(job_id))
        if after is None or str(after.status) != "done":
            return False, f"FAIL_export_worker_once_status:{after.status if after else 'missing'}"
        runtime = get_export_runtime_summary()
        if runtime.get("mode") != "dedicated_process":
            return False, f"FAIL_export_worker_runtime_mode:{runtime}"
        if runtime.get("worker_alive") != "true":
            return False, f"FAIL_export_worker_runtime_alive:{runtime}"
        if not str(runtime.get("worker_heartbeat_at", "") or "").strip():
            return False, f"FAIL_export_worker_runtime_heartbeat:{runtime}"
        if runtime.get("production_ready") != "true":
            return False, f"FAIL_export_worker_runtime_ready:{runtime}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        if original_worker_mode is None:
            os.environ.pop("EXPORT_WORKER_MODE", None)
        else:
            os.environ["EXPORT_WORKER_MODE"] = original_worker_mode
        if original_poll is None:
            os.environ.pop("EXPORT_WORKER_POLL_SECONDS", None)
        else:
            os.environ["EXPORT_WORKER_POLL_SECONDS"] = original_poll
        try:
            if EXPORT_WORKER_HEARTBEAT_PATH.exists():
                EXPORT_WORKER_HEARTBEAT_PATH.unlink()
        except Exception:
            pass
        _cleanup_sqlite_family(db_path)
