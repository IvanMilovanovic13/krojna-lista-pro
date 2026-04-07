# -*- coding: utf-8 -*-
from __future__ import annotations

from lemon_squeezy_service import (
    BillingActionResult as StripeActionResult,
    construct_webhook_event as _construct_webhook_event,
    create_checkout_session_for_email,
    create_customer_portal_for_email,
    get_billing_runtime_status,
)


def get_stripe_runtime_status() -> dict[str, str]:
    runtime = get_billing_runtime_status()
    return {
        "has_secret_key": str(runtime.get("has_api_key", "false")),
        "has_publishable_key": "false",
        "has_webhook_secret": str(runtime.get("has_webhook_secret", "false")),
        "has_price_id_pro_monthly": str(runtime.get("has_variant_id_weekly", "false")),
        "has_price_id_pro_yearly": str(runtime.get("has_variant_id_monthly", "false")),
        "checkout_success_url": str(runtime.get("checkout_success_url", "")),
        "checkout_cancel_url": "",
        "portal_return_url": str(runtime.get("portal_url", "")),
        "provider": "lemon_squeezy",
    }


def construct_webhook_event(*, payload_bytes: bytes, stripe_signature: str = "", webhook_signature: str = "") -> dict[str, object]:
    return _construct_webhook_event(
        payload_bytes=payload_bytes,
        webhook_signature=str(webhook_signature or stripe_signature or ""),
    )
