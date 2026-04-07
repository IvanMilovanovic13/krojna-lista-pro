# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def run_billing_ui_runtime_guard_check() -> tuple[bool, str]:
    auth_tab = Path(__file__).with_name("ui_auth_tab.py").read_text(encoding="utf-8")
    nova_tab = Path(__file__).with_name("ui_nova_tab.py").read_text(encoding="utf-8")
    access_gate = Path(__file__).with_name("ui_access_gate.py").read_text(encoding="utf-8")

    required_auth = [
        "stripe_ready = bool(billing.get('stripe_ready', False))",
        "stripe_ready,",
        "stripe_ready and bool(billing.get('has_portal', False))",
    ]
    missing_auth = [item for item in required_auth if item not in auth_tab]
    if missing_auth:
        return False, f"FAIL_billing_ui_guard_auth:{', '.join(missing_auth)}"

    required_nova = [
        "stripe_ready = bool(payload.get('stripe_ready', False))",
        "if not stripe_ready:",
        "if primary_mode != 'none' and str(primary_btn or '').strip():",
        "stripe_ready and bool(payload.get('has_portal', False))",
    ]
    missing_nova = [item for item in required_nova if item not in nova_tab]
    if missing_nova:
        return False, f"FAIL_billing_ui_guard_nova:{', '.join(missing_nova)}"

    required_gate = [
        "stripe_ready = bool(billing.get('stripe_ready', False))",
        "if stripe_ready and (bool(billing.get('has_checkout', False)) or str(billing.get('access_tier', '') or '') != 'paid'):",
        "if stripe_ready and bool(billing.get('has_portal', False)):",
    ]
    missing_gate = [item for item in required_gate if item not in access_gate]
    if missing_gate:
        return False, f"FAIL_billing_ui_guard_gate:{', '.join(missing_gate)}"

    return True, "OK"
