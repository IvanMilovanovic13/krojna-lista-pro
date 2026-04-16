# -*- coding: utf-8 -*-
from __future__ import annotations

from types import SimpleNamespace

from project_store import SubscriptionRecord, UserRecord
import lemon_squeezy_service as ss


def run_stripe_customer_persist_resilience_check() -> tuple[bool, str]:
    original_get_user = ss.get_user_by_email
    original_ensure_shell = ss.ensure_subscription_shell
    original_request = ss._request
    original_upsert = ss.upsert_user_subscription
    original_get_app_config = ss.get_app_config

    user = UserRecord(
        id=52,
        email="customer-user@example.com",
        username="customer-user",
        display_name="Customer User",
        auth_mode="password",
        access_tier="trial",
        status="trial_active",
        email_verified=True,
        created_at="2026-03-28T10:00:00+00:00",
        updated_at="2026-03-28T10:00:00+00:00",
    )
    subscription = SubscriptionRecord(
        id=12,
        user_id=52,
        provider="lemon_squeezy",
        plan_code="trial",
        billing_status="trial",
        customer_id="",
        subscription_id="",
        checkout_url="",
        portal_url="",
        current_period_end="",
        created_at="2026-03-28T10:00:00+00:00",
        updated_at="2026-03-28T10:00:00+00:00",
    )

    try:
        ss.get_user_by_email = lambda email: user if str(email) == user.email else None
        ss.ensure_subscription_shell = lambda email: subscription
        ss._request = lambda method, path, payload=None: (_ for _ in ()).throw(RuntimeError("request_not_expected"))
        ss.get_app_config = lambda: SimpleNamespace(
            lemon_squeezy_store_subdomain="my-store",
            lemon_squeezy_variant_id_weekly="5678",
            lemon_squeezy_variant_id_monthly="6789",
            lemon_squeezy_checkout_success_url="https://app.example/nalog?checkout=success",
            lemon_squeezy_store_id="1234",
            app_env="staging",
        )

        def _raise_on_upsert(**_: object) -> SubscriptionRecord:
            raise RuntimeError("subscription_store_unavailable")

        ss.upsert_user_subscription = _raise_on_upsert

        portal = ss.create_customer_portal_for_email(user.email)
        if not portal.ok or str(portal.url) != "https://my-store.lemonsqueezy.com/billing":
            return False, f"FAIL_customer_portal_fallback:{portal.ok}:{portal.url}:{portal.message}"
        return True, "OK"
    finally:
        ss.get_user_by_email = original_get_user
        ss.ensure_subscription_shell = original_ensure_shell
        ss._request = original_request
        ss.upsert_user_subscription = original_upsert
        ss.get_app_config = original_get_app_config
