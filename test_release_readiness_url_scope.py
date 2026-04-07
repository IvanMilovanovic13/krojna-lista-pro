# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from release_readiness import get_release_readiness_report


def run_release_readiness_url_scope_check() -> tuple[bool, str]:
    keys = (
        "APP_ENV",
        "BASE_URL",
        "SECRET_KEY",
        "DATABASE_URL",
        "LEMON_SQUEEZY_API_KEY",
        "LEMON_SQUEEZY_WEBHOOK_SECRET",
        "LEMON_SQUEEZY_STORE_ID",
        "LEMON_SQUEEZY_STORE_SUBDOMAIN",
        "LEMON_SQUEEZY_VARIANT_ID_WEEKLY",
        "LEMON_SQUEEZY_VARIANT_ID_MONTHLY",
        "LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL",
    )
    original = {key: os.environ.get(key) for key in keys}
    try:
        os.environ["APP_ENV"] = "staging"
        os.environ["BASE_URL"] = "http://staging.example.com"
        os.environ["SECRET_KEY"] = "staging-secret-key"
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
        os.environ["LEMON_SQUEEZY_API_KEY"] = "real_api_key_value"
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"] = "real_webhook_secret"
        os.environ["LEMON_SQUEEZY_STORE_ID"] = "1234"
        os.environ["LEMON_SQUEEZY_STORE_SUBDOMAIN"] = "my-store"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_WEEKLY"] = "5678"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_MONTHLY"] = "6789"
        os.environ["LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL"] = "https://wrong.example.com/nalog?checkout=success"

        bad = get_release_readiness_report(target="staging")
        blocker_keys = {str(item.get("key", "")) for item in bad.get("blockers", [])}
        expected = {
            "base_url_https",
            "billing_checkout_success_origin",
        }
        if not expected.issubset(blocker_keys):
            return False, f"FAIL_missing_origin_blockers:{blocker_keys}:{bad}"

        os.environ["BASE_URL"] = "https://staging.example.com"
        os.environ["LEMON_SQUEEZY_CHECKOUT_SUCCESS_URL"] = "https://staging.example.com/nalog?checkout=success"
        good = get_release_readiness_report(target="staging")
        good_blocker_keys = {str(item.get("key", "")) for item in good.get("blockers", [])}
        if expected & good_blocker_keys:
            return False, f"FAIL_origin_blockers_not_cleared:{good_blocker_keys}:{good}"
        return True, "OK"
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
