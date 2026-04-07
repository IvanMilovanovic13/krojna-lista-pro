# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from dataclasses import dataclass
from typing import Any

import requests

from app_config import get_app_config
from project_store import get_user_by_email, get_user_subscription, upsert_user_subscription

_LOG = logging.getLogger(__name__)
_API_BASE = "https://api.lemonsqueezy.com/v1"


@dataclass(frozen=True)
class BillingActionResult:
    ok: bool
    message: str
    url: str = ""


def _is_placeholder_like(value: str, *, kind: str = "") -> bool:
    raw = str(value or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    if any(token in lowered for token in ("change-me", "promeni-me", "placeholder", "example", "tvoj-domen", "...")):
        return True
    if kind == "lemonsqueezy_api_key":
        return lowered.endswith("...") or lowered in {"api_key", "test_api_key", "live_api_key"}
    if kind == "lemonsqueezy_webhook_secret":
        return lowered in {"webhook_secret", "signing_secret"}
    if kind == "store_id":
        return lowered in {"store_id", "12345"}
    if kind == "store_subdomain":
        return lowered in {"store-subdomain", "your-store"}
    if kind == "variant_id":
        return lowered in {"variant_id", "123456"}
    return False


def _api_headers() -> dict[str, str]:
    cfg = get_app_config()
    api_key = str(cfg.lemon_squeezy_api_key or "").strip()
    if not api_key:
        raise RuntimeError("LEMON_SQUEEZY_API_KEY nije postavljen.")
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {api_key}",
    }


def _request(method: str, path: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.request(
        method=method.upper(),
        url=f"{_API_BASE}{path}",
        headers=_api_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    parsed = response.json()
    return parsed if isinstance(parsed, dict) else {}


def ensure_subscription_shell(email: str):
    user = get_user_by_email(email)
    if user is None:
        raise RuntimeError("Korisnik nije pronadjen za billing zapis.")
    existing = get_user_subscription(int(user.id))
    if existing is not None:
        return existing
    return upsert_user_subscription(
        user_id=int(user.id),
        provider="lemon_squeezy",
        plan_code="trial",
        billing_status="trial",
    )


def _resolve_variant_id(plan_code: str) -> str:
    cfg = get_app_config()
    clean_plan = str(plan_code or "pro_monthly").strip().lower()
    mapping = {
        "pro_weekly": str(cfg.lemon_squeezy_variant_id_weekly or "").strip(),
        "pro_monthly": str(cfg.lemon_squeezy_variant_id_monthly or "").strip(),
        "trial_weekly": str(cfg.lemon_squeezy_variant_id_weekly or "").strip(),
    }
    variant_id = mapping.get(clean_plan, "")
    if not variant_id:
        raise RuntimeError(f"Lemon Squeezy variant ID nije postavljen za plan '{clean_plan}'.")
    return variant_id


def get_billing_runtime_status() -> dict[str, str]:
    cfg = get_app_config()
    api_key = str(cfg.lemon_squeezy_api_key or "").strip()
    webhook_secret = str(cfg.lemon_squeezy_webhook_secret or "").strip()
    store_id = str(cfg.lemon_squeezy_store_id or "").strip()
    store_subdomain = str(cfg.lemon_squeezy_store_subdomain or "").strip()
    weekly_variant = str(cfg.lemon_squeezy_variant_id_weekly or "").strip()
    monthly_variant = str(cfg.lemon_squeezy_variant_id_monthly or "").strip()
    return {
        "provider": "lemon_squeezy",
        "has_api_key": "true" if not _is_placeholder_like(api_key, kind="lemonsqueezy_api_key") else "false",
        "has_webhook_secret": "true" if not _is_placeholder_like(webhook_secret, kind="lemonsqueezy_webhook_secret") else "false",
        "has_store_id": "true" if not _is_placeholder_like(store_id, kind="store_id") else "false",
        "has_store_subdomain": "true" if not _is_placeholder_like(store_subdomain, kind="store_subdomain") else "false",
        "has_variant_id_weekly": "true" if not _is_placeholder_like(weekly_variant, kind="variant_id") else "false",
        "has_variant_id_monthly": "true" if not _is_placeholder_like(monthly_variant, kind="variant_id") else "false",
        "checkout_success_url": str(cfg.lemon_squeezy_checkout_success_url or ""),
        "portal_url": (
            f"https://{store_subdomain}.lemonsqueezy.com/billing"
            if store_subdomain and not _is_placeholder_like(store_subdomain, kind="store_subdomain")
            else ""
        ),
    }


def create_checkout_session_for_email(email: str, *, plan_code: str = "pro_monthly") -> BillingActionResult:
    user = get_user_by_email(email)
    if user is None:
        return BillingActionResult(False, "Korisnik nije pronadjen za Lemon Squeezy checkout.")

    cfg = get_app_config()
    primary_variant_id = _resolve_variant_id(plan_code)
    enabled_variants = [
        int(variant_id)
        for variant_id in {
            str(cfg.lemon_squeezy_variant_id_weekly or "").strip(),
            str(cfg.lemon_squeezy_variant_id_monthly or "").strip(),
        }
        if variant_id.isdigit()
    ]

    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "product_options": {
                    "redirect_url": str(cfg.lemon_squeezy_checkout_success_url or ""),
                    "enabled_variants": enabled_variants,
                },
                "checkout_data": {
                    "email": str(user.email),
                    "name": str(user.display_name or "").strip(),
                    "custom": {
                        "user_id": str(user.id),
                        "user_email": str(user.email),
                        "plan_code": str(plan_code),
                    },
                },
                "checkout_options": {
                    "subscription_preview": True,
                },
                "test_mode": str(cfg.app_env or "").strip().lower() != "production",
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": str(cfg.lemon_squeezy_store_id)}},
                "variant": {"data": {"type": "variants", "id": str(primary_variant_id)}},
            },
        }
    }

    try:
        parsed = _request("POST", "/checkouts", payload=payload)
        data = parsed.get("data", {}) if isinstance(parsed.get("data", {}), dict) else {}
        attributes = data.get("attributes", {}) if isinstance(data.get("attributes", {}), dict) else {}
        checkout_url = str(attributes.get("url", "") or "").strip()
        checkout_id = str(data.get("id", "") or "").strip()
        if not checkout_url:
            raise RuntimeError("Lemon Squeezy checkout nije vratio URL.")
        base = ensure_subscription_shell(str(user.email))
        try:
            upsert_user_subscription(
                user_id=int(user.id),
                provider="lemon_squeezy",
                plan_code=str(plan_code),
                billing_status=str(base.billing_status),
                customer_id=str(base.customer_id),
                subscription_id=str(base.subscription_id),
                checkout_url=checkout_url,
                portal_url=str(base.portal_url),
                current_period_end=str(base.current_period_end),
            )
        except Exception as persist_ex:
            _LOG.debug("create_checkout_session_for_email persist failed: %s", persist_ex)
        return BillingActionResult(True, f"Lemon Squeezy checkout je pripremljen ({checkout_id}).", checkout_url)
    except Exception as ex:
        return BillingActionResult(False, f"Ne mogu da napravim Lemon Squeezy checkout: {ex}")


