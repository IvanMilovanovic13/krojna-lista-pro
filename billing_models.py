# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

from project_store import (
    SubscriptionRecord,
    UserRecord,
    get_user_by_email,
    get_billing_event,
    get_user_subscription,
    record_billing_event,
    set_user_access_status,
    update_billing_event_status,
    upsert_user_subscription,
)
from lemon_squeezy_service import create_checkout_session_for_email, create_customer_portal_for_email, get_billing_runtime_status
import json


@dataclass(frozen=True)
class BillingSummary:
    email: str
    access_tier: str
    account_status: str
    billing_status: str
    plan_code: str
    provider: str
    current_period_end: str
    has_checkout: bool
    has_portal: bool
    billing_ready: bool


def _default_billing_status_for_user(user: UserRecord) -> str:
    status = str(user.status or "").strip().lower()
    if status == "local_active":
        return "local"
    if status == "trial_active":
        return "trial"
    if status == "paid_active":
        return "active"
    if status == "admin_active":
        return "admin"
    return "inactive"


def ensure_billing_record_for_user(user: UserRecord) -> SubscriptionRecord:
    existing = get_user_subscription(int(user.id))
    if existing is not None:
        return existing
    return upsert_user_subscription(
        user_id=int(user.id),
        provider="lemon_squeezy",
        plan_code="trial" if str(user.access_tier or "") == "trial" else "local",
        billing_status=_default_billing_status_for_user(user),
    )


def get_billing_summary_for_email(email: str) -> BillingSummary | None:
    user = get_user_by_email(email)
    if user is None:
        return None
    subscription = ensure_billing_record_for_user(user)
    billing_runtime = get_billing_runtime_status()
    return BillingSummary(
        email=str(user.email),
        access_tier=str(user.access_tier),
        account_status=str(user.status),
        billing_status=str(subscription.billing_status),
        plan_code=str(subscription.plan_code),
        provider=str(subscription.provider),
        current_period_end=str(subscription.current_period_end),
        has_checkout=bool(str(subscription.checkout_url or "").strip()),
        has_portal=bool(str(subscription.portal_url or "").strip()),
        billing_ready=(
            billing_runtime.get("has_api_key") == "true"
            and (
                billing_runtime.get("has_variant_id_weekly") == "true"
                or billing_runtime.get("has_variant_id_monthly") == "true"
            )
        ),
    )


def build_checkout_placeholder(email: str, plan_code: str = "pro_monthly") -> str:
    result = create_checkout_session_for_email(email, plan_code=str(plan_code or "pro_monthly"))
    return result.url if result.ok and result.url else result.message


def build_customer_portal_placeholder(email: str) -> str:
    result = create_customer_portal_for_email(email)
    return result.url if result.ok and result.url else result.message


def _status_to_access(status: str, plan_code: str) -> tuple[str, str]:
    clean = str(status or "").strip().lower()
    if clean in ("active", "paid", "on_trial"):
        return ("paid", "paid_active") if plan_code != "trial" else ("trial", "trial_active")
    if clean in ("trialing", "trial"):
        return ("trial", "trial_active")
    if clean in ("local",):
        return ("local_beta", "local_active")
    if clean in ("admin",):
        return ("admin", "admin_active")
    return ("blocked", "inactive")


def apply_billing_status_to_user(email: str, billing_status: str, plan_code: str = "paid") -> BillingSummary | None:
    status = str(billing_status or "").strip().lower()
    access_tier, user_status = _status_to_access(status, str(plan_code or "paid"))

    user = set_user_access_status(email=email, access_tier=access_tier, status=user_status, auth_mode="password")
    if user is None:
        return None

    upsert_user_subscription(
        user_id=int(user.id),
        provider="lemon_squeezy",
        plan_code=str(plan_code or "paid"),
        billing_status=status or "inactive",
    )
    return get_billing_summary_for_email(email)


def _extract_event_object(event: dict) -> dict:
    data = event.get("data", {}) if isinstance(event, dict) else {}
    return data if isinstance(data, dict) else {}


def _extract_email_from_event(event: dict) -> str:
    obj = _extract_event_object(event)
    attributes = obj.get("attributes", {}) if isinstance(obj.get("attributes", {}), dict) else {}
    custom_data = attributes.get("custom_data", {}) if isinstance(attributes.get("custom_data", {}), dict) else {}
    candidates = [
        custom_data.get("user_email"),
        attributes.get("user_email"),
        attributes.get("customer_email"),
        attributes.get("email"),
    ]
    for value in candidates:
        clean = str(value or "").strip().lower()
        if "@" in clean:
            return clean
    return ""


