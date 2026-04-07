# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from export_jobs import EXPORTS_DIR, enqueue_export_job, process_export_job
from project_store import (
    count_active_export_jobs_for_user,
    create_export_job,
    create_user_record,
    get_export_job,
    init_project_store,
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


def run_export_jobs_background_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("export_jobs_background")
    created_path: Path | None = None
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="export-background@example.com",
            display_name="Export Background",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        kitchen = {
            "language": "sr",
            "wall": {"length_mm": 3000, "height_mm": 2600},
            "worktop": {"enabled": True, "material": "Granit", "thickness": 4.0, "depth_mm": 600},
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
        job = create_export_job(
            user_id=int(user.id),
            project_id=0,
            job_type="csv",
            request_payload_json=__import__("json").dumps(
                {"job_type": "csv", "lang": "sr", "project_title": "Krojna lista PRO", "kitchen": kitchen},
                ensure_ascii=False,
            ),
        )
        process_export_job(int(job.id))
        done = get_export_job(int(job.id))
        if done is None:
            return False, "FAIL_missing_export_job"
        if str(done.status) != "done":
            return False, f"FAIL_export_job_status:{done.status}"
        if not str(done.result_ref).startswith("/exports/"):
            return False, f"FAIL_export_job_result_ref:{done.result_ref}"
        created_path = EXPORTS_DIR / str(done.result_ref).split("/exports/", 1)[1]
        if not created_path.exists():
            return False, f"FAIL_export_file_missing:{created_path}"
        if created_path.stat().st_size <= 0:
            return False, f"FAIL_export_file_empty:{created_path}"
        queued_payload = __import__("json").dumps(
            {"job_type": "csv", "lang": "sr", "project_title": "Krojna lista PRO", "kitchen": kitchen},
            ensure_ascii=False,
        )
        create_export_job(
            user_id=int(user.id),
            project_id=0,
            job_type="csv",
            request_payload_json=queued_payload,
        )
        create_export_job(
            user_id=int(user.id),
            project_id=0,
            job_type="csv",
            request_payload_json=queued_payload,
        )
        active_count = count_active_export_jobs_for_user(int(user.id))
        if active_count < 2:
            return False, f"FAIL_export_active_count:{active_count}"
        try:
            enqueue_export_job(
                user_id=int(user.id),
                project_id=0,
                kitchen=kitchen,
                job_type="csv",
                lang="sr",
                project_title="Krojna lista PRO",
            )
        except RuntimeError as ex:
            if "aktivnih export zadataka" not in str(ex):
                return False, f"FAIL_export_limit_message:{ex}"
        else:
            return False, "FAIL_export_limit_not_enforced"
        return True, "OK"
    finally:
        if created_path is not None:
            try:
                if created_path.exists():
                    created_path.unlink()
            except Exception:
                pass
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