def create_customer_portal_for_email(email: str) -> BillingActionResult:
    user = get_user_by_email(email)
    if user is None:
        return BillingActionResult(False, "Korisnik nije pronadjen za Lemon Squeezy portal.")

    cfg = get_app_config()
    subscription = ensure_subscription_shell(str(user.email))
    subscription_id = str(subscription.subscription_id or "").strip()
    customer_id = str(subscription.customer_id or "").strip()

    try:
        portal_url = ""
        if subscription_id:
            parsed = _request("GET", f"/subscriptions/{subscription_id}")
            data = parsed.get("data", {}) if isinstance(parsed.get("data", {}), dict) else {}
            attributes = data.get("attributes", {}) if isinstance(data.get("attributes", {}), dict) else {}
            urls = attributes.get("urls", {}) if isinstance(attributes.get("urls", {}), dict) else {}
            portal_url = str(urls.get("customer_portal", "") or "").strip()
        elif customer_id:
            parsed = _request("GET", f"/customers/{customer_id}")
            data = parsed.get("data", {}) if isinstance(parsed.get("data", {}), dict) else {}
            attributes = data.get("attributes", {}) if isinstance(data.get("attributes", {}), dict) else {}
            urls = attributes.get("urls", {}) if isinstance(attributes.get("urls", {}), dict) else {}
            portal_url = str(urls.get("customer_portal", "") or "").strip()
        if not portal_url:
            store_subdomain = str(cfg.lemon_squeezy_store_subdomain or "").strip()
            if not store_subdomain:
                raise RuntimeError("Lemon Squeezy store subdomain nije postavljen.")
            portal_url = f"https://{store_subdomain}.lemonsqueezy.com/billing"
        try:
            upsert_user_subscription(
                user_id=int(user.id),
                provider="lemon_squeezy",
                plan_code=str(subscription.plan_code),
                billing_status=str(subscription.billing_status),
                customer_id=str(customer_id),
                subscription_id=str(subscription_id),
                checkout_url=str(subscription.checkout_url),
                portal_url=portal_url,
                current_period_end=str(subscription.current_period_end),
            )
        except Exception as persist_ex:
            _LOG.debug("create_customer_portal_for_email persist failed: %s", persist_ex)
        return BillingActionResult(True, "Lemon Squeezy Customer Portal je pripremljen.", portal_url)
    except Exception as ex:
        return BillingActionResult(False, f"Ne mogu da otvorim Lemon Squeezy Customer Portal: {ex}")


def construct_webhook_event(*, payload_bytes: bytes, webhook_signature: str = "") -> dict[str, Any]:
    cfg = get_app_config()
    secret = str(cfg.lemon_squeezy_webhook_secret or "").strip()
    raw_body = payload_bytes.decode("utf-8")
    if secret:
        if not str(webhook_signature or "").strip():
            raise RuntimeError("X-Signature header nedostaje.")
        digest = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, str(webhook_signature or "").strip()):
            raise RuntimeError("Lemon Squeezy webhook verifikacija nije uspela.")
    parsed = json.loads(raw_body)
    if not isinstance(parsed, dict):
        raise RuntimeError("Webhook payload mora biti JSON objekat.")
    return parsed