def _extract_plan_code(event: dict) -> str:
    obj = _extract_event_object(event)
    attributes = obj.get("attributes", {}) if isinstance(obj.get("attributes", {}), dict) else {}
    custom_data = attributes.get("custom_data", {}) if isinstance(attributes.get("custom_data", {}), dict) else {}
    if custom_data.get("plan_code"):
        return str(custom_data.get("plan_code"))
    variant_name = str(attributes.get("variant_name", "") or "").strip().lower()
    if "month" in variant_name:
        return "pro_monthly"
    if "week" in variant_name or "7 days" in variant_name:
        return "pro_weekly"
    return str(attributes.get("product_name", "") or "paid")


def handle_billing_webhook_event(event: dict) -> dict[str, str]:
    meta = (event or {}).get("meta", {}) if isinstance((event or {}).get("meta", {}), dict) else {}
    event_type = str(meta.get("event_name", "") or (event or {}).get("type", "") or "").strip()
    event_id = str((event or {}).get("id", "") or "").strip()
    email = _extract_email_from_event(event)
    if not email:
        return {
            "ok": "false",
            "event_id": event_id,
            "event_type": event_type,
            "message": "Billing event nema korisnicki email.",
        }

    existing_event = get_billing_event(event_id) if event_id else None
    if existing_event is not None and str(existing_event.status).lower() == "processed":
        return {
            "ok": "true",
            "event_id": event_id,
            "event_type": event_type,
            "email": email,
            "billing_status": str(existing_event.billing_status or ""),
            "plan_code": str(existing_event.plan_code or "paid"),
            "duplicate": "true",
            "message": "Billing event je vec obradjen.",
        }

    obj = _extract_event_object(event)
    plan_code = _extract_plan_code(event)
    attributes = obj.get("attributes", {}) if isinstance(obj.get("attributes", {}), dict) else {}
    customer_id = str(attributes.get("customer_id", "") or "")
    subscription_id = str(obj.get("id", "") or "")
    current_period_end = str(attributes.get("renews_at", "") or attributes.get("trial_ends_at", "") or attributes.get("ends_at", "") or "")
    user = get_user_by_email(email)

    if event_id:
        record_billing_event(
            provider="lemon_squeezy",
            provider_event_id=event_id,
            event_type=event_type,
            user_id=int(user.id) if user is not None else 0,
            email=email,
            payload_json=json.dumps(event, ensure_ascii=False),
        )

    event_to_status = {
        "subscription_created": str(attributes.get("status", "") or "trial"),
        "subscription_updated": str(attributes.get("status", "") or "active"),
        "subscription_cancelled": "canceled",
        "subscription_resumed": "active",
        "order_created": "active",
        "order_refunded": "canceled",
    }
    billing_status = str(event_to_status.get(event_type, "") or "").strip().lower()
    if not billing_status:
        if event_id:
            update_billing_event_status(
                event_id,
                status="ignored",
                user_id=int(user.id) if user is not None else 0,
                email=email,
                plan_code=str(plan_code or "paid"),
                error_message="unsupported_event_type",
            )
        return {
            "ok": "false",
            "event_id": event_id,
            "event_type": event_type,
            "message": "Nepodrzan billing event.",
        }

    summary = apply_billing_status_to_user(email, billing_status, plan_code)
    user = get_user_by_email(email)
    if user is not None:
        upsert_user_subscription(
            user_id=int(user.id),
            provider="lemon_squeezy",
            plan_code=str(plan_code or "paid"),
            billing_status=billing_status,
            customer_id=customer_id,
            subscription_id=subscription_id,
            current_period_end=current_period_end,
        )
        summary = get_billing_summary_for_email(email)

    if event_id:
        update_billing_event_status(
            event_id,
            status="processed" if summary is not None else "failed",
            user_id=int(user.id) if user is not None else 0,
            email=email,
            billing_status=billing_status,
            plan_code=str(plan_code or "paid"),
            error_message="" if summary is not None else "billing_event_not_applied",
        )

    return {
        "ok": "true" if summary is not None else "false",
        "event_id": event_id,
        "event_type": event_type,
        "email": email,
        "billing_status": billing_status,
        "plan_code": str(plan_code or "paid"),
        "message": "Billing event je obradjen." if summary is not None else "Billing event nije upisan.",
    }
