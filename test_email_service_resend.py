# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import app_config
import email_service


class _StubResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {"id": "email_123"}
        self.text = ""

    def json(self) -> dict:
        return dict(self._payload)


def run_email_service_resend_check() -> tuple[bool, str]:
    keys = (
        "EMAIL_PROVIDER",
        "EMAIL_ENABLED",
        "EMAIL_API_KEY",
        "RESEND_API_KEY",
        "EMAIL_FROM",
        "EMAIL_FROM_NAME",
        "EMAIL_REPLY_TO",
    )
    original = {key: os.environ.get(key) for key in keys}
    captured: dict[str, object] = {}
    original_post = email_service.requests.post
    try:
        os.environ["EMAIL_PROVIDER"] = "resend"
        os.environ["EMAIL_ENABLED"] = "1"
        os.environ["EMAIL_API_KEY"] = "re_test_key"
        os.environ["EMAIL_FROM"] = "noreply@auth.example.com"
        os.environ["EMAIL_FROM_NAME"] = "CabinetCut Pro"
        os.environ["EMAIL_REPLY_TO"] = "support@example.com"
        app_config._ENV_LOADED = False

        def _stub_post(url: str, *, headers: dict | None = None, json: dict | None = None, timeout: int | None = None):
            captured["url"] = url
            captured["headers"] = dict(headers or {})
            captured["json"] = dict(json or {})
            captured["timeout"] = timeout
            return _StubResponse()

        email_service.requests.post = _stub_post
        ok, detail = email_service.send_verification_email(
            to_email="user@example.com",
            verification_url="https://example.com/verify-email?token=abc",
            display_name="Ivan",
        )
        if not ok:
            return False, f"FAIL_send_verification_email:{detail}"
        if str(captured.get("url")) != "https://api.resend.com/emails":
            return False, f"FAIL_resend_url:{captured.get('url')}"
        auth_header = str((captured.get("headers") or {}).get("Authorization", ""))
        if auth_header != "Bearer re_test_key":
            return False, f"FAIL_resend_auth_header:{auth_header}"
        payload = captured.get("json") or {}
        if str(payload.get("from", "")) != "CabinetCut Pro <noreply@auth.example.com>":
            return False, f"FAIL_from_header:{payload.get('from')}"
        if list(payload.get("to", [])) != ["user@example.com"]:
            return False, f"FAIL_to_payload:{payload.get('to')}"
        if str(payload.get("reply_to", "")) != "support@example.com":
            return False, f"FAIL_reply_to_payload:{payload.get('reply_to')}"
        if "verify-email?token=abc" not in str(payload.get("html", "")):
            return False, "FAIL_verification_link_missing_in_html"
        return True, "OK"
    finally:
        app_config._ENV_LOADED = False
        email_service.requests.post = original_post
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
