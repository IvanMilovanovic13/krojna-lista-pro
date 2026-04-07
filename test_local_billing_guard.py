# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_local_billing_guard_check() -> tuple[bool, str]:
    original_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_auth_mode = str(getattr(sl.state, "current_auth_mode", "") or "")
    try:
        sl.state.current_user_email = "local@offline"
        sl.state.current_auth_mode = "local"

        summary = sl.get_current_billing_summary()
        if summary is not None:
            return False, f"FAIL_local_billing_summary_visible:{summary}"

        ok_checkout, msg_checkout = sl.build_checkout_start_message()
        if ok_checkout or "lokalnu fallback sesiju" not in str(msg_checkout):
            return False, f"FAIL_local_checkout_not_blocked:{ok_checkout}:{msg_checkout}"

        ok_portal, msg_portal = sl.build_customer_portal_message()
        if ok_portal or "lokalnu fallback sesiju" not in str(msg_portal):
            return False, f"FAIL_local_portal_not_blocked:{ok_portal}:{msg_portal}"
        return True, "OK"
    finally:
        sl.state.current_user_email = original_email
        sl.state.current_auth_mode = original_auth_mode
