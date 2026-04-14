# -*- coding: utf-8 -*-
from __future__ import annotations

from billing_models import _status_to_access


def run_billing_on_trial_access_check() -> tuple[bool, str]:
    paid_access = _status_to_access("on_trial", "pro_weekly")
    if paid_access != ("paid", "paid_active"):
        return False, f"FAIL_on_trial_paid_mapping:{paid_access}"

    trial_access = _status_to_access("on_trial", "trial")
    if trial_access != ("trial", "trial_active"):
        return False, f"FAIL_on_trial_trial_mapping:{trial_access}"

    return True, "OK"
