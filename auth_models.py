# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

from project_store import UserRecord, ensure_local_user, get_effective_auth_session, get_user_by_id


ACCESS_OK_STATUSES = {"local_active", "trial_active", "paid_active", "admin_active"}


@dataclass(frozen=True)
class SessionUser:
    user_id: int
    email: str
    auth_mode: str
    access_tier: str
    subscription_status: str
    display_name: str


@dataclass(frozen=True)
class SessionState:
    user: SessionUser
    can_access_app: bool
    gate_reason: str


def _display_name_from_email(email: str) -> str:
    local = str(email or "").split("@", 1)[0].strip()
    return local or "local user"


def build_session_from_user(user: UserRecord) -> SessionState:
    status = str(user.status or "inactive").strip().lower()
    auth_mode = str(user.auth_mode or "").strip().lower()
    access_tier = str(user.access_tier or "").strip().lower()
    email_verified = bool(getattr(user, "email_verified", False))

    if not auth_mode or not access_tier:
        if status == "local_active":
            auth_mode = "local"
            access_tier = "local_beta"
        elif status == "trial_active":
            auth_mode = "password"
            access_tier = "trial"
        elif status == "paid_active":
            auth_mode = "password"
            access_tier = "paid"
        elif status == "admin_active":
            auth_mode = "password"
            access_tier = "admin"
        else:
            auth_mode = "unknown"
            access_tier = "blocked"

    session_user = SessionUser(
        user_id=int(user.id),
        email=str(user.email),
        auth_mode=auth_mode,
        access_tier=access_tier,
        subscription_status=status,
        display_name=str(user.display_name or _display_name_from_email(str(user.email))),
    )
    can_access = status in ACCESS_OK_STATUSES and email_verified
    gate_reason = ""
    if not email_verified:
        gate_reason = "Email nije potvrden. Potvrdi email link da bi nalog postao aktivan."
    elif not can_access:
        if status in ("inactive", "canceled"):
            gate_reason = "Pretplata nije aktivna. Aktiviraj PRO da nastavis rad bez prekida."
        elif status in ("past_due",):
            gate_reason = "Placanje nije uspesno obradjeno. Proveri naplatu i nastavi rad."
        elif status in ("pending_verification",):
            gate_reason = "Email nije potvrden. Potvrdi email link da bi nalog postao aktivan."
        else:
            gate_reason = "Pristup aplikaciji nije aktivan."
    return SessionState(
        user=session_user,
        can_access_app=can_access,
        gate_reason=gate_reason,
    )


def ensure_local_session() -> SessionState:
    user = ensure_local_user()
    return build_session_from_user(user)


def restore_session_from_token(session_token: str) -> SessionState | None:
    record = get_effective_auth_session(session_token)
    if record is None:
        return None
    if str(record.status or "").strip().lower() != "active":
        return None
    user = get_user_by_id(int(record.user_id))
    if user is None:
        return None
    return build_session_from_user(user)
