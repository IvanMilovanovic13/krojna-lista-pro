# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json

from project_store import cleanup_auth_artifacts, cleanup_billing_events, cleanup_export_jobs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintenance helper for auth/session cleanup")
    parser.add_argument("--keep-login-attempts-days", type=int, default=30)
    parser.add_argument("--keep-reset-tokens-days", type=int, default=7)
    parser.add_argument("--keep-revoked-sessions-days", type=int, default=30)
    parser.add_argument("--keep-billing-processed-days", type=int, default=180)
    parser.add_argument("--keep-billing-failed-days", type=int, default=30)
    parser.add_argument("--keep-billing-ignored-days", type=int, default=30)
    parser.add_argument("--keep-export-done-days", type=int, default=30)
    parser.add_argument("--keep-export-failed-days", type=int, default=30)
    parser.add_argument("--keep-export-canceled-days", type=int, default=14)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    result = cleanup_auth_artifacts(
        keep_login_attempts_days=int(args.keep_login_attempts_days),
        keep_reset_tokens_days=int(args.keep_reset_tokens_days),
        keep_revoked_sessions_days=int(args.keep_revoked_sessions_days),
    )
    result.update(
        cleanup_billing_events(
            keep_processed_days=int(args.keep_billing_processed_days),
            keep_failed_days=int(args.keep_billing_failed_days),
            keep_ignored_days=int(args.keep_billing_ignored_days),
        )
    )
    result.update(
        cleanup_export_jobs(
            keep_done_days=int(args.keep_export_done_days),
            keep_failed_days=int(args.keep_export_failed_days),
            keep_canceled_days=int(args.keep_export_canceled_days),
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
