# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json

from app_config import get_public_runtime_config
from export_jobs import get_export_runtime_summary
from project_store import (
    get_auth_runtime_summary,
    get_billing_event_summary,
    get_export_job_summary,
    get_project_store_runtime_info,
)
from release_readiness import get_release_readiness_report
from stripe_service import get_stripe_runtime_status


def main() -> int:
    parser = argparse.ArgumentParser(description="Runtime diagnostics and readiness checks.")
    parser.add_argument(
        "--readiness",
        action="store_true",
        help="Emit staging/production readiness report instead of raw runtime info.",
    )
    parser.add_argument(
        "--target",
        default="production",
        choices=["development", "staging", "production"],
        help="Readiness target environment.",
    )
    args = parser.parse_args()

    if args.readiness:
        payload = get_release_readiness_report(target=str(args.target))
    else:
        payload = {
            "app_config": get_public_runtime_config(),
            "project_store": get_project_store_runtime_info(),
            "auth_runtime": get_auth_runtime_summary(),
            "export_jobs": get_export_runtime_summary(),
            "export_job_counts": get_export_job_summary(),
            "stripe": get_stripe_runtime_status(),
            "billing_events": get_billing_event_summary(),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
