# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_protected_export_download_contract_check() -> tuple[bool, str]:
    app_text = Path(__file__).with_name("app.py").read_text(encoding="utf-8")
    export_jobs_text = Path(__file__).with_name("export_jobs.py").read_text(encoding="utf-8")
    cutlist_tab_text = Path(__file__).with_name("ui_cutlist_tab.py").read_text(encoding="utf-8")

    required_app = [
        "@app.get('/exports/{job_id}/{filename}')",
        "restore_session_from_token(clean_token)",
        'detail="paid_access_required"',
        "get_export_job(int(job_id), user_id=int(session.user.user_id))",
        'expected_ref = f"/exports/{int(job.id)}/{safe_name}"',
        "return FileResponse(",
    ]
    missing_app = [item for item in required_app if item not in app_text]
    if missing_app:
        return False, f"FAIL_protected_export_app:{', '.join(missing_app)}"

    if "app.add_static_files('/exports'" in app_text:
        return False, "FAIL_exports_still_public_static"

    required_jobs = [
        'result_ref=f"/exports/{int(job.id)}/{filename}"',
    ]
    missing_jobs = [item for item in required_jobs if item not in export_jobs_text]
    if missing_jobs:
        return False, f"FAIL_protected_export_jobs:{', '.join(missing_jobs)}"

    required_cutlist = [
        "_session_token = str(getattr(state, 'current_session_token', '') or '').strip()",
        "_download_url = f'{_result_ref}{_sep}token={_session_token}'",
        "target=str(_row.get('download_url', '') or _row['result_ref'])",
    ]
    missing_cutlist = [item for item in required_cutlist if item not in cutlist_tab_text]
    if missing_cutlist:
        return False, f"FAIL_protected_export_cutlist:{', '.join(missing_cutlist)}"

    return True, "OK"
