# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import app_config


def run_public_runtime_config_email_placeholders_check() -> tuple[bool, str]:
    keys = ("EMAIL_API_KEY", "EMAIL_FROM", "EMAIL_ENABLED", "EMAIL_PROVIDER")
    original = {key: os.environ.get(key) for key in keys}
    try:
        os.environ["EMAIL_PROVIDER"] = "resend"
        os.environ["EMAIL_ENABLED"] = "1"
        os.environ["EMAIL_API_KEY"] = "re_xxxxxxxxx"
        os.environ["EMAIL_FROM"] = "noreply@auth.tvoj-domen.rs"
        app_config._ENV_LOADED = False
        placeholder_cfg = app_config.get_public_runtime_config()
        if str(placeholder_cfg.get("has_email_api_key", "")) != "false":
            return False, f"FAIL_placeholder_email_api_key_visible:{placeholder_cfg.get('has_email_api_key')}"
        if str(placeholder_cfg.get("has_email_from", "")) != "false":
            return False, f"FAIL_placeholder_email_from_visible:{placeholder_cfg.get('has_email_from')}"

        os.environ["EMAIL_API_KEY"] = "re_real_key_value"
        os.environ["EMAIL_FROM"] = "noreply@auth.cabinetcutpro.com"
        app_config._ENV_LOADED = False
        real_cfg = app_config.get_public_runtime_config()
        if str(real_cfg.get("has_email_api_key", "")) != "true":
            return False, f"FAIL_real_email_api_key_hidden:{real_cfg.get('has_email_api_key')}"
        if str(real_cfg.get("has_email_from", "")) != "true":
            return False, f"FAIL_real_email_from_hidden:{real_cfg.get('has_email_from')}"
        return True, "OK"
    finally:
        app_config._ENV_LOADED = False
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
