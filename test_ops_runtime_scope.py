# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_ops_runtime_scope_check() -> tuple[bool, str]:
    original_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    try:
        sl.state.current_access_tier = "local_beta"
        local_beta_summary = sl.get_ops_runtime_summary()
        if str(local_beta_summary.get("error", "")) != "admin_only":
            return False, f"FAIL_local_beta_ops_not_blocked:{local_beta_summary}"
        if "billing_events" in local_beta_summary or "auth_runtime" in local_beta_summary:
            return False, f"FAIL_local_beta_ops_leaked_global_data:{local_beta_summary}"

        sl.state.current_access_tier = "admin"
        admin_summary = sl.get_ops_runtime_summary()
        if str(admin_summary.get("error", "")) == "admin_only":
            return False, f"FAIL_admin_ops_blocked:{admin_summary}"
        required_keys = ("app_config", "project_store", "auth_runtime", "billing_events", "runtime_health")
        missing = [key for key in required_keys if key not in admin_summary]
        if missing:
            return False, f"FAIL_admin_ops_missing_keys:{', '.join(missing)}"
        return True, "OK"
    finally:
        sl.state.current_access_tier = original_tier
