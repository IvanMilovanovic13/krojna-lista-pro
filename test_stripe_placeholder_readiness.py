# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from stripe_service import get_stripe_runtime_status


def run_stripe_placeholder_readiness_check() -> tuple[bool, str]:
    keys = (
        "LEMON_SQUEEZY_API_KEY",
        "LEMON_SQUEEZY_WEBHOOK_SECRET",
        "LEMON_SQUEEZY_STORE_ID",
        "LEMON_SQUEEZY_STORE_SUBDOMAIN",
        "LEMON_SQUEEZY_VARIANT_ID_WEEKLY",
        "LEMON_SQUEEZY_VARIANT_ID_MONTHLY",
    )
    original = {key: os.environ.get(key) for key in keys}
    try:
        os.environ["LEMON_SQUEEZY_API_KEY"] = "api_key..."
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"] = "webhook_secret..."
        os.environ["LEMON_SQUEEZY_STORE_ID"] = "12345"
        os.environ["LEMON_SQUEEZY_STORE_SUBDOMAIN"] = "your-store"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_WEEKLY"] = "123456"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_MONTHLY"] = "123456"
        status = get_stripe_runtime_status()
        expected_false = (
            "has_secret_key",
            "has_publishable_key",
            "has_webhook_secret",
            "has_price_id_pro_monthly",
            "has_price_id_pro_yearly",
        )
        wrong = [key for key in expected_false if status.get(key) != "false"]
        if wrong:
            return False, f"FAIL_placeholder_detected_as_real:{wrong}:{status}"

        os.environ["LEMON_SQUEEZY_API_KEY"] = "real_api_key_value"
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"] = "real_webhook_secret"
        os.environ["LEMON_SQUEEZY_STORE_ID"] = "67890"
        os.environ["LEMON_SQUEEZY_STORE_SUBDOMAIN"] = "real-store"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_WEEKLY"] = "5678"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_MONTHLY"] = "6789"
        status_real = get_stripe_runtime_status()
        wrong_real = [key for key in ("has_secret_key", "has_webhook_secret", "has_price_id_pro_monthly", "has_price_id_pro_yearly") if status_real.get(key) != "true"]
        if wrong_real:
            return False, f"FAIL_real_detected_as_placeholder:{wrong_real}:{status_real}"
        if status_real.get("has_publishable_key") != "false":
            return False, f"FAIL_publishable_should_remain_false:{status_real}"
        return True, "OK"
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
