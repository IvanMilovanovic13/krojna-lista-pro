# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from project_store import (
    cleanup_billing_events,
    create_user_record,
    get_billing_event_summary,
    hash_password,
    init_project_store,
    list_recent_billing_events,
    record_billing_event,
    update_billing_event_status,
)
from storage_backend import get_store_backend


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


def run_billing_event_ops_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("billing_event_ops")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()
        user = create_user_record(
            email="billing-ops@example.com",
            display_name="Billing Ops",
            password_hash=hash_password("ops-pass"),
            auth_mode="password",
            access_tier="admin",
            status="admin_active",
        )

        record_billing_event(
            provider_event_id="evt_billing_ops_001",
            event_type="invoice.paid",
            user_id=int(user.id),
            email=str(user.email),
            payload_json='{"id":"evt_billing_ops_001"}',
        )
        update_billing_event_status(
            "evt_billing_ops_001",
            status="processed",
            user_id=int(user.id),
            email=str(user.email),
            billing_status="active",
            plan_code="pro_monthly",
        )
        record_billing_event(
            provider_event_id="evt_billing_ops_002",
            event_type="invoice.payment_failed",
            user_id=int(user.id),
            email=str(user.email),
            payload_json='{"id":"evt_billing_ops_002"}',
        )
        update_billing_event_status(
            "evt_billing_ops_002",
            status="failed",
            user_id=int(user.id),
            email=str(user.email),
            billing_status="past_due",
            plan_code="pro_monthly",
            error_message="payment_failed",
        )

        summary = get_billing_event_summary()
        if int(summary.get("total", 0)) != 2:
            return False, f"FAIL_billing_event_summary_total:{summary}"
        if int(summary.get("processed", 0)) != 1 or int(summary.get("failed", 0)) != 1:
            return False, f"FAIL_billing_event_summary_breakdown:{summary}"

        recent = list_recent_billing_events(user_id=int(user.id), limit=10)
        if len(recent) != 2:
            return False, f"FAIL_recent_billing_events_len:{len(recent)}"
        failed_only = list_recent_billing_events(user_id=int(user.id), status="failed", limit=10)
        if len(failed_only) != 1 or str(failed_only[0].provider_event_id) != "evt_billing_ops_002":
            return False, f"FAIL_recent_billing_events_filter:{failed_only}"

        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=45)).replace(microsecond=0).isoformat()
        with get_store_backend().connect() as conn:
            conn.execute(
                "UPDATE billing_events SET updated_at = ? WHERE provider_event_id = ?",
                (old_timestamp, "evt_billing_ops_002"),
            )
        cleanup = cleanup_billing_events(
            keep_processed_days=180,
            keep_failed_days=30,
            keep_ignored_days=30,
        )
        if int(cleanup.get("pruned_billing_events", 0)) < 1:
            return False, f"FAIL_billing_event_cleanup:{cleanup}"
        remaining = list_recent_billing_events(user_id=int(user.id), limit=10)
        if len(remaining) != 1 or str(remaining[0].provider_event_id) != "evt_billing_ops_001":
            return False, f"FAIL_billing_event_remaining:{remaining}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
