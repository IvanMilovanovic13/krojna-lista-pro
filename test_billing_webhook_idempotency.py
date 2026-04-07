# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from billing_models import get_billing_summary_for_email, handle_billing_webhook_event
from project_store import create_user_record, export_store_snapshot, hash_password, init_project_store


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


def run_billing_webhook_idempotency_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("billing_webhook_idempotency")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()

        create_user_record(
            email="billing-idempotency@example.com",
            display_name="Billing Idempotency",
            password_hash=hash_password("billing-pass"),
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )

        event = {
            "id": "evt_test_duplicate_001",
            "meta": {
                "event_name": "subscription_created",
            },
            "data": {
                "type": "subscriptions",
                "id": "sub_test_001",
                "attributes": {
                    "customer_id": "cus_test_001",
                    "status": "active",
                    "renews_at": "2026-04-26T10:00:00+00:00",
                    "variant_name": "Monthly Access",
                    "custom_data": {
                        "user_email": "billing-idempotency@example.com",
                        "plan_code": "pro_monthly",
                    },
                },
            },
        }

        first = handle_billing_webhook_event(event)
        second = handle_billing_webhook_event(event)
        summary = get_billing_summary_for_email("billing-idempotency@example.com")
        snapshot = export_store_snapshot()
        billing_events = snapshot.get("billing_events", [])

        if str(first.get("ok", "")).lower() != "true":
            return False, f"FAIL_first_event_not_processed:{first}"
        if str(second.get("ok", "")).lower() != "true":
            return False, f"FAIL_second_event_not_processed:{second}"
        if str(second.get("duplicate", "")).lower() != "true":
            return False, f"FAIL_duplicate_flag_missing:{second}"
        if summary is None:
            return False, "FAIL_missing_billing_summary"
        if str(summary.billing_status) != "active":
            return False, f"FAIL_billing_status:{summary.billing_status}"
        if str(summary.account_status) != "paid_active":
            return False, f"FAIL_account_status:{summary.account_status}"
        if len([row for row in billing_events if str(row.get("provider_event_id", "")) == "evt_test_duplicate_001"]) != 1:
            return False, f"FAIL_duplicate_billing_event_rows:{billing_events}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
