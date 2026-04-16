# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

import state_logic as sl


@dataclass(frozen=True)
class _FakeUser:
    user_id: int
    email: str
    display_name: str
    auth_mode: str
    access_tier: str
    subscription_status: str


@dataclass(frozen=True)
class _FakeSession:
    user: _FakeUser
    can_access_app: bool
    gate_reason: str


def run_session_identity_project_reset_check() -> tuple[bool, str]:
    original_user_id = int(getattr(sl.state, "current_user_id", 0) or 0)
    original_user_email = str(getattr(sl.state, "current_user_email", "") or "")
    original_user_display = str(getattr(sl.state, "current_user_display", "") or "")
    original_auth_mode = str(getattr(sl.state, "current_auth_mode", "") or "")
    original_access_tier = str(getattr(sl.state, "current_access_tier", "") or "")
    original_subscription_status = str(getattr(sl.state, "current_subscription_status", "") or "")
    original_gate_reason = str(getattr(sl.state, "current_gate_reason", "") or "")
    original_can_access = bool(getattr(sl.state, "current_can_access_app", True))
    original_active_tab = str(getattr(sl.state, "active_tab", "") or "")
    original_project_id = int(getattr(sl.state, "current_project_id", 0) or 0)
    original_project_name = str(getattr(sl.state, "current_project_name", "") or "")
    original_project_source = str(getattr(sl.state, "current_project_source", "") or "")
    original_room = sl.copy.deepcopy(getattr(sl.state, "room", {}))
    original_kitchen = sl.copy.deepcopy(getattr(sl.state, "kitchen", {}))
    original_next_id = int(getattr(sl.state, "next_id", 1) or 1)
    try:
        sl.state.current_user_id = 7
        sl.state.current_user_email = "old-user@example.com"
        sl.state.current_project_id = 555
        sl.state.current_project_name = "Old Bound Project"
        sl.state.current_project_source = "store"
        sl.state.kitchen = sl._default_kitchen()
        sl.state.kitchen["modules"] = [{"id": 99, "template_id": "BASE_2_DOOR", "zone": "base"}]
        sl.state.room = sl._default_room()
        sl.state.room_setup_done = True
        sl.state.next_id = 100
        sl.state.active_tab = "nalog"

        new_session = _FakeSession(
            user=_FakeUser(
                user_id=12,
                email="new-user@example.com",
                display_name="New User",
                auth_mode="password",
                access_tier="trial",
                subscription_status="trial_active",
            ),
            can_access_app=True,
            gate_reason="",
        )
        sl._apply_session_state(new_session)

        if int(getattr(sl.state, "current_project_id", 0) or 0) != 0:
            return False, f"FAIL_project_id_not_reset:{sl.state.current_project_id}"
        if str(getattr(sl.state, "current_project_name", "") or ""):
            return False, f"FAIL_project_name_not_reset:{sl.state.current_project_name}"
        if str(getattr(sl.state, "current_project_source", "") or ""):
            return False, f"FAIL_project_source_not_reset:{sl.state.current_project_source}"
        if list((getattr(sl.state, "kitchen", {}) or {}).get("modules", []) or []):
            return False, "FAIL_workspace_modules_not_reset"
        if bool(getattr(sl.state, "room_setup_done", False)):
            return False, f"FAIL_room_setup_flag_not_reset:{sl.state.room_setup_done}"
        if int(getattr(sl.state, "next_id", 0) or 0) != 1:
            return False, f"FAIL_next_id_not_reset:{sl.state.next_id}"
        if str(getattr(sl.state, "current_user_email", "") or "") != "new-user@example.com":
            return False, f"FAIL_new_user_not_applied:{sl.state.current_user_email}"
        if str(getattr(sl.state, "active_tab", "") or "") != "nova":
            return False, f"FAIL_active_tab_not_redirected:{sl.state.active_tab}"
        return True, "OK"
    finally:
        sl.state.current_user_id = original_user_id
        sl.state.current_user_email = original_user_email
        sl.state.current_user_display = original_user_display
        sl.state.current_auth_mode = original_auth_mode
        sl.state.current_access_tier = original_access_tier
        sl.state.current_subscription_status = original_subscription_status
        sl.state.current_gate_reason = original_gate_reason
        sl.state.current_can_access_app = original_can_access
        sl.state.active_tab = original_active_tab
        sl.state.current_project_id = original_project_id
        sl.state.current_project_name = original_project_name
        sl.state.current_project_source = original_project_source
        sl.state.room = original_room
        sl.state.kitchen = original_kitchen
        sl.state.next_id = original_next_id
