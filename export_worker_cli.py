# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json

from export_jobs import get_export_runtime_summary, run_export_worker_loop, run_export_worker_once


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dedicated export worker for queued export jobs.")
    parser.add_argument("--once", action="store_true", help="Process at most one queued export job and exit.")
    parser.add_argument("--max-loops", type=int, default=0, help="Limit worker polling loops for diagnostics/testing.")
    parser.add_argument("--poll-seconds", type=int, default=0, help="Polling interval for dedicated worker loop.")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if args.once:
        processed = run_export_worker_once()
    else:
        processed = run_export_worker_loop(
            poll_seconds=int(args.poll_seconds or 0) or None,
            max_loops=int(args.max_loops or 0) or None,
        )
    payload = {
        "processed": int(processed),
        "runtime": get_export_runtime_summary(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
