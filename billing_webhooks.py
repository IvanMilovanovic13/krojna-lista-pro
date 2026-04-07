# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

from app_config import get_app_config
from billing_models import handle_billing_webhook_event
from lemon_squeezy_service import construct_webhook_event
from project_store import append_audit_log, get_user_by_email


def process_billing_webhook_payload(
    payload: dict[str, Any] | None = None,
    *,
    provided_secret: str = "",
    payload_bytes: bytes | None = None,
    webhook_signature: str = "",
) -> dict[str, str]:
    cfg = get_app_config()
    expected_secret = str(cfg.lemon_squeezy_webhook_secret or "").strip()

    try:
        if payload_bytes is not None:
            event = construct_webhook_event(
                payload_bytes=payload_bytes,
                webhook_signature=webhook_signature,
            )
        else:
            if expected_secret and str(provided_secret or "").strip() != expected_secret:
                return {
                    "ok": "false",
                    "message": "Webhook secret nije validan.",
                }
            if not isinstance(payload, dict):
                return {
                    "ok": "false",
                    "message": "Webhook payload mora biti JSON objekat.",
                }
            event = payload
    except Exception as ex:
        return {
            "ok": "false",
            "message": str(ex),
        }

    result = handle_billing_webhook_event(event)
    clean_email = str(result.get("email", "") or "").strip().lower()
    user = get_user_by_email(clean_email) if clean_email else None
    append_audit_log(
        event_type=f"billing.{str(result.get('event_type', 'unknown') or 'unknown')}",
        status="success" if str(result.get("ok", "")).lower() == "true" else "warning",
        detail=f"email={clean_email or 'n/a'} billing_status={str(result.get('billing_status', '') or '')}",
        user_id=int(user.id) if user is not None else 0,
    )
    if payload_bytes is not None and expected_secret:
        result["secret_validated"] = "true"
    elif expected_secret:
        result["secret_validated"] = "true"
    else:
        result["secret_validated"] = "false"
        result["note"] = "LEMON_SQUEEZY_WEBHOOK_SECRET nije postavljen; webhook radi u development modu."
    return result
