# -*- coding: utf-8 -*-
from __future__ import annotations

import os

import state_logic as sl


def run_billing_runtime_guard_check() -> tuple[bool, str]:
    keys = (
        "LEMON_SQUEEZY_API_KEY",
        "LEMON_SQUEEZY_STORE_ID",
        "LEMON_SQUEEZY_STORE_SUBDOMAIN",
        "LEMON_SQUEEZY_VARIANT_ID_WEEKLY",
        "LEMON_SQUEEZY_VARIANT_ID_MONTHLY",
    )
    original = {key: os.environ.get(key) for key in keys}
    original_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_auth_mode = str(getattr(sl.state, "current_auth_mode", "") or "")
    try:
        sl.state.current_user_email = "billing-user@example.com"
        sl.state.current_auth_mode = "password"

        os.environ.pop("LEMON_SQUEEZY_API_KEY", None)
        os.environ.pop("LEMON_SQUEEZY_STORE_ID", None)
        os.environ.pop("LEMON_SQUEEZY_STORE_SUBDOMAIN", None)
        os.environ.pop("LEMON_SQUEEZY_VARIANT_ID_WEEKLY", None)
        os.environ.pop("LEMON_SQUEEZY_VARIANT_ID_MONTHLY", None)

        ok_checkout, msg_checkout = sl.build_checkout_start_message()
        if ok_checkout or "nije konfigurisan" not in str(msg_checkout):
            return False, f"FAIL_checkout_guard_missing:{ok_checkout}:{msg_checkout}"

        ok_portal, msg_portal = sl.build_customer_portal_message()
        if ok_portal or "nije konfigurisan" not in str(msg_portal):
            return False, f"FAIL_portal_guard_missing:{ok_portal}:{msg_portal}"

        os.environ["LEMON_SQUEEZY_API_KEY"] = "real_api_key_value"
        os.environ["LEMON_SQUEEZY_STORE_ID"] = "1234"
        os.environ["LEMON_SQUEEZY_STORE_SUBDOMAIN"] = "my-store"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_WEEKLY"] = "5678"
        os.environ["LEMON_SQUEEZY_VARIANT_ID_MONTHLY"] = "6789"
        ok_checkout_ready, msg_checkout_ready = sl.build_checkout_start_message()
        if not ok_checkout_ready:
            return False, f"FAIL_checkout_guard_blocked_real_config:{msg_checkout_ready}"

        ok_portal_ready, msg_portal_ready = sl.build_customer_portal_message()
        if not ok_portal_ready:
            return False, f"FAIL_portal_guard_blocked_real_config:{msg_portal_ready}"
        return True, "OK"
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        sl.state.current_user_email = original_email
        sl.state.current_auth_mode = original_auth_mode
