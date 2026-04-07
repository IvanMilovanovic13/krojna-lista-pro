# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import app_config


def run_public_runtime_config_billing_placeholders_check() -> tuple[bool, str]:
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
        app_config._ENV_LOADED = False
        placeholder_cfg = app_config.get_public_runtime_config()
        expected_false = (
            "has_billing_api_key",
            "has_billing_webhook_secret",
            "has_billing_store_id",
            "has_billing_store_subdomain",
            "has_billing_variant_id_weekly",
            "has_billing_variant_id_monthly",
        )
        for key in expected_false:
            if str(placeholder_cfg.get(key, "")) != "false":
                return False, f"FAIL_placeholder_not_hidden:{key}={placeholder_cfg.get(key)}"

        os.environ["LEMON_SQUEEZY_API_KEY"] = "real_api_key_value"
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"] = "real_webhook_secret"
        os.environ["LEMON_SQUEEZY_STORE_ID"] = "67890"
        os.environ["LEMON_SQUEEZY_STORE_SUBDOMAIN"] = "real-store"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_WEEKLY"] = "5678"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_MONTHLY"] = "6789"
        app_config._ENV_LOADED = False
        real_cfg = app_config.get_public_runtime_config()
        expected_true = (
            "has_billing_api_key",
            "has_billing_webhook_secret",
            "has_billing_store_id",
            "has_billing_store_subdomain",
            "has_billing_variant_id_weekly",
            "has_billing_variant_id_monthly",
        )
        for key in expected_true:
            if str(real_cfg.get(key, "")) != "true":
                return False, f"FAIL_real_value_not_visible:{key}={real_cfg.get(key)}"
        return True, "OK"
    finally:
        app_config._ENV_LOADED = False
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
