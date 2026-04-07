# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_store import get_project_store_runtime_info, write_store_snapshot_file
from postgres_store_migration import get_postgres_schema_sql, import_snapshot_to_postgres


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project store admin helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("runtime", help="Show current project store runtime info")

    export_parser = sub.add_parser("export", help="Export store snapshot to JSON")
    export_parser.add_argument(
        "--out",
        default=str(Path("data") / "project_store_snapshot.json"),
        help="Output JSON file path",
    )

    sub.add_parser("postgres-schema", help="Print Postgres schema SQL")

    import_parser = sub.add_parser("postgres-import", help="Import exported snapshot into Postgres")
    import_parser.add_argument("--snapshot", required=True, help="Snapshot JSON path")
    import_parser.add_argument("--database-url", default="", help="Target Postgres DATABASE_URL")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "runtime":
        print(json.dumps(get_project_store_runtime_info(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "export":
        out = write_store_snapshot_file(str(args.out))
        print(out)
        return 0

    if args.command == "postgres-schema":
        print(get_postgres_schema_sql())
        return 0

    if args.command == "postgres-import":
        result = import_snapshot_to_postgres(
            snapshot_path=str(args.snapshot),
            database_url=str(args.database_url or ""),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
