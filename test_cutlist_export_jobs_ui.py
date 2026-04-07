# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_cutlist_export_jobs_ui_check() -> tuple[bool, str]:
    path = Path(__file__).with_name("ui_cutlist_tab.py")
    text = path.read_text(encoding="utf-8")
    required = [
        "enqueue_export_job",
        "get_export_job",
        "list_export_jobs_for_user",
        "_watch_export_and_download",
        "ui.navigate.to(_download_url, new_tab=True)",
        "cutlist.export_download_started",
        "cutlist.export_jobs_title",
        "cutlist.export_jobs_meta",
        "cutlist.export_job_queued",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return False, f"FAIL_cutlist_export_jobs_ui_missing:{', '.join(missing)}"
    return True, "OK"
