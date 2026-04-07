# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_postgres_export_jobs_migration_check() -> tuple[bool, str]:
    store_text = Path(__file__).with_name("project_store.py").read_text(encoding="utf-8")
    migration_text = Path(__file__).with_name("postgres_store_migration.py").read_text(encoding="utf-8")

    store_required = [
        '"login_attempts": [dict(row) for row in login_attempts]',
        '"export_jobs": [dict(row) for row in export_jobs]',
        "FROM login_attempts",
        "FROM export_jobs",
    ]
    store_missing = [item for item in store_required if item not in store_text]
    if store_missing:
        return False, f"FAIL_export_jobs_snapshot_missing:{', '.join(store_missing)}"

    migration_required = [
        'login_attempts = payload.get("login_attempts", [])',
        'export_jobs = payload.get("export_jobs", [])',
        "INSERT INTO login_attempts",
        "INSERT INTO export_jobs",
        "setval(pg_get_serial_sequence('login_attempts', 'id')",
        "setval(pg_get_serial_sequence('export_jobs', 'id')",
        '"login_attempts": str(len(login_attempts))',
        '"export_jobs": str(len(export_jobs))',
    ]
    migration_missing = [item for item in migration_required if item not in migration_text]
    if migration_missing:
        return False, f"FAIL_export_jobs_migration_missing:{', '.join(migration_missing)}"

    return True, "OK"
