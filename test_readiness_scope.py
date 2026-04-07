# -*- coding: utf-8 -*-
from __future__ import annotations

import state_logic as sl


def run_readiness_scope_check() -> tuple[bool, str]:
    original_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    try:
        sl.state.current_access_tier = "local_beta"
        local_beta_summary = sl.get_release_readiness_summary("staging")
        if str(local_beta_summary.get("error", "")) != "admin_only":
            return False, f"FAIL_local_beta_readiness_not_blocked:{local_beta_summary}"
        blockers = local_beta_summary.get("blockers", [])
        if not blockers or str(blockers[0].get("label", "")) != "admin_only":
            return False, f"FAIL_local_beta_readiness_missing_blocker:{local_beta_summary}"

        sl.state.current_access_tier = "admin"
        admin_summary = sl.get_release_readiness_summary("staging")
        if str(admin_summary.get("error", "")) == "admin_only":
            return False, f"FAIL_admin_readiness_blocked:{admin_summary}"
        required_keys = ("target", "ready", "summary", "blockers", "warnings")
        missing = [key for key in required_keys if key not in admin_summary]
        if missing:
            return False, f"FAIL_admin_readiness_missing_keys:{', '.join(missing)}"
        return True, "OK"
    finally:
        sl.state.current_access_tier = original_tier
