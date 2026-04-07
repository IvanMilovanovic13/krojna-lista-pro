# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path

from billing_webhooks import process_billing_webhook_payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Billing webhook test helper")
    parser.add_argument("--event-file", required=True, help="Path to JSON event payload")
    parser.add_argument("--secret", default="", help="Webhook secret override")
    parser.add_argument("--stripe-signature", default="", help="Legacy signature argument")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    payload_bytes = Path(args.event_file).read_bytes()
    payload = json.loads(payload_bytes.decode("utf-8"))
    result = process_billing_webhook_payload(
        payload,
        provided_secret=str(args.secret or ""),
        payload_bytes=payload_bytes,
        webhook_signature=str(args.stripe_signature or ""),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
