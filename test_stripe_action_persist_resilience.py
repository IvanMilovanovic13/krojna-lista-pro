# -*- coding: utf-8 -*-
from __future__ import annotations

from types import SimpleNamespace

from project_store import SubscriptionRecord, UserRecord
import lemon_squeezy_service as ss


def run_stripe_action_persist_resilience_check() -> tuple[bool, str]:
    original_get_user = ss.get_user_by_email
    original_request = ss._request
    original_ensure_shell = ss.ensure_subscription_shell
    original_upsert = ss.upsert_user_subscription
    original_get_app_config = ss.get_app_config

    user = UserRecord(
        id=41,
        email="billing-user@example.com",
        display_name="Billing User",
        auth_mode="password",
        access_tier="trial",
        status="trial_active",
        created_at="2026-03-28T10:00:00+00:00",
        updated_at="2026-03-28T10:00:00+00:00",
    )
    subscription = SubscriptionRecord(
        id=9,
        user_id=41,
        provider="lemon_squeezy",
        plan_code="trial",
        billing_status="trial",
        customer_id="cus_test_123",
        subscription_id="sub_test_123",
        checkout_url="",
        portal_url="",
        current_period_end="",
        created_at="2026-03-28T10:00:00+00:00",
        updated_at="2026-03-28T10:00:00+00:00",
    )

    def _fake_request(method: str, path: str, *, payload=None):
        if method == "POST" and path == "/checkouts":
            return {"data": {"id": "checkout_123", "attributes": {"url": "https://checkout.example/session"}}}
        if method == "GET" and path == "/subscriptions/sub_test_123":
            return {
                "data": {
                    "id": "sub_test_123",
                    "attributes": {"urls": {"customer_portal": "https://portal.example/session"}},
                }
            }
        raise RuntimeError(f"unexpected_request:{method}:{path}:{payload}")

    try:
        ss.get_user_by_email = lambda email: user if str(email) == user.email else None
        ss._request = _fake_request
        ss.ensure_subscription_shell = lambda email: subscription
        ss.get_app_config = lambda: SimpleNamespace(
            lemon_squeezy_variant_id_weekly="5678",
            lemon_squeezy_variant_id_monthly="6789",
            lemon_squeezy_checkout_success_url="https://app.example/nalog?checkout=success",
            lemon_squeezy_store_id="1234",
            app_env="staging",
            lemon_squeezy_store_subdomain="my-store",
        )

        def _raise_on_upsert(**_: object) -> SubscriptionRecord:
            raise RuntimeError("subscription_store_unavailable")

        ss.upsert_user_subscription = _raise_on_upsert

        checkout = ss.create_checkout_session_for_email(user.email, plan_code="pro_monthly")
        if not checkout.ok or str(checkout.url) != "https://checkout.example/session":
            return False, f"FAIL_checkout_persist_resilience:{checkout.ok}:{checkout.url}:{checkout.message}"

        portal = ss.create_customer_portal_for_email(user.email)
        if not portal.ok or str(portal.url) != "https://portal.example/session":
            return False, f"FAIL_portal_persist_resilience:{portal.ok}:{portal.url}:{portal.message}"

        return True, "OK"
    finally:
        ss.get_user_by_email = original_get_user
        ss._request = original_request
        ss.ensure_subscription_shell = original_ensure_shell
        ss.upsert_user_subscription = original_upsert
        ss.get_app_config = original_get_app_config
