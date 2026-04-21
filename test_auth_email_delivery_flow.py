# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import app_config
import email_service
from project_store import init_project_store
from state_logic import build_forgot_password_message, login_user_session, register_trial_user_session


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


def run_auth_email_delivery_flow_check() -> tuple[bool, str]:
    db_path = _test_db_path("auth_email_delivery_flow")
    env_keys = (
        "DATABASE_URL",
        "APP_ENV",
        "EMAIL_PROVIDER",
        "EMAIL_ENABLED",
        "EMAIL_API_KEY",
        "EMAIL_FROM",
        "EMAIL_FROM_NAME",
    )
    original = {key: os.environ.get(key) for key in env_keys}
    original_send_verification = email_service.send_verification_email
    original_send_reset = email_service.send_password_reset_email
    try:
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
        os.environ["APP_ENV"] = "staging"
        os.environ["EMAIL_PROVIDER"] = "resend"
        os.environ["EMAIL_ENABLED"] = "1"
        os.environ["EMAIL_API_KEY"] = "re_test_key"
        os.environ["EMAIL_FROM"] = "noreply@auth.example.com"
        os.environ["EMAIL_FROM_NAME"] = "CabinetCut Pro"
        app_config._ENV_LOADED = False
        init_project_store()

        email_service.send_verification_email = lambda **kwargs: (True, "email_sent")
        email_service.send_password_reset_email = lambda **kwargs: (True, "email_sent")

        ok_register, register_msg = register_trial_user_session(
            "flow@example.com",
            "Flow User",
            "secret123",
            "flow-user",
        )
        if not ok_register:
            return False, f"FAIL_register:{register_msg}"
        if "/verify-email?token=" in str(register_msg):
            return False, f"FAIL_register_leaked_token:{register_msg}"
        if "Proveri email" not in str(register_msg):
            return False, f"FAIL_register_email_message:{register_msg}"

        ok_login, login_msg = login_user_session("flow@example.com", "secret123")
        if ok_login:
            return False, "FAIL_unverified_login_should_not_succeed"
        if "/verify-email?token=" in str(login_msg):
            return False, f"FAIL_login_leaked_token:{login_msg}"
        if "Poslali smo novi verifikacioni email" not in str(login_msg):
            return False, f"FAIL_login_email_message:{login_msg}"

        ok_reset, reset_msg = build_forgot_password_message("flow@example.com")
        if not ok_reset:
            return False, f"FAIL_reset:{reset_msg}"
        if "reset_token" in str(reset_msg).lower() or "razvojni token" in str(reset_msg).lower():
            return False, f"FAIL_reset_leaked_token:{reset_msg}"
        if "Poslali smo email sa linkom za reset lozinke." not in str(reset_msg):
            return False, f"FAIL_reset_email_message:{reset_msg}"
        return True, "OK"
    finally:
        app_config._ENV_LOADED = False
        email_service.send_verification_email = original_send_verification
        email_service.send_password_reset_email = original_send_reset
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        _cleanup_sqlite_family(db_path)
