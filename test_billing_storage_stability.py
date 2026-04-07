# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from app_config import DatabaseConfig
from project_store import (
    create_user_record,
    get_user_subscription,
    init_project_store,
    upsert_user_subscription,
)
from storage_backend import SQLiteStoreBackend


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


def run_sqlite_backend_stability_check() -> tuple[bool, str]:
    db_path = _test_db_path("storage_stability")
    try:
        backend = SQLiteStoreBackend(
            DatabaseConfig(
                backend="sqlite",
                url=f"sqlite:///{db_path.as_posix()}",
                sqlite_path=db_path,
            )
        )
        with backend.connect() as conn:
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
            synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]

        if str(journal_mode).lower() != "wal":
            return False, f"FAIL_sqlite_journal_mode:{journal_mode}"
        if int(busy_timeout or 0) < 30000:
            return False, f"FAIL_sqlite_busy_timeout:{busy_timeout}"
        if int(synchronous or 0) not in (1, 2):
            return False, f"FAIL_sqlite_synchronous:{synchronous}"
        return True, "OK"
    finally:
        _cleanup_sqlite_family(db_path)


def run_subscription_upsert_preserves_fields_check() -> tuple[bool, str]:
    original_database_url = os.environ.get("DATABASE_URL")
    db_path = _test_db_path("billing_stability")
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"

        init_project_store()
        user = create_user_record(
            email="billing-test@example.com",
            display_name="Billing Test",
            password_hash="hash",
            auth_mode="password",
            access_tier="trial",
            status="trial_active",
        )
        upsert_user_subscription(
            user_id=int(user.id),
            provider="stripe",
            plan_code="pro_monthly",
            billing_status="active",
            customer_id="cus_123",
            subscription_id="sub_123",
            checkout_url="https://checkout.example/session",
            portal_url="https://portal.example/session",
            current_period_end="2026-04-26T10:00:00+00:00",
        )
        upsert_user_subscription(
            user_id=int(user.id),
            provider="stripe",
            plan_code="pro_monthly",
            billing_status="past_due",
        )
        record = get_user_subscription(int(user.id))
        if record is None:
            return False, "FAIL_missing_subscription_record"
        if str(record.customer_id) != "cus_123":
            return False, f"FAIL_customer_id_lost:{record.customer_id}"
        if str(record.subscription_id) != "sub_123":
            return False, f"FAIL_subscription_id_lost:{record.subscription_id}"
        if str(record.portal_url) != "https://portal.example/session":
            return False, f"FAIL_portal_url_lost:{record.portal_url}"
        if str(record.checkout_url) != "https://checkout.example/session":
            return False, f"FAIL_checkout_url_lost:{record.checkout_url}"
        if str(record.current_period_end) != "2026-04-26T10:00:00+00:00":
            return False, f"FAIL_period_end_lost:{record.current_period_end}"
        if str(record.billing_status) != "past_due":
            return False, f"FAIL_billing_status_not_updated:{record.billing_status}"
        return True, "OK"
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        _cleanup_sqlite_family(db_path)
