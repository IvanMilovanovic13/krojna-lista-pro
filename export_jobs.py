# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from app_config import DATA_DIR, get_app_config
from cutlist import build_cutlist_pdf_bytes, generate_cutlist, generate_cutlist_csv, generate_cutlist_excel
from project_store import (
    expire_stale_export_jobs_for_user,
    claim_next_export_job,
    count_active_export_jobs_for_user,
    create_export_job,
    get_export_job,
    update_export_job_status,
)


_LOG = logging.getLogger(__name__)
_EXPORT_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="export-job")
MAX_ACTIVE_EXPORT_JOBS_PER_USER = 2
STALE_QUEUED_EXPORT_MINUTES = 15
STALE_RUNNING_EXPORT_MINUTES = 30
EXPORTS_DIR = DATA_DIR / "exports"
EXPORT_WORKER_HEARTBEAT_PATH = EXPORTS_DIR / "worker_heartbeat.json"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _touch_export_worker_heartbeat() -> None:
    payload = {
        "heartbeat_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        EXPORT_WORKER_HEARTBEAT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _read_export_worker_heartbeat() -> tuple[str, bool]:
    try:
        if not EXPORT_WORKER_HEARTBEAT_PATH.exists():
            return "", False
        raw = json.loads(EXPORT_WORKER_HEARTBEAT_PATH.read_text(encoding="utf-8"))
        heartbeat_at = str((raw or {}).get("heartbeat_at", "") or "").strip()
        if not heartbeat_at:
            return "", False
        dt = datetime.fromisoformat(heartbeat_at)
        is_alive = dt >= (datetime.now() - timedelta(minutes=2))
        return heartbeat_at, bool(is_alive)
    except Exception:
        return "", False


def get_export_runtime_summary() -> dict[str, str]:
    cfg = get_app_config()
    max_workers = getattr(_EXPORT_EXECUTOR, "_max_workers", 0)
    mode = "dedicated_process" if str(cfg.export_worker_mode or "").strip().lower() == "dedicated_process" else "in_process_executor"
    heartbeat_at, worker_alive = _read_export_worker_heartbeat()
    production_ready = "true" if mode == "dedicated_process" and worker_alive else "false"
    note = (
        "Export jobovi se queue-uju u bazi i obradjuje ih poseban worker proces."
        if mode == "dedicated_process" and worker_alive
        else "Dedicated export worker mode je podeseno, ali heartbeat nije aktivan."
             if mode == "dedicated_process"
        else "Background export radi u app procesu preko ThreadPoolExecutor sloja. "
             "Dobro je za beta i manji multi-user rad, ali finalni production scale trazi izdvojen worker servis."
    )
    return {
        "mode": mode,
        "max_workers": str(int(max_workers or 0)),
        "max_active_jobs_per_user": str(int(MAX_ACTIVE_EXPORT_JOBS_PER_USER)),
        "poll_seconds": str(int(cfg.export_worker_poll_seconds or 0)),
        "exports_dir": str(EXPORTS_DIR),
        "worker_heartbeat_at": heartbeat_at,
        "worker_alive": "true" if worker_alive else "false",
        "production_ready": production_ready,
        "note": note,
    }


def enqueue_export_job(
    *,
    user_id: int,
    project_id: int,
    kitchen: dict[str, Any],
    job_type: str,
    lang: str = "sr",
    project_title: str = "Krojna lista PRO",
) -> int:
    cfg = get_app_config()
    expire_stale_export_jobs_for_user(
        int(user_id),
        queued_timeout_minutes=int(STALE_QUEUED_EXPORT_MINUTES),
        running_timeout_minutes=int(STALE_RUNNING_EXPORT_MINUTES),
    )
    active_jobs = count_active_export_jobs_for_user(int(user_id))
    if active_jobs >= int(MAX_ACTIVE_EXPORT_JOBS_PER_USER):
        raise RuntimeError(
            "Vec imas previse aktivnih export zadataka. "
            "Sacekaj da se trenutni eksporti zavrse pa pokusaj ponovo."
        )
    payload = {
        "job_type": str(job_type or "").strip().lower(),
        "lang": str(lang or "sr").strip().lower(),
        "project_title": str(project_title or "Krojna lista PRO"),
        "kitchen": kitchen,
    }
    job = create_export_job(
        user_id=int(user_id),
        project_id=int(project_id or 0),
        job_type=str(job_type or "").strip().lower(),
        request_payload_json=json.dumps(payload, ensure_ascii=False),
    )
    if str(cfg.export_worker_mode or "").strip().lower() == "dedicated_process":
        return int(job.id)
    _EXPORT_EXECUTOR.submit(process_export_job, int(job.id))
    return int(job.id)


def process_export_job(job_id: int, *, already_claimed: bool = False) -> None:
    job = get_export_job(int(job_id))
    if job is None:
        raise RuntimeError(f"Export job {job_id} nije pronađen.")

    if not already_claimed:
        update_export_job_status(int(job.id), status="running")
    try:
        payload = json.loads(str(job.request_payload_json or "{}"))
        kitchen = payload.get("kitchen", {}) if isinstance(payload, dict) else {}
        lang = str((payload or {}).get("lang", "sr") or "sr").strip().lower()
        project_title = str((payload or {}).get("project_title", "Krojna lista PRO") or "Krojna lista PRO")
        job_type = str((payload or {}).get("job_type", job.job_type) or job.job_type).strip().lower()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_job_{int(job.id)}_{timestamp}.{_ext_for_job_type(job_type)}"
        job_dir = EXPORTS_DIR / str(int(job.id))
        job_dir.mkdir(parents=True, exist_ok=True)
        out_path = job_dir / filename
        file_bytes = _build_job_bytes(job_type=job_type, kitchen=kitchen, lang=lang, project_title=project_title)
        out_path.write_bytes(file_bytes)
        update_export_job_status(
            int(job.id),
            status="done",
            result_ref=f"/exports/{int(job.id)}/{filename}",
        )
    except Exception as ex:
        _LOG.exception("Export job failed id=%s: %s", job_id, ex)
        update_export_job_status(int(job.id), status="failed", error_message=str(ex))


def _build_job_bytes(*, job_type: str, kitchen: dict[str, Any], lang: str, project_title: str) -> bytes:
    clean_type = str(job_type or "").strip().lower()
    if clean_type == "pdf":
        sections = generate_cutlist(kitchen)
        return build_cutlist_pdf_bytes(kitchen, sections, project_title=project_title, lang=lang)
    if clean_type == "excel":
        return generate_cutlist_excel(kitchen, title=project_title, lang=lang)
    if clean_type == "csv":
        return generate_cutlist_csv(kitchen, lang=lang)
    raise RuntimeError(f"Nepodrzan export job type: {clean_type}")


def _ext_for_job_type(job_type: str) -> str:
    clean_type = str(job_type or "").strip().lower()
    if clean_type == "pdf":
        return "pdf"
    if clean_type == "excel":
        return "xlsx"
    if clean_type == "csv":
        return "csv"
    return "bin"


def run_export_worker_once() -> int:
    _touch_export_worker_heartbeat()
    job = claim_next_export_job()
    if job is None:
        return 0
    process_export_job(int(job.id), already_claimed=True)
    return 1


def run_export_worker_loop(*, poll_seconds: int | None = None, max_loops: int | None = None) -> int:
    cfg = get_app_config()
    sleep_seconds = max(1, int(poll_seconds or cfg.export_worker_poll_seconds or 2))
    processed = 0
    loops = 0
    while True:
        _touch_export_worker_heartbeat()
        processed += run_export_worker_once()
        loops += 1
        if max_loops is not None and loops >= int(max_loops):
            break
        time.sleep(float(sleep_seconds))
    return processed
