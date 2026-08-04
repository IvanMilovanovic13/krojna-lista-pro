# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from billing_models import get_billing_summary_for_email, handle_billing_webhook_event
from project_store import create_user_record, hash_password, init_project_store


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


def run_billing_admin_protection_check() -> tuple[bool, str]:
    """Billing webhook ne sme da skine admin nalog na paid/trial tier
    kada admin lično uradi (test) kupovinu svojim emailom."""
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("billing_admin_protection")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        init_project_store()

        create_user_record(
            email="admin-billing@example.com",
            display_name="Admin Billing",
            password_hash=hash_password("admin-pass"),
            auth_mode="password",
            access_tier="admin",
            status="admin_active",
        )

        event = {
            "meta": {
                "event_name": "order_created",
                "webhook_id": "evt_admin_protection_001",
                "custom_data": {
                    "user_email": "admin-billing@example.com",
                    "plan_code": "pro_weekly",
                },
            },
            "data": {
                "type": "orders",
                "id": "order_test_001",
                "attributes": {
                    "customer_id": "cus_test_admin",
                    "status": "paid",
                    "variant_name": "7 Days Access",
                    "user_email": "someone-else@example.com",
                },
            },
        }

        result = handle_billing_webhook_event(event)
        summary = get_billing_summary_for_email("admin-billing@example.com")

        if str(result.get("ok", "")).lower() != "true":
            return False, f"FAIL_event_not_processed:{result}"
        if str(result.get("email", "")).lower() != "admin-billing@example.com":
            return False, f"FAIL_wrong_email_extracted:{result.get('email')}"
        if summary is None:
            return False, "FAIL_missing_billing_summary"
        if str(summary.access_tier) != "admin":
            return False, f"FAIL_admin_downgraded:{summary.access_tier}"
        if str(summary.account_status) != "admin_active":
            return False, f"FAIL_admin_status_changed:{summary.account_status}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
