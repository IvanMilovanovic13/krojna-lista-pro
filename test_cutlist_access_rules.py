# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_cutlist_access_rules_check() -> tuple[bool, str]:
    original_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_status = str(getattr(sl.state, "current_subscription_status", "") or "")
    original_source = str(getattr(sl.state, "current_project_source", "") or "")
    try:
        sl.state.current_access_tier = "trial"
        sl.state.current_subscription_status = "trial_active"
        sl.state.current_project_source = "user_store"
        free_access = sl.get_cutlist_access_state()
        if str(free_access.get("allowed", "")).lower() != "false":
            return False, f"FAIL_free_should_be_blocked:{free_access}"
        if "Free pristup" not in str(free_access.get("reason", "") or ""):
            return False, f"FAIL_free_reason:{free_access}"

        sl.state.current_access_tier = "paid"
        sl.state.current_subscription_status = "paid_active"
        sl.state.current_project_source = "user_store"
        paid_access = sl.get_cutlist_access_state()
        if str(paid_access.get("allowed", "")).lower() != "true":
            return False, f"FAIL_paid_should_be_allowed:{paid_access}"

        sl.state.current_access_tier = "trial"
        sl.state.current_subscription_status = "trial_active"
        sl.state.current_project_source = "builtin_demo"
        demo_access = sl.get_cutlist_access_state()
        if str(demo_access.get("allowed", "")).lower() != "true":
            return False, f"FAIL_demo_should_be_allowed:{demo_access}"
        if str(demo_access.get("mode", "") or "") != "demo":
            return False, f"FAIL_demo_mode:{demo_access}"
        return True, "OK"
    finally:
        sl.state.current_access_tier = original_tier
        sl.state.current_subscription_status = original_status
        sl.state.current_project_source = original_source

